import requests
import time
import logging
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from typing import Dict, List, Optional, Any
import json
import uuid

from .models import PosterGenerationJob, PosterTemplate
from organizations.middleware import get_current_organization

logger = logging.getLogger(__name__)


class NanoBananaPosterService:
    """Service for generating posters using NanoBanana API"""
    
    def __init__(self):
        self.api_key = settings.NANOBANANA_API_KEY
        self.base_url = "https://api.nanobanana.ai"
        self.timeout = 300  # 5 minutes timeout
    
    def generate_poster(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 20,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate poster using NanoBanana API
        
        Args:
            prompt: Text prompt for image generation
            negative_prompt: Negative prompt to avoid certain elements
            width: Image width in pixels
            height: Image height in pixels
            num_images: Number of images to generate
            guidance_scale: How closely to follow the prompt
            num_inference_steps: Number of denoising steps
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generation results
        """
        if not self.api_key:
            raise ValueError("NanoBanana API key not configured")
        
        # Prepare request payload
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_images": num_images,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
            "model": "stable-diffusion-xl",
            "safety_tolerance": 2,
            **kwargs
        }
        
        # Check cache first
        cache_key = self._get_cache_key(payload)
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached result for prompt: {prompt[:50]}...")
            return cached_result
        
        try:
            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Making NanoBanana API request for prompt: {prompt[:50]}...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/v1/generate",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract image URLs
                generated_images = []
                if 'images' in result:
                    generated_images = result['images']
                elif 'data' in result and 'images' in result['data']:
                    generated_images = result['data']['images']
                
                # Calculate cost (approximate)
                cost = self._calculate_cost(num_images, processing_time)
                
                result_data = {
                    'success': True,
                    'generated_images': generated_images,
                    'processing_time': processing_time,
                    'cost': cost,
                    'metadata': result.get('metadata', {}),
                    'cached': False
                }
                
                # Cache the result
                cache.set(cache_key, result_data, timeout=3600)  # Cache for 1 hour
                
                logger.info(f"Successfully generated {len(generated_images)} images in {processing_time:.2f}s")
                return result_data
                
            else:
                error_msg = f"NanoBanana API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'processing_time': processing_time
                }
                
        except requests.exceptions.Timeout:
            error_msg = "NanoBanana API request timed out"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'processing_time': self.timeout
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"NanoBanana API request failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'processing_time': 0
            }
    
    def _get_cache_key(self, payload: Dict[str, Any]) -> str:
        """Generate cache key for request payload"""
        # Create a hash of the payload for caching
        payload_str = json.dumps(payload, sort_keys=True)
        return f"nanobanana_poster:{hash(payload_str)}"
    
    def _calculate_cost(self, num_images: int, processing_time: float) -> float:
        """Calculate approximate cost for generation"""
        # Approximate cost calculation (adjust based on actual NanoBanana pricing)
        base_cost_per_image = 0.01  # $0.01 per image
        time_cost = processing_time * 0.001  # $0.001 per second
        return round((base_cost_per_image * num_images) + time_cost, 4)


class PosterGenerationService:
    """Service for managing poster generation jobs"""
    
    def __init__(self):
        self.nanobanana_service = NanoBananaPosterService()
    
    def create_generation_job(
        self,
        user,
        prompt: str,
        negative_prompt: str = "",
        design_metadata: Dict[str, Any] = None,
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 20,
        template_id: Optional[str] = None
    ) -> PosterGenerationJob:
        """
        Create a new poster generation job
        
        Args:
            user: User creating the job
            prompt: Text prompt for generation
            negative_prompt: Negative prompt
            design_metadata: Additional design metadata
            width: Image width
            height: Image height
            num_images: Number of images to generate
            guidance_scale: Guidance scale
            num_inference_steps: Number of inference steps
            template_id: Optional template ID to use
            
        Returns:
            Created PosterGenerationJob instance
        """
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        # If template is provided, merge its parameters
        if template_id:
            try:
                template = PosterTemplate.objects.get(
                    id=template_id,
                    is_active=True,
                    organization=organization
                )
                # Merge template parameters with provided parameters
                prompt = template.prompt_template.format(**design_metadata or {})
                if template.negative_prompt_template:
                    negative_prompt = template.negative_prompt_template
                
                # Update default parameters
                default_params = template.default_parameters or {}
                width = default_params.get('width', width)
                height = default_params.get('height', height)
                guidance_scale = default_params.get('guidance_scale', guidance_scale)
                num_inference_steps = default_params.get('num_inference_steps', num_inference_steps)
                
                # Increment template usage
                template.increment_usage()
                
            except PosterTemplate.DoesNotExist:
                logger.warning(f"Template {template_id} not found, using provided parameters")
        
        # Create the job
        job = PosterGenerationJob.objects.create(
            organization=organization,
            user=user,
            prompt=prompt,
            negative_prompt=negative_prompt,
            design_metadata=design_metadata or {},
            width=width,
            height=height,
            num_images=num_images,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps
        )
        
        logger.info(f"Created poster generation job {job.id} for user {user.id}")
        return job
    
    def process_generation_job(self, job: PosterGenerationJob) -> bool:
        """
        Process a poster generation job
        
        Args:
            job: PosterGenerationJob instance to process
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Mark job as processing
            job.mark_processing()
            
            # Generate poster using NanoBanana
            result = self.nanobanana_service.generate_poster(
                prompt=job.prompt,
                negative_prompt=job.negative_prompt or "",
                width=job.width,
                height=job.height,
                num_images=job.num_images,
                guidance_scale=job.guidance_scale,
                num_inference_steps=job.num_inference_steps
            )
            
            if result['success']:
                # Mark job as completed
                job.mark_completed(
                    generated_images=result['generated_images'],
                    processing_time=result['processing_time'],
                    cost=result['cost']
                )
                
                # Create history record
                PosterGenerationHistory.objects.create(
                    organization=job.organization,
                    user=job.user,
                    job=job
                )
                
                logger.info(f"Successfully processed poster generation job {job.id}")
                return True
            else:
                # Mark job as failed
                job.mark_failed(result['error'])
                logger.error(f"Failed to process poster generation job {job.id}: {result['error']}")
                return False
                
        except Exception as e:
            # Mark job as failed
            job.mark_failed(str(e))
            logger.error(f"Exception processing poster generation job {job.id}: {str(e)}")
            return False
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get status of a poster generation job
        
        Args:
            job_id: Job ID
            
        Returns:
            Dict containing job status information
        """
        try:
            job = PosterGenerationJob.objects.get(id=job_id)
            
            status_info = {
                'job_id': str(job.id),
                'status': job.status,
                'progress': self._calculate_progress(job),
                'message': self._get_status_message(job),
                'created_at': job.created_at,
                'updated_at': job.updated_at
            }
            
            if job.status == 'completed':
                status_info['generated_images'] = job.generated_images
                status_info['processing_time'] = job.processing_time
                status_info['cost'] = job.cost
            elif job.status == 'failed':
                status_info['error_message'] = job.error_message
            
            return status_info
            
        except PosterGenerationJob.DoesNotExist:
            return {
                'job_id': job_id,
                'status': 'not_found',
                'progress': 0,
                'message': 'Job not found',
                'error_message': 'The specified job ID does not exist'
            }
    
    def _calculate_progress(self, job: PosterGenerationJob) -> int:
        """Calculate progress percentage for a job"""
        if job.status == 'pending':
            return 10
        elif job.status == 'processing':
            return 50
        elif job.status == 'completed':
            return 100
        elif job.status == 'failed':
            return 0
        elif job.status == 'cancelled':
            return 0
        return 0
    
    def _get_status_message(self, job: PosterGenerationJob) -> str:
        """Get human-readable status message for a job"""
        if job.status == 'pending':
            return 'Job is queued for processing'
        elif job.status == 'processing':
            return 'Generating poster images...'
        elif job.status == 'completed':
            return 'Poster generation completed successfully'
        elif job.status == 'failed':
            return 'Poster generation failed'
        elif job.status == 'cancelled':
            return 'Poster generation was cancelled'
        return 'Unknown status'
    
    def cancel_job(self, job_id: str, user) -> bool:
        """
        Cancel a poster generation job
        
        Args:
            job_id: Job ID to cancel
            user: User requesting cancellation
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        try:
            job = PosterGenerationJob.objects.get(id=job_id, user=user)
            
            if job.status in ['pending', 'processing']:
                job.cancel()
                logger.info(f"Cancelled poster generation job {job.id}")
                return True
            else:
                logger.warning(f"Cannot cancel job {job.id} with status {job.status}")
                return False
                
        except PosterGenerationJob.DoesNotExist:
            logger.error(f"Job {job_id} not found for user {user.id}")
            return False
