"""
AI Caption Generation Service using Google Gemini 2.5 Flash - FIXED VERSION
Generate captions, descriptions, and content for textile products and images
"""
import os
import logging
import time
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
    
    def generate_product_caption(self, 
                                product_name: str, 
                                product_type: str = "textile",
                                style: str = "modern",
                                tone: str = "professional",
                                include_hashtags: bool = True,
                                include_emoji: bool = True,
                                max_length: int = 200) -> Dict[str, Any]:
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
            
        Returns:
            Dict containing generated caption
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating product caption for: {product_name}")
            
            # Create enhanced prompt for product caption
            prompt = self._create_product_caption_prompt(
                product_name, product_type, style, tone, 
                include_hashtags, include_emoji, max_length
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT'],
                    temperature=0.7,
                    max_output_tokens=500
                ),
            )
            
            # Process response with proper error handling
            generated_text = ""
            if response and response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            generated_text += part.text
                else:
                    return {"status": "error", "message": "No content in response"}
            else:
                return {"status": "error", "message": "No valid response from Gemini"}
            
            if not generated_text:
                return {"status": "error", "message": "No caption generated"}
            
            # Parse and structure the caption
            structured_caption = self._parse_caption_content(
                generated_text, include_hashtags, include_emoji
            )
            
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
                                    call_to_action: bool = True) -> Dict[str, Any]:
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
            
        Returns:
            Dict containing generated social media caption
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating social media caption for {platform}")
            
            # Create enhanced prompt for social media
            prompt = self._create_social_media_prompt(
                content, platform, post_type, style, tone,
                include_hashtags, include_emoji, call_to_action
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT'],
                    temperature=0.8,
                    max_output_tokens=600
                ),
            )
            
            # Process response with proper error handling
            generated_text = ""
            if response and response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            generated_text += part.text
                else:
                    return {"status": "error", "message": "No content in response"}
            else:
                return {"status": "error", "message": "No valid response from Gemini"}
            
            if not generated_text:
                return {"status": "error", "message": "No caption generated"}
            
            # Parse and structure the caption
            structured_caption = self._parse_caption_content(
                generated_text, include_hashtags, include_emoji
            )
            
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
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT'],
                    temperature=0.6,
                    max_output_tokens=400
                ),
            )
            
            # Process response with proper error handling
            generated_text = ""
            if response and response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            generated_text += part.text
                else:
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
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT'],
                    temperature=0.7,
                    max_output_tokens=2000
                ),
            )
            
            # Process response with proper error handling
            generated_text = ""
            if response and response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            generated_text += part.text
                else:
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
                                     max_length: int) -> str:
        """Create enhanced prompt for product caption generation"""
        
        style_instructions = {
            'modern': 'Use contemporary language and trendy expressions',
            'traditional': 'Use classic, timeless language',
            'casual': 'Use relaxed, conversational language',
            'formal': 'Use professional, business-appropriate language'
        }
        
        tone_instructions = {
            'professional': 'Maintain a professional, authoritative tone',
            'friendly': 'Use a warm, approachable tone',
            'authoritative': 'Use a confident, expert tone',
            'conversational': 'Use a natural, conversational tone'
        }
        
        prompt = f"""
        Create a compelling product caption for a {product_type} item named "{product_name}".
        
        Requirements:
        - Style: {style_instructions.get(style, 'Use modern language')}
        - Tone: {tone_instructions.get(tone, 'Use a professional tone')}
        - Maximum length: {max_length} characters
        - Focus on textile/fashion appeal and quality
        """
        
        if include_hashtags:
            prompt += "\n- Include 3-5 relevant hashtags for textile/fashion industry"
        
        if include_emoji:
            prompt += "\n- Use 1-2 appropriate emojis"
        
        prompt += """
        
        Format the response as:
        - Main caption text
        - Hashtags (if requested)
        - Call-to-action (if appropriate)
        
        Make it engaging, informative, and suitable for textile/fashion marketing.
        """
        
        return prompt
    
    def _create_social_media_prompt(self, 
                                   content: str,
                                   platform: str,
                                   post_type: str,
                                   style: str,
                                   tone: str,
                                   include_hashtags: bool,
                                   include_emoji: bool,
                                   call_to_action: bool) -> str:
        """Create enhanced prompt for social media caption generation"""
        
        platform_instructions = {
            'instagram': 'Create an Instagram-optimized caption with visual appeal',
            'facebook': 'Create a Facebook post that encourages engagement',
            'twitter': 'Create a concise Twitter post with impact',
            'linkedin': 'Create a professional LinkedIn post for business audience'
        }
        
        post_type_instructions = {
            'product_showcase': 'Focus on highlighting product features and benefits',
            'behind_scenes': 'Create content that shows the process or story',
            'educational': 'Provide valuable information about textiles/fashion',
            'promotional': 'Create compelling promotional content'
        }
        
        prompt = f"""
        Create a {platform} caption for a {post_type} post about: {content}
        
        Platform: {platform_instructions.get(platform, 'Create an engaging social media post')}
        Post Type: {post_type_instructions.get(post_type, 'Create engaging content')}
        Style: {style} - Use {style} language and approach
        Tone: {tone} - Maintain a {tone} tone throughout
        
        IMPORTANT: Create a caption that:
        - Tells a story and creates emotional connection
        - Uses power words like "stunning", "elegant", "breathtaking", "gorgeous"
        - Includes sensory descriptions (colors, textures, feelings)
        - Creates urgency or FOMO (fear of missing out)
        - Mentions the craftsmanship and quality
        - Appeals to the target audience's aspirations
        - Uses conversational language that feels personal
        - Includes relatable scenarios or occasions
        """
        
        if include_hashtags:
            prompt += """
        - Include 8-12 highly relevant hashtags for textile/fashion industry
        - Mix popular hashtags (#fashion, #style) with niche ones (#handmade, #artisan)
        - Include seasonal/occasion hashtags when relevant
        - Use trending fashion hashtags
        - Include location-based hashtags if applicable
        - Add lifestyle and aspiration hashtags"""
        
        if include_emoji:
            prompt += "\n- Use 2-3 appropriate emojis"
        
        if call_to_action:
            prompt += """
        - Include a compelling call-to-action that creates urgency
        - Use action words like "Shop now", "Get yours", "Don't miss out"
        - Create FOMO with phrases like "Limited time", "Exclusive", "Only a few left"
        - Include contact information or next steps
        - Make it feel personal and direct"""
        
        prompt += """
        
        Format the response as:
        - Main caption text
        - Hashtags (if requested)
        - Call-to-action (if requested)
        
        Make it highly engaging and optimized for the specified platform.
        """
        
        return prompt
    
    def _create_image_caption_prompt(self, 
                                    image_description: str,
                                    caption_type: str,
                                    style: str,
                                    tone: str,
                                    include_hashtags: bool,
                                    include_emoji: bool) -> str:
        """Create enhanced prompt for image caption generation"""
        
        caption_type_instructions = {
            'descriptive': 'Create a detailed description of the image',
            'marketing': 'Create a marketing-focused caption that sells',
            'educational': 'Create an informative caption that teaches',
            'artistic': 'Create a creative, artistic caption'
        }
        
        prompt = f"""
        Create a {caption_type} caption for a textile image described as: {image_description}
        
        Caption Type: {caption_type_instructions.get(caption_type, 'Create a descriptive caption')}
        Style: {style} - Use {style} language
        Tone: {tone} - Maintain a {tone} tone
        """
        
        if include_hashtags:
            prompt += "\n- Include relevant hashtags"
        
        if include_emoji:
            prompt += "\n- Use appropriate emojis"
        
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
        
        # If no hashtags found but requested, extract from text
        if include_hashtags and not hashtags:
            import re
            hashtag_matches = re.findall(r'#\w+', text)
            hashtags = hashtag_matches[:5]  # Limit to 5 hashtags
        
        return {
            'main_content': main_content,
            'hashtags': hashtags,
            'call_to_action': call_to_action,
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
