"""
Poster Generator Service with AI Caption Suggestions
Implements Phase 1 Week 1 Member 3 tasks for textile poster generation
"""
import logging
import json
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.utils import timezone
from .models import AIGenerationRequest, AIProvider, AITemplate
from .services import AIGenerationService, AIPromptEngineeringService

logger = logging.getLogger(__name__)


class TextilePosterGenerator:
    """Service for generating textile posters with AI-powered captions"""
    
    def __init__(self):
        self.ai_service = AIGenerationService()
        self.prompt_service = AIPromptEngineeringService()
    
    def generate_poster_with_caption(self, 
                                   organization,
                                   user,
                                   fabric_image_url: str = None,
                                   fabric_type: str = 'saree',
                                   festival: str = 'deepavali',
                                   price_range: str = '₹2999',
                                   style: str = 'elegant',
                                   color_scheme: str = None,
                                   custom_text: str = None,
                                   offer_details: str = None) -> Dict[str, Any]:
        """
        Generate a textile poster with AI-suggested caption
        
        Args:
            organization: Organization instance
            user: User instance
            fabric_image_url: URL of the fabric image (optional)
            fabric_type: Type of fabric (saree, cotton, silk, etc.)
            festival: Festival theme (deepavali, pongal, wedding, etc.)
            price_range: Price range text
            style: Design style (elegant, modern, traditional)
            color_scheme: Color scheme description
            custom_text: Custom text to include
            
        Returns:
            Dict containing poster generation results and caption suggestions
        """
        try:
            # Generate AI caption suggestions
            caption_suggestions = self.generate_caption_suggestions(
                fabric_type=fabric_type,
                festival=festival,
                price_range=price_range,
                style=style,
                custom_text=custom_text
            )
            
            # Select best caption for poster generation
            selected_caption = caption_suggestions[0]['text'] if caption_suggestions else "Elegant Textile Collection"
            
            # Generate poster prompt
            poster_prompt = self.create_poster_prompt(
                fabric_type=fabric_type,
                festival=festival,
                style=style,
                color_scheme=color_scheme,
                caption_text=selected_caption
            )
            
            # Get or create NanoBanana provider
            provider = self.get_nanobanana_provider()
            
            # Create generation request
            request = AIGenerationRequest.objects.create(
                organization=organization,
                user=user,
                provider=provider,
                generation_type='poster',
                prompt=poster_prompt,
                negative_prompt=self.prompt_service.generate_negative_prompt('poster'),
                parameters={
                    'fabric_type': fabric_type,
                    'festival': festival,
                    'style': style,
                    'color_scheme': color_scheme,
                    'price_range': price_range,
                    'width': 1024,
                    'height': 1024,
                    'steps': 20,
                    'guidance_scale': 7.5
                }
            )
            
            # Process the generation request
            success = self.ai_service.process_generation_request(request)
            
            if success:
                result = {
                    'success': True,
                    'request_id': str(request.id),
                    'poster_urls': request.result_urls,
                    'caption_suggestions': caption_suggestions,
                    'selected_caption': selected_caption,
                    'prompt_used': poster_prompt,
                    'parameters': request.parameters,
                    'cost': float(request.cost or 0),
                    'processing_time': request.processing_time
                }
            else:
                result = {
                    'success': False,
                    'error': request.error_message,
                    'caption_suggestions': caption_suggestions,
                    'request_id': str(request.id)
                }
            
            logger.info(f"Poster generation completed for request {request.id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate poster: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'caption_suggestions': []
            }
    
    def generate_caption_suggestions(self,
                                   fabric_type: str,
                                   festival: str = None,
                                   price_range: str = None,
                                   style: str = 'elegant',
                                   custom_text: str = None,
                                   product_name: str = None,
                                   offer_details: str = None) -> List[Dict[str, Any]]:
        """
        Generate AI-powered caption suggestions for textile posters
        
        Returns:
            List of caption suggestions with metadata
        """
        suggestions = []
        
        # Template-based caption generation
        base_templates = self.get_caption_templates(fabric_type, festival, style)
        
        for template in base_templates:
            caption = template['template'].format(
                fabric_type=fabric_type.title(),
                festival=festival.title() if festival else '',
                price=price_range or '₹2999',
                style=style.title()
            )
            
            suggestions.append({
                'text': caption,
                'type': template['type'],
                'tone': template['tone'],
                'target_audience': template['target_audience'],
                'effectiveness_score': template['score']
            })
        
        # Add custom text variations if provided
        if custom_text:
            custom_variations = self.create_custom_text_variations(custom_text, fabric_type, price_range)
            suggestions.extend(custom_variations)
        
        # Sort by effectiveness score
        suggestions.sort(key=lambda x: x['effectiveness_score'], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_caption_templates(self, fabric_type: str, festival: str, style: str) -> List[Dict[str, Any]]:
        """Get caption templates based on fabric type and festival"""
        
        templates = []
        
        # Festival-specific templates
        if festival:
            festival_templates = {
                'deepavali': [
                    {
                        'template': '✨ Celebrate Deepavali in Style! ✨\n{fabric_type} Collection Starting {price}\n#Deepavali2024 #FestiveWear',
                        'type': 'festival_celebration',
                        'tone': 'festive',
                        'target_audience': 'festival_shoppers',
                        'score': 9.2
                    },
                    {
                        'template': '🪔 Light up your Deepavali! 🪔\nExquisite {fabric_type} - From {price}\nShop Now for Festival Season!',
                        'type': 'festival_urgent',
                        'tone': 'urgent_festive',
                        'target_audience': 'last_minute_shoppers',
                        'score': 8.8
                    }
                ],
                'pongal': [
                    {
                        'template': '🌾 Pongal Special Collection 🌾\nTraditional {fabric_type} Starting {price}\n#PongalFestival #TraditionalWear',
                        'type': 'traditional_festival',
                        'tone': 'traditional',
                        'target_audience': 'traditional_buyers',
                        'score': 9.0
                    }
                ],
                'wedding': [
                    {
                        'template': '💍 Wedding Season Special 💍\nLuxurious {fabric_type} Collection\nStarting {price} - Perfect for Your Big Day!',
                        'type': 'wedding_luxury',
                        'tone': 'luxurious',
                        'target_audience': 'wedding_shoppers',
                        'score': 9.5
                    }
                ]
            }
            
            if festival.lower() in festival_templates:
                templates.extend(festival_templates[festival.lower()])
        
        # General templates
        general_templates = [
            {
                'template': '🌟 New Arrival Alert! 🌟\n{style} {fabric_type} Collection\nStarting {price} - Limited Stock!',
                'type': 'new_arrival',
                'tone': 'exciting',
                'target_audience': 'fashion_conscious',
                'score': 8.5
            },
            {
                'template': '💫 Premium {fabric_type} Collection 💫\nCrafted with Love, Priced with Care\nStarting {price}',
                'type': 'premium_quality',
                'tone': 'premium',
                'target_audience': 'quality_seekers',
                'score': 8.7
            },
            {
                'template': '🛍️ Special Offer! 🛍️\nBeautiful {fabric_type} Collection\nStarting {price} - Don\'t Miss Out!',
                'type': 'special_offer',
                'tone': 'promotional',
                'target_audience': 'bargain_hunters',
                'score': 8.3
            }
        ]
        
        templates.extend(general_templates)
        return templates
    
    def create_custom_text_variations(self, custom_text: str, fabric_type: str, price_range: str) -> List[Dict[str, Any]]:
        """Create variations of custom text"""
        variations = []
        
        # Simple variations
        variations.append({
            'text': f"{custom_text}\n{fabric_type.title()} Collection - {price_range}",
            'type': 'custom_simple',
            'tone': 'neutral',
            'target_audience': 'general',
            'effectiveness_score': 7.5
        })
        
        # Enhanced variation
        variations.append({
            'text': f"✨ {custom_text} ✨\nPremium {fabric_type.title()} Starting {price_range}",
            'type': 'custom_enhanced',
            'tone': 'enhanced',
            'target_audience': 'general',
            'effectiveness_score': 8.0
        })
        
        return variations
    
    def create_poster_prompt(self,
                           fabric_type: str,
                           festival: str = None,
                           style: str = 'elegant',
                           color_scheme: str = None,
                           caption_text: str = None) -> str:
        """Create AI prompt for poster generation"""
        
        # Base prompt for textile poster
        base_prompt = f"Professional textile poster design for {fabric_type}"
        
        # Add style elements
        style_elements = {
            'elegant': 'elegant design, sophisticated layout, premium feel',
            'modern': 'modern design, clean lines, contemporary style',
            'traditional': 'traditional design, cultural motifs, classic patterns',
            'festive': 'festive design, celebratory elements, vibrant colors'
        }
        
        if style.lower() in style_elements:
            base_prompt += f", {style_elements[style.lower()]}"
        
        # Add festival elements
        if festival:
            festival_elements = {
                'deepavali': 'Deepavali theme, golden colors, diyas, rangoli patterns, festive lighting',
                'pongal': 'Pongal theme, harvest colors, traditional motifs, cultural elements',
                'wedding': 'wedding theme, auspicious colors, elegant borders, ceremonial design'
            }
            
            if festival.lower() in festival_elements:
                base_prompt += f", {festival_elements[festival.lower()]}"
        
        # Add color scheme
        if color_scheme:
            base_prompt += f", color palette: {color_scheme}"
        
        # Add fabric-specific elements
        fabric_elements = {
            'saree': 'silk saree display, draping showcase, traditional elegance',
            'cotton': 'cotton fabric texture, natural appearance, comfortable feel',
            'silk': 'silk fabric luxury, lustrous finish, premium quality',
            'linen': 'linen fabric texture, breathable appearance, casual elegance'
        }
        
        if fabric_type.lower() in fabric_elements:
            base_prompt += f", {fabric_elements[fabric_type.lower()]}"
        
        # Add poster-specific requirements
        base_prompt += ", commercial poster design, high resolution, professional layout"
        base_prompt += ", suitable for printing, eye-catching design, marketing poster"
        
        return base_prompt
    
    def get_nanobanana_provider(self) -> AIProvider:
        """Get or create NanoBanana AI provider"""
        provider, created = AIProvider.objects.get_or_create(
            name='nanobanana',
            defaults={
                'api_key': settings.NANOBANANA_API_KEY,
                'api_url': 'https://api.banana.dev',
                'is_active': True,
                'rate_limit_per_minute': 10,
                'rate_limit_per_hour': 100
            }
        )
        
        if created:
            logger.info("Created new NanoBanana AI provider")
        
        return provider
    
    def get_poster_templates(self, category: str = 'textile') -> List[Dict[str, Any]]:
        """Get available poster templates"""
        from django.db import models
        
        templates = AITemplate.objects.filter(
            category='poster',
            is_active=True
        ).filter(
            models.Q(is_public=True) | models.Q(organization=None)
        )
        
        template_list = []
        for template in templates:
            template_list.append({
                'id': str(template.id),
                'name': template.name,
                'description': template.description,
                'prompt_template': template.prompt_template,
                'usage_count': template.usage_count
            })
        
        return template_list
    
    def save_poster_template(self,
                           organization,
                           name: str,
                           description: str,
                           prompt_template: str,
                           parameters: Dict = None) -> str:
        """Save a custom poster template"""
        template = AITemplate.objects.create(
            organization=organization,
            name=name,
            description=description,
            category='poster',
            prompt_template=prompt_template,
            default_parameters=parameters or {}
        )
        
        logger.info(f"Created poster template {template.id} for organization {organization.name}")
        return str(template.id)


class FestivalKitGenerator:
    """Service for generating festival-specific design kits"""
    
    def __init__(self):
        self.poster_generator = TextilePosterGenerator()
    
    def generate_festival_kit(self,
                            organization,
                            user,
                            festival: str,
                            fabric_types: List[str] = None,
                            color_schemes: List[str] = None,
                            price_ranges: List[str] = None) -> Dict[str, Any]:
        """
        Generate a complete festival kit with multiple posters and themes
        
        Args:
            organization: Organization instance
            user: User instance
            festival: Festival name (deepavali, pongal, wedding)
            fabric_types: List of fabric types to include
            color_schemes: List of color schemes
            price_ranges: List of price ranges
            
        Returns:
            Dict containing festival kit results
        """
        try:
            fabric_types = fabric_types or ['saree', 'silk', 'cotton']
            color_schemes = color_schemes or ['golden', 'red and gold', 'traditional']
            price_ranges = price_ranges or ['₹1999', '₹2999', '₹4999']
            
            kit_results = {
                'festival': festival,
                'posters': [],
                'themes': self.get_festival_themes(festival),
                'color_palettes': self.get_festival_color_palettes(festival),
                'success': True,
                'total_cost': 0
            }
            
            # Generate posters for each combination
            for i, fabric_type in enumerate(fabric_types):
                color_scheme = color_schemes[i % len(color_schemes)]
                price_range = price_ranges[i % len(price_ranges)]
                
                poster_result = self.poster_generator.generate_poster_with_caption(
                    organization=organization,
                    user=user,
                    fabric_type=fabric_type,
                    festival=festival,
                    price_range=price_range,
                    color_scheme=color_scheme,
                    style='festive'
                )
                
                if poster_result['success']:
                    kit_results['posters'].append({
                        'fabric_type': fabric_type,
                        'color_scheme': color_scheme,
                        'price_range': price_range,
                        'poster_urls': poster_result['poster_urls'],
                        'caption': poster_result['selected_caption'],
                        'request_id': poster_result['request_id']
                    })
                    kit_results['total_cost'] += poster_result.get('cost', 0)
            
            logger.info(f"Generated festival kit for {festival} with {len(kit_results['posters'])} posters")
            return kit_results
            
        except Exception as e:
            logger.error(f"Failed to generate festival kit: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'festival': festival
            }
    
    def get_festival_themes(self, festival: str) -> List[Dict[str, Any]]:
        """Get theme suggestions for a festival"""
        themes = {
            'deepavali': [
                {
                    'name': 'Golden Elegance',
                    'colors': ['#FFD700', '#FFA500', '#FF6347'],
                    'elements': ['diyas', 'rangoli', 'golden borders'],
                    'mood': 'luxurious'
                },
                {
                    'name': 'Traditional Lights',
                    'colors': ['#FF4500', '#FFD700', '#8B0000'],
                    'elements': ['oil lamps', 'traditional patterns', 'warm lighting'],
                    'mood': 'traditional'
                }
            ],
            'pongal': [
                {
                    'name': 'Harvest Colors',
                    'colors': ['#DAA520', '#228B22', '#FF6347'],
                    'elements': ['rice patterns', 'harvest motifs', 'traditional pots'],
                    'mood': 'earthy'
                }
            ],
            'wedding': [
                {
                    'name': 'Royal Wedding',
                    'colors': ['#FFD700', '#8B0000', '#FF1493'],
                    'elements': ['floral borders', 'elegant patterns', 'ceremonial designs'],
                    'mood': 'royal'
                }
            ]
        }
        
        return themes.get(festival.lower(), [])
    
    def get_festival_color_palettes(self, festival: str) -> List[Dict[str, Any]]:
        """Get color palette suggestions for a festival"""
        palettes = {
            'deepavali': [
                {
                    'name': 'Golden Glow',
                    'primary': '#FFD700',
                    'secondary': '#FFA500',
                    'accent': '#FF6347',
                    'background': '#FFF8DC'
                },
                {
                    'name': 'Royal Red',
                    'primary': '#8B0000',
                    'secondary': '#FFD700',
                    'accent': '#FF4500',
                    'background': '#FFF5EE'
                }
            ],
            'pongal': [
                {
                    'name': 'Harvest Gold',
                    'primary': '#DAA520',
                    'secondary': '#228B22',
                    'accent': '#FF6347',
                    'background': '#F5F5DC'
                }
            ],
            'wedding': [
                {
                    'name': 'Bridal Elegance',
                    'primary': '#FFD700',
                    'secondary': '#8B0000',
                    'accent': '#FF1493',
                    'background': '#FFF0F5'
                }
            ]
        }
        
        return palettes.get(festival.lower(), [])
