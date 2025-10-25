"""
AI Poster Generation Service using Google Gemini 2.5 Flash
Clean, production-ready implementation for textile poster generation
"""
import os
import logging
import time
import uuid
from typing import Dict, List, Any, Optional
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .ai_caption_service import AICaptionService
from .brand_overlay_service import BrandOverlayService

# Import Google GenAI
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    logging.error("Google GenAI not available. Please install: pip install google-genai")
    genai = None
    types = None
    GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIPosterService:
    """Service class for AI poster generation using Gemini 2.5 Flash"""

    @staticmethod
    def _build_image_config(types_module, aspect_ratio: str):
        """Builds an image generation config compatible across google-genai versions.
        Tries ImageConfig first; falls back to ImageGenerationConfig if available; otherwise None.
        """
        if not types_module:
            return None
        # Newer SDKs may rename ImageConfig to ImageGenerationConfig
        if hasattr(types_module, "ImageConfig"):
            try:
                return types_module.ImageConfig(aspect_ratio=aspect_ratio)
            except Exception:
                pass
        if hasattr(types_module, "ImageGenerationConfig"):
            try:
                return types_module.ImageGenerationConfig(aspect_ratio=aspect_ratio)
            except Exception:
                pass
        # If neither exists, do not pass image_config at all
        return None

    @staticmethod
    def _choose_dimensions_for_ratio(aspect_ratio: str, max_width: int = 1536) -> Optional[tuple]:
        """Return (width, height) tuple for a reasonable max edge size while matching ratio.
        Uses max dimension ≈ 1536 to balance quality and latency.
        """
        # Normalize common ratios
        ar = str(aspect_ratio or "1:1").strip()
        choices = {
            "1:1": (1024, 1024),
            "16:9": (1536, 864),
            "9:16": (864, 1536),
            "4:5": (1024, 1280),
            "5:4": (1280, 1024),
            "3:2": (1536, 1024),
            "2:3": (1024, 1536),
        }
        if ar in choices:
            return choices[ar]
        # Fallback: parse float and compute based on provided max_width
        try:
            if ":" in ar:
                w, h = ar.split(":", 1)
                ratio = float(w) / float(h)
            else:
                ratio = float(ar)
            width = max_width
            height = int(round(width / ratio))
            return (width, height)
        except Exception:
            return None

    @classmethod
    def _build_image_config_with_dimensions(cls, types_module, aspect_ratio: str, max_width: int = 1536):
        """Attempt to build an image config using explicit dimensions supported by SDK.
        Tries size, width/height variations across ImageConfig and ImageGenerationConfig.
        Returns None if not constructible.
        """
        if not types_module:
            return None
        dims = cls._choose_dimensions_for_ratio(aspect_ratio, max_width=max_width)
        if not dims:
            return None
        width, height = dims
        candidates = []
        if hasattr(types_module, "ImageConfig"):
            candidates.append(types_module.ImageConfig)
        if hasattr(types_module, "ImageGenerationConfig"):
            candidates.append(types_module.ImageGenerationConfig)
        for ctor in candidates:
            # Try common field names
            for kwargs in (
                {"size": f"{width}x{height}"},
                {"width": width, "height": height},
                {"image_size": f"{width}x{height}"},
            ):
                try:
                    return ctor(**kwargs)
                except Exception:
                    continue
        return None

    @classmethod
    def _build_best_dimension_configs(cls, types_module, aspect_ratio: str) -> List[Any]:
        """Return a list of image_config objects trying multiple explicit sizes for better compliance."""
        if not types_module:
            return []
        configs: List[Any] = []
        for max_w in (1024, 1280, 1536, 1792, 2048):
            try:
                cfg = cls._build_image_config_with_dimensions(types_module, aspect_ratio, max_width=max_w)
                if cfg is not None:
                    configs.append(cfg)
            except Exception:
                continue
        # De-duplicate by repr
        seen = set()
        unique = []
        for c in configs:
            r = repr(c)
            if r in seen:
                continue
            seen.add(r)
            unique.append(c)
        return unique

    @staticmethod
    def _parse_aspect_ratio(aspect_ratio: str) -> Optional[float]:
        """Parse aspect ratio like '16:9' or '1:1' or '4:5' into a float width/height.
        Returns None if parsing fails.
        """
        try:
            if not aspect_ratio:
                return None
            if isinstance(aspect_ratio, (int, float)):
                return float(aspect_ratio)
            if ":" in aspect_ratio:
                parts = aspect_ratio.split(":", 1)
                w = float(parts[0].strip())
                h = float(parts[1].strip())
                if h == 0:
                    return None
                return w / h
            # If it's a single number string
            return float(aspect_ratio)
        except Exception:
            return None

    @staticmethod
    def _normalize_aspect_ratio_value(aspect_ratio: str) -> str:
        """Normalize aspect ratio to a canonical string the SDK expects, e.g., '1:1', '16:9', '4:5'.
        Accepts float (as string) and returns nearest common ratio when possible.
        """
        if not aspect_ratio:
            return "1:1"
        s = str(aspect_ratio).strip()
        if ":" in s:
            return s
        # Convert float-like to nearest known ratios
        try:
            val = float(s)
            # Map a few common floats
            candidates = {
                1.0: "1:1",
                16/9: "16:9",
                9/16: "9:16",
                4/5: "4:5",
                5/4: "5:4",
                3/2: "3:2",
                2/3: "2:3",
            }
            closest = min(candidates.keys(), key=lambda k: abs(k - val))
            if abs(closest - val) < 0.02:
                return candidates[closest]
        except Exception:
            pass
        return s

    @classmethod
    def _is_aspect_ratio_match(cls, image: Image.Image, aspect_ratio: str, tolerance: float = 0.005) -> bool:
        """Return True if image's aspect ratio matches requested ratio within tolerance."""
        target = cls._parse_aspect_ratio(aspect_ratio)
        if not target:
            return True
        w, h = image.size
        if w == 0 or h == 0:
            return True
        current = w / h
        return abs(current - target) <= tolerance

    @classmethod
    def _enforce_aspect_ratio(cls, image: Image.Image, aspect_ratio: str) -> Image.Image:
        """Center-crop the PIL image to match the target aspect ratio.
        If parsing fails, returns image unchanged.
        """
        target = cls._parse_aspect_ratio(aspect_ratio)
        if not target:
            return image
        width, height = image.size
        if width == 0 or height == 0:
            return image
        current = width / height
        # Close enough: do nothing
        if abs(current - target) < 1e-3:
            return image
        # Need to crop: if current > target -> too wide => crop width; else crop height
        if current > target:
            # New width based on target
            new_width = int(round(height * target))
            left = (width - new_width) // 2
            right = left + new_width
            top = 0
            bottom = height
        else:
            # Too tall -> crop height
            new_height = int(round(width / target))
            top = (height - new_height) // 2
            bottom = top + new_height
            left = 0
            right = width
        try:
            return image.crop((left, top, right, bottom))
        except Exception:
            return image
    
    @staticmethod
    def _ensure_min_short_side(image: Image.Image, min_short_side: int = 1080) -> Image.Image:
        """Upscale the image so that the shorter side is at least min_short_side.
        Never downsizes; preserves aspect ratio.
        """
        try:
            width, height = image.size
            if width == 0 or height == 0:
                return image
            current_short = min(width, height)
            if current_short >= min_short_side:
                return image
            scale = float(min_short_side) / float(current_short)
            new_width = max(1, int(round(width * scale)))
            new_height = max(1, int(round(height * scale)))
            # Pillow 10 uses Image.Resampling
            resample = getattr(Image, "Resampling", None)
            if resample is not None:
                return image.resize((new_width, new_height), resample.LANCZOS)
            # Fallback for older Pillow
            return image.resize((new_width, new_height), Image.LANCZOS)
        except Exception:
            return image
    
    def __init__(self):
        """Initialize the AI poster service"""
        self.api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, 'GEMINI_API_KEY', None)
        self.client = None
        self.caption_service = AICaptionService()
        self.brand_overlay_service = BrandOverlayService()
        
        if not GENAI_AVAILABLE:
            logger.error("Google GenAI library not available")
            return
            
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not configured")
            return
            
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            self.client = None
    
    def generate_from_prompt(self, prompt: str, aspect_ratio: str = "1:1", user=None) -> Dict[str, Any]:
        """
        Generate poster image from text prompt only
        
        Args:
            prompt: Text description for the poster
            aspect_ratio: Image aspect ratio (1:1, 16:9, 4:5)
            
        Returns:
            Dict containing status and image path
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating poster from prompt: {prompt[:50]}...")
            
            # Check if user has company profile for branding
            has_branding = False
            if user:
                try:
                    from users.models import CompanyProfile
                    company_profile = getattr(user, 'company_profile', None)
                    if company_profile and company_profile.has_complete_profile:
                        has_branding = True
                        logger.info("User has complete company profile - will apply branding")
                except Exception as e:
                    logger.warning(f"Error checking company profile: {e}")
            
            # Create base prompt with enhanced instructions for better image generation
            normalized_ar = self._normalize_aspect_ratio_value(aspect_ratio)
            ar_directive = f"Strict aspect ratio: {normalized_ar}. Generate the canvas at {normalized_ar} without padding, borders, or letterboxing."
            
            # Enhanced contrast and clarity instructions for main subject with gradient transitions
            contrast_instructions = """
            
            MAIN SUBJECT ENHANCEMENT:
            - Always enhance the contrast and clarity of the main subject so it stands out clearly from the background
            - Ensure the main subject has strong visual presence and is the focal point of the image
            - Use lighting, shadows, and color contrast to make the subject pop
            - Keep the main subject centered within the safe visual zone (avoiding top 20% and bottom 15%)
            - Maintain clear subject contrast against the background while ensuring smooth tonal transitions
            """
            
            # Determine if prompt is short/simple and handle accordingly
            is_simple_prompt = len(prompt.strip().split()) <= 5 and not any(word in prompt.lower() for word in ['design', 'create', 'generate', 'make', 'show'])
            
            if is_simple_prompt:
                # For simple prompts, send as-is with minimal additions
                base_prompt = f"{ar_directive}\n{contrast_instructions}\n{prompt}"
            else:
                # For complex prompts, add more detailed instructions
                base_prompt = f"{ar_directive}\n{contrast_instructions}\n{prompt}"
            
            if has_branding:
                # Add instructions for seamless gradient transitions in overlay areas
                branding_layout_instructions = """
                
                LAYOUT REQUIREMENTS:
                - Maintain all main content and primary text within the center safe zone (middle 65% of image)
                - When generating the poster, make sure any main subject mentioned in the prompt is fully visible and completely inside the frame. Do not crop or cut off the subject's head, body, or important parts. Keep proper framing and composition so the entire subject fits naturally within the image.
                """
                base_prompt = f"{base_prompt}{branding_layout_instructions}"
            else:
                # Add instructions to avoid random brand names when no branding is provided with gradient transitions
                no_branding_instructions = """
                
                DESIGN REQUIREMENTS:
                - Do NOT include any company names, brand names, or business names in the design
                - Do NOT add any random or placeholder brand names, prices, or marketing phrases
                - Focus purely on the visual design and aesthetic elements with full-bleed composition
                - Do not include any text that suggests a specific company or brand
                - Avoid adding any blank margins or white bands; fill the full canvas edge-to-edge
                - Keep main content centered in the safe visual zone (middle 65% of image)
                - When generating the poster, make sure any main subject mentioned in the prompt is fully visible and completely inside the frame. Do not crop or cut off the subject's head, body, or important parts. Keep proper framing and composition so the entire subject fits naturally within the image.
                """
                base_prompt = f"{base_prompt}{no_branding_instructions}"
            
            # Try multiple prompt variations if the first one fails
            prompts_to_try = [
                base_prompt,
                f"Create a high-quality image: {base_prompt}",
                f"Generate a professional image: {base_prompt}",
                f"Design an image: {base_prompt}"
            ]
            
            for attempt, current_prompt in enumerate(prompts_to_try):
                logger.info(f"Attempt {attempt + 1}: Trying prompt: {current_prompt[:50]}...")
                
                # Configure image generation (prefer explicit dimensions; fallback to aspect_ratio)
                image_config = self._build_image_config_with_dimensions(types, normalized_ar) or \
                               self._build_image_config(types, normalized_ar)
                
                config_kwargs = {"response_modalities": ['Image']}
                if image_config is not None:
                    config_kwargs["image_config"] = image_config
                else:
                    logger.info("Image generation: image_config not available; relying on prompt directive for aspect ratio")
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=[current_prompt],
                    config=types.GenerateContentConfig(**config_kwargs),
                )
            
                # Process response and save image
                if not response.candidates or len(response.candidates) == 0:
                    logger.warning(f"Attempt {attempt + 1}: No candidates returned from Gemini model")
                    if attempt < len(prompts_to_try) - 1:
                        continue
                    return {"status": "error", "message": "No candidates returned from model"}
                
                candidate = response.candidates[0]
                logger.info(f"Attempt {attempt + 1}: Gemini response candidate: {candidate}")
                
                if not candidate.content:
                    logger.warning(f"Attempt {attempt + 1}: No content in Gemini response candidate")
                    if attempt < len(prompts_to_try) - 1:
                        continue
                    return {"status": "error", "message": "No content returned from model"}
                
                if not candidate.content.parts:
                    logger.warning(f"Attempt {attempt + 1}: No content parts in Gemini response")
                    logger.warning(f"Content object: {candidate.content}")
                    if attempt < len(prompts_to_try) - 1:
                        continue
                    return {"status": "error", "message": "No content parts returned from model"}
                
                logger.info(f"Attempt {attempt + 1}: Found {len(candidate.content.parts)} content parts")
                
                # Try to process the image
                image_processed = False
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data is not None:
                        try:
                            image = Image.open(BytesIO(part.inline_data.data))

                            # Strict AR enforcement with retries
                            max_retries = 2
                            attempt_idx = 0
                            while not self._is_aspect_ratio_match(image, normalized_ar) and attempt_idx < max_retries:
                                logger.warning(f"Generated image AR mismatch (attempt {attempt_idx+1}); retrying with strict dimensions")
                                # Build a series of image_config attempts with escalating dimensions
                                dim_configs = self._build_best_dimension_configs(types, normalized_ar) or [self._build_image_config(types, normalized_ar)]
                                # Include exact pixel directive in prompt
                                w_h = self._choose_dimensions_for_ratio(normalized_ar, max_width=1536)
                                px_directive = f"Generate exactly {w_h[0]}x{w_h[1]} pixels, no padding or borders. " if w_h else ""
                                stricter_prompt = f"ABSOLUTE REQUIREMENT: Output must be exactly {normalized_ar}. {px_directive}{current_prompt}"
                                retry_succeeded = False
                                for dim_config in dim_configs:
                                    retry_kwargs = dict(config_kwargs)
                                    if dim_config is not None:
                                        retry_kwargs["image_config"] = dim_config
                                    response_retry = self.client.models.generate_content(
                                        model="gemini-2.5-flash-image",
                                        contents=[stricter_prompt],
                                        config=types.GenerateContentConfig(**retry_kwargs),
                                    )
                                    for retry_part in response_retry.candidates[0].content.parts:
                                        if getattr(retry_part, 'inline_data', None) is not None:
                                            retry_img = Image.open(BytesIO(retry_part.inline_data.data))
                                            image = retry_img
                                            if self._is_aspect_ratio_match(image, normalized_ar):
                                                retry_succeeded = True
                                                break
                                    if retry_succeeded:
                                        break
                                attempt_idx += 1
                            # Fallback: if still mismatched after retries, enforce by center-cropping
                            if not self._is_aspect_ratio_match(image, normalized_ar):
                                logger.warning("Model did not honor aspect ratio after strict retries; enforcing via cropping")
                                image = self._enforce_aspect_ratio(image, normalized_ar)

                            # Generate unique filename
                            timestamp = int(time.time())
                            filename = f"generated_poster_{timestamp}.png"
                            output_path = f"generated_posters/{filename}"
                            
                            # Ensure minimum short side before saving
                            image = self._ensure_min_short_side(image, min_short_side=1080)

                            # Save to media storage
                            image_bytes = BytesIO()
                            image.save(image_bytes, format='PNG')
                            image_bytes.seek(0)
                            
                            saved_path = default_storage.save(output_path, ContentFile(image_bytes.getvalue()))
                            image_url = default_storage.url(saved_path)
                            # Ensure full URL for download
                            if not image_url.startswith('http'):
                                image_url = f"http://localhost:8000{image_url}"
                            
                            final_w, final_h = image.size
                            logger.info(f"Poster generated successfully on attempt {attempt + 1}: {saved_path}; size={final_w}x{final_h}")
                            
                            # Generate caption and hashtags for the poster
                            caption_result = self.generate_caption_and_hashtags(prompt, image_url)
                            
                            # Add brand overlay if user has company profile
                            final_result = {
                                "status": "success", 
                                "image_path": saved_path,
                                "image_url": image_url,
                                "filename": filename,
                                "width": final_w,
                                "height": final_h,
                                "aspect_ratio_final": f"{final_w}:{final_h}",
                                "caption": caption_result.get("caption", ""),
                                "full_caption": caption_result.get("full_caption", ""),
                                "hashtags": caption_result.get("hashtags", []),
                                "emoji": caption_result.get("emoji", ""),
                                "call_to_action": caption_result.get("call_to_action", ""),
                                "branding_applied": False
                            }
                            
                            # Apply brand overlay if user is provided and has company profile
                            logger.info(f"=== BRANDING DEBUG ===")
                            logger.info(f"User provided: {user}")
                            if user:
                                logger.info(f"User details: {user.username} ({user.email})")
                                try:
                                    from users.models import CompanyProfile
                                    company_profile = getattr(user, 'company_profile', None)
                                    logger.info(f"Company profile: {company_profile}")
                                    
                                    if company_profile:
                                        logger.info(f"Company name: {company_profile.company_name}")
                                        logger.info(f"Has logo: {bool(company_profile.logo)}")
                                        if company_profile.logo:
                                            logger.info(f"Logo path: {company_profile.logo.path}")
                                            logger.info(f"Logo file exists: {os.path.exists(company_profile.logo.path)}")
                                        else:
                                            logger.info("No logo uploaded")
                                        logger.info(f"Contact info: {company_profile.get_contact_info()}")
                                        logger.info(f"Profile complete: {company_profile.has_complete_profile}")
                                        
                                        if company_profile.has_complete_profile:
                                            logger.info("Applying brand overlay...")
                                            brand_result = self.brand_overlay_service.create_branded_poster(
                                                saved_path, company_profile
                                            )
                                            logger.info(f"Brand overlay result: {brand_result}")
                                            
                                            if brand_result.get('status') == 'success':
                                                logger.info("Brand overlay applied successfully!")
                                                final_result.update({
                                                    "image_path": brand_result.get("image_path", saved_path),
                                                    "image_url": brand_result.get("image_url", image_url),
                                                    "filename": brand_result.get("filename", filename),
                                                    "branding_applied": True,
                                                    "logo_added": brand_result.get("logo_added", False),
                                                    "contact_info_added": brand_result.get("contact_info_added", False),
                                                    "branding_metadata": brand_result.get("branding_metadata", {})
                                                })
                                            else:
                                                logger.warning(f"Brand overlay failed: {brand_result.get('message')}")
                                        else:
                                            logger.warning("Company profile is not complete - skipping branding")
                                            logger.warning(f"Missing: logo={not company_profile.logo}, contact={not company_profile.get_contact_info()}")
                                    else:
                                        logger.warning("No company profile found for user")
                                except Exception as brand_error:
                                    logger.error(f"Brand overlay error: {str(brand_error)}")
                                    import traceback
                                    traceback.print_exc()
                            else:
                                logger.warning("No user provided - skipping branding")
                            
                            return final_result
                        except Exception as img_error:
                            logger.error(f"Error processing image: {str(img_error)}")
                            continue
                
                if not image_processed:
                    logger.warning(f"Attempt {attempt + 1}: No valid image data found in response")
                    if attempt < len(prompts_to_try) - 1:
                        continue
                    return {"status": "error", "message": "No valid image data found in response"}
            
            return {"status": "error", "message": "All prompt attempts failed"}
            
        except Exception as e:
            logger.error(f"Error generating poster from prompt: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def generate_with_image(self, prompt: str, image_path: str, aspect_ratio: str = "1:1", user=None) -> Dict[str, Any]:
        """
        Generate edited poster using prompt + uploaded image with branding
        
        Args:
            prompt: Text description for the edit
            image_path: Path to uploaded image (Django storage path)
            aspect_ratio: Image aspect ratio (1:1, 16:9, 4:5)
            user: User object for automatic branding
            
        Returns:
            Dict containing status and image path
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating edited poster with prompt: {prompt[:50]}...")
            
            # Check if user has company profile for branding
            has_branding = False
            if user:
                try:
                    from users.models import CompanyProfile
                    company_profile = getattr(user, 'company_profile', None)
                    if company_profile and company_profile.has_complete_profile:
                        has_branding = True
                        logger.info("User has complete company profile - will apply branding")
                except Exception as e:
                    logger.warning(f"Error checking company profile: {e}")
            
            # Create base prompt with enhanced instructions for better image generation
            normalized_ar = self._normalize_aspect_ratio_value(aspect_ratio)
            ar_directive = f"Strict aspect ratio: {normalized_ar}. Generate the canvas at {normalized_ar} without padding, borders, or letterboxing."
            
            # Enhanced contrast and clarity instructions for main subject with gradient transitions
            contrast_instructions = """
            
            MAIN SUBJECT ENHANCEMENT:
            - Always enhance the contrast and clarity of the main subject so it stands out clearly from the background
            - Ensure the main subject has strong visual presence and is the focal point of the image
            - Use lighting, shadows, and color contrast to make the subject pop
            - Keep the main subject centered within the safe visual zone (avoiding top 20% and bottom 15%)
            - Maintain clear subject contrast against the background while ensuring smooth tonal transitions
            """
            
            # Determine if prompt is short/simple and handle accordingly
            is_simple_prompt = len(prompt.strip().split()) <= 5 and not any(word in prompt.lower() for word in ['design', 'create', 'generate', 'make', 'show'])
            
            if is_simple_prompt:
                # For simple prompts, send as-is with minimal additions
                base_prompt = f"{ar_directive}\n{contrast_instructions}\n{prompt}"
            else:
                # For complex prompts, add more detailed instructions
                base_prompt = f"{ar_directive}\n{contrast_instructions}\n{prompt}"
            
            if has_branding:
                # Add instructions for seamless gradient transitions in overlay areas
                branding_layout_instructions = """
                
                LAYOUT REQUIREMENTS:
                - Maintain all main content and primary text within the center safe zone (middle 65% of image)
                - When generating the poster, make sure any main subject mentioned in the prompt is fully visible and completely inside the frame. Do not crop or cut off the subject's head, body, or important parts. Keep proper framing and composition so the entire subject fits naturally within the image.
                """
                base_prompt = f"{base_prompt}{branding_layout_instructions}"
            else:
                # Add instructions to avoid random brand names when no branding is provided with gradient transitions
                no_branding_instructions = """
                
                DESIGN REQUIREMENTS:
                - Do NOT include any company names, brand names, or business names in the design
                - Do NOT add any random or placeholder brand names, prices, or marketing phrases
                - Focus purely on the visual design and aesthetic elements with full-bleed composition
                - Do not include any text that suggests a specific company or brand
                - Avoid adding any blank margins or white bands; fill the full canvas edge-to-edge
                - Keep main content centered in the safe visual zone (middle 65% of image)
                - When generating the poster, make sure any main subject mentioned in the prompt is fully visible and completely inside the frame. Do not crop or cut off the subject's head, body, or important parts. Keep proper framing and composition so the entire subject fits naturally within the image.
                """
                base_prompt = f"{base_prompt}{no_branding_instructions}"
            
            # Load and prepare image from Django storage
            try:
                # Try to get the file from Django storage
                with default_storage.open(image_path, 'rb') as f:
                    image_data = f.read()
            except Exception as storage_error:
                logger.error(f"Failed to open image from storage: {str(storage_error)}")
                # Fallback: try direct file system access
                try:
                    full_path = default_storage.path(image_path)
                    with open(full_path, "rb") as f:
                        image_data = f.read()
                except Exception as fs_error:
                    logger.error(f"Failed to open image from file system: {str(fs_error)}")
                    return {"status": "error", "message": f"Failed to load image: {str(fs_error)}"}
            
            # Create image part
            image_part = types.Part(
                inline_data=types.Blob(
                    data=image_data,
                    mime_type="image/jpeg"
                )
            )
            
            # Configure image generation (prefer explicit dimensions; fallback to aspect_ratio)
            image_config = self._build_image_config_with_dimensions(types, normalized_ar) or \
                           self._build_image_config(types, normalized_ar)
            
            config_kwargs = {"response_modalities": ['Image']}
            if image_config is not None:
                config_kwargs["image_config"] = image_config
            else:
                logger.info("Image generation: image_config not available; relying on prompt directive for aspect ratio")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[image_part, base_prompt],
                config=types.GenerateContentConfig(**config_kwargs),
            )
            
            # Process response and save image
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    edited_image = Image.open(BytesIO(part.inline_data.data))

                    # Strict AR enforcement with retries
                    max_retries = 2
                    attempt_idx = 0
                    while not self._is_aspect_ratio_match(edited_image, normalized_ar) and attempt_idx < max_retries:
                        logger.warning(f"Edited image AR mismatch (attempt {attempt_idx+1}); retrying with strict dimensions")
                        dim_configs = self._build_best_dimension_configs(types, normalized_ar) or [self._build_image_config(types, normalized_ar)]
                        w_h = self._choose_dimensions_for_ratio(normalized_ar, max_width=1536)
                        px_directive = f"Generate exactly {w_h[0]}x{w_h[1]} pixels, no padding or borders. " if w_h else ""
                        stricter_prompt = f"ABSOLUTE REQUIREMENT: Output must be exactly {normalized_ar}. {px_directive}{base_prompt}"
                        retry_succeeded = False
                        for dim_config in dim_configs:
                            retry_kwargs = dict(config_kwargs)
                            if dim_config is not None:
                                retry_kwargs["image_config"] = dim_config
                            response_retry = self.client.models.generate_content(
                                model="gemini-2.5-flash-image",
                                contents=[image_part, stricter_prompt],
                                config=types.GenerateContentConfig(**retry_kwargs),
                            )
                            for retry_part in response_retry.candidates[0].content.parts:
                                if getattr(retry_part, 'inline_data', None) is not None:
                                    retry_img = Image.open(BytesIO(retry_part.inline_data.data))
                                    edited_image = retry_img
                                    if self._is_aspect_ratio_match(edited_image, normalized_ar):
                                        retry_succeeded = True
                                        break
                            if retry_succeeded:
                                break
                        attempt_idx += 1
                    # Fallback: if still mismatched after retries, enforce by center-cropping
                    if not self._is_aspect_ratio_match(edited_image, normalized_ar):
                        logger.warning("Model did not honor aspect ratio for edit after strict retries; enforcing via cropping")
                        edited_image = self._enforce_aspect_ratio(edited_image, normalized_ar)
                    
                    # Generate unique filename
                    timestamp = int(time.time())
                    filename = f"edited_poster_{timestamp}.png"
                    output_path = f"generated_posters/{filename}"
                    
                    # Ensure minimum short side before saving
                    edited_image = self._ensure_min_short_side(edited_image, min_short_side=1080)

                    # Save to media storage
                    image_bytes = BytesIO()
                    edited_image.save(image_bytes, format='PNG')
                    image_bytes.seek(0)
                    
                    saved_path = default_storage.save(output_path, ContentFile(image_bytes.getvalue()))
                    image_url = default_storage.url(saved_path)
                    # Ensure full URL for download
                    if not image_url.startswith('http'):
                        image_url = f"http://localhost:8000{image_url}"
                    
                    final_w, final_h = edited_image.size
                    logger.info(f"Edited poster generated successfully: {saved_path}; size={final_w}x{final_h}")
                    
                    # Generate caption and hashtags for the poster
                    caption_result = self.generate_caption_and_hashtags(prompt, image_url)
                    
                    # Add brand overlay if user has company profile
                    final_result = {
                        "status": "success", 
                        "image_path": saved_path,
                        "image_url": image_url,
                        "filename": filename,
                        "width": final_w,
                        "height": final_h,
                        "aspect_ratio_final": f"{final_w}:{final_h}",
                        "caption": caption_result.get("caption", ""),
                        "full_caption": caption_result.get("full_caption", ""),
                        "hashtags": caption_result.get("hashtags", []),
                        "emoji": caption_result.get("emoji", ""),
                        "call_to_action": caption_result.get("call_to_action", ""),
                        "branding_applied": False
                    }
                    
                    # Apply brand overlay if user is provided and has company profile
                    logger.info(f"=== BRANDING DEBUG (EDIT POSTER) ===")
                    logger.info(f"User provided: {user}")
                    if user:
                        logger.info(f"User details: {user.username} ({user.email})")
                        try:
                            from users.models import CompanyProfile
                            company_profile = getattr(user, 'company_profile', None)
                            logger.info(f"Company profile: {company_profile}")
                            
                            if company_profile:
                                logger.info(f"Company name: {company_profile.company_name}")
                                logger.info(f"Has logo: {bool(company_profile.logo)}")
                                if company_profile.logo:
                                    logger.info(f"Logo path: {company_profile.logo.path}")
                                    logger.info(f"Logo file exists: {os.path.exists(company_profile.logo.path)}")
                                else:
                                    logger.info("No logo uploaded")
                                logger.info(f"Contact info: {company_profile.get_contact_info()}")
                                logger.info(f"Profile complete: {company_profile.has_complete_profile}")
                                
                                if company_profile.has_complete_profile:
                                    logger.info("Applying brand overlay to edited poster...")
                                    brand_result = self.brand_overlay_service.create_branded_poster(
                                        saved_path, company_profile
                                    )
                                    logger.info(f"Brand overlay result: {brand_result}")
                                    
                                    if brand_result.get('status') == 'success':
                                        logger.info("Brand overlay applied successfully to edited poster!")
                                        final_result.update({
                                            "image_path": brand_result.get("image_path", saved_path),
                                            "image_url": brand_result.get("image_url", image_url),
                                            "filename": brand_result.get("filename", filename),
                                            "branding_applied": True,
                                            "logo_added": brand_result.get("logo_added", False),
                                            "contact_info_added": brand_result.get("contact_info_added", False),
                                            "branding_metadata": brand_result.get("branding_metadata", {})
                                        })
                                    else:
                                        logger.warning(f"Brand overlay failed: {brand_result.get('message')}")
                                else:
                                    logger.warning("Company profile is not complete - skipping branding")
                                    logger.warning(f"Missing: logo={not company_profile.logo}, contact={not company_profile.get_contact_info()}")
                            else:
                                logger.warning("No company profile found for user")
                        except Exception as brand_error:
                            logger.error(f"Brand overlay error: {str(brand_error)}")
                            import traceback
                            traceback.print_exc()
                    else:
                        logger.warning("No user provided - skipping branding")
                    
                    return final_result
            
            return {"status": "error", "message": "No edited image returned from model"}
            
        except Exception as e:
            logger.error(f"Error generating edited poster: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def generate_composite(self, prompt: str, image_paths: List[str], aspect_ratio: str = "16:9") -> Dict[str, Any]:
        """
        Generate composite poster combining multiple images + text prompt
        
        Args:
            prompt: Text description for the composite
            image_paths: List of image file paths
            aspect_ratio: Image aspect ratio (1:1, 16:9, 4:5)
            
        Returns:
            Dict containing status and image path
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating composite poster with {len(image_paths)} images and prompt: {prompt[:50]}...")
            
            # Create enhanced prompt with smart layout guidance for branding areas
            spacing_instructions = """
            
            IMPORTANT LAYOUT REQUIREMENTS:
            - Keep the TOP-RIGHT corner (approximately 25% of image width and height) free of text but NOT empty - use background patterns, colors, or visual elements
            - Keep the BOTTOM area (bottom 18% of image height) free of text but NOT empty - use background patterns, colors, or visual elements  
            - Place all main text and visual elements in the CENTER and LEFT areas of the image
            - Ensure text is readable and doesn't overlap with reserved areas
            - Use the center-left 55% of the image for main content
            - Maintain all textual content within the middle 65% of the canvas
            - Fill the reserved areas with background elements, patterns, or colors - do not leave them blank
            - Make the design cohesive while keeping logo and contact areas text-free but visually rich
            - When generating the poster, make sure any main subject mentioned in the prompt (such as a man, woman, or product) is fully visible and completely inside the frame. Do not crop or cut off the subject's head, body, or important parts. Keep proper framing and composition so the entire subject fits naturally within the image.
            """
            
            # Create enhanced prompt with smart branding area guidance and AR directive
            normalized_ar = self._normalize_aspect_ratio_value(aspect_ratio)
            ar_directive = f"Strict aspect ratio: {normalized_ar}. Generate the canvas at {normalized_ar} without padding, borders, or letterboxing."
            enhanced_prompt = f"{ar_directive}\n{prompt}{spacing_instructions}"
            
            # Load all images
            image_parts = []
            for image_path in image_paths:
                try:
                    # Try to get the file from Django storage first
                    try:
                        with default_storage.open(image_path, 'rb') as f:
                            image_data = f.read()
                    except Exception as storage_error:
                        logger.warning(f"Failed to open image from storage: {str(storage_error)}")
                        # Fallback: try direct file system access
                        full_path = default_storage.path(image_path)
                        with open(full_path, "rb") as f:
                            image_data = f.read()
                    
                    image_part = types.Part(
                        inline_data=types.Blob(
                            data=image_data,
                            mime_type="image/jpeg"
                        )
                    )
                    image_parts.append(image_part)
                except Exception as e:
                    logger.warning(f"Failed to load image {image_path}: {str(e)}")
                    continue
            
            if not image_parts:
                return {"status": "error", "message": "No valid images provided"}
            
            # Add text prompt
            contents = image_parts + [enhanced_prompt]
            
            # Configure image generation (version-safe)
            image_config = self._build_image_config(types, normalized_ar)
            
            config_kwargs = {"response_modalities": ['Image']}
            if image_config is not None:
                config_kwargs["image_config"] = image_config
            else:
                logger.info("Image generation: image_config not available; relying on prompt directive for aspect ratio")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=contents,
                config=types.GenerateContentConfig(**config_kwargs),
            )
            
            # Process response and save image
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    composite_image = Image.open(BytesIO(part.inline_data.data))

                    # Strict AR enforcement with retries
                    max_retries = 2
                    attempt_idx = 0
                    while not self._is_aspect_ratio_match(composite_image, normalized_ar) and attempt_idx < max_retries:
                        logger.warning(f"Composite image AR mismatch (attempt {attempt_idx+1}); retrying with strict dimensions")
                        dim_configs = self._build_best_dimension_configs(types, normalized_ar) or [self._build_image_config(types, normalized_ar)]
                        w_h = self._choose_dimensions_for_ratio(normalized_ar, max_width=1536)
                        px_directive = f"Generate exactly {w_h[0]}x{w_h[1]} pixels, no padding or borders. " if w_h else ""
                        stricter_prompt = f"ABSOLUTE REQUIREMENT: Output must be exactly {normalized_ar}. {px_directive}{enhanced_prompt}"
                        retry_succeeded = False
                        for dim_config in dim_configs:
                            retry_kwargs = dict(config_kwargs)
                            if dim_config is not None:
                                retry_kwargs["image_config"] = dim_config
                            response_retry = self.client.models.generate_content(
                                model="gemini-2.5-flash-image",
                                contents=contents[:-1] + [stricter_prompt],
                                config=types.GenerateContentConfig(**retry_kwargs),
                            )
                            for retry_part in response_retry.candidates[0].content.parts:
                                if getattr(retry_part, 'inline_data', None) is not None:
                                    retry_img = Image.open(BytesIO(retry_part.inline_data.data))
                                    composite_image = retry_img
                                    if self._is_aspect_ratio_match(composite_image, normalized_ar):
                                        retry_succeeded = True
                                        break
                            if retry_succeeded:
                                break
                        attempt_idx += 1
                    # Fallback: if still mismatched after retries, enforce by center-cropping
                    if not self._is_aspect_ratio_match(composite_image, normalized_ar):
                        logger.warning("Model did not honor aspect ratio for composite after strict retries; enforcing via cropping")
                        composite_image = self._enforce_aspect_ratio(composite_image, normalized_ar)
                    
                    # Generate unique filename
                    timestamp = int(time.time())
                    filename = f"composite_poster_{timestamp}.png"
                    output_path = f"generated_posters/{filename}"
                    
                    # Ensure minimum short side before saving
                    composite_image = self._ensure_min_short_side(composite_image, min_short_side=1080)

                    # Save to media storage
                    image_bytes = BytesIO()
                    composite_image.save(image_bytes, format='PNG')
                    image_bytes.seek(0)
                    
                    saved_path = default_storage.save(output_path, ContentFile(image_bytes.getvalue()))
                    image_url = default_storage.url(saved_path)
                    # Ensure full URL for download
                    if not image_url.startswith('http'):
                        image_url = f"http://localhost:8000{image_url}"
                    
                    final_w, final_h = composite_image.size
                    logger.info(f"Composite poster generated successfully: {saved_path}; size={final_w}x{final_h}")
                    if not self._is_aspect_ratio_match(composite_image, normalized_ar):
                        logger.warning("Composite image aspect ratio mismatch; retrying once with stricter directive")
                        stricter_prompt = f"ABSOLUTE REQUIREMENT: Output must be exactly {normalized_ar}. No padding, no borders, no letterboxing. {enhanced_prompt}"
                        dim_config = self._build_image_config_with_dimensions(types, normalized_ar)
                        retry_kwargs = dict(config_kwargs)
                        if dim_config is not None:
                            retry_kwargs["image_config"] = dim_config
                            logger.info("Retry (composite) with dimension-based image_config")
                        response_retry = self.client.models.generate_content(
                            model="gemini-2.5-flash-image",
                            contents=contents[:-1] + [stricter_prompt],
                            config=types.GenerateContentConfig(**retry_kwargs),
                        )
                        for retry_part in response_retry.candidates[0].content.parts:
                            if getattr(retry_part, 'inline_data', None) is not None:
                                retry_img = Image.open(BytesIO(retry_part.inline_data.data))
                                if self._is_aspect_ratio_match(retry_img, normalized_ar):
                                    composite_image = retry_img
                                    # Ensure minimum short side before saving
                                    composite_image = self._ensure_min_short_side(composite_image, min_short_side=1080)

                                    image_bytes = BytesIO()
                                    composite_image.save(image_bytes, format='PNG')
                                    image_bytes.seek(0)
                                    saved_path = default_storage.save(output_path, ContentFile(image_bytes.getvalue()))
                                    image_url = default_storage.url(saved_path)
                                    if not image_url.startswith('http'):
                                        image_url = f"http://localhost:8000{image_url}"
                                    logger.info("Retry produced correct aspect ratio image for composite; using retry output")
                                    break
                    
                    # Generate caption and hashtags for the poster
                    caption_result = self.generate_caption_and_hashtags(prompt, image_url)
                    
                    return {
                        "status": "success", 
                        "image_path": saved_path,
                        "image_url": image_url,
                        "filename": filename,
                        "width": final_w,
                        "height": final_h,
                        "aspect_ratio_final": f"{final_w}:{final_h}",
                        "caption": caption_result.get("caption", ""),
                        "full_caption": caption_result.get("full_caption", ""),
                        "hashtags": caption_result.get("hashtags", []),
                        "emoji": caption_result.get("emoji", ""),
                        "call_to_action": caption_result.get("call_to_action", "")
                    }
            
            return {"status": "error", "message": "No composite image returned"}
            
        except Exception as e:
            logger.error(f"Error generating composite poster: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def add_text_overlay(self, image_path: str, text_prompt: str, text_style: str = "elegant") -> Dict[str, Any]:
        """
        Add text overlay to an existing textile image using AI
        
        Args:
            image_path: Path to the uploaded textile image
            text_prompt: Text to add to the image
            text_style: Style of the text (elegant, bold, modern, vintage)
            
        Returns:
            Dict containing status and image path
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Adding text overlay to image with prompt: {text_prompt[:50]}...")
            
            # Load and prepare image from Django storage
            try:
                # Try to get the file from Django storage
                with default_storage.open(image_path, 'rb') as f:
                    image_data = f.read()
            except Exception as storage_error:
                logger.error(f"Failed to open image from storage: {str(storage_error)}")
                # Fallback: try direct file system access
                try:
                    full_path = default_storage.path(image_path)
                    with open(full_path, "rb") as f:
                        image_data = f.read()
                except Exception as fs_error:
                    logger.error(f"Failed to open image from file system: {str(fs_error)}")
                    return {"status": "error", "message": f"Failed to load image: {str(fs_error)}"}
            
            # Create image part
            image_part = types.Part(
                inline_data=types.Blob(
                    data=image_data,
                    mime_type="image/jpeg"
                )
            )
            
            # Create enhanced prompt for text overlay with spacing considerations
            enhanced_prompt = f"""
            Add the following text to this textile image: "{text_prompt}"
            
            Style requirements:
            - Text style: {text_style}
            - Make the text clearly visible and readable
            - Position the text appropriately on the textile
            - Use colors that complement the textile design
            - Ensure the text enhances the overall design
            - Maintain the textile's aesthetic appeal
            
            IMPORTANT DESIGN REQUIREMENTS:
            - Do NOT include any company names, brand names, or business names in the design
            - Do NOT add any random or placeholder brand names
            - Focus purely on the visual design and aesthetic elements
            - Do not include any text that suggests a specific company or brand
            - Keep the design clean and focused on the main content only
            
            IMPORTANT LAYOUT REQUIREMENTS:
            - Keep the TOP-RIGHT corner (≈25% of image width/height) completely free of ANY elements (no text, no graphics)
            - Keep the BOTTOM area (bottom 18% of image height) completely free of ANY elements (no text, no graphics)
            - Do not add bars or artificial padding; keep the natural background continuous
            - Maintain all textual content within the middle 65% of the canvas
            - Ensure text is readable and doesn't overlap with the top-right or bottom areas
            - When generating the poster, make sure any main subject mentioned in the prompt (such as a man, woman, or product) is fully visible and completely inside the frame. Do not crop or cut off the subject's head, body, or important parts. Keep proper framing and composition so the entire subject fits naturally within the image.
            """
            
            # Configure image generation (version-safe). Text overlay remains square.
            normalized_ar = self._normalize_aspect_ratio_value("1:1")
            image_config = self._build_image_config(types, normalized_ar)
            
            config_kwargs = {"response_modalities": ['Image']}
            if image_config is not None:
                config_kwargs["image_config"] = image_config
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[image_part, enhanced_prompt],
                config=types.GenerateContentConfig(**config_kwargs),
            )
            
            # Process response and save image
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    edited_image = Image.open(BytesIO(part.inline_data.data))
                    
                    # Generate unique filename
                    timestamp = int(time.time())
                    filename = f"text_overlay_{timestamp}.png"
                    output_path = f"generated_posters/{filename}"
                    
                    # Ensure minimum short side before saving
                    edited_image = self._ensure_min_short_side(edited_image, min_short_side=1080)

                    # Save to media storage
                    image_bytes = BytesIO()
                    edited_image.save(image_bytes, format='PNG')
                    image_bytes.seek(0)
                    
                    saved_path = default_storage.save(output_path, ContentFile(image_bytes.getvalue()))
                    image_url = default_storage.url(saved_path)
                    # Ensure full URL for download
                    if not image_url.startswith('http'):
                        image_url = f"http://localhost:8000{image_url}"
                    
                    logger.info(f"Text overlay added successfully: {saved_path}")
                    
                    # Generate caption and hashtags for the poster
                    caption_result = self.generate_caption_and_hashtags(text_prompt, image_url)
                    
                    return {
                        "status": "success", 
                        "image_path": saved_path,
                        "image_url": image_url,
                        "filename": filename,
                        "text_added": text_prompt,
                        "style": text_style,
                        "caption": caption_result.get("caption", ""),
                        "full_caption": caption_result.get("full_caption", ""),
                        "hashtags": caption_result.get("hashtags", []),
                        "emoji": caption_result.get("emoji", ""),
                        "call_to_action": caption_result.get("call_to_action", "")
                    }
            
            return {"status": "error", "message": "No edited image returned from model"}
            
        except Exception as e:
            logger.error(f"Error adding text overlay: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def generate_caption_and_hashtags(self, prompt: str, image_url: str = None) -> Dict[str, Any]:
        """
        Generate caption and hashtags for the generated poster
        
        Args:
            prompt: Original prompt used to generate the poster
            image_url: URL of the generated image (optional)
            
        Returns:
            Dict containing caption and hashtags
        """
        try:
            if not self.caption_service.client:
                return {"status": "error", "message": "Caption service not available"}
            
            logger.info(f"Generating caption and hashtags for generated poster...")
            
            # Create enhanced content for better social media captions without using the exact prompt
            enhanced_content = """
            Create an engaging social media caption for a beautiful textile/fashion poster that showcases elegant design and style.
            
            The caption should be:
            - Engaging and attention-grabbing
            - Perfect for Instagram, Facebook, and other social platforms
            - Include emotional appeal and storytelling
            - Mention the beauty and elegance of the textile/fashion item
            - Create desire and interest in the product
            - Be conversational and relatable
            - Include relevant fashion/beauty keywords
            - Focus on the visual appeal and craftsmanship
            - Highlight the elegance and style of the design
            - Create a sense of aspiration and desire
            """
            
            # Generate social media caption with enhanced content
            caption_result = self.caption_service.generate_social_media_caption(
                content=enhanced_content,
                platform="instagram",
                post_type="product_showcase",
                style="engaging",
                tone="friendly",
                include_hashtags=True,
                include_emoji=True,
                call_to_action=True
            )
            
            if caption_result.get("status") == "success":
                caption_data = caption_result.get("caption", {})
                
                # Extract hashtags from the caption
                hashtags = []
                if "hashtags" in caption_data:
                    hashtags = caption_data["hashtags"]
                elif "full_caption" in caption_data:
                    # Extract hashtags from full caption
                    import re
                    hashtag_matches = re.findall(r'#\w+', caption_data["full_caption"])
                    hashtags = list(set(hashtag_matches))  # Remove duplicates
                
                # Generate additional textile-specific hashtags
                textile_hashtags = [
                    "#textile", "#fashion", "#design", "#style", "#trendy",
                    "#handmade", "#artisan", "#craft", "#beautiful", "#elegant"
                ]
                
                # Combine hashtags and remove duplicates
                all_hashtags = list(set(hashtags + textile_hashtags))
                
                logger.info(f"Caption and hashtags generated successfully")
                return {
                    "status": "success",
                    "caption": caption_data.get("main_text", ""),
                    "full_caption": caption_data.get("full_caption", ""),
                    "hashtags": all_hashtags[:15],  # Limit to 15 hashtags
                    "emoji": caption_data.get("emoji", ""),
                    "call_to_action": caption_data.get("call_to_action", "")
                }
            else:
                logger.warning(f"Caption generation failed: {caption_result.get('message', 'Unknown error')}")
                # Create more meaningful fallback captions
                fallback_captions = [
                    "✨ Discover the elegance of this stunning textile design... Perfect for making a statement! ✨",
                    "🌟 Elevate your style with this beautiful creation... A must-have for your wardrobe! 🌟",
                    "💫 Fall in love with this gorgeous design... Timeless beauty meets modern elegance! 💫",
                    "🌸 Embrace the beauty of this elegant piece... Where tradition meets contemporary fashion! 🌸",
                    "✨ Step into elegance with this breathtaking design... Perfect for any special occasion! ✨",
                    "🌟 Make a statement with this gorgeous textile... Timeless style that never goes out of fashion! 🌟"
                ]
                
                import random
                selected_caption = random.choice(fallback_captions)
                
                return {
                    "status": "success",
                    "caption": selected_caption,
                    "full_caption": f"{selected_caption}\n\n✨ Perfect for special occasions, festivals, or everyday elegance ✨\n\n💫 Handcrafted with love and attention to detail 💫\n\n🌸 Available now - don't miss out on this beauty! 🌸",
                    "hashtags": ["#fashion", "#style", "#elegant", "#beautiful", "#textile", "#design", "#trendy", "#outfit", "#fashionista", "#styleinspo", "#ootd", "#fashionblogger", "#stylegoals", "#fashionlover", "#styletips"],
                    "emoji": "✨",
                    "call_to_action": "✨ Shop now and elevate your style! ✨"
                }
                
        except Exception as e:
            logger.error(f"Error generating caption and hashtags: {str(e)}")
            # Create meaningful fallback even for exceptions
            fallback_captions = [
                "✨ Discover the elegance of this stunning textile design... Perfect for making a statement! ✨",
                "🌟 Elevate your style with this beautiful creation... A must-have for your wardrobe! 🌟",
                "💫 Fall in love with this gorgeous design... Timeless beauty meets modern elegance! 💫",
                "🌸 Embrace the beauty of this elegant piece... Where tradition meets contemporary fashion! 🌸",
                "✨ Step into elegance with this breathtaking design... Perfect for any special occasion! ✨"
            ]
            
            import random
            selected_caption = random.choice(fallback_captions)
            
            return {
                "status": "success",
                "caption": selected_caption,
                "full_caption": f"{selected_caption}\n\n✨ Perfect for special occasions, festivals, or everyday elegance ✨\n\n💫 Handcrafted with love and attention to detail 💫\n\n🌸 Available now - don't miss out on this beauty! 🌸",
                "hashtags": ["#fashion", "#style", "#elegant", "#beautiful", "#textile", "#design", "#trendy", "#outfit", "#fashionista", "#styleinspo", "#ootd", "#fashionblogger", "#stylegoals", "#fashionlover", "#styletips"],
                "emoji": "✨",
                "call_to_action": "✨ Shop now and elevate your style! ✨"
            }
    
    def is_available(self) -> bool:
        """Check if the AI poster service is available"""
        return self.client is not None and self.api_key is not None
