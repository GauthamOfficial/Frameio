"""
AI Poster Generation Service using Google Gemini 2.5 Flash
Clean, production-ready implementation for textile poster generation
"""
import os
import logging
import time
import uuid
import random
from typing import Dict, List, Any, Optional
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .ai_caption_service import AICaptionService
from .brand_overlay_service import BrandOverlayService
from .utils.cloudinary_utils import upload_to_cloudinary, create_shareable_html_page, upload_html_to_cloudinary

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

    def _retry_api_call(self, api_func, *args, **kwargs):
        """
        Retry API call with exponential backoff for transient errors
        
        Args:
            api_func: The API function to call
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result from the API call
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return api_func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                error_str = str(e)
                
                # Check if it's a retryable error (500, 503, rate limit, etc.)
                is_retryable = (
                    '500' in error_str or 
                    '503' in error_str or 
                    'INTERNAL' in error_str or
                    'rate limit' in error_str.lower() or
                    'quota' in error_str.lower() or
                    'temporarily unavailable' in error_str.lower()
                )
                
                if not is_retryable or attempt == self.max_retries - 1:
                    # Not retryable or last attempt
                    raise
                
                # Calculate exponential backoff with jitter
                delay = self.retry_delay_base * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"API call failed (attempt {attempt + 1}/{self.max_retries}): {error_str}")
                logger.info(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
        
        # If we get here, all retries failed
        raise last_exception
    
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
        # Initialize caption service - it will use the same API key from environment/settings
        self.caption_service = AICaptionService()
        # Verify caption service is initialized
        if not self.caption_service.client:
            logger.warning("Caption service client not initialized - captions may not work")
            logger.warning(f"Caption service API key exists: {bool(self.caption_service.api_key)}")
        else:
            logger.info("Caption service initialized successfully")
        self.brand_overlay_service = BrandOverlayService()
        self.max_retries = 3  # Maximum number of retries for API calls
        self.retry_delay_base = 1  # Base delay in seconds for exponential backoff
        
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
                
                try:
                    response = self._retry_api_call(
                        self.client.models.generate_content,
                        model="gemini-2.5-flash-image",
                        contents=[current_prompt],
                        config=types.GenerateContentConfig(**config_kwargs),
                    )
                except Exception as api_error:
                    error_str = str(api_error)
                    logger.error(f"API call failed after retries: {error_str}")
                    
                    # Check for specific error types
                    if '500' in error_str or 'INTERNAL' in error_str:
                        if attempt < len(prompts_to_try) - 1:
                            logger.info(f"Retrying with different prompt variation...")
                            time.sleep(2)  # Wait before trying next prompt
                            continue
                        return {
                            "status": "error",
                            "message": "Google API is experiencing temporary issues. Please try again in a few moments. If the problem persists, please check your API quota and configuration."
                        }
                    else:
                        # For other errors, return immediately
                        return {
                            "status": "error",
                            "message": f"Image generation failed: {error_str}"
                        }
            
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
                                    try:
                                        response_retry = self._retry_api_call(
                                            self.client.models.generate_content,
                                            model="gemini-2.5-flash-image",
                                            contents=[stricter_prompt],
                                            config=types.GenerateContentConfig(**retry_kwargs),
                                        )
                                    except Exception as retry_error:
                                        logger.warning(f"Retry attempt failed: {retry_error}")
                                        continue
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
                            # Ensure full URL for sharing and download
                            if not image_url.startswith('http'):
                                # Use request context if available, otherwise fallback to localhost
                                request = getattr(self, '_request', None)
                                if request:
                                    image_url = request.build_absolute_uri(image_url)
                                else:
                                    image_url = f"http://localhost:8000{image_url}"
                            
                            final_w, final_h = image.size
                            logger.info(f"Poster generated successfully on attempt {attempt + 1}: {saved_path}; size={final_w}x{final_h}")
                            
                            # Upload to Cloudinary for public sharing - CRITICAL STEP
                            logger.info(f"=== STARTING CLOUDINARY UPLOAD ===")
                            logger.info(f"Image saved to: {saved_path}")
                            logger.info(f"Verifying file exists before upload...")
                            
                            # Verify file exists before uploading
                            if not default_storage.exists(saved_path):
                                logger.error(f"CRITICAL: File does not exist at {saved_path} before Cloudinary upload!")
                            else:
                                logger.info(f"File exists, proceeding with Cloudinary upload...")
                            
                            # CRITICAL: Ensure upload happens BEFORE caption generation
                            # This ensures public_url is available for HTML page creation
                            
                            public_url = None
                            try:
                                logger.info(f"Calling upload_to_cloudinary with path: {saved_path}")
                                public_url = upload_to_cloudinary(saved_path)
                                if public_url:
                                    logger.info(f"SUCCESS: Poster uploaded to Cloudinary: {public_url}")
                                else:
                                    logger.error(f"FAILED: Cloudinary upload returned None")
                                    logger.error(f"   This means the poster cannot be shared on Facebook immediately!")
                                    logger.error(f"   Check Cloudinary credentials and network connectivity")
                            except Exception as e:
                                logger.error(f"EXCEPTION during Cloudinary upload: {str(e)}")
                                import traceback
                                traceback.print_exc()
                                # Continue even if Cloudinary upload fails, but log the error
                            
                            logger.info(f"=== END CLOUDINARY UPLOAD ===")
                            logger.info(f"Final public_url after upload: {public_url}")
                            
                            # CRITICAL: If upload failed, try one more time
                            if not public_url:
                                logger.warning("First upload attempt failed, retrying...")
                                try:
                                    public_url = upload_to_cloudinary(saved_path)
                                    if public_url:
                                        logger.info(f"SUCCESS on retry: Poster uploaded to Cloudinary: {public_url}")
                                    else:
                                        logger.error(f"FAILED on retry: Cloudinary upload still returned None")
                                except Exception as retry_error:
                                    logger.error(f"EXCEPTION on retry: {retry_error}")
                            
                            # Generate caption and hashtags for the poster
                            logger.info("Starting caption generation...")
                            caption_result = self.generate_caption_and_hashtags(prompt, image_url, user)
                            logger.info(f"Caption generation result status: {caption_result.get('status')}")
                            
                            # Check if caption generation failed
                            if caption_result.get("status") == "error":
                                error_msg = caption_result.get("message", "Unknown error")
                                logger.error(f"Caption generation failed: {error_msg}")
                                # Still continue with poster generation, but log the error
                                # The frontend can handle empty captions
                            
                            # Create shareable HTML page with Open Graph tags for Facebook
                            # This allows Facebook to automatically fetch both image and caption
                            shareable_page_url = None
                            logger.info(f"=== HTML PAGE CREATION DEBUG ===")
                            logger.info(f"public_url available: {bool(public_url)}")
                            if public_url:
                                logger.info(f"public_url value: {public_url}")
                                try:
                                    caption_text = caption_result.get("caption", "")
                                    full_caption_text = caption_result.get("full_caption", caption_text)
                                    logger.info(f"Caption text available: {bool(caption_text)}")
                                    logger.info(f"Full caption text available: {bool(full_caption_text)}")
                                    
                                    if caption_text or full_caption_text:
                                        logger.info("Creating HTML page content...")
                                        html_content = create_shareable_html_page(
                                            public_url,
                                            caption_text,
                                            full_caption_text
                                        )
                                        logger.info(f"HTML content created, length: {len(html_content)}")
                                        
                                        logger.info("Uploading HTML page to Cloudinary...")
                                        shareable_page_url = upload_html_to_cloudinary(
                                            html_content,
                                            filename=f"poster_{int(time.time())}"
                                        )
                                        if shareable_page_url:
                                            logger.info(f"SUCCESS: Shareable HTML page created successfully: {shareable_page_url}")
                                        else:
                                            logger.error("FAILED: Failed to upload HTML page to Cloudinary, using image URL directly")
                                            shareable_page_url = public_url  # Fallback to image URL
                                    else:
                                        logger.warning("WARNING: No caption available, using image URL directly")
                                        shareable_page_url = public_url  # Fallback to image URL
                                except Exception as html_error:
                                    logger.error(f"ERROR: Error creating shareable HTML page: {html_error}")
                                    import traceback
                                    traceback.print_exc()
                                    shareable_page_url = public_url  # Fallback to image URL
                            else:
                                logger.error("ERROR: No public_url available, cannot create HTML page")
                            
                            logger.info(f"Final shareable_page_url: {shareable_page_url}")
                            logger.info(f"=== END HTML PAGE CREATION DEBUG ===")
                            
                            # Ensure public_url is always set - prioritize HTML page, then Cloudinary image, then local image_url
                            final_public_url = shareable_page_url or public_url or image_url
                            
                            # If we don't have a Cloudinary URL, try to upload the image now
                            if not public_url and not shareable_page_url:
                                logger.warning("⚠️  No Cloudinary URL found, attempting to upload image now...")
                                try:
                                    public_url = upload_to_cloudinary(saved_path)
                                    if public_url:
                                        logger.info(f"✅ Image uploaded to Cloudinary: {public_url}")
                                        # Now create HTML page
                                        caption_text = caption_result.get("caption", "")
                                        full_caption_text = caption_result.get("full_caption", caption_text)
                                        if caption_text or full_caption_text:
                                            html_content = create_shareable_html_page(
                                                public_url,
                                                caption_text,
                                                full_caption_text
                                            )
                                            shareable_page_url = upload_html_to_cloudinary(
                                                html_content,
                                                filename=f"poster_{int(time.time())}"
                                            )
                                            if shareable_page_url:
                                                logger.info(f"✅ HTML page created: {shareable_page_url}")
                                                final_public_url = shareable_page_url
                                            else:
                                                final_public_url = public_url
                                        else:
                                            final_public_url = public_url
                                    else:
                                        logger.error("❌ Failed to upload to Cloudinary, using image_url")
                                        final_public_url = image_url
                                except Exception as upload_error:
                                    logger.error(f"❌ Error uploading to Cloudinary: {upload_error}")
                                    final_public_url = image_url
                            
                            if not final_public_url:
                                logger.error("CRITICAL: No public_url available at all! Using image_url as fallback")
                                final_public_url = image_url
                            
                            logger.info(f"=== FINAL RESULT DEBUG ===")
                            logger.info(f"shareable_page_url: {shareable_page_url}")
                            logger.info(f"public_url (image): {public_url}")
                            logger.info(f"final_public_url: {final_public_url}")
                            logger.info(f"image_url: {image_url}")
                            
                            # Add brand overlay if user has company profile
                            # CRITICAL: Set public_url in final_result - this is what gets returned to the API
                            # Ensure public_url is always set (even if empty)
                            # Also include cloudinary_url as the direct image URL (not HTML page)
                            cloudinary_image_url = public_url if public_url and not shareable_page_url else (public_url if public_url else '')
                            
                            final_result = {
                                "status": "success", 
                                "image_path": saved_path,
                                "image_url": image_url,
                                "public_url": final_public_url if final_public_url else '',  # Always set, even if empty (may be HTML page)
                                "cloudinary_url": cloudinary_image_url,  # Direct Cloudinary image URL (not HTML page)
                                "filename": filename,
                                "width": final_w,
                                "height": final_h,
                                "aspect_ratio_final": f"{final_w}:{final_h}",
                                "caption": caption_result.get("caption", ""),
                                "full_caption": caption_result.get("full_caption", ""),
                                "hashtags": caption_result.get("hashtags", []),
                                "emoji": caption_result.get("emoji", ""),
                                "call_to_action": caption_result.get("call_to_action", ""),
                                "caption_error": caption_result.get("message") if caption_result.get("status") == "error" else None,
                                "branding_applied": False
                            }
                            
                            # CRITICAL: Ensure public_url key exists
                            if 'public_url' not in final_result:
                                logger.error("CRITICAL: public_url key missing from final_result!")
                                final_result['public_url'] = ''
                            
                            # Final verification before returning
                            logger.info(f"Final result public_url: {final_result.get('public_url')}")
                            logger.info(f"Final result keys: {list(final_result.keys())}")
                            if not final_result.get('public_url'):
                                logger.error("CRITICAL: public_url missing in final_result! Setting to image_url")
                                final_result['public_url'] = image_url
                            logger.info(f"=== END FINAL RESULT DEBUG ===")
                            
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
                                                branded_path = brand_result.get("image_path", saved_path)
                                                
                                                # Upload branded poster to Cloudinary (replaces original upload)
                                                branded_public_url = None
                                                try:
                                                    branded_public_url = upload_to_cloudinary(branded_path)
                                                    if branded_public_url:
                                                        logger.info(f"Branded poster uploaded to Cloudinary: {branded_public_url}")
                                                    else:
                                                        logger.warning("Cloudinary upload failed for branded poster, using original URL")
                                                        branded_public_url = public_url  # Fallback to original
                                                except Exception as e:
                                                    logger.error(f"Error uploading branded poster to Cloudinary: {str(e)}")
                                                    branded_public_url = public_url  # Fallback to original
                                                
                                                # Create shareable HTML page for branded poster
                                                logger.info(f"=== BRANDED HTML PAGE CREATION DEBUG ===")
                                                branded_shareable_url = None
                                                if branded_public_url:
                                                    logger.info(f"branded_public_url available: {branded_public_url}")
                                                    try:
                                                        caption_text = final_result.get("caption", "")
                                                        full_caption_text = final_result.get("full_caption", caption_text)
                                                        logger.info(f"Caption available for branded: {bool(caption_text or full_caption_text)}")
                                                        
                                                        if caption_text or full_caption_text:
                                                            logger.info("Creating branded HTML page content...")
                                                            html_content = create_shareable_html_page(
                                                                branded_public_url,
                                                                caption_text,
                                                                full_caption_text
                                                            )
                                                            logger.info(f"Branded HTML content created, length: {len(html_content)}")
                                                            
                                                            logger.info("Uploading branded HTML page to Cloudinary...")
                                                            branded_shareable_url = upload_html_to_cloudinary(
                                                                html_content,
                                                                filename=f"branded_poster_{int(time.time())}"
                                                            )
                                                            if branded_shareable_url:
                                                                logger.info(f"✅ Branded shareable HTML page created: {branded_shareable_url}")
                                                            else:
                                                                logger.error("❌ Failed to create branded HTML page, using image URL")
                                                                branded_shareable_url = branded_public_url
                                                        else:
                                                            logger.warning("⚠️  No caption for branded poster, using image URL")
                                                            branded_shareable_url = branded_public_url
                                                    except Exception as html_error:
                                                        logger.error(f"❌ Error creating branded shareable HTML page: {html_error}")
                                                        import traceback
                                                        traceback.print_exc()
                                                        branded_shareable_url = branded_public_url
                                                else:
                                                    logger.error("❌ No branded_public_url, cannot create HTML page")
                                                
                                                final_branded_url = branded_shareable_url or branded_public_url or shareable_page_url or public_url
                                                logger.info(f"Final branded public_url: {final_branded_url}")
                                                
                                                # CRITICAL: Verify final_branded_url is a Cloudinary URL, not a local URL
                                                if final_branded_url and not final_branded_url.startswith('http'):
                                                    logger.error(f"CRITICAL: final_branded_url is not a Cloudinary URL: {final_branded_url}")
                                                    logger.error("Attempting emergency upload of branded poster...")
                                                    # Try to upload the branded image now
                                                    try:
                                                        emergency_branded_url = upload_to_cloudinary(branded_path)
                                                        if emergency_branded_url:
                                                            logger.info(f"SUCCESS: Emergency branded upload succeeded: {emergency_branded_url}")
                                                            final_branded_url = emergency_branded_url
                                                            # Also create HTML page
                                                            caption_text = final_result.get("caption", "")
                                                            full_caption_text = final_result.get("full_caption", caption_text)
                                                            if caption_text or full_caption_text:
                                                                html_content = create_shareable_html_page(
                                                                    emergency_branded_url,
                                                                    caption_text,
                                                                    full_caption_text
                                                                )
                                                                emergency_html_url = upload_html_to_cloudinary(
                                                                    html_content,
                                                                    filename=f"branded_emergency_{int(time.time())}"
                                                                )
                                                                if emergency_html_url:
                                                                    final_branded_url = emergency_html_url
                                                                    logger.info(f"SUCCESS: Emergency HTML page created: {emergency_html_url}")
                                                        else:
                                                            logger.error("ERROR: Emergency branded upload failed")
                                                    except Exception as emergency_error:
                                                        logger.error(f"ERROR: Emergency branded upload exception: {emergency_error}")
                                                
                                                logger.info(f"=== END BRANDED HTML PAGE CREATION DEBUG ===")
                                                
                                                # CRITICAL: Ensure public_url is always set (even if empty)
                                                final_branded_url = final_branded_url if final_branded_url else ''
                                                
                                                # Extract cloudinary_url for branded poster (direct image URL, not HTML page)
                                                branded_cloudinary_url = branded_public_url if branded_public_url else (public_url if public_url else '')
                                                
                                                final_result.update({
                                                    "image_path": branded_path,
                                                    "image_url": brand_result.get("image_url", image_url),
                                                    "public_url": final_branded_url,  # Use HTML page URL if available, or empty string
                                                    "cloudinary_url": branded_cloudinary_url,  # Direct Cloudinary image URL (not HTML page)
                                                    "filename": brand_result.get("filename", filename),
                                                    "branding_applied": True,
                                                    "logo_added": brand_result.get("logo_added", False),
                                                    "contact_info_added": brand_result.get("contact_info_added", False),
                                                    "branding_metadata": brand_result.get("branding_metadata", {})
                                                })
                                                
                                                # CRITICAL: Ensure public_url key exists after update
                                                if 'public_url' not in final_result:
                                                    logger.error("CRITICAL: public_url key missing after branding update!")
                                                    final_result['public_url'] = ''
                                                elif final_result.get('public_url') is None:
                                                    logger.error("CRITICAL: public_url is None after branding update!")
                                                    final_result['public_url'] = ''
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
                            
                            # Final check before returning - ENSURE public_url is ALWAYS set and is a Cloudinary URL
                            current_public_url = final_result.get('public_url')
                            
                            # Check if public_url is missing OR is a local URL (not Cloudinary)
                            if not current_public_url or (current_public_url and not current_public_url.startswith('http')):
                                logger.error("CRITICAL ERROR: public_url is missing or is not a Cloudinary URL!")
                                logger.error(f"Current public_url: {current_public_url}")
                                logger.error(f"Available keys: {list(final_result.keys())}")
                                logger.error(f"shareable_page_url: {shareable_page_url}")
                                logger.error(f"public_url (image): {public_url}")
                                logger.error(f"image_url: {image_url}")
                                
                                # Determine which file to upload (branded or original)
                                file_to_upload = None
                                if final_result.get('branding_applied') and final_result.get('image_path'):
                                    file_to_upload = final_result.get('image_path')
                                    logger.info(f"Using branded image path for emergency upload: {file_to_upload}")
                                elif saved_path:
                                    file_to_upload = saved_path
                                    logger.info(f"Using original image path for emergency upload: {file_to_upload}")
                                
                                # Last resort: try to upload again if we have a file path
                                if file_to_upload and default_storage.exists(file_to_upload):
                                    logger.warning("WARNING: Attempting emergency Cloudinary upload...")
                                    try:
                                        emergency_url = upload_to_cloudinary(file_to_upload)
                                        if emergency_url:
                                            logger.info(f"SUCCESS: Emergency upload succeeded: {emergency_url}")
                                            # Try to create HTML page too
                                            caption_text = final_result.get("caption", "")
                                            full_caption_text = final_result.get("full_caption", caption_text)
                                            if caption_text or full_caption_text:
                                                html_content = create_shareable_html_page(
                                                    emergency_url,
                                                    caption_text,
                                                    full_caption_text
                                                )
                                                emergency_html_url = upload_html_to_cloudinary(
                                                    html_content,
                                                    filename=f"emergency_{int(time.time())}"
                                                )
                                                if emergency_html_url:
                                                    final_result['public_url'] = emergency_html_url
                                                    final_result['cloudinary_url'] = emergency_url  # Direct image URL
                                                    logger.info(f"SUCCESS: Emergency HTML page created: {emergency_html_url}")
                                                else:
                                                    final_result['public_url'] = emergency_url
                                                    final_result['cloudinary_url'] = emergency_url
                                            else:
                                                final_result['public_url'] = emergency_url
                                                final_result['cloudinary_url'] = emergency_url
                                        else:
                                            logger.error("ERROR: Emergency upload also failed")
                                            logger.error("WARNING: Setting public_url to empty - Facebook sharing will not work")
                                            final_result['public_url'] = ''
                                            final_result['cloudinary_url'] = ''
                                    except Exception as emergency_error:
                                        logger.error(f"ERROR: Emergency upload exception: {emergency_error}")
                                        import traceback
                                        traceback.print_exc()
                                        final_result['public_url'] = ''
                                        final_result['cloudinary_url'] = ''
                                else:
                                    logger.error(f"ERROR: No file to upload. saved_path: {saved_path}, file_to_upload: {file_to_upload}")
                                    final_result['public_url'] = ''
                                    final_result['cloudinary_url'] = ''
                                
                                logger.info(f"Final public_url after emergency fix: {final_result.get('public_url')}")
                            
                            # CRITICAL: Final verification - ensure public_url and cloudinary_url keys exist and are strings
                            if 'public_url' not in final_result:
                                logger.error("CRITICAL: public_url key missing from final_result!")
                                final_result['public_url'] = ''
                            elif final_result.get('public_url') is None:
                                logger.error("CRITICAL: public_url is None in final_result!")
                                final_result['public_url'] = ''
                            else:
                                # Ensure it's a string
                                final_result['public_url'] = str(final_result.get('public_url', ''))
                            
                            # Ensure cloudinary_url is also set (use public_url if it's a direct image URL, not HTML page)
                            if 'cloudinary_url' not in final_result:
                                # If public_url is a Cloudinary image URL (not HTML), use it
                                current_public = final_result.get('public_url', '')
                                if current_public and current_public.startswith('http') and 'cloudinary' in current_public and not current_public.endswith('.html'):
                                    final_result['cloudinary_url'] = current_public
                                else:
                                    final_result['cloudinary_url'] = ''
                            elif final_result.get('cloudinary_url') is None:
                                final_result['cloudinary_url'] = ''
                            
                            # Verify public_url is actually set
                            if not final_result.get('public_url'):
                                logger.error("CRITICAL: public_url is STILL empty after all attempts!")
                                logger.error("This will cause Facebook sharing to fail!")
                            
                            logger.info(f"=== RETURNING RESULT ===")
                            logger.info(f"public_url: {final_result.get('public_url')}")
                            logger.info(f"public_url type: {type(final_result.get('public_url'))}")
                            logger.info(f"public_url in final_result: {'public_url' in final_result}")
                            logger.info(f"status: {final_result.get('status')}")
                            logger.info(f"All result keys: {list(final_result.keys())}")
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
            
            try:
                response = self._retry_api_call(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash-image",
                    contents=[image_part, base_prompt],
                    config=types.GenerateContentConfig(**config_kwargs),
                )
            except Exception as api_error:
                error_str = str(api_error)
                logger.error(f"API call failed after retries: {error_str}")
                return {
                    "status": "error",
                    "message": "Google API is experiencing temporary issues. Please try again in a few moments." if ('500' in error_str or 'INTERNAL' in error_str) else f"Image generation failed: {error_str}"
                }
            
            # Process response and save image
            if not response.candidates or len(response.candidates) == 0:
                logger.error("No candidates returned from Gemini model for image edit")
                return {"status": "error", "message": "No candidates returned from model"}
            
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                logger.error("No content parts in Gemini response for image edit")
                return {"status": "error", "message": "No content parts returned from model"}
            
            for part in candidate.content.parts:
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
                            try:
                                response_retry = self._retry_api_call(
                                    self.client.models.generate_content,
                                    model="gemini-2.5-flash-image",
                                    contents=[image_part, stricter_prompt],
                                    config=types.GenerateContentConfig(**retry_kwargs),
                                )
                            except Exception as retry_error:
                                logger.warning(f"Aspect ratio retry failed: {retry_error}")
                                continue
                            if not response_retry.candidates or len(response_retry.candidates) == 0:
                                continue
                            if not response_retry.candidates[0].content or not response_retry.candidates[0].content.parts:
                                continue
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
                    
                    # Upload to Cloudinary for public sharing
                    public_url = None
                    try:
                        public_url = upload_to_cloudinary(saved_path)
                        if public_url:
                            logger.info(f"Edited poster uploaded to Cloudinary: {public_url}")
                        else:
                            logger.warning("Cloudinary upload failed for edited poster, but continuing with local URL")
                    except Exception as e:
                        logger.error(f"Error uploading edited poster to Cloudinary: {str(e)}")
                        # Continue even if Cloudinary upload fails
                    
                    # Generate caption and hashtags for the poster
                    logger.info("Starting caption generation for edited poster...")
                    caption_result = self.generate_caption_and_hashtags(prompt, image_url, user)
                    logger.info(f"Caption generation result status: {caption_result.get('status')}")
                    
                    # Check if caption generation failed
                    if caption_result.get("status") == "error":
                        error_msg = caption_result.get("message", "Unknown error")
                        logger.error(f"Caption generation failed: {error_msg}")
                    
                    # Create shareable HTML page with Open Graph tags for Facebook
                    shareable_page_url = None
                    if public_url:
                        try:
                            caption_text = caption_result.get("caption", "")
                            full_caption_text = caption_result.get("full_caption", caption_text)
                            
                            if caption_text or full_caption_text:
                                html_content = create_shareable_html_page(
                                    public_url,
                                    caption_text,
                                    full_caption_text
                                )
                                shareable_page_url = upload_html_to_cloudinary(
                                    html_content,
                                    filename=f"edited_poster_{int(time.time())}"
                                )
                                if shareable_page_url:
                                    logger.info(f"Edited shareable HTML page created: {shareable_page_url}")
                        except Exception as html_error:
                            logger.warning(f"Error creating edited shareable HTML page: {html_error}")
                    
                    # Add brand overlay if user has company profile
                    final_result = {
                        "status": "success", 
                        "image_path": saved_path,
                        "image_url": image_url,
                        "public_url": shareable_page_url or public_url,  # Use HTML page URL if available, else image URL
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
                                        branded_path = brand_result.get("image_path", saved_path)
                                        
                                        # Upload branded poster to Cloudinary (replaces original upload)
                                        branded_public_url = None
                                        try:
                                            branded_public_url = upload_to_cloudinary(branded_path)
                                            if branded_public_url:
                                                logger.info(f"Branded edited poster uploaded to Cloudinary: {branded_public_url}")
                                            else:
                                                logger.warning("Cloudinary upload failed for branded edited poster, using original URL")
                                                branded_public_url = public_url  # Fallback to original
                                        except Exception as e:
                                            logger.error(f"Error uploading branded edited poster to Cloudinary: {str(e)}")
                                            branded_public_url = public_url  # Fallback to original
                                        
                                        final_result.update({
                                            "image_path": branded_path,
                                            "image_url": brand_result.get("image_url", image_url),
                                            "public_url": branded_public_url,  # Use branded Cloudinary URL
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
            
            GRADIENT OVERLAY REQUIREMENT:
            - Add a black gradient overlay to the bottom 10% of the image
            - The gradient should transition smoothly from transparent (at the top of the bottom 10% area) to fully black (at the bottom edge)
            - This gradient overlay should be applied to every poster without exception
            - Ensure the gradient blends seamlessly with the underlying image content
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
            
            try:
                response = self._retry_api_call(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash-image",
                    contents=contents,
                    config=types.GenerateContentConfig(**config_kwargs),
                )
            except Exception as api_error:
                error_str = str(api_error)
                logger.error(f"API call failed after retries: {error_str}")
                return {
                    "status": "error",
                    "message": "Google API is experiencing temporary issues. Please try again in a few moments." if ('500' in error_str or 'INTERNAL' in error_str) else f"Image generation failed: {error_str}"
                }
            
            # Process response and save image
            if not response.candidates or len(response.candidates) == 0:
                logger.error("No candidates returned from Gemini model for composite")
                return {"status": "error", "message": "No candidates returned from model"}
            
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
                            try:
                                response_retry = self._retry_api_call(
                                    self.client.models.generate_content,
                                    model="gemini-2.5-flash-image",
                                    contents=contents[:-1] + [stricter_prompt],
                                    config=types.GenerateContentConfig(**retry_kwargs),
                                )
                            except Exception as retry_error:
                                logger.warning(f"Composite aspect ratio retry failed: {retry_error}")
                                continue
                            if not response_retry.candidates or len(response_retry.candidates) == 0:
                                continue
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
                    
                    # Upload to Cloudinary for public sharing
                    public_url = None
                    try:
                        public_url = upload_to_cloudinary(saved_path)
                        if public_url:
                            logger.info(f"Composite poster uploaded to Cloudinary: {public_url}")
                        else:
                            logger.warning("Cloudinary upload failed for composite, but continuing with local URL")
                    except Exception as e:
                        logger.error(f"Error uploading composite to Cloudinary: {str(e)}")
                        # Continue even if Cloudinary upload fails
                    if not self._is_aspect_ratio_match(composite_image, normalized_ar):
                        logger.warning("Composite image aspect ratio mismatch; retrying once with stricter directive")
                        stricter_prompt = f"ABSOLUTE REQUIREMENT: Output must be exactly {normalized_ar}. No padding, no borders, no letterboxing. {enhanced_prompt}"
                        dim_config = self._build_image_config_with_dimensions(types, normalized_ar)
                        retry_kwargs = dict(config_kwargs)
                        if dim_config is not None:
                            retry_kwargs["image_config"] = dim_config
                            logger.info("Retry (composite) with dimension-based image_config")
                        try:
                            response_retry = self._retry_api_call(
                                self.client.models.generate_content,
                                model="gemini-2.5-flash-image",
                                contents=contents[:-1] + [stricter_prompt],
                                config=types.GenerateContentConfig(**retry_kwargs),
                            )
                        except Exception as retry_error:
                            logger.warning(f"Composite dimension retry failed: {retry_error}")
                            continue
                        if not response_retry.candidates or len(response_retry.candidates) == 0:
                            continue
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
                                    
                                    # Upload to Cloudinary for public sharing (retry case)
                                    try:
                                        public_url = upload_to_cloudinary(saved_path)
                                        if public_url:
                                            logger.info(f"Composite poster (retry) uploaded to Cloudinary: {public_url}")
                                    except Exception as e:
                                        logger.error(f"Error uploading composite (retry) to Cloudinary: {str(e)}")
                                    
                                    logger.info("Retry produced correct aspect ratio image for composite; using retry output")
                                    break
                    
                    # Generate caption and hashtags for the poster
                    caption_result = self.generate_caption_and_hashtags(prompt, image_url, None)
                    
                    return {
                        "status": "success", 
                        "image_path": saved_path,
                        "image_url": image_url,
                        "public_url": public_url,  # Cloudinary URL for sharing
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
            
            GRADIENT OVERLAY REQUIREMENT:
            - Add a black gradient overlay to the bottom 10% of the image
            - The gradient should transition smoothly from transparent (at the top of the bottom 10% area) to fully black (at the bottom edge)
            - This gradient overlay should be applied to every poster without exception
            - Ensure the gradient blends seamlessly with the underlying image content
            """
            
            # Configure image generation (version-safe). Text overlay remains square.
            normalized_ar = self._normalize_aspect_ratio_value("1:1")
            image_config = self._build_image_config(types, normalized_ar)
            
            config_kwargs = {"response_modalities": ['Image']}
            if image_config is not None:
                config_kwargs["image_config"] = image_config
            
            try:
                response = self._retry_api_call(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash-image",
                    contents=[image_part, enhanced_prompt],
                    config=types.GenerateContentConfig(**config_kwargs),
                )
            except Exception as api_error:
                error_str = str(api_error)
                logger.error(f"API call failed after retries: {error_str}")
                return {
                    "status": "error",
                    "message": "Google API is experiencing temporary issues. Please try again in a few moments." if ('500' in error_str or 'INTERNAL' in error_str) else f"Text overlay failed: {error_str}"
                }
            
            # Process response and save image
            if not response.candidates or len(response.candidates) == 0:
                logger.error("No candidates returned from Gemini model for text overlay")
                return {"status": "error", "message": "No candidates returned from model"}
            
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
                    caption_result = self.generate_caption_and_hashtags(text_prompt, image_url, None)
                    
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
    
    def generate_caption_and_hashtags(self, prompt: str, image_url: str = None, user=None) -> Dict[str, Any]:
        """
        Generate caption and hashtags for the generated poster with contact details
        
        Args:
            prompt: Original prompt used to generate the poster
            image_url: URL of the generated image (optional)
            user: User object for contact details
            
        Returns:
            Dict containing caption and hashtags
        """
        try:
            logger.info(f"=== CAPTION GENERATION DEBUG ===")
            logger.info(f"Caption service available: {self.caption_service.client is not None}")
            logger.info(f"Caption service API key exists: {bool(self.caption_service.api_key)}")
            logger.info(f"Caption service API key length: {len(self.caption_service.api_key) if self.caption_service.api_key else 0}")
            
            if not self.caption_service.client:
                logger.error("Caption service client not available - checking initialization...")
                # Try to reinitialize the caption service
                try:
                    from .ai_caption_service import AICaptionService
                    self.caption_service = AICaptionService()
                    logger.info(f"Reinitialized caption service. Client available: {self.caption_service.client is not None}")
                    if not self.caption_service.client:
                        logger.error("Caption service client still not available after reinitialization")
                        return {"status": "error", "message": "Caption service not available - API key may be missing or invalid"}
                except Exception as init_error:
                    logger.error(f"Failed to reinitialize caption service: {init_error}")
                    return {"status": "error", "message": f"Caption service initialization failed: {str(init_error)}"}
            
            logger.info(f"Generating caption and hashtags for generated poster...")
            logger.info(f"User provided for caption generation: {user}")
            logger.info(f"Prompt: {prompt[:100]}...")
            
            # Get user contact details if available
            contact_info = ""
            company_name = ""
            if user:
                try:
                    from users.models import CompanyProfile
                    company_profile = getattr(user, 'company_profile', None)
                    if company_profile and company_profile.has_complete_profile:
                        company_name = company_profile.company_name or ""
                        contact_dict = company_profile.get_contact_info() or {}
                        
                        # Format contact information properly
                        contact_details = []
                        if contact_dict.get('whatsapp'):
                            contact_details.append(f"📱 WhatsApp: {contact_dict['whatsapp']}")
                        if contact_dict.get('email'):
                            contact_details.append(f"✉️ Email: {contact_dict['email']}")
                        if contact_dict.get('facebook'):
                            contact_details.append(f"📘 Facebook: {contact_dict['facebook']}")
                        
                        contact_info = "\n".join(contact_details)
                        logger.info(f"Using contact info for caption: {contact_info}")
                except Exception as e:
                    logger.warning(f"Error getting contact info: {e}")
            
            # Create enhanced content based on the original prompt for better social media captions
            enhanced_content = f"""Create an engaging social media caption for a beautiful textile/fashion poster based on this description: "{prompt}"

Requirements:
- Capture the essence and details from the prompt
- Highlight specific features, colors, materials, or style mentioned
- Create emotional connection with the target audience
- Be conversational and relatable
- Include a compelling call-to-action"""
            
            # Add contact details to the content if available
            if contact_info and company_name:
                enhanced_content += f"""

MANDATORY: You MUST include the following contact information at the end of the caption:

Company: {company_name}

Contact Details (format exactly as shown, each on separate line):
{contact_info}

CRITICAL FORMATTING:
- Place contact details at the END of the caption after main content
- Use EXACT formatting shown above (with emojis)
- Each contact method on its own line
- Add spacing before contact section
- Do NOT modify contact details - use exactly as provided"""
            
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
            
            logger.info(f"Caption generation result status: {caption_result.get('status')}")
            logger.info(f"Caption generation result keys: {list(caption_result.keys())}")
            
            if caption_result.get("status") == "success":
                caption_data = caption_result.get("caption", {})
                logger.info(f"Caption data type: {type(caption_data)}")
                logger.info(f"Caption data received: {caption_data}")
                
                # Ensure caption_data is a dict
                if not isinstance(caption_data, dict):
                    logger.error(f"Caption data is not a dict, it's: {type(caption_data)}")
                    return {
                        "status": "error",
                        "message": f"Invalid caption data format: expected dict, got {type(caption_data)}",
                        "caption_source": "format_error",
                        "ai_generated": False
                    }

                # Validate and ensure we have a complete caption
                try:
                    main_text = (caption_data.get("main_text") or "").strip()
                    full_text = (caption_data.get("full_caption") or "").strip()
                    
                    # Check if caption is incomplete (ends with incomplete sentence or is too short)
                    if not main_text or len(main_text) < 20:
                        logger.error("AI generated incomplete or empty main_text")
                        return {
                            "status": "error",
                            "message": "AI generated incomplete caption. Please try again.",
                            "caption_source": "ai_incomplete",
                            "ai_generated": False
                        }
                    
                    # Check if caption appears truncated (ends with incomplete words/sentences)
                    incomplete_indicators = ['...', '…', '..', '--', '---']
                    if any(main_text.endswith(ind) for ind in incomplete_indicators):
                        logger.warning("Caption may be incomplete - ends with ellipsis")
                    
                    if not full_text:
                        caption_data["full_caption"] = main_text
                        full_text = main_text
                    
                    # Ensure full_caption starts with the main_text
                    if not full_text.startswith(main_text):
                        caption_data["full_caption"] = f"{main_text}\n\n{full_text}".strip()
                except Exception as _e:
                    logger.error(f"Failed to validate caption: {_e}")
                    return {
                        "status": "error",
                        "message": f"Error validating AI caption: {str(_e)}. Please try again.",
                        "caption_source": "validation_error",
                        "ai_generated": False
                    }

                # Extract hashtags from the caption FIRST (before adding contact details)
                # This ensures contact details go between caption and hashtags
                import re
                hashtags = []
                try:
                    if "hashtags" in caption_data and caption_data["hashtags"]:
                        hashtags = caption_data["hashtags"]
                        # Ensure hashtags are in list format and have # prefix
                        if isinstance(hashtags, list):
                            hashtags = [tag if isinstance(tag, str) and tag.startswith('#') else f"#{tag}" if isinstance(tag, str) else str(tag) for tag in hashtags if tag]
                        else:
                            hashtags = []
                    else:
                        # Extract hashtags from full caption as backup
                        full_caption_text = caption_data.get("full_caption", "")
                        if full_caption_text:
                            hashtag_matches = re.findall(r'#\w+', full_caption_text)
                            hashtags = list(set(hashtag_matches))  # Remove duplicates
                    
                    # Remove hashtags from caption text so we can add contact details between caption and hashtags
                    if hashtags:
                        # Remove hashtags from main_text and full_caption using regex for safer removal
                        main_text_clean = caption_data.get("main_text", "")
                        full_caption_clean = caption_data.get("full_caption", main_text_clean)
                        
                        # Use regex to remove hashtags (more precise than string replace)
                        try:
                            hashtag_pattern = '|'.join(re.escape(tag) for tag in hashtags if tag)
                            if hashtag_pattern:
                                # Remove hashtags with surrounding whitespace
                                main_text_clean = re.sub(r'\s*' + hashtag_pattern + r'\s*', ' ', main_text_clean, flags=re.IGNORECASE)
                                full_caption_clean = re.sub(r'\s*' + hashtag_pattern + r'\s*', ' ', full_caption_clean, flags=re.IGNORECASE)
                        except Exception as pattern_error:
                            logger.warning(f"Error creating hashtag pattern: {pattern_error}")
                            # Fallback to simple string replacement
                            for tag in hashtags:
                                if tag:
                                    main_text_clean = main_text_clean.replace(tag, " ").strip()
                                    full_caption_clean = full_caption_clean.replace(tag, " ").strip()
                        
                        # Clean up extra spaces and newlines
                        main_text_clean = re.sub(r'\s+', ' ', main_text_clean).strip()
                        full_caption_clean = re.sub(r'\n\s*\n+', '\n\n', full_caption_clean).strip()
                        
                        # Only update if we have valid text
                        if main_text_clean:
                            caption_data["main_text"] = main_text_clean
                        if full_caption_clean:
                            caption_data["full_caption"] = full_caption_clean
                except Exception as hashtag_error:
                    logger.warning(f"Error processing hashtags: {hashtag_error}")
                    # Continue without removing hashtags if there's an error
                    # Ensure hashtags is still a list even if processing failed
                    if not isinstance(hashtags, list):
                        hashtags = []
                    import traceback
                    logger.debug(f"Hashtag processing traceback: {traceback.format_exc()}")

                # Add contact details between caption and hashtags
                try:
                    if contact_info and company_name:
                        original_main = caption_data.get("main_text", "") or ""
                        original_full = caption_data.get("full_caption", original_main) or ""

                        # Avoid duplicating if already present
                        needs_append = not ("WhatsApp" in original_full or "Email" in original_full or "Facebook" in original_full)
                        if needs_append:
                            # Format contact details with proper line breaks
                            formatted_block = f"\n\n📞 Contact us for inquiries:\n{contact_info}"
                            caption_data["full_caption"] = f"{original_full}{formatted_block}".strip()
                            caption_data["main_text"] = f"{original_main}{formatted_block}".strip()
                        else:
                            # Post-process existing contact details to ensure proper formatting
                            # Replace any single-line contact details with properly formatted ones
                            contact_pattern = r'(📱 WhatsApp: [^\n]+)(?:\s+)(✉️ Email: [^\n]+)(?:\s+)(📘 Facebook: [^\n]+)'
                            if re.search(contact_pattern, original_full):
                                # Replace with properly formatted version using the already formatted contact_info
                                formatted_contacts = f"\n{contact_info}"
                                caption_data["full_caption"] = re.sub(contact_pattern, formatted_contacts, original_full)
                                caption_data["main_text"] = re.sub(contact_pattern, formatted_contacts, original_main)
                except Exception as _e:
                    logger.warning(f"Failed to append contact details to caption text: {_e}")
                
                # If no hashtags or insufficient hashtags, generate using AI
                if not hashtags or len(hashtags) < 10:
                    logger.info("Generating additional AI hashtags...")
                    caption_text = caption_data.get("full_caption", caption_data.get("main_text", ""))
                    hashtag_result = self.caption_service.generate_hashtags(
                        content=prompt,
                        caption_text=caption_text,
                        count=15
                    )
                    
                    if hashtag_result.get("status") == "success":
                        ai_hashtags = hashtag_result.get("hashtags", [])
                        # Combine with existing hashtags and remove duplicates
                        all_hashtags = list(set(hashtags + ai_hashtags))
                        logger.info(f"Generated {len(ai_hashtags)} AI hashtags")
                    else:
                        logger.warning(f"AI hashtag generation failed: {hashtag_result.get('message')}")
                        # Use existing hashtags or empty list
                        all_hashtags = hashtags if hashtags else []
                else:
                    all_hashtags = hashtags
                
                logger.info(f"Caption and hashtags generated successfully")
                final_caption_result = {
                    "status": "success",
                    "caption": caption_data.get("main_text", ""),
                    "full_caption": caption_data.get("full_caption", ""),
                    "hashtags": all_hashtags[:15],  # Limit to 15 hashtags
                    "emoji": caption_data.get("emoji", ""),
                    "call_to_action": caption_data.get("call_to_action", ""),
                    "caption_source": "ai",
                    "ai_generated": True
                }
                logger.info(f"Final caption result: {final_caption_result}")
                return final_caption_result
            else:
                error_message = caption_result.get('message', 'Unknown error')
                logger.error(f"AI caption generation failed: {error_message}")
                # Return error instead of fallback - user requested no fallback captions
                return {
                    "status": "error",
                    "message": f"AI caption generation failed: {error_message}. Please try again or check your API configuration.",
                    "caption_source": "ai_failed",
                    "ai_generated": False
                }
                
        except Exception as e:
            logger.error(f"Error generating caption and hashtags: {str(e)}")
            # Return error instead of fallback - user requested no fallback captions
            return {
                "status": "error",
                "message": f"Error generating AI caption: {str(e)}. Please try again or check your API configuration.",
                "caption_source": "error",
                "ai_generated": False
            }
    
    def is_available(self) -> bool:
        """Check if the AI poster service is available"""
        return self.client is not None and self.api_key is not None
