"""
AI Services module for handling AI generation requests
"""
import logging
import time
import requests
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.utils import timezone
from .models import AIGenerationRequest, AIUsageQuota

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass


class AIGenerationService:
    """Service class for handling AI generation requests"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 60  # 60 seconds timeout
    
    def process_generation_request(self, request: AIGenerationRequest) -> bool:
        """
        Process an AI generation request
        
        Args:
            request: AIGenerationRequest instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Mark as processing
            request.status = 'processing'
            request.save(update_fields=['status'])
            
            start_time = time.time()
            
            # Get provider configuration
            provider = request.provider
            
            # Route to appropriate AI service
            if provider.name == 'gemini':
                result = self._process_gemini_request(request)
            elif provider.name == 'openai':
                result = self._process_openai_request(request)
            else:
                raise AIServiceError(f"Unsupported provider: {provider.name}")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Mark as completed
            request.mark_completed(
                result_data=result.get('data', {}),
                result_text=result.get('text', '')
            )
            request.processing_time = processing_time
            request.cost = result.get('cost', 0)
            request.save(update_fields=['processing_time', 'cost'])
            
            # Update usage quota
            self._update_usage_quota(request)
            
            logger.info(f"Successfully processed AI request {request.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process AI request {request.id}: {str(e)}")
            request.mark_failed(str(e))
            return False
    
    def _process_text_generation_request(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """Process text generation request"""
        try:
            # AI image generation has been disabled
            request.mark_failed("AI image generation services have been disabled")
            return False
                
        except Exception as e:
            logger.error(f"Text generation error for request {request.id}: {str(e)}")
            request.mark_failed(f"Text generation error: {str(e)}")
            return False
    
    def _process_gemini_request(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """Process Google Gemini API request for text generation"""
        try:
            # AI image generation has been disabled
            request.mark_failed("AI image generation services have been disabled")
            return False
                
        except Exception as e:
            logger.error(f"Gemini API error for request {request.id}: {str(e)}")
            request.mark_failed(f"Gemini API error: {str(e)}")
            return False
    
    def _get_mock_text_result(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """Generate mock text result for development"""
        import time
        timestamp = int(time.time() * 1000)
        
        # Generate mock text based on prompt
        mock_text = f"Generated text response for: {request.prompt[:100]}..."
        
        return {
            "success": True,
            "data": {
                "prompt_used": request.prompt,
                "generation_id": f"mock_{request.id}",
                "model_used": "mock-service",
                "processing_time": 1.5,
                "generated_at": timezone.now().isoformat(),
                "unique_id": f"gen_{timestamp}"
            },
            "text": mock_text,
            "cost": 0.001
        }
    
    def _enhance_text_prompt(self, base_prompt: str, parameters: Dict) -> str:
        """Enhance prompt for text generation"""
        context = parameters.get('context', '')
        style = parameters.get('style', 'professional')
        length = parameters.get('length', 'medium')
        
        enhancements = []
        
        # Add context if provided
        if context:
            enhancements.append(f"Context: {context}")
        
        # Add style guidance
        if style:
            style_map = {
                'professional': 'professional tone, clear and concise',
                'casual': 'casual tone, friendly and approachable',
                'technical': 'technical language, detailed explanations',
                'creative': 'creative writing, engaging and imaginative'
            }
            if style.lower() in style_map:
                enhancements.append(style_map[style.lower()])
        
        # Add length guidance
        if length:
            length_map = {
                'short': 'brief and concise response',
                'medium': 'moderate length, well-developed',
                'long': 'comprehensive and detailed response'
            }
            if length.lower() in length_map:
                enhancements.append(length_map[length.lower()])
        
        # Combine with base prompt
        enhanced = f"{base_prompt}"
        if enhancements:
            enhanced += f". Please provide a {', '.join(enhancements)} response."
        
        return enhanced
    
    def _process_openai_request(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """Process OpenAI GPT request"""
        # Placeholder for OpenAI integration
        # TODO: Implement actual OpenAI GPT API integration
        
        mock_result = {
            'data': {
                'prompt_used': request.prompt,
                'model': 'gpt-4',
                'generation_id': f"openai_{request.id}",
            },
            'text': f"Generated text response for: {request.prompt[:100]}...",
            'cost': 0.02  # Mock cost
        }
        
        return mock_result
    
    def _update_usage_quota(self, request: AIGenerationRequest):
        """Update usage quota for the organization"""
        try:
            # Update monthly quota
            quota, created = AIUsageQuota.objects.get_or_create(
                organization=request.organization,
                provider=request.provider,
                generation_type=request.generation_type,
                quota_type='monthly',
                defaults={
                    'max_requests': 1000,
                    'max_cost': 100.00,
                    'reset_at': timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timezone.timedelta(days=32)
                }
            )
            
            quota.increment_usage(cost=float(request.cost or 0))
            
        except Exception as e:
            logger.error(f"Failed to update usage quota for request {request.id}: {str(e)}")


class AIPromptEngineeringService:
    """Service for AI prompt engineering and optimization"""
    
    @staticmethod
    def enhance_text_prompt(base_prompt: str, context: str = None, 
                          style: str = None, length: str = None) -> str:
        """
        Enhance a basic prompt for text generation
        
        Args:
            base_prompt: Basic prompt text
            context: Additional context for the generation
            style: Writing style (professional, casual, technical, creative)
            length: Desired length (short, medium, long)
            
        Returns:
            Enhanced prompt string
        """
        enhancements = []
        
        # Add context if provided
        if context:
            enhancements.append(f"Context: {context}")
        
        # Add style guidance
        if style:
            style_enhancements = {
                'professional': 'professional tone, clear and concise',
                'casual': 'casual tone, friendly and approachable',
                'technical': 'technical language, detailed explanations',
                'creative': 'creative writing, engaging and imaginative'
            }
            if style.lower() in style_enhancements:
                enhancements.append(style_enhancements[style.lower()])
        
        # Add length guidance
        if length:
            length_enhancements = {
                'short': 'brief and concise response',
                'medium': 'moderate length, well-developed',
                'long': 'comprehensive and detailed response'
            }
            if length.lower() in length_enhancements:
                enhancements.append(length_enhancements[length.lower()])
        
        # Combine base prompt with enhancements
        enhanced_prompt = base_prompt
        if enhancements:
            enhanced_prompt += f". Please provide a {', '.join(enhancements)} response."
        
        return enhanced_prompt
    
    @staticmethod
    def generate_negative_prompt(generation_type: str) -> str:
        """
        Generate appropriate negative prompt based on generation type
        
        Args:
            generation_type: Type of generation (text_generation, content_analysis, etc.)
            
        Returns:
            Negative prompt string
        """
        base_negative = "avoid vague, unclear, or unhelpful responses"
        
        type_specific = {
            'text_generation': "avoid repetitive content, ensure originality",
            'content_analysis': "avoid superficial analysis, provide deep insights",
            'data_processing': "avoid incomplete processing, ensure accuracy",
            'reporting': "avoid unorganized information, ensure clear structure"
        }
        
        if generation_type in type_specific:
            return f"{base_negative}, {type_specific[generation_type]}"
        
        return base_negative


class AIContentAnalysisService:
    """Service for AI-powered content analysis and processing"""
    
    @staticmethod
    def analyze_text_content(text: str) -> Dict[str, Any]:
        """
        Analyze text content for various metrics
        
        Args:
            text: Text content to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        # Placeholder implementation
        # TODO: Implement actual text analysis using NLP
        
        mock_analysis = {
            'word_count': len(text.split()),
            'character_count': len(text),
            'sentiment': 'neutral',
            'readability_score': 75,
            'key_topics': ['topic1', 'topic2', 'topic3'],
            'language': 'en'
        }
        
        return mock_analysis
    
    @staticmethod
    def extract_key_insights(text: str) -> List[str]:
        """
        Extract key insights from text content
        
        Args:
            text: Text content to analyze
            
        Returns:
            List of key insights
        """
        # Placeholder implementation
        # TODO: Implement actual insight extraction
        
        mock_insights = [
            'Key insight 1 based on content analysis',
            'Key insight 2 highlighting important points',
            'Key insight 3 providing actionable information'
        ]
        
        return mock_insights
