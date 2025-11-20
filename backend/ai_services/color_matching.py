"""
Advanced Color Matching Algorithms for Phase 1 Week 4
Implements K-Means clustering and LAB color similarity for fabric color analysis
"""
import logging
import numpy as np
import cv2
from typing import Dict, List, Any, Optional, Tuple
from sklearn.cluster import KMeans
from PIL import Image
import colorsys
import requests
from io import BytesIO
from django.conf import settings

logger = logging.getLogger(__name__)


class SmartColorMatcher:
    """Advanced color matching service using K-Means clustering and LAB color space"""
    
    def __init__(self):
        self.kmeans_clusters = 8  # Number of clusters for K-Means
        self.color_tolerance = 15  # LAB color difference tolerance
    
    def extract_dominant_colors(self, image_url: str, num_colors: int = 8) -> List[Dict[str, Any]]:
        """
        Extract dominant colors from fabric image using K-Means clustering
        
        Args:
            image_url: URL of the fabric image
            num_colors: Number of dominant colors to extract
            
        Returns:
            List of color dictionaries with hex, RGB, LAB, and percentage
        """
        try:
            # Download and process image
            image = self._download_image(image_url)
            if image is None:
                raise ValueError("Failed to download image")
            
            # Resize image for faster processing
            image = self._resize_image(image, max_size=300)
            
            # Convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Reshape image for K-Means
            pixels = image_rgb.reshape(-1, 3)
            
            # Apply K-Means clustering
            kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get cluster centers (dominant colors)
            colors = kmeans.cluster_centers_.astype(int)
            
            # Get cluster labels and counts
            labels = kmeans.labels_
            unique_labels, counts = np.unique(labels, return_counts=True)
            
            # Calculate percentages
            total_pixels = len(pixels)
            percentages = (counts / total_pixels) * 100
            
            # Create color palette
            color_palette = []
            for i, (color, percentage) in enumerate(zip(colors, percentages)):
                hex_color = self._rgb_to_hex(color)
                lab_color = self._rgb_to_lab(color)
                
                color_info = {
                    'hex': hex_color,
                    'rgb': color.tolist(),
                    'lab': lab_color,
                    'percentage': round(percentage, 2),
                    'cluster_id': int(unique_labels[i]),
                    'name': self._get_color_name(color),
                    'hsv': self._rgb_to_hsv(color),
                    'hsl': self._rgb_to_hsl(color)
                }
                color_palette.append(color_info)
            
            # Sort by percentage (most dominant first)
            color_palette.sort(key=lambda x: x['percentage'], reverse=True)
            
            logger.info(f"Extracted {len(color_palette)} dominant colors from {image_url}")
            return color_palette
            
        except Exception as e:
            logger.error(f"Failed to extract dominant colors: {str(e)}")
            return []
    
    def match_colors(self, fabric_colors: List[Dict], design_colors: List[Dict]) -> Dict[str, Any]:
        """
        Match colors between fabric and design using LAB color similarity
        
        Args:
            fabric_colors: List of fabric color dictionaries
            design_colors: List of design color dictionaries
            
        Returns:
            Dictionary containing matching results and suggestions
        """
        try:
            matches = []
            unmatched_fabric = []
            unmatched_design = []
            
            # Create copies for tracking
            fabric_remaining = fabric_colors.copy()
            design_remaining = design_colors.copy()
            
            # Find matches using LAB color distance
            for fabric_color in fabric_colors:
                best_match = None
                best_distance = float('inf')
                best_design_idx = -1
                
                for i, design_color in enumerate(design_remaining):
                    distance = self._calculate_lab_distance(
                        fabric_color['lab'], 
                        design_color['lab']
                    )
                    
                    if distance < best_distance and distance <= self.color_tolerance:
                        best_distance = distance
                        best_match = design_color
                        best_design_idx = i
                
                if best_match:
                    match_info = {
                        'fabric_color': fabric_color,
                        'design_color': best_match,
                        'distance': round(best_distance, 2),
                        'similarity_score': round((1 - best_distance / 100) * 100, 1),
                        'match_quality': self._get_match_quality(best_distance)
                    }
                    matches.append(match_info)
                    
                    # Remove matched design color
                    if best_design_idx >= 0:
                        design_remaining.pop(best_design_idx)
                else:
                    unmatched_fabric.append(fabric_color)
            
            # Remaining design colors are unmatched
            unmatched_design = design_remaining
            
            # Calculate overall matching score
            total_fabric_percentage = sum(c['percentage'] for c in fabric_colors)
            matched_percentage = sum(c['fabric_color']['percentage'] for c in matches)
            overall_score = (matched_percentage / total_fabric_percentage) * 100 if total_fabric_percentage > 0 else 0
            
            # Generate color harmony suggestions
            harmony_suggestions = self._generate_harmony_suggestions(fabric_colors, design_colors)
            
            result = {
                'matches': matches,
                'unmatched_fabric': unmatched_fabric,
                'unmatched_design': unmatched_design,
                'overall_matching_score': round(overall_score, 1),
                'total_matches': len(matches),
                'harmony_suggestions': harmony_suggestions,
                'color_analysis': self._analyze_color_relationships(fabric_colors, design_colors)
            }
            
            logger.info(f"Color matching completed: {len(matches)} matches found")
            return result
            
        except Exception as e:
            logger.error(f"Failed to match colors: {str(e)}")
            return {
                'matches': [],
                'unmatched_fabric': fabric_colors,
                'unmatched_design': design_colors,
                'overall_matching_score': 0,
                'error': str(e)
            }
    
    def suggest_color_adjustments(self, fabric_colors: List[Dict], target_harmony: str = 'complementary') -> List[Dict[str, Any]]:
        """
        Suggest color adjustments for better harmony
        
        Args:
            fabric_colors: List of fabric colors
            target_harmony: Target harmony type (complementary, analogous, triadic, etc.)
            
        Returns:
            List of color adjustment suggestions
        """
        try:
            suggestions = []
            
            for color in fabric_colors:
                if target_harmony == 'complementary':
                    adj_colors = self._get_complementary_colors(color)
                elif target_harmony == 'analogous':
                    adj_colors = self._get_analogous_colors(color)
                elif target_harmony == 'triadic':
                    adj_colors = self._get_triadic_colors(color)
                elif target_harmony == 'split_complementary':
                    adj_colors = self._get_split_complementary_colors(color)
                else:
                    adj_colors = self._get_complementary_colors(color)
                
                suggestion = {
                    'original_color': color,
                    'target_harmony': target_harmony,
                    'suggested_colors': adj_colors,
                    'adjustment_type': 'harmony_based',
                    'confidence': self._calculate_harmony_confidence(color, target_harmony)
                }
                suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to suggest color adjustments: {str(e)}")
            return []
    
    def _download_image(self, image_url: str) -> Optional[np.ndarray]:
        """Download image from URL and convert to OpenCV format"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Convert to PIL Image
            image = Image.open(BytesIO(response.content))
            
            # Convert to OpenCV format
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            return image_cv
            
        except Exception as e:
            logger.error(f"Failed to download image {image_url}: {str(e)}")
            return None
    
    def _resize_image(self, image: np.ndarray, max_size: int = 300) -> np.ndarray:
        """Resize image while maintaining aspect ratio"""
        height, width = image.shape[:2]
        
        if max(height, width) <= max_size:
            return image
        
        if height > width:
            new_height = max_size
            new_width = int(width * max_size / height)
        else:
            new_width = max_size
            new_height = int(height * max_size / width)
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    def _rgb_to_hex(self, rgb: np.ndarray) -> str:
        """Convert RGB array to hex string"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def _rgb_to_lab(self, rgb: np.ndarray) -> List[float]:
        """Convert RGB to LAB color space"""
        # Normalize RGB values
        rgb_norm = rgb.astype(np.float32) / 255.0
        
        # Convert to LAB using OpenCV
        lab = cv2.cvtColor(np.uint8([[rgb_norm * 255]]), cv2.COLOR_RGB2LAB)[0][0]
        
        return lab.tolist()
    
    def _rgb_to_hsv(self, rgb: np.ndarray) -> List[float]:
        """Convert RGB to HSV"""
        rgb_norm = rgb.astype(np.float32) / 255.0
        hsv = colorsys.rgb_to_hsv(rgb_norm[0], rgb_norm[1], rgb_norm[2])
        return [hsv[0] * 360, hsv[1] * 100, hsv[2] * 100]  # Convert to standard ranges
    
    def _rgb_to_hsl(self, rgb: np.ndarray) -> List[float]:
        """Convert RGB to HSL"""
        rgb_norm = rgb.astype(np.float32) / 255.0
        hsl = colorsys.rgb_to_hls(rgb_norm[0], rgb_norm[1], rgb_norm[2])
        return [hsl[0] * 360, hsl[2] * 100, hsl[1] * 100]  # Convert to standard ranges
    
    def _get_color_name(self, rgb: np.ndarray) -> str:
        """Get approximate color name based on RGB values"""
        r, g, b = rgb
        
        # Simple color name mapping based on RGB values
        if r > 200 and g < 100 and b < 100:
            return "Red"
        elif r < 100 and g > 200 and b < 100:
            return "Green"
        elif r < 100 and g < 100 and b > 200:
            return "Blue"
        elif r > 200 and g > 200 and b < 100:
            return "Yellow"
        elif r > 200 and g < 100 and b > 200:
            return "Magenta"
        elif r < 100 and g > 200 and b > 200:
            return "Cyan"
        elif r > 200 and g > 200 and b > 200:
            return "White"
        elif r < 100 and g < 100 and b < 100:
            return "Black"
        elif r > 150 and g > 150 and b < 100:
            return "Orange"
        elif r > 150 and g < 100 and b > 150:
            return "Purple"
        elif r < 100 and g > 150 and b > 150:
            return "Teal"
        else:
            return "Mixed"
    
    def _calculate_lab_distance(self, lab1: List[float], lab2: List[float]) -> float:
        """Calculate Euclidean distance in LAB color space"""
        return np.sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2)))
    
    def _get_match_quality(self, distance: float) -> str:
        """Get match quality based on LAB distance"""
        if distance <= 5:
            return "Excellent"
        elif distance <= 10:
            return "Good"
        elif distance <= 15:
            return "Fair"
        elif distance <= 25:
            return "Poor"
        else:
            return "Very Poor"
    
    def _generate_harmony_suggestions(self, fabric_colors: List[Dict], design_colors: List[Dict]) -> List[Dict[str, Any]]:
        """Generate color harmony suggestions"""
        suggestions = []
        
        # Analyze current harmony
        fabric_harmony = self._analyze_color_harmony(fabric_colors)
        design_harmony = self._analyze_color_harmony(design_colors)
        
        # Suggest improvements
        if fabric_harmony['type'] != design_harmony['type']:
            suggestions.append({
                'type': 'harmony_mismatch',
                'message': f"Fabric uses {fabric_harmony['type']} harmony while design uses {design_harmony['type']}",
                'suggestion': f"Consider adjusting design to use {fabric_harmony['type']} harmony for better cohesion"
            })
        
        # Suggest complementary colors for unmatched colors
        for color in fabric_colors:
            if color['percentage'] > 20:  # Only for dominant colors
                complementary = self._get_complementary_colors(color)
                suggestions.append({
                    'type': 'complementary_suggestion',
                    'base_color': color,
                    'suggested_colors': complementary,
                    'reason': f"Complementary colors for dominant {color['name']} ({color['percentage']}%)"
                })
        
        return suggestions
    
    def _analyze_color_harmony(self, colors: List[Dict]) -> Dict[str, Any]:
        """Analyze color harmony type"""
        if len(colors) < 2:
            return {'type': 'single', 'score': 0}
        
        # Get hue values
        hues = [color['hsv'][0] for color in colors[:5]]  # Top 5 colors
        
        # Calculate hue spread
        hue_spread = max(hues) - min(hues)
        
        # Determine harmony type
        if hue_spread < 30:
            return {'type': 'monochromatic', 'score': 9.0}
        elif hue_spread < 60:
            return {'type': 'analogous', 'score': 8.5}
        elif any(abs(h1 - h2) > 150 for h1 in hues for h2 in hues if h1 != h2):
            return {'type': 'complementary', 'score': 8.0}
        else:
            return {'type': 'triadic', 'score': 7.5}
    
    def _analyze_color_relationships(self, fabric_colors: List[Dict], design_colors: List[Dict]) -> Dict[str, Any]:
        """Analyze relationships between fabric and design colors"""
        analysis = {
            'fabric_dominance': self._get_dominant_color_info(fabric_colors),
            'design_dominance': self._get_dominant_color_info(design_colors),
            'color_temperature_match': self._analyze_temperature_match(fabric_colors, design_colors),
            'saturation_balance': self._analyze_saturation_balance(fabric_colors, design_colors),
            'contrast_level': self._analyze_contrast_level(fabric_colors, design_colors)
        }
        
        return analysis
    
    def _get_dominant_color_info(self, colors: List[Dict]) -> Dict[str, Any]:
        """Get information about dominant colors"""
        if not colors:
            return {'primary': None, 'secondary': None}
        
        dominant = colors[0] if colors else None
        secondary = colors[1] if len(colors) > 1 else None
        
        return {
            'primary': dominant,
            'secondary': secondary,
            'total_colors': len(colors)
        }
    
    def _analyze_temperature_match(self, fabric_colors: List[Dict], design_colors: List[Dict]) -> Dict[str, Any]:
        """Analyze color temperature match between fabric and design"""
        fabric_temp = self._get_color_temperature(fabric_colors)
        design_temp = self._get_color_temperature(design_colors)
        
        match_score = 10 if fabric_temp == design_temp else 5
        
        return {
            'fabric_temperature': fabric_temp,
            'design_temperature': design_temp,
            'match_score': match_score,
            'recommendation': 'Good match' if match_score >= 8 else 'Consider temperature adjustment'
        }
    
    def _get_color_temperature(self, colors: List[Dict]) -> str:
        """Determine overall color temperature"""
        if not colors:
            return 'neutral'
        
        warm_score = 0
        cool_score = 0
        
        for color in colors:
            hsv = color['hsv']
            hue = hsv[0]
            percentage = color['percentage']
            
            # Warm colors (reds, oranges, yellows)
            if 0 <= hue <= 60 or 300 <= hue <= 360:
                warm_score += percentage
            # Cool colors (blues, greens, purples)
            elif 120 <= hue <= 240:
                cool_score += percentage
        
        if warm_score > cool_score * 1.2:
            return 'warm'
        elif cool_score > warm_score * 1.2:
            return 'cool'
        else:
            return 'neutral'
    
    def _analyze_saturation_balance(self, fabric_colors: List[Dict], design_colors: List[Dict]) -> Dict[str, Any]:
        """Analyze saturation balance between fabric and design"""
        fabric_sat = sum(c['hsv'][1] * c['percentage'] for c in fabric_colors) / 100
        design_sat = sum(c['hsv'][1] * c['percentage'] for c in design_colors) / 100
        
        balance_score = 10 - abs(fabric_sat - design_sat) / 10
        
        return {
            'fabric_saturation': round(fabric_sat, 1),
            'design_saturation': round(design_sat, 1),
            'balance_score': round(balance_score, 1),
            'recommendation': 'Good balance' if balance_score >= 7 else 'Consider saturation adjustment'
        }
    
    def _analyze_contrast_level(self, fabric_colors: List[Dict], design_colors: List[Dict]) -> Dict[str, Any]:
        """Analyze contrast level between fabric and design"""
        # Calculate average brightness
        fabric_brightness = sum(c['hsv'][2] * c['percentage'] for c in fabric_colors) / 100
        design_brightness = sum(c['hsv'][2] * c['percentage'] for c in design_colors) / 100
        
        contrast = abs(fabric_brightness - design_brightness)
        
        if contrast > 50:
            level = 'high'
        elif contrast > 25:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'fabric_brightness': round(fabric_brightness, 1),
            'design_brightness': round(design_brightness, 1),
            'contrast_level': level,
            'contrast_value': round(contrast, 1),
            'recommendation': f'{level.title()} contrast - {"Good for readability" if level == "high" else "Consider increasing contrast"}'
        }
    
    def _get_complementary_colors(self, color: Dict) -> List[Dict[str, Any]]:
        """Get complementary colors for a given color"""
        hsv = color['hsv']
        hue = hsv[0]
        
        # Calculate complementary hue (180 degrees opposite)
        comp_hue = (hue + 180) % 360
        
        # Create complementary color variations
        complementary_colors = []
        
        for sat_adj in [0.8, 1.0, 1.2]:
            for val_adj in [0.7, 0.9, 1.1]:
                new_sat = min(100, hsv[1] * sat_adj)
                new_val = min(100, hsv[2] * val_adj)
                
                # Convert back to RGB
                rgb = colorsys.hsv_to_rgb(comp_hue/360, new_sat/100, new_val/100)
                rgb_array = np.array([int(c * 255) for c in rgb])
                
                comp_color = {
                    'hex': self._rgb_to_hex(rgb_array),
                    'rgb': rgb_array.tolist(),
                    'hsv': [comp_hue, new_sat, new_val],
                    'name': f"Complementary {color['name']}",
                    'relationship': 'complementary'
                }
                complementary_colors.append(comp_color)
        
        return complementary_colors[:3]  # Return top 3 variations
    
    def _get_analogous_colors(self, color: Dict) -> List[Dict[str, Any]]:
        """Get analogous colors for a given color"""
        hsv = color['hsv']
        hue = hsv[0]
        
        analogous_colors = []
        
        # Create analogous colors (±30 degrees)
        for hue_offset in [-30, -15, 15, 30]:
            new_hue = (hue + hue_offset) % 360
            
            rgb = colorsys.hsv_to_rgb(new_hue/360, hsv[1]/100, hsv[2]/100)
            rgb_array = np.array([int(c * 255) for c in rgb])
            
            analog_color = {
                'hex': self._rgb_to_hex(rgb_array),
                'rgb': rgb_array.tolist(),
                'hsv': [new_hue, hsv[1], hsv[2]],
                'name': f"Analogous {color['name']}",
                'relationship': 'analogous'
            }
            analogous_colors.append(analog_color)
        
        return analogous_colors
    
    def _get_triadic_colors(self, color: Dict) -> List[Dict[str, Any]]:
        """Get triadic colors for a given color"""
        hsv = color['hsv']
        hue = hsv[0]
        
        triadic_colors = []
        
        # Create triadic colors (±120 degrees)
        for hue_offset in [120, 240]:
            new_hue = (hue + hue_offset) % 360
            
            rgb = colorsys.hsv_to_rgb(new_hue/360, hsv[1]/100, hsv[2]/100)
            rgb_array = np.array([int(c * 255) for c in rgb])
            
            triadic_color = {
                'hex': self._rgb_to_hex(rgb_array),
                'rgb': rgb_array.tolist(),
                'hsv': [new_hue, hsv[1], hsv[2]],
                'name': f"Triadic {color['name']}",
                'relationship': 'triadic'
            }
            triadic_colors.append(triadic_color)
        
        return triadic_colors
    
    def _get_split_complementary_colors(self, color: Dict) -> List[Dict[str, Any]]:
        """Get split complementary colors for a given color"""
        hsv = color['hsv']
        hue = hsv[0]
        
        split_comp_colors = []
        
        # Create split complementary colors (±150 degrees)
        for hue_offset in [150, 210]:
            new_hue = (hue + hue_offset) % 360
            
            rgb = colorsys.hsv_to_rgb(new_hue/360, hsv[1]/100, hsv[2]/100)
            rgb_array = np.array([int(c * 255) for c in rgb])
            
            split_comp_color = {
                'hex': self._rgb_to_hex(rgb_array),
                'rgb': rgb_array.tolist(),
                'hsv': [new_hue, hsv[1], hsv[2]],
                'name': f"Split Complementary {color['name']}",
                'relationship': 'split_complementary'
            }
            split_comp_colors.append(split_comp_color)
        
        return split_comp_colors
    
    def _calculate_harmony_confidence(self, color: Dict, harmony_type: str) -> float:
        """Calculate confidence score for harmony suggestion"""
        # Base confidence on color properties
        hsv = color['hsv']
        saturation = hsv[1]
        value = hsv[2]
        
        # Higher saturation and value generally work better for harmony
        confidence = (saturation + value) / 200
        
        # Adjust based on harmony type
        if harmony_type == 'complementary' and saturation > 70:
            confidence += 0.1
        elif harmony_type == 'analogous' and 30 <= saturation <= 80:
            confidence += 0.1
        
        return min(1.0, confidence)

