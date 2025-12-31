"""
AI Caption Generation Service using Google Gemini 2.5 Flash - FIXED VERSION
Generate captions, descriptions, and content for textile products and images
"""
import os
import logging
import time
import random
from typing import Dict, List, Any, Optional
from django.conf import settings

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


class AICaptionService:
    """Service class for AI caption generation using Gemini 2.5 Flash"""
    
    def __init__(self):
        """Initialize the AI caption service"""
        self.api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, 'GEMINI_API_KEY', None)
        self.client = None
        self.max_retries = 3  # Maximum number of retries for API calls
        self.retry_delay_base = 1  # Base delay in seconds for exponential backoff
        
        if not GENAI_AVAILABLE:
            logger.error("Google GenAI library not available")
            return
            
        if not self.api_key:
            logger.error("GEMINI_API_KEY not configured")
            return
            
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini client initialized successfully for caption generation")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            self.client = None
    
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
                logger.warning(f"Caption API call failed (attempt {attempt + 1}/{self.max_retries}): {error_str}")
                logger.info(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
        
        # If we get here, all retries failed
        raise last_exception
    
    def _get_contact_details(self, user) -> tuple:
        """
        Get contact details from user's company profile
        
        Args:
            user: User object
            
        Returns:
            Tuple of (contact_info_string, company_name)
        """
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
                    logger.info(f"Retrieved contact info for caption: {contact_info}")
            except Exception as e:
                logger.warning(f"Error getting contact info: {e}")
        
        return contact_info, company_name
    
    def generate_product_caption(self, 
                                product_name: str, 
                                product_type: str = "textile",
                                style: str = "modern",
                                tone: str = "professional",
                                include_hashtags: bool = True,
                                include_emoji: bool = True,
                                max_length: int = 200,
                                user=None) -> Dict[str, Any]:
        """
        Generate product caption for textile items
        
        Args:
            product_name: Name of the product
            product_type: Type of product (textile, saree, fabric, etc.)
            style: Writing style (modern, traditional, casual, formal)
            tone: Tone of voice (professional, friendly, authoritative, etc.)
            include_hashtags: Whether to include hashtags
            include_emoji: Whether to include emojis
            max_length: Maximum character length
            user: User object for contact details
            
        Returns:
            Dict containing generated caption
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating product caption for: {product_name}")
            
            # Get contact details if user provided
            contact_info, company_name = self._get_contact_details(user)
            
            # Create enhanced prompt for product caption
            prompt = self._create_product_caption_prompt(
                product_name, product_type, style, tone, 
                include_hashtags, include_emoji, max_length,
                contact_info, company_name
            )
            
            try:
                response = self._retry_api_call(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash",
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT'],
                        temperature=0.7,
                        max_output_tokens=500
                    ),
                )
            except Exception as api_error:
                error_str = str(api_error)
                logger.error(f"Product caption API call failed: {error_str}")
                return {
                    "status": "error",
                    "message": "Caption generation failed due to API error. Please try again." if ('500' in error_str or 'INTERNAL' in error_str) else f"Caption generation failed: {error_str}"
                }
            
            # Process response with proper error handling
            generated_text = ""
            if response and response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            generated_text += part.text
                elif candidate.finish_reason and candidate.finish_reason.name == 'MAX_TOKENS':
                    # Handle case where response was truncated due to token limit
                    logger.warning("Response truncated due to MAX_TOKENS limit")
                    return {"status": "error", "message": "Response too long, please try a shorter prompt"}
                else:
                    logger.error(f"No content parts in candidate. Content: {candidate.content}")
                    return {"status": "error", "message": "No content in response"}
            else:
                return {"status": "error", "message": "No valid response from Gemini"}
            
            if not generated_text:
                return {"status": "error", "message": "No caption generated"}
            
            # Parse and structure the caption
            structured_caption = self._parse_caption_content(
                generated_text, include_hashtags, include_emoji
            )
            
            # Append contact details to full_caption if available and not already included
            if contact_info and company_name:
                contact_text = f"\n\nCompany: {company_name}\n{contact_info}"
                if contact_text not in structured_caption.get('full_caption', ''):
                    structured_caption['full_caption'] = (structured_caption.get('full_caption', '') + contact_text).strip()
            
            logger.info(f"Product caption generated successfully for: {product_name}")
            return {
                "status": "success",
                "caption": structured_caption,
                "product_name": product_name,
                "product_type": product_type,
                "style": style,
                "tone": tone,
                "generation_id": f"caption_{int(time.time())}"
            }
            
        except Exception as e:
            logger.error(f"Error generating product caption: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def generate_social_media_caption(self, 
                                    content: str,
                                    platform: str = "instagram",
                                    post_type: str = "product_showcase",
                                    style: str = "engaging",
                                    tone: str = "friendly",
                                    include_hashtags: bool = True,
                                    include_emoji: bool = True,
                                    call_to_action: bool = True,
                                    user=None) -> Dict[str, Any]:
        """
        Generate social media caption for textile content
        
        Args:
            content: Base content or description
            platform: Social media platform (instagram, facebook, twitter, linkedin)
            post_type: Type of post (product_showcase, behind_scenes, educational, promotional)
            style: Writing style (engaging, professional, casual, creative)
            tone: Tone of voice (friendly, authoritative, inspirational, conversational)
            include_hashtags: Whether to include hashtags
            include_emoji: Whether to include emojis
            call_to_action: Whether to include call-to-action
            user: User object for contact details
            
        Returns:
            Dict containing generated social media caption
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating social media caption for {platform}")
            
            # Get contact details if user provided
            contact_info, company_name = self._get_contact_details(user)
            
            # Create enhanced prompt for social media
            prompt = self._create_social_media_prompt(
                content, platform, post_type, style, tone,
                include_hashtags, include_emoji, call_to_action,
                contact_info, company_name
            )
            
            try:
                logger.info(f"Making API call with prompt length: {len(prompt)}")
                logger.debug(f"Prompt preview: {prompt[:200]}...")
                response = self._retry_api_call(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash",
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT'],
                        temperature=0.8,
                        max_output_tokens=4000  # Increased to prevent truncation
                    ),
                )
                logger.info(f"API call succeeded. Response type: {type(response)}")
                logger.info(f"Response has candidates: {hasattr(response, 'candidates') and response.candidates is not None}")
                if hasattr(response, 'candidates') and response.candidates:
                    logger.info(f"Number of candidates: {len(response.candidates)}")
            except Exception as api_error:
                error_str = str(api_error)
                logger.error(f"Caption API call failed after retries: {error_str}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return {
                    "status": "error",
                    "message": "Caption generation failed due to API error. Please try again." if ('500' in error_str or 'INTERNAL' in error_str) else f"Caption generation failed: {error_str}"
                }
            
            # Process response with proper error handling
            if not response:
                logger.error("API call returned None or empty response")
                return {"status": "error", "message": "No response from Gemini API"}
            
            generated_text = ""
            if not hasattr(response, 'candidates') or not response.candidates:
                logger.error(f"Response missing candidates. Response type: {type(response)}, attributes: {dir(response)}")
                return {"status": "error", "message": "Invalid response structure from Gemini API"}
            
            if len(response.candidates) == 0:
                logger.error("Response has empty candidates list")
                return {"status": "error", "message": "No candidates in response from Gemini API"}
            
            candidate = response.candidates[0]
            logger.info(f"Candidate type: {type(candidate)}, finish_reason: {getattr(candidate, 'finish_reason', None)}")
            
            # Check for finish reason first - handle MAX_TOKENS retry
            if candidate.finish_reason:
                finish_reason_name = candidate.finish_reason.name if hasattr(candidate.finish_reason, 'name') else str(candidate.finish_reason)
                if finish_reason_name == 'MAX_TOKENS':
                    logger.warning("Response truncated due to MAX_TOKENS limit - retrying with higher limit")
                    # Retry with higher token limit
                    try:
                        response = self._retry_api_call(
                            self.client.models.generate_content,
                            model="gemini-2.5-flash",
                            contents=[prompt],
                            config=types.GenerateContentConfig(
                                response_modalities=['TEXT'],
                                temperature=0.8,
                                max_output_tokens=8000  # Much higher limit for retry
                            ),
                        )
                        if response and response.candidates and len(response.candidates) > 0:
                            candidate = response.candidates[0]
                            # Re-check finish reason after retry
                            if candidate.finish_reason:
                                finish_reason_name = candidate.finish_reason.name if hasattr(candidate.finish_reason, 'name') else str(candidate.finish_reason)
                                if finish_reason_name not in ['STOP', None]:
                                    logger.error(f"Retry still has finish reason: {finish_reason_name}")
                                    return {"status": "error", "message": f"AI response blocked: {finish_reason_name}"}
                    except Exception as retry_error:
                        logger.error(f"Retry failed: {retry_error}")
                        return {"status": "error", "message": "AI response was too long and retry failed - please try with a shorter prompt"}
                elif finish_reason_name not in ['STOP', None]:
                    # SAFETY, RECITATION, or other blocking reasons
                    logger.error(f"Response blocked by finish reason: {finish_reason_name}")
                    return {"status": "error", "message": f"AI response was blocked: {finish_reason_name}"}
            
            # Extract text from response - try multiple methods
            logger.info(f"Processing candidate. Has content: {bool(candidate.content)}")
            
            # Method 1: Try direct text property on candidate
            if hasattr(candidate, 'text') and candidate.text:
                generated_text = candidate.text
                logger.info(f"Extracted text using candidate.text: {len(generated_text)} chars")
            
            # Method 2: Try content.parts (standard method)
            elif candidate.content:
                logger.info(f"Content has parts: {bool(candidate.content.parts)}")
                if candidate.content.parts:
                    logger.info(f"Number of parts: {len(candidate.content.parts)}")
                    for i, part in enumerate(candidate.content.parts):
                        logger.info(f"Part {i} type: {type(part)}")
                        # Try multiple ways to get text from part
                        part_text = None
                        if hasattr(part, 'text') and part.text:
                            part_text = part.text
                        elif isinstance(part, str):
                            part_text = part
                        elif hasattr(part, '__dict__'):
                            # Try to find text in part's attributes
                            for attr in ['text', 'content', 'data']:
                                if hasattr(part, attr):
                                    attr_value = getattr(part, attr)
                                    if isinstance(attr_value, str) and attr_value:
                                        part_text = attr_value
                                        break
                        
                        if part_text:
                            generated_text += part_text
                            logger.info(f"Extracted {len(part_text)} chars from part {i}")
                    
                    if not generated_text:
                        logger.error(f"No text found in {len(candidate.content.parts)} parts. Finish reason: {candidate.finish_reason}")
                        logger.error(f"Part details: {[str(p) for p in candidate.content.parts]}")
                        return {"status": "error", "message": "No text content in AI response"}
                else:
                    logger.error(f"No content parts in candidate. Finish reason: {candidate.finish_reason}")
                    return {"status": "error", "message": "No content parts in response from AI"}
            else:
                logger.error(f"No content in candidate. Finish reason: {candidate.finish_reason}")
                return {"status": "error", "message": "No content in response from AI"}
            
            # Method 3: Try response.text property (some API versions)
            if not generated_text and hasattr(response, 'text') and response.text:
                generated_text = response.text
                logger.info(f"Extracted text using response.text: {len(generated_text)} chars")
            
            if not generated_text or not generated_text.strip():
                logger.error("Generated text is empty")
                return {"status": "error", "message": "AI generated empty caption - please try again"}
            
            # Parse and structure the caption
            structured_caption = self._parse_caption_content(
                generated_text, include_hashtags, include_emoji
            )
            
            # Append contact details to full_caption if available and not already included
            if contact_info and company_name:
                contact_text = f"\n\nCompany: {company_name}\n{contact_info}"
                full_caption = structured_caption.get('full_caption', '')
                if contact_text not in full_caption and company_name not in full_caption:
                    structured_caption['full_caption'] = (full_caption + contact_text).strip()
            
            logger.info(f"Social media caption generated successfully for {platform}")
            return {
                "status": "success",
                "caption": structured_caption,
                "platform": platform,
                "post_type": post_type,
                "style": style,
                "tone": tone,
                "generation_id": f"social_caption_{int(time.time())}"
            }
            
        except Exception as e:
            logger.error(f"Error generating social media caption: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def generate_image_caption(self, 
                              image_description: str,
                              caption_type: str = "descriptive",
                              style: str = "professional",
                              tone: str = "informative",
                              include_hashtags: bool = False,
                              include_emoji: bool = False) -> Dict[str, Any]:
        """
        Generate caption for textile images
        
        Args:
            image_description: Description of the image content
            caption_type: Type of caption (descriptive, marketing, educational, artistic)
            style: Writing style (professional, creative, technical, casual)
            tone: Tone of voice (informative, persuasive, educational, artistic)
            include_hashtags: Whether to include hashtags
            include_emoji: Whether to include emojis
            
        Returns:
            Dict containing generated image caption
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating image caption for: {image_description[:50]}...")
            
            # Create enhanced prompt for image caption
            prompt = self._create_image_caption_prompt(
                image_description, caption_type, style, tone,
                include_hashtags, include_emoji
            )
            
            try:
                response = self._retry_api_call(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash",
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT'],
                        temperature=0.6,
                        max_output_tokens=400
                    ),
                )
            except Exception as api_error:
                error_str = str(api_error)
                logger.error(f"Image caption API call failed: {error_str}")
                return {
                    "status": "error",
                    "message": "Caption generation failed due to API error. Please try again." if ('500' in error_str or 'INTERNAL' in error_str) else f"Caption generation failed: {error_str}"
                }
            
            # Process response with proper error handling
            generated_text = ""
            if response and response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            generated_text += part.text
                elif candidate.finish_reason and candidate.finish_reason.name == 'MAX_TOKENS':
                    # Handle case where response was truncated due to token limit
                    logger.warning("Response truncated due to MAX_TOKENS limit")
                    return {"status": "error", "message": "Response too long, please try a shorter prompt"}
                else:
                    logger.error(f"No content parts in candidate. Content: {candidate.content}")
                    return {"status": "error", "message": "No content in response"}
            else:
                return {"status": "error", "message": "No valid response from Gemini"}
            
            if not generated_text:
                return {"status": "error", "message": "No caption generated"}
            
            # Parse and structure the caption
            structured_caption = self._parse_caption_content(
                generated_text, include_hashtags, include_emoji
            )
            
            logger.info(f"Image caption generated successfully")
            return {
                "status": "success",
                "caption": structured_caption,
                "caption_type": caption_type,
                "style": style,
                "tone": tone,
                "generation_id": f"image_caption_{int(time.time())}"
            }
            
        except Exception as e:
            logger.error(f"Error generating image caption: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def generate_hashtags(self, 
                         content: str,
                         caption_text: str = "",
                         count: int = 15) -> Dict[str, Any]:
        """
        Generate AI-powered hashtags based on content and caption
        
        Args:
            content: Original prompt or product description
            caption_text: Generated caption text (optional)
            count: Number of hashtags to generate (default 15)
            
        Returns:
            Dict containing generated hashtags
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating AI hashtags for content: {content[:50]}...")
            
            # Create prompt for hashtag generation
            hashtag_prompt = f"""Generate {count} highly relevant, specific hashtags for a social media post about: {content}

"""
            if caption_text:
                hashtag_prompt += f"The caption is: {caption_text}\n\n"
            
            hashtag_prompt += f"""Requirements:
- Generate {count} specific, relevant hashtags
- Mix popular and niche hashtags for better reach
- Include hashtags specific to the product type, style, occasion, and target audience
- Avoid generic hashtags - be specific to the content
- Include fashion/textile industry hashtags
- Consider trending and relevant tags
- Each hashtag should be relevant and add value

Return ONLY a JSON array of hashtags (with # prefix), like this:
["#hashtag1", "#hashtag2", "#hashtag3", ...]

Do not include any other text, just the JSON array."""
            
            try:
                response = self._retry_api_call(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash",
                    contents=[hashtag_prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT'],
                        temperature=0.7,
                        max_output_tokens=500
                    ),
                )
            except Exception as api_error:
                error_str = str(api_error)
                logger.error(f"Hashtag generation API call failed: {error_str}")
                return {
                    "status": "error",
                    "message": "Hashtag generation failed due to API error. Please try again." if ('500' in error_str or 'INTERNAL' in error_str) else f"Hashtag generation failed: {error_str}"
                }
            
            # Process response
            generated_text = ""
            if response and response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            generated_text += part.text
            
            if not generated_text:
                return {"status": "error", "message": "No hashtags generated"}
            
            # Parse JSON array
            try:
                import json
                import re
                # Extract JSON array from response
                json_match = re.search(r'\[.*?\]', generated_text, re.DOTALL)
                if json_match:
                    hashtags = json.loads(json_match.group())
                    # Ensure all hashtags have # prefix
                    hashtags = [tag if tag.startswith('#') else f"#{tag}" for tag in hashtags]
                    hashtags = [tag for tag in hashtags if tag.strip()]  # Remove empty
                    return {
                        "status": "success",
                        "hashtags": hashtags[:count],
                        "count": len(hashtags[:count])
                    }
                else:
                    # Fallback: extract hashtags from text
                    hashtag_matches = re.findall(r'#\w+', generated_text)
                    if hashtag_matches:
                        return {
                            "status": "success",
                            "hashtags": list(set(hashtag_matches))[:count],
                            "count": len(list(set(hashtag_matches))[:count])
                        }
                    else:
                        return {"status": "error", "message": "Could not parse hashtags from response"}
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error parsing hashtag JSON: {e}")
                # Try to extract hashtags from text
                import re
                hashtag_matches = re.findall(r'#\w+', generated_text)
                if hashtag_matches:
                    return {
                        "status": "success",
                        "hashtags": list(set(hashtag_matches))[:count],
                        "count": len(list(set(hashtag_matches))[:count])
                    }
                return {"status": "error", "message": f"Failed to parse hashtags: {str(e)}"}
            
        except Exception as e:
            logger.error(f"Error generating hashtags: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def generate_bulk_captions(self, 
                             products: List[Dict[str, Any]],
                             caption_style: str = "consistent",
                             brand_voice: str = "professional") -> Dict[str, Any]:
        """
        Generate multiple captions for bulk products
        
        Args:
            products: List of product dictionaries with names and types
            caption_style: Style for all captions (consistent, varied, seasonal)
            brand_voice: Brand voice to maintain across captions
            
        Returns:
            Dict containing all generated captions
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating bulk captions for {len(products)} products")
            
            # Create bulk prompt
            prompt = self._create_bulk_caption_prompt(products, caption_style, brand_voice)
            
            try:
                response = self._retry_api_call(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash",
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT'],
                        temperature=0.7,
                        max_output_tokens=2000
                    ),
                )
            except Exception as api_error:
                error_str = str(api_error)
                logger.error(f"Bulk caption API call failed: {error_str}")
                return {
                    "status": "error",
                    "message": "Bulk caption generation failed due to API error. Please try again." if ('500' in error_str or 'INTERNAL' in error_str) else f"Bulk caption generation failed: {error_str}"
                }
            
            # Process response with proper error handling
            generated_text = ""
            if response and response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            generated_text += part.text
                elif candidate.finish_reason and candidate.finish_reason.name == 'MAX_TOKENS':
                    # Handle case where response was truncated due to token limit
                    logger.warning("Response truncated due to MAX_TOKENS limit")
                    return {"status": "error", "message": "Response too long, please try a shorter prompt"}
                else:
                    logger.error(f"No content parts in candidate. Content: {candidate.content}")
                    return {"status": "error", "message": "No content in response"}
            else:
                return {"status": "error", "message": "No valid response from Gemini"}
            
            if not generated_text:
                return {"status": "error", "message": "No captions generated"}
            
            # Parse bulk captions
            structured_captions = self._parse_bulk_captions(generated_text, products)
            
            logger.info(f"Bulk captions generated successfully for {len(products)} products")
            return {
                "status": "success",
                "captions": structured_captions,
                "total_products": len(products),
                "caption_style": caption_style,
                "brand_voice": brand_voice,
                "generation_id": f"bulk_captions_{int(time.time())}"
            }
            
        except Exception as e:
            logger.error(f"Error generating bulk captions: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _create_product_caption_prompt(self, 
                                     product_name: str, 
                                     product_type: str,
                                     style: str, 
                                     tone: str,
                                     include_hashtags: bool,
                                     include_emoji: bool,
                                     max_length: int,
                                     contact_info: str = "",
                                     company_name: str = "") -> str:
        """Create prompt for product caption generation"""
        
        prompt = f"Create a product caption for a {product_type} named {product_name}."
        
        if include_hashtags:
            prompt += " Include hashtags."
        
        if include_emoji:
            prompt += " Include emojis."
        
        # Add contact details if available
        if contact_info and company_name:
            prompt += f"\n\nInclude the following contact information at the end:\nCompany: {company_name}\n{contact_info}"
        
        return prompt
    
    def _create_social_media_prompt(self, 
                                   content: str,
                                   platform: str,
                                   post_type: str,
                                   style: str,
                                   tone: str,
                                   include_hashtags: bool,
                                   include_emoji: bool,
                                   call_to_action: bool,
                                   contact_info: str = "",
                                   company_name: str = "") -> str:
        """Create prompt for social media caption generation"""
        
        prompt = f"Create a {platform} caption about: {content}"
        
        if include_hashtags:
            prompt += " Include hashtags."
        
        if include_emoji:
            prompt += " Include emojis."
        
        if call_to_action:
            prompt += " Include call to action."
        
        # Add contact details if available
        contact_section = ""
        if contact_info and company_name:
            contact_section = f"\n\nMANDATORY: Include the following contact information at the end of the caption:\nCompany: {company_name}\n{contact_info}\n\nFormat contact details exactly as shown above, each on separate line."
        
        prompt += f"""

Return as JSON:
{{
    "main_text": "Main caption text",
    "full_caption": "Full caption with hashtags{(' and contact details' if contact_info else '')}",
    "hashtags": ["#tag1", "#tag2"],
    "emoji": "✨",
    "call_to_action": "CTA text"
}}{contact_section}"""
        
        return prompt
    
    def _create_image_caption_prompt(self, 
                                    image_description: str,
                                    caption_type: str,
                                    style: str,
                                    tone: str,
                                    include_hashtags: bool,
                                    include_emoji: bool) -> str:
        """Create prompt for image caption generation"""
        
        prompt = f"Create a {caption_type} caption for: {image_description}"
        
        if include_hashtags:
            prompt += " Include hashtags."
        
        if include_emoji:
            prompt += " Include emojis."
        
        prompt += """
        
        Focus on the textile/fashion aspects and make it engaging for the target audience.
        """
        
        return prompt
    
    def _create_bulk_caption_prompt(self, 
                                   products: List[Dict[str, Any]],
                                   caption_style: str,
                                   brand_voice: str) -> str:
        """Create enhanced prompt for bulk caption generation"""
        
        product_list = "\n".join([f"- {p.get('name', 'Unknown')} ({p.get('type', 'textile')})" for p in products])
        
        prompt = f"""
        Create captions for the following textile products:
        
        {product_list}
        
        Requirements:
        - Caption Style: {caption_style} - Maintain consistency across all captions
        - Brand Voice: {brand_voice} - Use a {brand_voice} voice throughout
        - Include hashtags for each product
        - Use appropriate emojis
        - Make each caption unique but consistent with brand voice
        
        Format the response as:
        Product 1: [Caption]
        Product 2: [Caption]
        etc.
        
        Ensure each caption is engaging and suitable for textile/fashion marketing.
        """
        
        return prompt
    
    def _parse_caption_content(self, 
                             text: str, 
                             include_hashtags: bool, 
                             include_emoji: bool) -> Dict[str, Any]:
        """Parse and structure the generated caption content"""
        
        # Try to parse as JSON first
        try:
            import json
            import re
            # Look for JSON in the text - try multiple strategies
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = text[json_start:json_end]
                
                # Try to fix common JSON issues
                # Remove trailing commas before closing braces
                json_text = re.sub(r',\s*}', '}', json_text)
                json_text = re.sub(r',\s*]', ']', json_text)
                
                try:
                    parsed_json = json.loads(json_text)
                except json.JSONDecodeError as e:
                    # Try to extract partial JSON if complete parsing fails
                    logger.warning(f"JSON parse error: {e}, attempting to extract partial data")
                    # Try to extract fields manually using regex
                    main_match = re.search(r'"main_text"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', json_text, re.DOTALL)
                    full_match = re.search(r'"full_caption"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', json_text, re.DOTALL)
                    hashtags_match = re.search(r'"hashtags"\s*:\s*\[(.*?)\]', json_text, re.DOTALL)
                    
                    main_content = main_match.group(1).replace('\\"', '"').replace('\\n', '\n') if main_match else ''
                    full_caption = full_match.group(1).replace('\\"', '"').replace('\\n', '\n') if full_match else main_content
                    hashtags = []
                    if hashtags_match:
                        hashtag_text = hashtags_match.group(1)
                        hashtags = re.findall(r'"([^"]+)"', hashtag_text)
                        hashtags = [tag if tag.startswith('#') else f"#{tag}" for tag in hashtags]
                    
                    if main_content:
                        return {
                            'main_text': main_content,
                            'full_caption': full_caption or main_content,
                            'hashtags': hashtags,
                            'call_to_action': '',
                            'emoji': '',
                            'word_count': len(main_content.split()),
                            'character_count': len(main_content),
                            'has_emoji': any(ord(char) > 127 for char in main_content)
                        }
                    else:
                        raise  # Re-raise to fall through to text parsing
                
                # Extract data from JSON
                main_content = parsed_json.get('main_text', '').strip()
                full_caption = parsed_json.get('full_caption', main_content).strip()
                hashtags = parsed_json.get('hashtags', [])
                call_to_action = parsed_json.get('call_to_action', '').strip()
                emoji = parsed_json.get('emoji', '').strip()
                
                # Validate that main_content is not empty
                if not main_content:
                    raise ValueError("main_text is empty in JSON response")
                
                return {
                    'main_text': main_content,
                    'full_caption': full_caption or main_content,
                    'hashtags': hashtags if isinstance(hashtags, list) else [],
                    'call_to_action': call_to_action,
                    'emoji': emoji,
                    'word_count': len(main_content.split()),
                    'character_count': len(main_content),
                    'has_emoji': bool(emoji) or any(ord(char) > 127 for char in main_content)
                }
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"JSON parsing failed: {e}, falling back to text parsing")
            # Fall back to text parsing if JSON parsing fails
            pass
        
        # Fallback to original text parsing
        lines = text.strip().split('\n')
        main_content = ""
        hashtags = []
        call_to_action = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                hashtags.append(line)
            elif line.lower().startswith(('call to action', 'cta', 'action')):
                call_to_action = line
            elif line and not line.startswith('#'):
                if main_content:
                    main_content += " " + line
                else:
                    main_content = line
        
        # If no hashtags found but requested, generate them using AI
        if include_hashtags and not hashtags:
            # Try to extract from text first
            import re
            hashtag_matches = re.findall(r'#\w+', text)
            if hashtag_matches:
                hashtags = list(set(hashtag_matches))  # Remove duplicates
            else:
                # If still no hashtags, we'll need to generate them separately
                # This will be handled by the calling function
                logger.warning("No hashtags found in generated text - will need AI generation")
        
        return {
            'main_text': main_content,
            'full_caption': main_content,
            'hashtags': hashtags,
            'call_to_action': call_to_action,
            'emoji': '',
            'word_count': len(main_content.split()),
            'character_count': len(main_content),
            'has_emoji': any(ord(char) > 127 for char in main_content)
        }
    
    def _parse_bulk_captions(self, 
                           text: str, 
                           products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse bulk captions from generated text"""
        
        captions = []
        lines = text.strip().split('\n')
        
        for i, product in enumerate(products):
            product_name = product.get('name', f'Product {i+1}')
            
            # Find caption for this product
            caption_text = ""
            for line in lines:
                if product_name.lower() in line.lower() or f"Product {i+1}" in line:
                    caption_text = line.split(':', 1)[1].strip() if ':' in line else line
                    break
            
            if not caption_text:
                caption_text = f"Beautiful {product.get('type', 'textile')} - {product_name}"
            
            # Parse hashtags
            import re
            hashtags = re.findall(r'#\w+', caption_text)
            
            captions.append({
                'product_name': product_name,
                'product_type': product.get('type', 'textile'),
                'caption': caption_text,
                'hashtags': hashtags,
                'word_count': len(caption_text.split()),
                'character_count': len(caption_text)
            })
        
        return captions
    
    def is_available(self) -> bool:
        """Check if the AI caption service is available"""
        return self.client is not None and self.api_key is not None
