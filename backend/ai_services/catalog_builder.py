"""
Catalog Builder Service with AI Auto-fill Descriptions
Implements Phase 1 Week 1 Member 3 tasks for textile catalog generation
"""
import logging
import json
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.utils import timezone
from .models import AIGenerationRequest, AIProvider, AITemplate
from .services import AIGenerationService, AIPromptEngineeringService

logger = logging.getLogger(__name__)


class TextileCatalogBuilder:
    """Service for building textile catalogs with AI-generated descriptions"""
    
    def __init__(self):
        self.ai_service = AIGenerationService()
        self.prompt_service = AIPromptEngineeringService()
    
    def build_catalog_with_ai_descriptions(self,
                                         organization,
                                         user,
                                         products: List[Dict[str, Any]],
                                         catalog_style: str = 'modern',
                                         layout_type: str = 'grid',
                                         theme: str = 'professional',
                                         auto_generate_descriptions: bool = True) -> Dict[str, Any]:
        """
        Build a complete catalog with AI-generated product descriptions
        
        Args:
            organization: Organization instance
            user: User instance
            products: List of product dictionaries with basic info
            catalog_style: Style of the catalog (modern, traditional, elegant)
            layout_type: Layout type (grid, list, magazine)
            theme: Theme (professional, festive, luxury)
            auto_generate_descriptions: Whether to auto-generate descriptions
            
        Returns:
            Dict containing catalog generation results
        """
        try:
            # Process products and generate descriptions
            processed_products = []
            total_cost = 0
            
            for product in products:
                if auto_generate_descriptions:
                    # Generate AI description for each product
                    description_result = self.generate_product_description(
                        organization=organization,
                        user=user,
                        product_info=product
                    )
                    
                    if description_result['success']:
                        product['ai_description'] = description_result['description']
                        product['description_variations'] = description_result['variations']
                        total_cost += description_result.get('cost', 0)
                    else:
                        product['ai_description'] = self.get_fallback_description(product)
                        product['description_variations'] = []
                
                processed_products.append(product)
            
            # Generate catalog layout
            catalog_result = self.generate_catalog_layout(
                organization=organization,
                user=user,
                products=processed_products,
                style=catalog_style,
                layout_type=layout_type,
                theme=theme
            )
            
            if catalog_result['success']:
                result = {
                    'success': True,
                    'catalog_id': catalog_result['request_id'],
                    'catalog_urls': catalog_result['catalog_urls'],
                    'products': processed_products,
                    'layout_info': {
                        'style': catalog_style,
                        'layout_type': layout_type,
                        'theme': theme,
                        'product_count': len(processed_products)
                    },
                    'total_cost': total_cost + catalog_result.get('cost', 0),
                    'processing_time': catalog_result.get('processing_time', 0)
                }
            else:
                result = {
                    'success': False,
                    'error': catalog_result.get('error', 'Catalog generation failed'),
                    'products': processed_products,
                    'total_cost': total_cost
                }
            
            logger.info(f"Catalog building completed with {len(processed_products)} products")
            return result
            
        except Exception as e:
            logger.error(f"Failed to build catalog: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'products': []
            }
    
    def generate_product_description(self,
                                   organization,
                                   user,
                                   product_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered product description
        
        Args:
            organization: Organization instance
            user: User instance
            product_info: Dictionary containing product information
            
        Returns:
            Dict containing generated description and variations
        """
        try:
            # Extract product information
            product_name = product_info.get('name', 'Textile Product')
            fabric_type = product_info.get('fabric_type', 'cotton')
            color = product_info.get('color', '')
            price = product_info.get('price', '')
            category = product_info.get('category', 'textile')
            features = product_info.get('features', [])
            
            # Generate multiple description variations
            descriptions = self.create_description_variations(
                product_name=product_name,
                fabric_type=fabric_type,
                color=color,
                price=price,
                category=category,
                features=features
            )
            
            # Select the best description
            best_description = descriptions[0] if descriptions else self.get_fallback_description(product_info)
            
            result = {
                'success': True,
                'description': best_description['text'],
                'variations': descriptions,
                'product_name': product_name,
                'cost': 0.02  # Mock cost for description generation
            }
            
            logger.info(f"Generated description for product: {product_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate product description: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'description': self.get_fallback_description(product_info)['text'],
                'variations': []
            }
    
    def create_description_variations(self,
                                    product_name: str,
                                    fabric_type: str,
                                    color: str = '',
                                    price: str = '',
                                    category: str = 'textile',
                                    features: List[str] = None) -> List[Dict[str, Any]]:
        """Create multiple description variations for a product"""
        
        features = features or []
        variations = []
        
        # Professional/Commercial Description
        professional_desc = self.create_professional_description(
            product_name, fabric_type, color, price, features
        )
        variations.append({
            'text': professional_desc,
            'style': 'professional',
            'tone': 'formal',
            'target_audience': 'business_buyers',
            'effectiveness_score': 9.0
        })
        
        # Marketing/Sales Description
        marketing_desc = self.create_marketing_description(
            product_name, fabric_type, color, price, features
        )
        variations.append({
            'text': marketing_desc,
            'style': 'marketing',
            'tone': 'persuasive',
            'target_audience': 'end_consumers',
            'effectiveness_score': 8.5
        })
        
        # Detailed/Technical Description
        technical_desc = self.create_technical_description(
            product_name, fabric_type, color, price, features
        )
        variations.append({
            'text': technical_desc,
            'style': 'technical',
            'tone': 'informative',
            'target_audience': 'quality_conscious',
            'effectiveness_score': 8.0
        })
        
        # Emotional/Lifestyle Description
        lifestyle_desc = self.create_lifestyle_description(
            product_name, fabric_type, color, price, features
        )
        variations.append({
            'text': lifestyle_desc,
            'style': 'lifestyle',
            'tone': 'emotional',
            'target_audience': 'lifestyle_buyers',
            'effectiveness_score': 7.8
        })
        
        # Sort by effectiveness score
        variations.sort(key=lambda x: x['effectiveness_score'], reverse=True)
        
        return variations
    
    def create_professional_description(self, name: str, fabric: str, color: str, price: str, features: List[str]) -> str:
        """Create professional product description"""
        desc = f"{name}"
        
        if fabric:
            fabric_qualities = {
                'cotton': 'premium cotton fabric with natural breathability',
                'silk': 'luxurious silk with lustrous finish and elegant drape',
                'linen': 'high-quality linen with crisp texture and durability',
                'saree': 'traditional saree with authentic craftsmanship'
            }
            desc += f" crafted from {fabric_qualities.get(fabric.lower(), f'quality {fabric}')}"
        
        if color:
            desc += f" in {color}"
        
        if features:
            desc += f". Features: {', '.join(features)}"
        
        desc += ". Perfect for both casual and formal occasions."
        
        if price:
            desc += f" Available at {price}."
        
        return desc
    
    def create_marketing_description(self, name: str, fabric: str, color: str, price: str, features: List[str]) -> str:
        """Create marketing-focused product description"""
        desc = f"✨ Discover the elegance of {name}! ✨"
        
        if fabric:
            fabric_benefits = {
                'cotton': 'Stay comfortable all day with our premium cotton',
                'silk': 'Experience luxury with our exquisite silk',
                'linen': 'Embrace sophistication with our finest linen',
                'saree': 'Celebrate tradition with our authentic saree'
            }
            desc += f" {fabric_benefits.get(fabric.lower(), f'Enjoy the quality of {fabric}')}"
        
        if color:
            desc += f" in stunning {color}"
        
        desc += ". "
        
        if features:
            desc += f"Special features include {', '.join(features)}. "
        
        desc += "Don't miss this exclusive piece!"
        
        if price:
            desc += f" Starting at just {price}!"
        
        return desc
    
    def create_technical_description(self, name: str, fabric: str, color: str, price: str, features: List[str]) -> str:
        """Create technical product description"""
        desc = f"{name} - Technical Specifications:"
        
        if fabric:
            fabric_specs = {
                'cotton': '100% pure cotton, 180 GSM, pre-shrunk',
                'silk': 'Pure silk, 22 momme weight, natural sheen',
                'linen': '100% linen, 200 GSM, enzyme washed',
                'saree': 'Traditional weave, 5.5 meters length'
            }
            desc += f" Material: {fabric_specs.get(fabric.lower(), f'{fabric} fabric')}"
        
        if color:
            desc += f", Color: {color}"
        
        if features:
            desc += f", Features: {', '.join(features)}"
        
        desc += ". Quality tested and certified."
        
        if price:
            desc += f" Price: {price}"
        
        return desc
    
    def create_lifestyle_description(self, name: str, fabric: str, color: str, price: str, features: List[str]) -> str:
        """Create lifestyle-focused product description"""
        desc = f"Transform your wardrobe with {name}."
        
        if fabric:
            fabric_lifestyle = {
                'cotton': 'Feel the natural comfort that moves with you',
                'silk': 'Embrace the luxury that makes every moment special',
                'linen': 'Experience the effortless elegance of premium linen',
                'saree': 'Connect with your heritage through timeless beauty'
            }
            desc += f" {fabric_lifestyle.get(fabric.lower(), f'Enjoy the comfort of {fabric}')}"
        
        if color:
            desc += f" in beautiful {color}"
        
        desc += ". "
        
        if features:
            desc += f"With {', '.join(features)}, "
        
        desc += "it's perfect for creating memorable moments."
        
        if price:
            desc += f" Make it yours for {price}."
        
        return desc
    
    def get_fallback_description(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback description when AI generation fails"""
        name = product_info.get('name', 'Quality Textile Product')
        fabric = product_info.get('fabric_type', '')
        price = product_info.get('price', '')
        
        fallback_text = f"{name}"
        if fabric:
            fallback_text += f" made from quality {fabric}"
        fallback_text += ". Excellent craftsmanship and attention to detail."
        if price:
            fallback_text += f" Available at {price}."
        
        return {
            'text': fallback_text,
            'style': 'fallback',
            'tone': 'neutral',
            'target_audience': 'general',
            'effectiveness_score': 6.0
        }
    
    def generate_catalog_layout(self,
                              organization,
                              user,
                              products: List[Dict[str, Any]],
                              style: str = 'modern',
                              layout_type: str = 'grid',
                              theme: str = 'professional') -> Dict[str, Any]:
        """
        Generate catalog layout using AI
        
        Args:
            organization: Organization instance
            user: User instance
            products: List of processed products
            style: Catalog style
            layout_type: Layout type
            theme: Theme
            
        Returns:
            Dict containing catalog generation results
        """
        try:
            # Create catalog prompt
            catalog_prompt = self.create_catalog_prompt(
                products=products,
                style=style,
                layout_type=layout_type,
                theme=theme
            )
            
            # Get provider
            provider = self.get_gemini_provider()
            
            # Create generation request
            request = AIGenerationRequest.objects.create(
                organization=organization,
                user=user,
                provider=provider,
                generation_type='catalog',
                prompt=catalog_prompt,
                negative_prompt=self.prompt_service.generate_negative_prompt('catalog'),
                parameters={
                    'style': style,
                    'layout_type': layout_type,
                    'theme': theme,
                    'product_count': len(products),
                    'width': 1200,
                    'height': 1600,
                    'steps': 25,
                    'guidance_scale': 8.0
                }
            )
            
            # Process the generation request
            success = self.ai_service.process_generation_request(request)
            
            if success:
                result = {
                    'success': True,
                    'request_id': str(request.id),
                    'catalog_urls': request.result_urls,
                    'prompt_used': catalog_prompt,
                    'parameters': request.parameters,
                    'cost': float(request.cost or 0),
                    'processing_time': request.processing_time
                }
            else:
                result = {
                    'success': False,
                    'error': request.error_message,
                    'request_id': str(request.id)
                }
            
            logger.info(f"Catalog layout generation completed for request {request.id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate catalog layout: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_catalog_prompt(self,
                            products: List[Dict[str, Any]],
                            style: str,
                            layout_type: str,
                            theme: str) -> str:
        """Create AI prompt for catalog generation"""
        
        # Base prompt
        prompt = f"Professional textile catalog design, {style} style, {layout_type} layout"
        
        # Add theme elements
        theme_elements = {
            'professional': 'clean design, business-focused, corporate aesthetic',
            'festive': 'celebratory colors, festive elements, joyful atmosphere',
            'luxury': 'premium design, elegant typography, sophisticated layout',
            'traditional': 'cultural motifs, traditional patterns, heritage design',
            'modern': 'contemporary design, minimalist approach, trendy aesthetics'
        }
        
        if theme.lower() in theme_elements:
            prompt += f", {theme_elements[theme.lower()]}"
        
        # Add layout-specific elements
        layout_elements = {
            'grid': 'organized grid layout, equal spacing, systematic arrangement',
            'list': 'vertical list layout, detailed product information, easy scanning',
            'magazine': 'magazine-style layout, editorial design, visual storytelling',
            'mosaic': 'mosaic layout, varied sizes, dynamic arrangement'
        }
        
        if layout_type.lower() in layout_elements:
            prompt += f", {layout_elements[layout_type.lower()]}"
        
        # Add product information
        product_count = len(products)
        prompt += f", showcasing {product_count} textile products"
        
        # Extract fabric types for context
        fabric_types = list(set([p.get('fabric_type', '') for p in products if p.get('fabric_type')]))
        if fabric_types:
            prompt += f", featuring {', '.join(fabric_types[:3])} textiles"
        
        # Add catalog-specific requirements
        prompt += ", high-resolution catalog design, commercial quality"
        prompt += ", suitable for printing, professional product showcase"
        prompt += ", clear product visibility, attractive layout composition"
        
        return prompt
    
    def get_gemini_provider(self) -> AIProvider:
        """Get or create Gemini AI provider"""
        provider, created = AIProvider.objects.get_or_create(
            name='gemini',
            defaults={
                'api_key': settings.GEMINI_API_KEY,
                'api_url': 'https://generativelanguage.googleapis.com',
                'is_active': True,
                'rate_limit_per_minute': 10,
                'rate_limit_per_hour': 100
            }
        )
        
        return provider
    
    def get_catalog_templates(self) -> List[Dict[str, Any]]:
        """Get available catalog templates"""
        templates = [
            {
                'id': 'modern_grid',
                'name': 'Modern Grid Layout',
                'description': 'Clean grid layout with modern typography',
                'style': 'modern',
                'layout_type': 'grid',
                'best_for': 'Contemporary textile collections'
            },
            {
                'id': 'traditional_magazine',
                'name': 'Traditional Magazine Style',
                'description': 'Magazine-style layout with traditional elements',
                'style': 'traditional',
                'layout_type': 'magazine',
                'best_for': 'Heritage and traditional textiles'
            },
            {
                'id': 'luxury_showcase',
                'name': 'Luxury Showcase',
                'description': 'Premium layout for high-end products',
                'style': 'luxury',
                'layout_type': 'mosaic',
                'best_for': 'Premium and luxury textiles'
            },
            {
                'id': 'festive_celebration',
                'name': 'Festive Celebration',
                'description': 'Colorful layout for festival collections',
                'style': 'festive',
                'layout_type': 'grid',
                'best_for': 'Festival and celebration wear'
            }
        ]
        
        return templates
    
    def export_catalog_data(self, catalog_id: str, format: str = 'json') -> Dict[str, Any]:
        """Export catalog data in various formats"""
        try:
            # Get catalog request
            request = AIGenerationRequest.objects.get(id=catalog_id)
            
            catalog_data = {
                'catalog_id': catalog_id,
                'generation_type': request.generation_type,
                'created_at': request.created_at.isoformat(),
                'parameters': request.parameters,
                'result_urls': request.result_urls,
                'organization': request.organization.name,
                'user': request.user.email,
                'cost': float(request.cost or 0),
                'processing_time': request.processing_time
            }
            
            if format.lower() == 'json':
                return {
                    'success': True,
                    'format': 'json',
                    'data': catalog_data
                }
            elif format.lower() == 'csv':
                # Convert to CSV format (simplified)
                csv_data = []
                for key, value in catalog_data.items():
                    csv_data.append(f"{key},{value}")
                
                return {
                    'success': True,
                    'format': 'csv',
                    'data': '\n'.join(csv_data)
                }
            else:
                return {
                    'success': False,
                    'error': f'Unsupported format: {format}'
                }
                
        except Exception as e:
            logger.error(f"Failed to export catalog data: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

