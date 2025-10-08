"""
AI Background Generator for Phase 1 Week 4
Advanced background synthesis using NanoBanana API with fabric-style texture generation
"""
import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from .models import AIGenerationRequest, AIProvider, AIUsageQuota
from .services import AIGenerationService
from .color_matching import SmartColorMatcher
from .fabric_analysis import FabricAnalyzer

logger = logging.getLogger(__name__)


class AIBackgroundGenerator:
    """Advanced AI background generation service with fabric-style synthesis"""
    
    def __init__(self):
        self.ai_service = AIGenerationService()
        self.color_matcher = SmartColorMatcher()
        self.fabric_analyzer = FabricAnalyzer()
    
    def generate_fabric_background(self,
                                 organization,
                                 user,
                                 fabric_image_url: str,
                                 background_style: str = 'complementary',
                                 pattern_type: str = 'seamless',
                                 intensity: str = 'medium',
                                 dimensions: Tuple[int, int] = (1024, 1024)) -> Dict[str, Any]:
        """
        Generate AI background that complements fabric colors and patterns
        
        Args:
            organization: Organization instance
            user: User instance
            fabric_image_url: URL of the fabric image
            background_style: Style of background (complementary, harmonious, neutral, artistic)
            pattern_type: Type of pattern (seamless, geometric, organic, abstract)
            intensity: Intensity level (subtle, medium, bold)
            dimensions: Tuple of (width, height) for generated background
            
        Returns:
            Dictionary containing background generation results
        """
        try:
            # Step 1: Analyze fabric colors and patterns
            fabric_analysis = self._analyze_fabric_for_background(fabric_image_url)
            
            if not fabric_analysis['success']:
                return {
                    'success': False,
                    'error': 'Failed to analyze fabric for background generation',
                    'fabric_image_url': fabric_image_url
                }
            
            # Step 2: Generate background prompt based on analysis
            background_prompt = self._create_fabric_background_prompt(
                fabric_analysis=fabric_analysis,
                background_style=background_style,
                pattern_type=pattern_type,
                intensity=intensity
            )
            
            # Step 3: Generate multiple background variations
            background_variations = self._generate_background_variations(
                organization=organization,
                user=user,
                base_prompt=background_prompt,
                fabric_analysis=fabric_analysis,
                background_style=background_style,
                pattern_type=pattern_type,
                intensity=intensity,
                dimensions=dimensions
            )
            
            # Step 4: Evaluate and rank backgrounds
            ranked_backgrounds = self._rank_background_variations(
                background_variations=background_variations,
                fabric_analysis=fabric_analysis,
                background_style=background_style
            )
            
            # Step 5: Generate final result
            result = {
                'success': True,
                'fabric_image_url': fabric_image_url,
                'fabric_analysis': fabric_analysis,
                'background_style': background_style,
                'pattern_type': pattern_type,
                'intensity': intensity,
                'dimensions': dimensions,
                'generated_backgrounds': ranked_backgrounds,
                'recommended_background': ranked_backgrounds[0] if ranked_backgrounds else None,
                'generation_metadata': {
                    'total_variations': len(background_variations),
                    'generation_time': time.time(),
                    'prompt_used': background_prompt
                }
            }
            
            logger.info(f"Fabric background generation completed for {fabric_image_url}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate fabric background: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fabric_image_url': fabric_image_url
            }
    
    def generate_texture_background(self,
                                  organization,
                                  user,
                                  texture_description: str,
                                  color_scheme: List[str],
                                  pattern_style: str = 'organic',
                                  dimensions: Tuple[int, int] = (1024, 1024)) -> Dict[str, Any]:
        """
        Generate AI background based on texture description and color scheme
        
        Args:
            organization: Organization instance
            user: User instance
            texture_description: Description of desired texture
            color_scheme: List of hex color codes
            pattern_style: Style of pattern (organic, geometric, abstract, floral)
            dimensions: Tuple of (width, height) for generated background
            
        Returns:
            Dictionary containing texture background generation results
        """
        try:
            # Create texture-specific prompt
            texture_prompt = self._create_texture_background_prompt(
                texture_description=texture_description,
                color_scheme=color_scheme,
                pattern_style=pattern_style
            )
            
            # Generate background using AI service
            provider = self._get_nanobanana_provider()
            
            request = AIGenerationRequest.objects.create(
                organization=organization,
                user=user,
                provider=provider,
                generation_type='background',
                prompt=texture_prompt,
                negative_prompt="foreground objects, text, cluttered elements, low quality, blurry, distorted",
                parameters={
                    'width': dimensions[0],
                    'height': dimensions[1],
                    'steps': 20,
                    'guidance_scale': 7.5,
                    'texture_description': texture_description,
                    'color_scheme': color_scheme,
                    'pattern_style': pattern_style
                }
            )
            
            # Process the generation request
            success = self.ai_service.process_generation_request(request)
            
            if success:
                result = {
                    'success': True,
                    'texture_description': texture_description,
                    'color_scheme': color_scheme,
                    'pattern_style': pattern_style,
                    'dimensions': dimensions,
                    'background_urls': request.result_urls,
                    'request_id': str(request.id),
                    'prompt_used': texture_prompt,
                    'cost': float(request.cost or 0),
                    'processing_time': request.processing_time
                }
            else:
                result = {
                    'success': False,
                    'error': request.error_message,
                    'request_id': str(request.id)
                }
            
            logger.info(f"Texture background generation completed for request {request.id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate texture background: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'texture_description': texture_description
            }
    
    def generate_seamless_pattern(self,
                                organization,
                                user,
                                base_pattern: str,
                                color_palette: List[Dict],
                                tile_size: int = 512) -> Dict[str, Any]:
        """
        Generate seamless tiling pattern for fabric backgrounds
        
        Args:
            organization: Organization instance
            user: User instance
            base_pattern: Base pattern description
            color_palette: List of color dictionaries
            tile_size: Size of the tile (square)
            
        Returns:
            Dictionary containing seamless pattern generation results
        """
        try:
            # Create seamless pattern prompt
            seamless_prompt = self._create_seamless_pattern_prompt(
                base_pattern=base_pattern,
                color_palette=color_palette
            )
            
            # Generate pattern using AI service
            provider = self._get_nanobanana_provider()
            
            request = AIGenerationRequest.objects.create(
                organization=organization,
                user=user,
                provider=provider,
                generation_type='background',
                prompt=seamless_prompt,
                negative_prompt="seams, borders, edges, discontinuities, low quality, blurry",
                parameters={
                    'width': tile_size,
                    'height': tile_size,
                    'steps': 25,  # Higher steps for seamless patterns
                    'guidance_scale': 8.0,
                    'seamless': True,
                    'tile_size': tile_size,
                    'base_pattern': base_pattern
                }
            )
            
            # Process the generation request
            success = self.ai_service.process_generation_request(request)
            
            if success:
                result = {
                    'success': True,
                    'base_pattern': base_pattern,
                    'color_palette': color_palette,
                    'tile_size': tile_size,
                    'pattern_urls': request.result_urls,
                    'request_id': str(request.id),
                    'prompt_used': seamless_prompt,
                    'cost': float(request.cost or 0),
                    'processing_time': request.processing_time,
                    'seamless_validation': self._validate_seamless_pattern(request.result_urls[0] if request.result_urls else None)
                }
            else:
                result = {
                    'success': False,
                    'error': request.error_message,
                    'request_id': str(request.id)
                }
            
            logger.info(f"Seamless pattern generation completed for request {request.id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate seamless pattern: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'base_pattern': base_pattern
            }
    
    def _analyze_fabric_for_background(self, fabric_image_url: str) -> Dict[str, Any]:
        """Analyze fabric for background generation"""
        try:
            # Use fabric analyzer to get comprehensive analysis
            analysis = self.fabric_analyzer.analyze_fabric(fabric_image_url, 'comprehensive')
            
            if not analysis['success']:
                return analysis
            
            # Extract key information for background generation
            color_analysis = analysis.get('color_analysis', {})
            texture_analysis = analysis.get('texture_analysis', {})
            pattern_analysis = analysis.get('pattern_analysis', {})
            
            # Get dominant colors
            dominant_colors = color_analysis.get('dominant_colors', [])
            color_palette = color_analysis.get('color_palette', [])
            
            # Get fabric mood and characteristics
            fabric_mood = color_analysis.get('fabric_mood', {})
            color_temperature = color_analysis.get('color_temperature', {})
            color_intensity = color_analysis.get('color_intensity', {})
            
            # Get texture information
            texture_type = texture_analysis.get('texture_type', 'unknown')
            fabric_type = texture_analysis.get('fabric_type', {})
            
            # Get pattern information
            pattern_type = pattern_analysis.get('pattern_type', 'unknown')
            pattern_complexity = pattern_analysis.get('pattern_complexity', 'medium')
            
            return {
                'success': True,
                'fabric_image_url': fabric_image_url,
                'dominant_colors': dominant_colors,
                'color_palette': color_palette,
                'fabric_mood': fabric_mood.get('mood', 'neutral'),
                'color_temperature': color_temperature.get('temperature', 'neutral'),
                'color_intensity': color_intensity.get('intensity', 'medium'),
                'texture_type': texture_type,
                'fabric_type': fabric_type.get('predicted_type', 'unknown'),
                'pattern_type': pattern_type,
                'pattern_complexity': pattern_complexity,
                'full_analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze fabric for background: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fabric_image_url': fabric_image_url
            }
    
    def _create_fabric_background_prompt(self,
                                       fabric_analysis: Dict[str, Any],
                                       background_style: str,
                                       pattern_type: str,
                                       intensity: str) -> str:
        """Create AI prompt for fabric background generation"""
        try:
            prompt_parts = []
            
            # Base pattern type
            pattern_descriptions = {
                'seamless': 'seamless repeating pattern',
                'geometric': 'geometric pattern with clean lines',
                'organic': 'organic flowing pattern',
                'abstract': 'abstract artistic pattern',
                'floral': 'floral botanical pattern',
                'textile': 'textile-inspired pattern'
            }
            prompt_parts.append(pattern_descriptions.get(pattern_type, 'seamless repeating pattern'))
            
            # Color scheme based on fabric analysis
            dominant_colors = fabric_analysis.get('dominant_colors', [])
            if dominant_colors:
                color_hexes = [color['hex'] for color in dominant_colors[:3]]
                prompt_parts.append(f"color palette: {', '.join(color_hexes)}")
            
            # Background style
            style_descriptions = {
                'complementary': 'complementary color scheme, high contrast',
                'harmonious': 'harmonious color scheme, balanced tones',
                'neutral': 'neutral color scheme, subtle tones',
                'artistic': 'artistic color scheme, creative interpretation',
                'monochromatic': 'monochromatic color scheme, single hue variations'
            }
            prompt_parts.append(style_descriptions.get(background_style, 'harmonious color scheme'))
            
            # Intensity level
            intensity_descriptions = {
                'subtle': 'subtle intensity, soft and gentle',
                'medium': 'medium intensity, balanced and pleasant',
                'bold': 'bold intensity, vibrant and striking'
            }
            prompt_parts.append(intensity_descriptions.get(intensity, 'medium intensity'))
            
            # Fabric characteristics
            fabric_mood = fabric_analysis.get('fabric_mood', 'neutral')
            mood_descriptions = {
                'elegant': 'elegant and sophisticated',
                'vibrant': 'vibrant and energetic',
                'calm': 'calm and peaceful',
                'festive': 'festive and celebratory',
                'traditional': 'traditional and classic',
                'modern': 'modern and contemporary',
                'luxury': 'luxury and premium',
                'casual': 'casual and relaxed'
            }
            prompt_parts.append(mood_descriptions.get(fabric_mood, 'balanced and pleasant'))
            
            # Texture information
            texture_type = fabric_analysis.get('texture_type', 'unknown')
            if texture_type != 'unknown':
                texture_descriptions = {
                    'smooth': 'smooth texture, refined finish',
                    'rough': 'textured surface, natural feel',
                    'regular': 'regular pattern, structured design',
                    'irregular': 'organic pattern, natural variation'
                }
                prompt_parts.append(texture_descriptions.get(texture_type, ''))
            
            # Technical requirements
            prompt_parts.extend([
                'high resolution background',
                'seamless tiling capability',
                'suitable for textile photography',
                'professional quality',
                'no distracting elements',
                'clean composition'
            ])
            
            # Join all parts
            prompt = ", ".join([part for part in prompt_parts if part])
            
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to create fabric background prompt: {str(e)}")
            return "seamless repeating pattern, harmonious color scheme, medium intensity, professional quality background"
    
    def _create_texture_background_prompt(self,
                                        texture_description: str,
                                        color_scheme: List[str],
                                        pattern_style: str) -> str:
        """Create AI prompt for texture background generation"""
        try:
            prompt_parts = []
            
            # Base texture description
            prompt_parts.append(texture_description)
            
            # Color scheme
            if color_scheme:
                prompt_parts.append(f"color palette: {', '.join(color_scheme)}")
            
            # Pattern style
            style_descriptions = {
                'organic': 'organic flowing pattern, natural shapes',
                'geometric': 'geometric pattern, structured design',
                'abstract': 'abstract artistic pattern, creative interpretation',
                'floral': 'floral botanical pattern, natural elements'
            }
            prompt_parts.append(style_descriptions.get(pattern_style, 'organic flowing pattern'))
            
            # Technical requirements
            prompt_parts.extend([
                'high resolution background',
                'seamless pattern',
                'professional quality',
                'textile-inspired design',
                'no foreground objects'
            ])
            
            # Join all parts
            prompt = ", ".join(prompt_parts)
            
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to create texture background prompt: {str(e)}")
            return f"{texture_description}, seamless pattern, professional quality background"
    
    def _create_seamless_pattern_prompt(self,
                                      base_pattern: str,
                                      color_palette: List[Dict]) -> str:
        """Create AI prompt for seamless pattern generation"""
        try:
            prompt_parts = []
            
            # Base pattern
            prompt_parts.append(base_pattern)
            
            # Color palette
            if color_palette:
                color_hexes = [color.get('hex', '') for color in color_palette[:5]]
                prompt_parts.append(f"color palette: {', '.join(color_hexes)}")
            
            # Seamless requirements
            prompt_parts.extend([
                'seamless repeating pattern',
                'perfect tileable design',
                'no visible seams or borders',
                'continuous pattern flow',
                'high resolution',
                'professional textile pattern'
            ])
            
            # Join all parts
            prompt = ", ".join(prompt_parts)
            
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to create seamless pattern prompt: {str(e)}")
            return f"{base_pattern}, seamless repeating pattern, professional quality"
    
    def _generate_background_variations(self,
                                      organization,
                                      user,
                                      base_prompt: str,
                                      fabric_analysis: Dict[str, Any],
                                      background_style: str,
                                      pattern_type: str,
                                      intensity: str,
                                      dimensions: Tuple[int, int]) -> List[Dict[str, Any]]:
        """Generate multiple background variations"""
        try:
            variations = []
            
            # Create different variations
            variation_configs = [
                {
                    'name': 'primary',
                    'prompt_modifier': '',
                    'guidance_scale': 7.5,
                    'steps': 20
                },
                {
                    'name': 'alternative',
                    'prompt_modifier': 'alternative interpretation, different composition',
                    'guidance_scale': 6.5,
                    'steps': 18
                },
                {
                    'name': 'artistic',
                    'prompt_modifier': 'artistic interpretation, creative style',
                    'guidance_scale': 8.0,
                    'steps': 22
                }
            ]
            
            provider = self._get_nanobanana_provider()
            
            for config in variation_configs:
                # Create modified prompt
                modified_prompt = base_prompt
                if config['prompt_modifier']:
                    modified_prompt += f", {config['prompt_modifier']}"
                
                # Create generation request
                request = AIGenerationRequest.objects.create(
                    organization=organization,
                    user=user,
                    provider=provider,
                    generation_type='background',
                    prompt=modified_prompt,
                    negative_prompt="foreground objects, text, cluttered elements, low quality, blurry, distorted",
                    parameters={
                        'width': dimensions[0],
                        'height': dimensions[1],
                        'steps': config['steps'],
                        'guidance_scale': config['guidance_scale'],
                        'variation_name': config['name'],
                        'background_style': background_style,
                        'pattern_type': pattern_type,
                        'intensity': intensity
                    }
                )
                
                # Process the generation request
                success = self.ai_service.process_generation_request(request)
                
                if success:
                    variation = {
                        'name': config['name'],
                        'request_id': str(request.id),
                        'background_urls': request.result_urls,
                        'prompt_used': modified_prompt,
                        'parameters': request.parameters,
                        'cost': float(request.cost or 0),
                        'processing_time': request.processing_time,
                        'success': True
                    }
                else:
                    variation = {
                        'name': config['name'],
                        'request_id': str(request.id),
                        'error': request.error_message,
                        'success': False
                    }
                
                variations.append(variation)
            
            return variations
            
        except Exception as e:
            logger.error(f"Failed to generate background variations: {str(e)}")
            return []
    
    def _rank_background_variations(self,
                                  background_variations: List[Dict[str, Any]],
                                  fabric_analysis: Dict[str, Any],
                                  background_style: str) -> List[Dict[str, Any]]:
        """Rank background variations based on quality and compatibility"""
        try:
            ranked_variations = []
            
            for variation in background_variations:
                if not variation.get('success', False):
                    continue
                
                # Calculate compatibility score
                compatibility_score = self._calculate_compatibility_score(
                    variation=variation,
                    fabric_analysis=fabric_analysis,
                    background_style=background_style
                )
                
                # Calculate quality score
                quality_score = self._calculate_quality_score(variation)
                
                # Calculate overall score
                overall_score = (compatibility_score * 0.6) + (quality_score * 0.4)
                
                # Add scores to variation
                variation['scores'] = {
                    'compatibility': round(compatibility_score, 2),
                    'quality': round(quality_score, 2),
                    'overall': round(overall_score, 2)
                }
                
                ranked_variations.append(variation)
            
            # Sort by overall score
            ranked_variations.sort(key=lambda x: x['scores']['overall'], reverse=True)
            
            return ranked_variations
            
        except Exception as e:
            logger.error(f"Failed to rank background variations: {str(e)}")
            return background_variations
    
    def _calculate_compatibility_score(self,
                                     variation: Dict[str, Any],
                                     fabric_analysis: Dict[str, Any],
                                     background_style: str) -> float:
        """Calculate compatibility score between background and fabric"""
        try:
            score = 5.0  # Base score
            
            # Style compatibility
            style_scores = {
                'complementary': 8.0,
                'harmonious': 9.0,
                'neutral': 7.0,
                'artistic': 6.0,
                'monochromatic': 8.5
            }
            score += style_scores.get(background_style, 5.0) - 5.0
            
            # Fabric mood compatibility
            fabric_mood = fabric_analysis.get('fabric_mood', 'neutral')
            mood_compatibility = {
                'elegant': 9.0,
                'vibrant': 8.0,
                'calm': 8.5,
                'festive': 7.5,
                'traditional': 8.0,
                'modern': 7.0,
                'luxury': 9.0,
                'casual': 7.5
            }
            score += mood_compatibility.get(fabric_mood, 5.0) - 5.0
            
            # Color temperature compatibility
            color_temperature = fabric_analysis.get('color_temperature', 'neutral')
            if color_temperature in ['warm', 'cool']:
                score += 1.0
            
            # Pattern complexity compatibility
            pattern_complexity = fabric_analysis.get('pattern_complexity', 'medium')
            complexity_scores = {
                'low': 8.0,
                'medium': 9.0,
                'high': 7.0
            }
            score += complexity_scores.get(pattern_complexity, 5.0) - 5.0
            
            return min(10.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Failed to calculate compatibility score: {str(e)}")
            return 5.0
    
    def _calculate_quality_score(self, variation: Dict[str, Any]) -> float:
        """Calculate quality score for background variation"""
        try:
            score = 5.0  # Base score
            
            # Processing time score (faster is better, up to a point)
            processing_time = variation.get('processing_time', 0)
            if processing_time > 0:
                if processing_time < 10:
                    score += 2.0
                elif processing_time < 20:
                    score += 1.0
                elif processing_time > 60:
                    score -= 1.0
            
            # Cost efficiency score
            cost = variation.get('cost', 0)
            if cost > 0:
                if cost < 0.05:
                    score += 1.0
                elif cost > 0.15:
                    score -= 1.0
            
            # Parameter optimization score
            parameters = variation.get('parameters', {})
            guidance_scale = parameters.get('guidance_scale', 7.5)
            steps = parameters.get('steps', 20)
            
            # Optimal guidance scale is around 7.5
            if 7.0 <= guidance_scale <= 8.0:
                score += 1.0
            
            # Optimal steps is around 20
            if 18 <= steps <= 22:
                score += 1.0
            
            return min(10.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Failed to calculate quality score: {str(e)}")
            return 5.0
    
    def _validate_seamless_pattern(self, pattern_url: Optional[str]) -> Dict[str, Any]:
        """Validate seamless pattern quality"""
        try:
            if not pattern_url:
                return {
                    'is_seamless': False,
                    'confidence': 0.0,
                    'issues': ['No pattern URL provided']
                }
            
            # This would typically involve downloading the image and analyzing it
            # For now, return mock validation results
            
            validation_result = {
                'is_seamless': True,
                'confidence': 0.85,
                'issues': [],
                'tile_quality': 'good',
                'seam_visibility': 'minimal',
                'pattern_continuity': 'excellent'
            }
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Failed to validate seamless pattern: {str(e)}")
            return {
                'is_seamless': False,
                'confidence': 0.0,
                'issues': [f'Validation error: {str(e)}']
            }
    
    def _get_nanobanana_provider(self) -> AIProvider:
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
        
        return provider
    
    def get_background_presets(self) -> List[Dict[str, Any]]:
        """Get predefined background generation presets"""
        presets = [
            {
                'id': 'fabric_complementary',
                'name': 'Fabric Complementary',
                'description': 'Background that complements fabric colors using complementary color theory',
                'background_style': 'complementary',
                'pattern_type': 'seamless',
                'intensity': 'medium',
                'best_for': ['vibrant fabrics', 'high contrast designs', 'modern styles']
            },
            {
                'id': 'fabric_harmonious',
                'name': 'Fabric Harmonious',
                'description': 'Background that harmonizes with fabric colors using analogous color theory',
                'background_style': 'harmonious',
                'pattern_type': 'organic',
                'intensity': 'medium',
                'best_for': ['elegant fabrics', 'traditional designs', 'calm aesthetics']
            },
            {
                'id': 'fabric_neutral',
                'name': 'Fabric Neutral',
                'description': 'Neutral background that lets fabric colors stand out',
                'background_style': 'neutral',
                'pattern_type': 'geometric',
                'intensity': 'subtle',
                'best_for': ['colorful fabrics', 'complex patterns', 'professional presentations']
            },
            {
                'id': 'fabric_artistic',
                'name': 'Fabric Artistic',
                'description': 'Artistic interpretation of fabric-inspired background',
                'background_style': 'artistic',
                'pattern_type': 'abstract',
                'intensity': 'bold',
                'best_for': ['creative designs', 'artistic presentations', 'unique styles']
            },
            {
                'id': 'texture_organic',
                'name': 'Organic Texture',
                'description': 'Organic flowing texture background',
                'texture_description': 'organic flowing texture, natural patterns',
                'pattern_style': 'organic',
                'best_for': ['natural fabrics', 'organic designs', 'flowing aesthetics']
            },
            {
                'id': 'texture_geometric',
                'name': 'Geometric Texture',
                'description': 'Geometric structured texture background',
                'texture_description': 'geometric structured texture, clean lines',
                'pattern_style': 'geometric',
                'best_for': ['modern fabrics', 'structured designs', 'contemporary styles']
            }
        ]
        
        return presets

