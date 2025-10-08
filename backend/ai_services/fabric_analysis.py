"""
Fabric Analysis Service for Phase 1 Week 4
Advanced fabric color extraction and texture pattern analysis using OpenCV and PIL
"""
import logging
import numpy as np
import cv2
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image, ImageStat
import requests
from io import BytesIO
from django.conf import settings
from .color_matching import SmartColorMatcher
from .models import AIGenerationRequest, AIProvider
from .services import AIGenerationService

logger = logging.getLogger(__name__)


class FabricAnalyzer:
    """Advanced fabric analysis service for color extraction and texture analysis"""
    
    def __init__(self):
        self.color_matcher = SmartColorMatcher()
        self.ai_service = AIGenerationService()
    
    def analyze_fabric(self, fabric_image_url: str, analysis_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        Comprehensive fabric analysis including colors, textures, and patterns
        
        Args:
            fabric_image_url: URL of the fabric image
            analysis_type: Type of analysis ('comprehensive', 'colors_only', 'texture_only')
            
        Returns:
            Dictionary containing comprehensive fabric analysis
        """
        try:
            # Download and process image
            image = self._download_image(fabric_image_url)
            if image is None:
                raise ValueError("Failed to download fabric image")
            
            # Initialize result structure
            analysis_result = {
                'success': True,
                'image_url': fabric_image_url,
                'analysis_type': analysis_type,
                'image_info': self._get_image_info(image),
                'timestamp': self._get_timestamp()
            }
            
            # Color analysis
            if analysis_type in ['comprehensive', 'colors_only']:
                color_analysis = self._analyze_fabric_colors(image, fabric_image_url)
                analysis_result['color_analysis'] = color_analysis
            
            # Texture analysis
            if analysis_type in ['comprehensive', 'texture_only']:
                texture_analysis = self._analyze_fabric_texture(image)
                analysis_result['texture_analysis'] = texture_analysis
            
            # Pattern analysis
            if analysis_type == 'comprehensive':
                pattern_analysis = self._analyze_fabric_patterns(image)
                analysis_result['pattern_analysis'] = pattern_analysis
            
            # Quality assessment
            if analysis_type == 'comprehensive':
                quality_assessment = self._assess_fabric_quality(image)
                analysis_result['quality_assessment'] = quality_assessment
            
            # Generate recommendations
            recommendations = self._generate_fabric_recommendations(analysis_result)
            analysis_result['recommendations'] = recommendations
            
            logger.info(f"Fabric analysis completed for {fabric_image_url}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Failed to analyze fabric: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'image_url': fabric_image_url,
                'analysis_type': analysis_type
            }
    
    def extract_color_palette(self, fabric_image_url: str, num_colors: int = 8) -> Dict[str, Any]:
        """
        Extract detailed color palette from fabric image
        
        Args:
            fabric_image_url: URL of the fabric image
            num_colors: Number of colors to extract
            
        Returns:
            Dictionary containing color palette with HEX, RGB, LAB values
        """
        try:
            # Use the smart color matcher for extraction
            color_palette = self.color_matcher.extract_dominant_colors(fabric_image_url, num_colors)
            
            if not color_palette:
                raise ValueError("Failed to extract color palette")
            
            # Enhance with additional color information
            enhanced_palette = []
            for color in color_palette:
                enhanced_color = {
                    **color,
                    'color_family': self._get_color_family(color),
                    'seasonal_association': self._get_seasonal_association(color),
                    'cultural_significance': self._get_cultural_significance(color),
                    'fashion_trends': self._get_fashion_trends(color),
                    'accessibility_score': self._calculate_accessibility_score(color)
                }
                enhanced_palette.append(enhanced_color)
            
            # Generate color harmony analysis
            harmony_analysis = self._analyze_color_harmony(enhanced_palette)
            
            result = {
                'success': True,
                'image_url': fabric_image_url,
                'color_palette': enhanced_palette,
                'harmony_analysis': harmony_analysis,
                'total_colors': len(enhanced_palette),
                'dominant_color': enhanced_palette[0] if enhanced_palette else None,
                'color_diversity_score': self._calculate_color_diversity(enhanced_palette)
            }
            
            logger.info(f"Color palette extracted: {len(enhanced_palette)} colors from {fabric_image_url}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract color palette: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'image_url': fabric_image_url
            }
    
    def analyze_texture_patterns(self, fabric_image_url: str) -> Dict[str, Any]:
        """
        Analyze fabric texture and patterns using computer vision
        
        Args:
            fabric_image_url: URL of the fabric image
            
        Returns:
            Dictionary containing texture and pattern analysis
        """
        try:
            # Download and process image
            image = self._download_image(fabric_image_url)
            if image is None:
                raise ValueError("Failed to download fabric image")
            
            # Convert to grayscale for texture analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Texture analysis
            texture_features = self._extract_texture_features(gray)
            
            # Pattern detection
            pattern_features = self._detect_patterns(gray)
            
            # Fabric type classification
            fabric_type = self._classify_fabric_type(image, texture_features, pattern_features)
            
            result = {
                'success': True,
                'image_url': fabric_image_url,
                'texture_features': texture_features,
                'pattern_features': pattern_features,
                'fabric_type': fabric_type,
                'texture_quality': self._assess_texture_quality(texture_features),
                'pattern_complexity': self._assess_pattern_complexity(pattern_features)
            }
            
            logger.info(f"Texture analysis completed for {fabric_image_url}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze texture patterns: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'image_url': fabric_image_url
            }
    
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
    
    def _get_image_info(self, image: np.ndarray) -> Dict[str, Any]:
        """Get basic image information"""
        height, width = image.shape[:2]
        
        return {
            'dimensions': {'width': width, 'height': height},
            'aspect_ratio': round(width / height, 2),
            'total_pixels': width * height,
            'channels': image.shape[2] if len(image.shape) > 2 else 1
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from django.utils import timezone
        return timezone.now().isoformat()
    
    def _analyze_fabric_colors(self, image: np.ndarray, image_url: str) -> Dict[str, Any]:
        """Analyze fabric colors using the smart color matcher"""
        try:
            # Convert to RGB for color analysis
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Save temporary image for color extraction
            temp_path = f"/tmp/temp_fabric_{hash(image_url)}.jpg"
            cv2.imwrite(temp_path, image)
            
            # Use smart color matcher
            color_palette = self.color_matcher.extract_dominant_colors(f"file://{temp_path}")
            
            # Clean up temp file
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Analyze color properties
            color_analysis = {
                'dominant_colors': color_palette[:3] if color_palette else [],
                'color_harmony': self._analyze_color_harmony(color_palette),
                'color_temperature': self._analyze_color_temperature(color_palette),
                'color_intensity': self._analyze_color_intensity(color_palette),
                'fabric_mood': self._determine_fabric_mood(color_palette),
                'complementary_colors': self._get_complementary_colors(color_palette[:2]) if len(color_palette) >= 2 else [],
                'total_colors': len(color_palette)
            }
            
            return color_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze fabric colors: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_fabric_texture(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze fabric texture using computer vision techniques"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Extract texture features
            texture_features = self._extract_texture_features(gray)
            
            # Analyze texture properties
            texture_analysis = {
                'roughness': texture_features['roughness'],
                'smoothness': texture_features['smoothness'],
                'regularity': texture_features['regularity'],
                'directionality': texture_features['directionality'],
                'texture_type': self._classify_texture_type(texture_features),
                'surface_quality': self._assess_surface_quality(texture_features)
            }
            
            return texture_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze fabric texture: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_fabric_patterns(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze fabric patterns and motifs"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect patterns
            pattern_features = self._detect_patterns(gray)
            
            # Analyze pattern properties
            pattern_analysis = {
                'pattern_type': pattern_features['type'],
                'pattern_complexity': pattern_features['complexity'],
                'pattern_regularity': pattern_features['regularity'],
                'motif_size': pattern_features['motif_size'],
                'repeat_frequency': pattern_features['repeat_frequency'],
                'pattern_direction': pattern_features['direction'],
                'cultural_motifs': self._identify_cultural_motifs(pattern_features)
            }
            
            return pattern_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze fabric patterns: {str(e)}")
            return {'error': str(e)}
    
    def _assess_fabric_quality(self, image: np.ndarray) -> Dict[str, Any]:
        """Assess overall fabric quality"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate quality metrics
            sharpness = self._calculate_sharpness(gray)
            contrast = self._calculate_contrast(gray)
            brightness = self._calculate_brightness(gray)
            
            # Overall quality score
            quality_score = (sharpness + contrast + brightness) / 3
            
            quality_assessment = {
                'sharpness_score': round(sharpness, 2),
                'contrast_score': round(contrast, 2),
                'brightness_score': round(brightness, 2),
                'overall_quality_score': round(quality_score, 2),
                'quality_grade': self._get_quality_grade(quality_score),
                'recommendations': self._get_quality_recommendations(quality_score, sharpness, contrast, brightness)
            }
            
            return quality_assessment
            
        except Exception as e:
            logger.error(f"Failed to assess fabric quality: {str(e)}")
            return {'error': str(e)}
    
    def _extract_texture_features(self, gray_image: np.ndarray) -> Dict[str, float]:
        """Extract texture features using various methods"""
        try:
            # Calculate Local Binary Pattern (LBP) features
            lbp_features = self._calculate_lbp_features(gray_image)
            
            # Calculate Gabor filter responses
            gabor_features = self._calculate_gabor_features(gray_image)
            
            # Calculate statistical features
            statistical_features = self._calculate_statistical_features(gray_image)
            
            # Combine all features
            texture_features = {
                'roughness': lbp_features['roughness'],
                'smoothness': lbp_features['smoothness'],
                'regularity': gabor_features['regularity'],
                'directionality': gabor_features['directionality'],
                'contrast': statistical_features['contrast'],
                'homogeneity': statistical_features['homogeneity'],
                'energy': statistical_features['energy'],
                'correlation': statistical_features['correlation']
            }
            
            return texture_features
            
        except Exception as e:
            logger.error(f"Failed to extract texture features: {str(e)}")
            return {}
    
    def _calculate_lbp_features(self, gray_image: np.ndarray) -> Dict[str, float]:
        """Calculate Local Binary Pattern features"""
        try:
            # Simple LBP implementation
            height, width = gray_image.shape
            lbp_image = np.zeros_like(gray_image)
            
            for i in range(1, height - 1):
                for j in range(1, width - 1):
                    center = gray_image[i, j]
                    binary_string = ""
                    
                    # 8-neighborhood
                    neighbors = [
                        gray_image[i-1, j-1], gray_image[i-1, j], gray_image[i-1, j+1],
                        gray_image[i, j+1], gray_image[i+1, j+1], gray_image[i+1, j],
                        gray_image[i+1, j-1], gray_image[i, j-1]
                    ]
                    
                    for neighbor in neighbors:
                        binary_string += "1" if neighbor >= center else "0"
                    
                    lbp_image[i, j] = int(binary_string, 2)
            
            # Calculate texture features
            lbp_hist = cv2.calcHist([lbp_image], [0], None, [256], [0, 256])
            lbp_hist = lbp_hist.flatten()
            
            # Normalize histogram
            lbp_hist = lbp_hist / np.sum(lbp_hist)
            
            # Calculate roughness and smoothness
            roughness = np.sum(lbp_hist * np.arange(256)) / 255
            smoothness = 1 - roughness
            
            return {
                'roughness': float(roughness),
                'smoothness': float(smoothness)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate LBP features: {str(e)}")
            return {'roughness': 0.5, 'smoothness': 0.5}
    
    def _calculate_gabor_features(self, gray_image: np.ndarray) -> Dict[str, float]:
        """Calculate Gabor filter features"""
        try:
            # Create Gabor filters
            gabor_responses = []
            
            for angle in [0, 45, 90, 135]:
                kernel = cv2.getGaborKernel((21, 21), 5, np.radians(angle), 10, 0.5, 0, ktype=cv2.CV_32F)
                response = cv2.filter2D(gray_image, cv2.CV_8UC3, kernel)
                gabor_responses.append(response)
            
            # Calculate regularity and directionality
            response_variance = np.var([np.mean(resp) for resp in gabor_responses])
            regularity = 1 / (1 + response_variance)
            
            # Find dominant direction
            max_response_idx = np.argmax([np.mean(resp) for resp in gabor_responses])
            directionality = max_response_idx * 45  # Convert to degrees
            
            return {
                'regularity': float(regularity),
                'directionality': float(directionality)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate Gabor features: {str(e)}")
            return {'regularity': 0.5, 'directionality': 0}
    
    def _calculate_statistical_features(self, gray_image: np.ndarray) -> Dict[str, float]:
        """Calculate statistical texture features"""
        try:
            # Calculate GLCM (Gray Level Co-occurrence Matrix) features
            glcm = self._calculate_glcm(gray_image)
            
            # Calculate features from GLCM
            contrast = np.sum(glcm * np.square(np.arange(glcm.shape[0])[:, np.newaxis] - np.arange(glcm.shape[1])))
            homogeneity = np.sum(glcm / (1 + np.abs(np.arange(glcm.shape[0])[:, np.newaxis] - np.arange(glcm.shape[1]))))
            energy = np.sum(glcm ** 2)
            correlation = self._calculate_correlation(glcm)
            
            return {
                'contrast': float(contrast),
                'homogeneity': float(homogeneity),
                'energy': float(energy),
                'correlation': float(correlation)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate statistical features: {str(e)}")
            return {'contrast': 0.5, 'homogeneity': 0.5, 'energy': 0.5, 'correlation': 0.5}
    
    def _calculate_glcm(self, gray_image: np.ndarray, levels: int = 8) -> np.ndarray:
        """Calculate Gray Level Co-occurrence Matrix"""
        try:
            # Quantize image to reduce levels
            quantized = (gray_image // (256 // levels)).astype(np.uint8)
            
            # Initialize GLCM
            glcm = np.zeros((levels, levels), dtype=np.float32)
            
            # Calculate co-occurrence matrix
            for i in range(quantized.shape[0] - 1):
                for j in range(quantized.shape[1] - 1):
                    glcm[quantized[i, j], quantized[i, j + 1]] += 1
                    glcm[quantized[i, j], quantized[i + 1, j]] += 1
            
            # Normalize
            glcm = glcm / np.sum(glcm)
            
            return glcm
            
        except Exception as e:
            logger.error(f"Failed to calculate GLCM: {str(e)}")
            return np.ones((8, 8)) / 64
    
    def _calculate_correlation(self, glcm: np.ndarray) -> float:
        """Calculate correlation from GLCM"""
        try:
            i, j = np.meshgrid(np.arange(glcm.shape[0]), np.arange(glcm.shape[1]), indexing='ij')
            
            mu_i = np.sum(i * glcm)
            mu_j = np.sum(j * glcm)
            
            sigma_i = np.sqrt(np.sum(glcm * (i - mu_i) ** 2))
            sigma_j = np.sqrt(np.sum(glcm * (j - mu_j) ** 2))
            
            if sigma_i == 0 or sigma_j == 0:
                return 0
            
            correlation = np.sum(glcm * (i - mu_i) * (j - mu_j)) / (sigma_i * sigma_j)
            
            return float(correlation)
            
        except Exception as e:
            logger.error(f"Failed to calculate correlation: {str(e)}")
            return 0
    
    def _detect_patterns(self, gray_image: np.ndarray) -> Dict[str, Any]:
        """Detect patterns in fabric"""
        try:
            # Use template matching for pattern detection
            patterns = {
                'type': 'unknown',
                'complexity': 'medium',
                'regularity': 0.5,
                'motif_size': 'medium',
                'repeat_frequency': 'medium',
                'direction': 'none'
            }
            
            # Detect geometric patterns
            geometric_score = self._detect_geometric_patterns(gray_image)
            
            # Detect floral patterns
            floral_score = self._detect_floral_patterns(gray_image)
            
            # Detect abstract patterns
            abstract_score = self._detect_abstract_patterns(gray_image)
            
            # Determine pattern type
            if geometric_score > floral_score and geometric_score > abstract_score:
                patterns['type'] = 'geometric'
            elif floral_score > abstract_score:
                patterns['type'] = 'floral'
            else:
                patterns['type'] = 'abstract'
            
            # Calculate pattern complexity
            complexity = self._calculate_pattern_complexity(gray_image)
            patterns['complexity'] = complexity
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to detect patterns: {str(e)}")
            return {'type': 'unknown', 'complexity': 'medium', 'regularity': 0.5}
    
    def _detect_geometric_patterns(self, gray_image: np.ndarray) -> float:
        """Detect geometric patterns"""
        try:
            # Use edge detection
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Detect lines
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            # Detect circles
            circles = cv2.HoughCircles(gray_image, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0)
            
            # Calculate geometric score
            line_score = len(lines) if lines is not None else 0
            circle_score = len(circles[0]) if circles is not None else 0
            
            geometric_score = (line_score + circle_score) / 100
            
            return min(1.0, geometric_score)
            
        except Exception as e:
            logger.error(f"Failed to detect geometric patterns: {str(e)}")
            return 0
    
    def _detect_floral_patterns(self, gray_image: np.ndarray) -> float:
        """Detect floral patterns"""
        try:
            # Use blob detection for floral patterns
            params = cv2.SimpleBlobDetector_Params()
            params.filterByArea = True
            params.minArea = 100
            params.maxArea = 10000
            
            detector = cv2.SimpleBlobDetector_create(params)
            keypoints = detector.detect(gray_image)
            
            # Calculate floral score based on blob count and distribution
            floral_score = len(keypoints) / 50
            
            return min(1.0, floral_score)
            
        except Exception as e:
            logger.error(f"Failed to detect floral patterns: {str(e)}")
            return 0
    
    def _detect_abstract_patterns(self, gray_image: np.ndarray) -> float:
        """Detect abstract patterns"""
        try:
            # Use texture analysis for abstract patterns
            texture_features = self._extract_texture_features(gray_image)
            
            # Abstract patterns typically have high contrast and irregularity
            contrast = texture_features.get('contrast', 0)
            regularity = texture_features.get('regularity', 0)
            
            abstract_score = (contrast + (1 - regularity)) / 2
            
            return abstract_score
            
        except Exception as e:
            logger.error(f"Failed to detect abstract patterns: {str(e)}")
            return 0
    
    def _calculate_pattern_complexity(self, gray_image: np.ndarray) -> str:
        """Calculate pattern complexity"""
        try:
            # Use edge density as complexity measure
            edges = cv2.Canny(gray_image, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            if edge_density < 0.1:
                return 'low'
            elif edge_density < 0.3:
                return 'medium'
            else:
                return 'high'
                
        except Exception as e:
            logger.error(f"Failed to calculate pattern complexity: {str(e)}")
            return 'medium'
    
    def _classify_fabric_type(self, image: np.ndarray, texture_features: Dict, pattern_features: Dict) -> Dict[str, Any]:
        """Classify fabric type based on analysis"""
        try:
            # Simple fabric type classification based on features
            fabric_types = {
                'cotton': {'smoothness': 0.7, 'regularity': 0.6, 'pattern_complexity': 'low'},
                'silk': {'smoothness': 0.9, 'regularity': 0.8, 'pattern_complexity': 'medium'},
                'wool': {'smoothness': 0.4, 'regularity': 0.3, 'pattern_complexity': 'high'},
                'linen': {'smoothness': 0.5, 'regularity': 0.4, 'pattern_complexity': 'medium'},
                'denim': {'smoothness': 0.3, 'regularity': 0.7, 'pattern_complexity': 'low'}
            }
            
            # Calculate similarity scores
            scores = {}
            for fabric_type, characteristics in fabric_types.items():
                smoothness_diff = abs(texture_features.get('smoothness', 0.5) - characteristics['smoothness'])
                regularity_diff = abs(texture_features.get('regularity', 0.5) - characteristics['regularity'])
                
                score = 1 - (smoothness_diff + regularity_diff) / 2
                scores[fabric_type] = score
            
            # Find best match
            best_match = max(scores, key=scores.get)
            confidence = scores[best_match]
            
            return {
                'predicted_type': best_match,
                'confidence': round(confidence, 2),
                'all_scores': {k: round(v, 2) for k, v in scores.items()}
            }
            
        except Exception as e:
            logger.error(f"Failed to classify fabric type: {str(e)}")
            return {'predicted_type': 'unknown', 'confidence': 0}
    
    def _calculate_sharpness(self, gray_image: np.ndarray) -> float:
        """Calculate image sharpness using Laplacian variance"""
        try:
            laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
            sharpness = laplacian.var()
            
            # Normalize to 0-10 scale
            normalized_sharpness = min(10, sharpness / 1000)
            
            return normalized_sharpness
            
        except Exception as e:
            logger.error(f"Failed to calculate sharpness: {str(e)}")
            return 5.0
    
    def _calculate_contrast(self, gray_image: np.ndarray) -> float:
        """Calculate image contrast"""
        try:
            contrast = gray_image.std()
            
            # Normalize to 0-10 scale
            normalized_contrast = min(10, contrast / 25)
            
            return normalized_contrast
            
        except Exception as e:
            logger.error(f"Failed to calculate contrast: {str(e)}")
            return 5.0
    
    def _calculate_brightness(self, gray_image: np.ndarray) -> float:
        """Calculate image brightness"""
        try:
            brightness = gray_image.mean()
            
            # Normalize to 0-10 scale (optimal around 128)
            normalized_brightness = 10 - abs(brightness - 128) / 12.8
            
            return max(0, normalized_brightness)
            
        except Exception as e:
            logger.error(f"Failed to calculate brightness: {str(e)}")
            return 5.0
    
    def _get_quality_grade(self, quality_score: float) -> str:
        """Get quality grade based on score"""
        if quality_score >= 8:
            return 'A'
        elif quality_score >= 6:
            return 'B'
        elif quality_score >= 4:
            return 'C'
        else:
            return 'D'
    
    def _get_quality_recommendations(self, quality_score: float, sharpness: float, contrast: float, brightness: float) -> List[str]:
        """Get quality improvement recommendations"""
        recommendations = []
        
        if sharpness < 5:
            recommendations.append("Image appears blurry - consider using higher resolution or better lighting")
        
        if contrast < 5:
            recommendations.append("Low contrast detected - adjust lighting or image processing")
        
        if brightness < 5:
            recommendations.append("Image too dark or too bright - adjust exposure settings")
        
        if quality_score < 6:
            recommendations.append("Overall image quality could be improved for better analysis results")
        
        return recommendations
    
    def _get_color_family(self, color: Dict) -> str:
        """Get color family classification"""
        hsv = color['hsv']
        hue = hsv[0]
        
        if 0 <= hue <= 15 or 345 <= hue <= 360:
            return 'Red'
        elif 15 <= hue <= 45:
            return 'Orange'
        elif 45 <= hue <= 75:
            return 'Yellow'
        elif 75 <= hue <= 105:
            return 'Yellow-Green'
        elif 105 <= hue <= 135:
            return 'Green'
        elif 135 <= hue <= 165:
            return 'Blue-Green'
        elif 165 <= hue <= 195:
            return 'Blue'
        elif 195 <= hue <= 225:
            return 'Blue-Violet'
        elif 225 <= hue <= 255:
            return 'Violet'
        elif 255 <= hue <= 285:
            return 'Red-Violet'
        elif 285 <= hue <= 315:
            return 'Red'
        else:
            return 'Unknown'
    
    def _get_seasonal_association(self, color: Dict) -> str:
        """Get seasonal color association"""
        hsv = color['hsv']
        hue = hsv[0]
        saturation = hsv[1]
        value = hsv[2]
        
        # Spring: Light, bright colors
        if value > 70 and saturation > 50:
            if 60 <= hue <= 120:  # Greens and yellows
                return 'Spring'
        
        # Summer: Cool, muted colors
        if value > 60 and saturation < 60:
            if 180 <= hue <= 240:  # Blues and purples
                return 'Summer'
        
        # Autumn: Warm, rich colors
        if 60 <= value <= 80 and saturation > 60:
            if 0 <= hue <= 60 or 300 <= hue <= 360:  # Reds, oranges, yellows
                return 'Autumn'
        
        # Winter: Cool, bright colors
        if value > 80 and saturation > 70:
            if 240 <= hue <= 300:  # Purples and blues
                return 'Winter'
        
        return 'All Seasons'
    
    def _get_cultural_significance(self, color: Dict) -> Dict[str, str]:
        """Get cultural significance of color"""
        color_name = color['name'].lower()
        
        cultural_meanings = {
            'red': {
                'western': 'Passion, love, danger',
                'eastern': 'Good luck, prosperity, celebration',
                'indian': 'Purity, fertility, marriage'
            },
            'blue': {
                'western': 'Trust, stability, calm',
                'eastern': 'Immortality, healing',
                'indian': 'Divine, spiritual'
            },
            'green': {
                'western': 'Nature, growth, harmony',
                'eastern': 'Balance, harmony, growth',
                'indian': 'New beginnings, fertility'
            },
            'yellow': {
                'western': 'Happiness, optimism, energy',
                'eastern': 'Royalty, wisdom',
                'indian': 'Knowledge, learning, peace'
            },
            'white': {
                'western': 'Purity, innocence, peace',
                'eastern': 'Mourning, death',
                'indian': 'Purity, peace, mourning'
            },
            'black': {
                'western': 'Elegance, mystery, death',
                'eastern': 'Mystery, elegance',
                'indian': 'Evil, negativity'
            }
        }
        
        for color_key, meanings in cultural_meanings.items():
            if color_key in color_name:
                return meanings
        
        return {
            'western': 'Neutral, versatile',
            'eastern': 'Balanced, harmonious',
            'indian': 'Traditional, cultural'
        }
    
    def _get_fashion_trends(self, color: Dict) -> Dict[str, Any]:
        """Get current fashion trend information for color"""
        # This would typically connect to a fashion trend API
        # For now, return mock trend data
        
        color_name = color['name'].lower()
        
        trend_data = {
            'trend_score': np.random.randint(1, 10),
            'season': 'Spring/Summer 2024',
            'popularity': 'High' if np.random.random() > 0.5 else 'Medium',
            'style_categories': ['Casual', 'Formal', 'Streetwear'],
            'recommended_combinations': ['White', 'Black', 'Navy']
        }
        
        return trend_data
    
    def _calculate_accessibility_score(self, color: Dict) -> float:
        """Calculate accessibility score for color"""
        hsv = color['hsv']
        value = hsv[2]  # Brightness
        
        # Higher brightness generally means better accessibility
        accessibility_score = value / 100
        
        return round(accessibility_score, 2)
    
    def _analyze_color_harmony(self, color_palette: List[Dict]) -> Dict[str, Any]:
        """Analyze color harmony in the palette"""
        if len(color_palette) < 2:
            return {'type': 'single', 'score': 0}
        
        # Use the smart color matcher's harmony analysis
        return self.color_matcher._analyze_color_harmony(color_palette)
    
    def _analyze_color_temperature(self, color_palette: List[Dict]) -> Dict[str, Any]:
        """Analyze color temperature"""
        if not color_palette:
            return {'temperature': 'neutral', 'score': 0}
        
        return self.color_matcher._get_color_temperature(color_palette)
    
    def _analyze_color_intensity(self, color_palette: List[Dict]) -> Dict[str, Any]:
        """Analyze color intensity"""
        if not color_palette:
            return {'intensity': 'medium', 'score': 0}
        
        return self.color_matcher._analyze_color_intensity(color_palette)
    
    def _determine_fabric_mood(self, color_palette: List[Dict]) -> Dict[str, Any]:
        """Determine fabric mood"""
        if not color_palette:
            return {'mood': 'neutral', 'confidence': 0}
        
        return self.color_matcher._determine_fabric_mood(color_palette)
    
    def _get_complementary_colors(self, base_colors: List[Dict]) -> List[Dict[str, Any]]:
        """Get complementary colors"""
        if not base_colors:
            return []
        
        return self.color_matcher._get_complementary_colors(base_colors[0])
    
    def _calculate_color_diversity(self, color_palette: List[Dict]) -> float:
        """Calculate color diversity score"""
        if len(color_palette) < 2:
            return 0
        
        # Calculate average distance between colors in LAB space
        total_distance = 0
        pair_count = 0
        
        for i in range(len(color_palette)):
            for j in range(i + 1, len(color_palette)):
                distance = self.color_matcher._calculate_lab_distance(
                    color_palette[i]['lab'],
                    color_palette[j]['lab']
                )
                total_distance += distance
                pair_count += 1
        
        if pair_count == 0:
            return 0
        
        average_distance = total_distance / pair_count
        
        # Normalize to 0-10 scale
        diversity_score = min(10, average_distance / 10)
        
        return round(diversity_score, 2)
    
    def _classify_texture_type(self, texture_features: Dict) -> str:
        """Classify texture type based on features"""
        smoothness = texture_features.get('smoothness', 0.5)
        roughness = texture_features.get('roughness', 0.5)
        regularity = texture_features.get('regularity', 0.5)
        
        if smoothness > 0.7 and regularity > 0.6:
            return 'Smooth'
        elif roughness > 0.7 and regularity < 0.4:
            return 'Rough'
        elif regularity > 0.7:
            return 'Regular'
        elif regularity < 0.3:
            return 'Irregular'
        else:
            return 'Mixed'
    
    def _assess_surface_quality(self, texture_features: Dict) -> str:
        """Assess surface quality based on texture features"""
        smoothness = texture_features.get('smoothness', 0.5)
        regularity = texture_features.get('regularity', 0.5)
        
        quality_score = (smoothness + regularity) / 2
        
        if quality_score > 0.8:
            return 'Excellent'
        elif quality_score > 0.6:
            return 'Good'
        elif quality_score > 0.4:
            return 'Fair'
        else:
            return 'Poor'
    
    def _assess_texture_quality(self, texture_features: Dict) -> str:
        """Assess texture quality"""
        return self._assess_surface_quality(texture_features)
    
    def _assess_pattern_complexity(self, pattern_features: Dict) -> str:
        """Assess pattern complexity"""
        complexity = pattern_features.get('complexity', 'medium')
        return complexity
    
    def _identify_cultural_motifs(self, pattern_features: Dict) -> List[str]:
        """Identify cultural motifs in patterns"""
        # This would typically use more sophisticated pattern recognition
        # For now, return mock cultural motifs based on pattern type
        
        pattern_type = pattern_features.get('type', 'unknown')
        
        cultural_motifs = {
            'geometric': ['Islamic', 'Celtic', 'Native American'],
            'floral': ['Indian', 'Chinese', 'European'],
            'abstract': ['Modern', 'Contemporary', 'Artistic']
        }
        
        return cultural_motifs.get(pattern_type, ['Unknown'])
    
    def _generate_fabric_recommendations(self, analysis_result: Dict) -> List[Dict[str, Any]]:
        """Generate recommendations based on fabric analysis"""
        recommendations = []
        
        # Color recommendations
        if 'color_analysis' in analysis_result:
            color_analysis = analysis_result['color_analysis']
            
            if color_analysis.get('color_temperature', {}).get('temperature') == 'warm':
                recommendations.append({
                    'type': 'color_temperature',
                    'message': 'Warm color palette detected',
                    'suggestion': 'Consider pairing with cool accent colors for balance',
                    'priority': 'medium'
                })
            
            if color_analysis.get('color_intensity', {}).get('intensity') == 'high':
                recommendations.append({
                    'type': 'color_intensity',
                    'message': 'High intensity colors detected',
                    'suggestion': 'Use neutral backgrounds to let colors stand out',
                    'priority': 'high'
                })
        
        # Texture recommendations
        if 'texture_analysis' in analysis_result:
            texture_analysis = analysis_result['texture_analysis']
            
            if texture_analysis.get('texture_type') == 'Rough':
                recommendations.append({
                    'type': 'texture',
                    'message': 'Rough texture detected',
                    'suggestion': 'Consider smooth, contrasting textures for visual interest',
                    'priority': 'medium'
                })
        
        # Quality recommendations
        if 'quality_assessment' in analysis_result:
            quality_assessment = analysis_result['quality_assessment']
            
            if quality_assessment.get('quality_grade') in ['C', 'D']:
                recommendations.append({
                    'type': 'quality',
                    'message': 'Image quality could be improved',
                    'suggestion': 'Use higher resolution images for better analysis results',
                    'priority': 'high'
                })
        
        return recommendations

