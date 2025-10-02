"""
Background Matching Service with Fabric Color Detection
Implements Phase 1 Week 1 Member 3 tasks for AI-powered background matching
"""
import logging
import json
import colorsys
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings
from django.utils import timezone
from .models import AIGenerationRequest, AIProvider
from .services import AIGenerationService, AIColorAnalysisService

logger = logging.getLogger(__name__)


class FabricColorDetector:
    """Service for detecting and analyzing fabric colors"""
    
    def __init__(self):
        self.color_analysis_service = AIColorAnalysisService()
    
    def analyze_fabric_colors(self, fabric_image_url: str) -> Dict[str, Any]:
        """
        Analyze colors in a fabric image
        
        Args:
            fabric_image_url: URL of the fabric image
            
        Returns:
            Dict containing color analysis results
        """
        try:
            # Extract color palette from fabric image
            color_palette = self.color_analysis_service.extract_color_palette(fabric_image_url)
            
            # Analyze color properties
            color_analysis = {
                'dominant_colors': color_palette[:3],  # Top 3 colors
                'color_harmony': self.analyze_color_harmony(color_palette),
                'color_temperature': self.analyze_color_temperature(color_palette),
                'color_intensity': self.analyze_color_intensity(color_palette),
                'fabric_mood': self.determine_fabric_mood(color_palette),
                'complementary_colors': self.get_complementary_colors(color_palette[:2]),
                'total_colors': len(color_palette)
            }
            
            logger.info(f"Analyzed fabric colors from {fabric_image_url}")
            return {
                'success': True,
                'image_url': fabric_image_url,
                'color_palette': color_palette,
                'analysis': color_analysis
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze fabric colors: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'image_url': fabric_image_url
            }
    
    def analyze_color_harmony(self, color_palette: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze color harmony in the palette"""
        if not color_palette:
            return {'type': 'unknown', 'score': 0}
        
        # Convert hex colors to HSV for analysis
        hsv_colors = []
        for color in color_palette[:5]:  # Analyze top 5 colors
            hex_color = color['hex'].lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            hsv_colors.append(hsv)
        
        # Analyze hue relationships
        hues = [hsv[0] * 360 for hsv in hsv_colors]
        
        # Determine harmony type
        harmony_type = 'complementary'
        harmony_score = 8.0
        
        # Check for monochromatic (similar hues)
        hue_range = max(hues) - min(hues)
        if hue_range < 30:
            harmony_type = 'monochromatic'
            harmony_score = 9.0
        elif hue_range < 60:
            harmony_type = 'analogous'
            harmony_score = 8.5
        elif any(abs(h1 - h2) > 150 for h1 in hues for h2 in hues if h1 != h2):
            harmony_type = 'complementary'
            harmony_score = 7.5
        else:
            harmony_type = 'triadic'
            harmony_score = 8.0
        
        return {
            'type': harmony_type,
            'score': harmony_score,
            'hue_range': hue_range,
            'description': self.get_harmony_description(harmony_type)
        }
    
    def analyze_color_temperature(self, color_palette: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze color temperature (warm/cool)"""
        if not color_palette:
            return {'temperature': 'neutral', 'score': 0}
        
        warm_score = 0
        cool_score = 0
        
        for color in color_palette:
            hex_color = color['hex'].lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Simple warm/cool analysis based on RGB values
            if rgb[0] > rgb[2]:  # More red than blue
                warm_score += color['percentage']
            elif rgb[2] > rgb[0]:  # More blue than red
                cool_score += color['percentage']
        
        if warm_score > cool_score * 1.2:
            temperature = 'warm'
            score = warm_score / (warm_score + cool_score)
        elif cool_score > warm_score * 1.2:
            temperature = 'cool'
            score = cool_score / (warm_score + cool_score)
        else:
            temperature = 'neutral'
            score = 0.5
        
        return {
            'temperature': temperature,
            'score': round(score, 2),
            'warm_percentage': round(warm_score, 1),
            'cool_percentage': round(cool_score, 1)
        }
    
    def analyze_color_intensity(self, color_palette: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze color intensity/saturation"""
        if not color_palette:
            return {'intensity': 'medium', 'score': 0}
        
        total_saturation = 0
        total_brightness = 0
        
        for color in color_palette:
            hex_color = color['hex'].lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            
            total_saturation += hsv[1] * color['percentage']
            total_brightness += hsv[2] * color['percentage']
        
        avg_saturation = total_saturation / 100
        avg_brightness = total_brightness / 100
        
        if avg_saturation > 0.7:
            intensity = 'high'
        elif avg_saturation > 0.4:
            intensity = 'medium'
        else:
            intensity = 'low'
        
        return {
            'intensity': intensity,
            'saturation_score': round(avg_saturation, 2),
            'brightness_score': round(avg_brightness, 2),
            'overall_score': round((avg_saturation + avg_brightness) / 2, 2)
        }
    
    def determine_fabric_mood(self, color_palette: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine the mood/feeling of the fabric based on colors"""
        if not color_palette:
            return {'mood': 'neutral', 'confidence': 0}
        
        # Color mood associations
        mood_scores = {
            'elegant': 0,
            'vibrant': 0,
            'calm': 0,
            'festive': 0,
            'traditional': 0,
            'modern': 0,
            'luxury': 0,
            'casual': 0
        }
        
        for color in color_palette:
            hex_color = color['hex'].lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            percentage = color['percentage']
            
            # Analyze color properties for mood
            r, g, b = rgb
            
            # Gold/yellow tones - festive, luxury
            if r > 200 and g > 180 and b < 100:
                mood_scores['festive'] += percentage * 0.8
                mood_scores['luxury'] += percentage * 0.6
            
            # Red tones - vibrant, festive
            elif r > 180 and g < 100 and b < 100:
                mood_scores['vibrant'] += percentage * 0.9
                mood_scores['festive'] += percentage * 0.7
            
            # Blue tones - calm, elegant
            elif b > 150 and r < 100 and g < 150:
                mood_scores['calm'] += percentage * 0.8
                mood_scores['elegant'] += percentage * 0.6
            
            # Green tones - calm, traditional
            elif g > 150 and r < 120 and b < 120:
                mood_scores['calm'] += percentage * 0.7
                mood_scores['traditional'] += percentage * 0.5
            
            # Dark colors - elegant, luxury
            elif max(rgb) < 80:
                mood_scores['elegant'] += percentage * 0.8
                mood_scores['luxury'] += percentage * 0.7
            
            # Light colors - casual, modern
            elif min(rgb) > 200:
                mood_scores['casual'] += percentage * 0.6
                mood_scores['modern'] += percentage * 0.5
        
        # Find dominant mood
        dominant_mood = max(mood_scores, key=mood_scores.get)
        confidence = mood_scores[dominant_mood] / 100
        
        return {
            'mood': dominant_mood,
            'confidence': round(confidence, 2),
            'all_scores': {k: round(v, 1) for k, v in mood_scores.items()},
            'description': self.get_mood_description(dominant_mood)
        }
    
    def get_complementary_colors(self, base_colors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get complementary colors for the base colors"""
        complementary = []
        
        for color in base_colors:
            hex_color = color['hex'].lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Calculate complementary color
            comp_rgb = (255 - rgb[0], 255 - rgb[1], 255 - rgb[2])
            comp_hex = '#{:02x}{:02x}{:02x}'.format(*comp_rgb)
            
            complementary.append({
                'hex': comp_hex,
                'rgb': list(comp_rgb),
                'name': f"Complement of {color['name']}",
                'relationship': 'complementary'
            })
        
        return complementary
    
    def get_harmony_description(self, harmony_type: str) -> str:
        """Get description for harmony type"""
        descriptions = {
            'monochromatic': 'Colors from the same hue family, creating unity and sophistication',
            'analogous': 'Adjacent colors on the color wheel, creating harmony and comfort',
            'complementary': 'Opposite colors creating high contrast and visual interest',
            'triadic': 'Three evenly spaced colors creating vibrant yet balanced design'
        }
        return descriptions.get(harmony_type, 'Unique color combination')
    
    def get_mood_description(self, mood: str) -> str:
        """Get description for mood"""
        descriptions = {
            'elegant': 'Sophisticated and refined, perfect for formal occasions',
            'vibrant': 'Bold and energetic, great for making a statement',
            'calm': 'Peaceful and serene, ideal for relaxation',
            'festive': 'Joyful and celebratory, perfect for special occasions',
            'traditional': 'Classic and timeless, honoring cultural heritage',
            'modern': 'Contemporary and fresh, suitable for current trends',
            'luxury': 'Premium and exclusive, representing high quality',
            'casual': 'Relaxed and comfortable, perfect for everyday wear'
        }
        return descriptions.get(mood, 'Unique aesthetic appeal')


class BackgroundMatcher:
    """Service for matching backgrounds to fabric colors"""
    
    def __init__(self):
        self.ai_service = AIGenerationService()
        self.color_detector = FabricColorDetector()
    
    def generate_matching_background(self,
                                   organization,
                                   user,
                                   fabric_image_url: str,
                                   background_style: str = 'complementary',
                                   pattern_type: str = 'seamless',
                                   intensity: str = 'medium') -> Dict[str, Any]:
        """
        Generate a background that matches the fabric colors
        
        Args:
            organization: Organization instance
            user: User instance
            fabric_image_url: URL of the fabric image
            background_style: Style of background (complementary, harmonious, neutral)
            pattern_type: Type of pattern (seamless, textured, gradient, solid)
            intensity: Intensity level (subtle, medium, bold)
            
        Returns:
            Dict containing background generation results
        """
        try:
            # Analyze fabric colors
            color_analysis = self.color_detector.analyze_fabric_colors(fabric_image_url)
            
            if not color_analysis['success']:
                return {
                    'success': False,
                    'error': 'Failed to analyze fabric colors',
                    'fabric_image_url': fabric_image_url
                }
            
            # Generate background suggestions
            background_suggestions = self.create_background_suggestions(
                color_analysis=color_analysis,
                background_style=background_style,
                pattern_type=pattern_type,
                intensity=intensity
            )
            
            # Generate the best matching background
            best_suggestion = background_suggestions[0] if background_suggestions else None
            
            if best_suggestion:
                background_result = self.generate_background_from_suggestion(
                    organization=organization,
                    user=user,
                    suggestion=best_suggestion,
                    fabric_analysis=color_analysis
                )
                
                if background_result['success']:
                    result = {
                        'success': True,
                        'fabric_image_url': fabric_image_url,
                        'fabric_analysis': color_analysis,
                        'background_suggestions': background_suggestions,
                        'selected_suggestion': best_suggestion,
                        'background_urls': background_result['background_urls'],
                        'request_id': background_result['request_id'],
                        'matching_score': best_suggestion['matching_score'],
                        'cost': background_result.get('cost', 0),
                        'processing_time': background_result.get('processing_time', 0)
                    }
                else:
                    result = {
                        'success': False,
                        'error': background_result.get('error', 'Background generation failed'),
                        'fabric_analysis': color_analysis,
                        'background_suggestions': background_suggestions
                    }
            else:
                result = {
                    'success': False,
                    'error': 'No suitable background suggestions found',
                    'fabric_analysis': color_analysis
                }
            
            logger.info(f"Background matching completed for fabric {fabric_image_url}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate matching background: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fabric_image_url': fabric_image_url
            }
    
    def create_background_suggestions(self,
                                    color_analysis: Dict[str, Any],
                                    background_style: str,
                                    pattern_type: str,
                                    intensity: str) -> List[Dict[str, Any]]:
        """Create background suggestions based on fabric color analysis"""
        
        suggestions = []
        fabric_colors = color_analysis['color_palette']
        analysis = color_analysis['analysis']
        
        # Get dominant colors
        dominant_colors = analysis['dominant_colors']
        fabric_mood = analysis['fabric_mood']['mood']
        color_temperature = analysis['color_temperature']['temperature']
        
        # Create suggestions based on style
        if background_style == 'complementary':
            suggestions.extend(self.create_complementary_suggestions(
                dominant_colors, fabric_mood, pattern_type, intensity
            ))
        elif background_style == 'harmonious':
            suggestions.extend(self.create_harmonious_suggestions(
                dominant_colors, fabric_mood, pattern_type, intensity
            ))
        elif background_style == 'neutral':
            suggestions.extend(self.create_neutral_suggestions(
                color_temperature, fabric_mood, pattern_type, intensity
            ))
        else:
            # Create mixed suggestions
            suggestions.extend(self.create_complementary_suggestions(
                dominant_colors, fabric_mood, pattern_type, intensity
            )[:2])
            suggestions.extend(self.create_harmonious_suggestions(
                dominant_colors, fabric_mood, pattern_type, intensity
            )[:2])
            suggestions.extend(self.create_neutral_suggestions(
                color_temperature, fabric_mood, pattern_type, intensity
            )[:1])
        
        # Sort by matching score
        suggestions.sort(key=lambda x: x['matching_score'], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def create_complementary_suggestions(self, dominant_colors: List[Dict], mood: str, pattern_type: str, intensity: str) -> List[Dict[str, Any]]:
        """Create complementary background suggestions"""
        suggestions = []
        
        for i, color in enumerate(dominant_colors[:2]):
            # Calculate complementary color
            hex_color = color['hex'].lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            comp_rgb = (255 - rgb[0], 255 - rgb[1], 255 - rgb[2])
            comp_hex = '#{:02x}{:02x}{:02x}'.format(*comp_rgb)
            
            suggestion = {
                'style': 'complementary',
                'primary_color': comp_hex,
                'secondary_color': color['hex'],
                'pattern_type': pattern_type,
                'intensity': intensity,
                'description': f"Complementary background using {comp_hex} to contrast with fabric's {color['hex']}",
                'matching_score': 9.0 - (i * 0.5),  # First color gets higher score
                'mood_compatibility': self.calculate_mood_compatibility(mood, 'complementary'),
                'prompt_elements': [
                    f"{pattern_type} background pattern",
                    f"primary color {comp_hex}",
                    f"secondary accents in {color['hex']}",
                    f"{intensity} intensity",
                    "complementary color scheme"
                ]
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def create_harmonious_suggestions(self, dominant_colors: List[Dict], mood: str, pattern_type: str, intensity: str) -> List[Dict[str, Any]]:
        """Create harmonious background suggestions"""
        suggestions = []
        
        for i, color in enumerate(dominant_colors[:2]):
            # Create analogous colors (similar hues)
            hex_color = color['hex'].lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            
            # Shift hue slightly for analogous color
            new_hue = (hsv[0] + 0.1) % 1.0  # Shift by 36 degrees
            analogous_rgb = colorsys.hsv_to_rgb(new_hue, hsv[1] * 0.7, hsv[2] * 0.9)
            analogous_rgb = tuple(int(c * 255) for c in analogous_rgb)
            analogous_hex = '#{:02x}{:02x}{:02x}'.format(*analogous_rgb)
            
            suggestion = {
                'style': 'harmonious',
                'primary_color': analogous_hex,
                'secondary_color': color['hex'],
                'pattern_type': pattern_type,
                'intensity': intensity,
                'description': f"Harmonious background using {analogous_hex} to complement fabric's {color['hex']}",
                'matching_score': 8.5 - (i * 0.3),
                'mood_compatibility': self.calculate_mood_compatibility(mood, 'harmonious'),
                'prompt_elements': [
                    f"{pattern_type} background pattern",
                    f"primary color {analogous_hex}",
                    f"harmonious tones with {color['hex']}",
                    f"{intensity} intensity",
                    "analogous color scheme"
                ]
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def create_neutral_suggestions(self, color_temperature: str, mood: str, pattern_type: str, intensity: str) -> List[Dict[str, Any]]:
        """Create neutral background suggestions"""
        suggestions = []
        
        # Choose neutral colors based on temperature
        if color_temperature == 'warm':
            neutral_colors = ['#F5F5DC', '#FAF0E6', '#FDF5E6']  # Warm neutrals
        elif color_temperature == 'cool':
            neutral_colors = ['#F0F8FF', '#F5F5F5', '#E6E6FA']  # Cool neutrals
        else:
            neutral_colors = ['#F8F8FF', '#F5F5F5', '#FAFAFA']  # Pure neutrals
        
        for i, neutral_color in enumerate(neutral_colors):
            suggestion = {
                'style': 'neutral',
                'primary_color': neutral_color,
                'secondary_color': None,
                'pattern_type': pattern_type,
                'intensity': 'subtle',  # Neutrals are always subtle
                'description': f"Neutral {color_temperature} background in {neutral_color}",
                'matching_score': 7.5 - (i * 0.2),
                'mood_compatibility': self.calculate_mood_compatibility(mood, 'neutral'),
                'prompt_elements': [
                    f"{pattern_type} background pattern",
                    f"neutral {color_temperature} tone",
                    f"color {neutral_color}",
                    "subtle intensity",
                    "clean minimal design"
                ]
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def calculate_mood_compatibility(self, fabric_mood: str, background_style: str) -> float:
        """Calculate compatibility score between fabric mood and background style"""
        compatibility_matrix = {
            'elegant': {'complementary': 8.0, 'harmonious': 9.0, 'neutral': 8.5},
            'vibrant': {'complementary': 9.5, 'harmonious': 7.0, 'neutral': 6.0},
            'calm': {'complementary': 6.0, 'harmonious': 9.0, 'neutral': 9.5},
            'festive': {'complementary': 9.0, 'harmonious': 8.0, 'neutral': 5.0},
            'traditional': {'complementary': 7.0, 'harmonious': 9.0, 'neutral': 8.0},
            'modern': {'complementary': 8.5, 'harmonious': 7.5, 'neutral': 9.0},
            'luxury': {'complementary': 8.0, 'harmonious': 8.5, 'neutral': 9.0},
            'casual': {'complementary': 7.5, 'harmonious': 8.0, 'neutral': 8.5}
        }
        
        return compatibility_matrix.get(fabric_mood, {}).get(background_style, 7.0)
    
    def generate_background_from_suggestion(self,
                                          organization,
                                          user,
                                          suggestion: Dict[str, Any],
                                          fabric_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate background using AI based on suggestion"""
        try:
            # Create background prompt
            background_prompt = self.create_background_prompt(suggestion, fabric_analysis)
            
            # Get provider
            provider = self.get_nanobanana_provider()
            
            # Create generation request
            request = AIGenerationRequest.objects.create(
                organization=organization,
                user=user,
                provider=provider,
                generation_type='background',
                prompt=background_prompt,
                negative_prompt="foreground objects, text, cluttered elements, low quality, blurry",
                parameters={
                    'style': suggestion['style'],
                    'primary_color': suggestion['primary_color'],
                    'secondary_color': suggestion.get('secondary_color'),
                    'pattern_type': suggestion['pattern_type'],
                    'intensity': suggestion['intensity'],
                    'width': 1024,
                    'height': 1024,
                    'steps': 15,
                    'guidance_scale': 6.0
                }
            )
            
            # Process the generation request
            success = self.ai_service.process_generation_request(request)
            
            if success:
                result = {
                    'success': True,
                    'request_id': str(request.id),
                    'background_urls': request.result_urls,
                    'prompt_used': background_prompt,
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
            
            logger.info(f"Background generation completed for request {request.id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate background from suggestion: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_background_prompt(self, suggestion: Dict[str, Any], fabric_analysis: Dict[str, Any]) -> str:
        """Create AI prompt for background generation"""
        
        # Start with base elements
        prompt_parts = suggestion['prompt_elements'].copy()
        
        # Add fabric mood context
        fabric_mood = fabric_analysis['analysis']['fabric_mood']['mood']
        mood_elements = {
            'elegant': 'sophisticated design, refined aesthetics',
            'vibrant': 'energetic patterns, dynamic composition',
            'calm': 'peaceful design, serene atmosphere',
            'festive': 'celebratory elements, joyful patterns',
            'traditional': 'classic motifs, cultural elements',
            'modern': 'contemporary design, clean lines',
            'luxury': 'premium quality, elegant finish',
            'casual': 'relaxed design, comfortable feel'
        }
        
        if fabric_mood in mood_elements:
            prompt_parts.append(mood_elements[fabric_mood])
        
        # Add technical requirements
        prompt_parts.extend([
            "high resolution background",
            "seamless tiling capability",
            "suitable for textile photography",
            "professional quality",
            "no distracting elements"
        ])
        
        # Join all elements
        prompt = ", ".join(prompt_parts)
        
        return prompt
    
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
        
        return provider
    
    def get_background_presets(self) -> List[Dict[str, Any]]:
        """Get predefined background presets"""
        presets = [
            {
                'id': 'elegant_neutral',
                'name': 'Elegant Neutral',
                'description': 'Sophisticated neutral background for elegant fabrics',
                'style': 'neutral',
                'pattern_type': 'subtle',
                'intensity': 'low',
                'best_for': ['elegant', 'luxury', 'formal']
            },
            {
                'id': 'vibrant_complementary',
                'name': 'Vibrant Complementary',
                'description': 'High-contrast background for vibrant fabrics',
                'style': 'complementary',
                'pattern_type': 'geometric',
                'intensity': 'high',
                'best_for': ['vibrant', 'festive', 'modern']
            },
            {
                'id': 'calm_harmonious',
                'name': 'Calm Harmonious',
                'description': 'Peaceful harmonious background for calm fabrics',
                'style': 'harmonious',
                'pattern_type': 'organic',
                'intensity': 'medium',
                'best_for': ['calm', 'traditional', 'casual']
            },
            {
                'id': 'festive_celebration',
                'name': 'Festive Celebration',
                'description': 'Celebratory background for festival fabrics',
                'style': 'complementary',
                'pattern_type': 'decorative',
                'intensity': 'high',
                'best_for': ['festive', 'traditional', 'vibrant']
            }
        ]
        
        return presets
