"""
Arcjet integration service for usage limits
"""
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from organizations.models import Organization

logger = logging.getLogger(__name__)


class ArcjetService:
    """Service for managing Arcjet usage limits"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'ARCJET_API_KEY', None)
        self.base_url = getattr(settings, 'ARCJET_BASE_URL', 'https://api.arcjet.com')
        self.timeout = 30
    
    def check_usage_limit(self, organization: Organization, service_type: str) -> Dict[str, Any]:
        """
        Check if organization has exceeded usage limits for a service
        
        Args:
            organization: Organization instance
            service_type: Type of service (poster_generation, caption_generation, etc.)
            
        Returns:
            Dict with limit check result
        """
        try:
            # TODO: Implement actual Arcjet API integration
            # For now, return mock data based on organization plan
            
            # Mock implementation based on organization plan
            if hasattr(organization, 'plan'):
                plan = organization.plan
            else:
                # Default to free plan
                plan = 'free'
            
            # Mock limits based on plan
            limits = {
                'free': {
                    'poster_generation': {'monthly': 10, 'daily': 2},
                    'caption_generation': {'monthly': 50, 'daily': 10},
                    'scheduled_posts': {'monthly': 20, 'daily': 5}
                },
                'premium': {
                    'poster_generation': {'monthly': 100, 'daily': 20},
                    'caption_generation': {'monthly': 500, 'daily': 100},
                    'scheduled_posts': {'monthly': 200, 'daily': 50}
                },
                'enterprise': {
                    'poster_generation': {'monthly': 1000, 'daily': 200},
                    'caption_generation': {'monthly': 5000, 'daily': 1000},
                    'scheduled_posts': {'monthly': 2000, 'daily': 500}
                }
            }
            
            # Get limits for the service type
            service_limits = limits.get(plan, limits['free']).get(service_type, limits['free']['poster_generation'])
            
            # Mock current usage (in real implementation, this would come from Arcjet API)
            current_usage = {
                'monthly': 5,  # Mock current monthly usage
                'daily': 1     # Mock current daily usage
            }
            
            # Check if limits are exceeded
            monthly_exceeded = current_usage['monthly'] >= service_limits['monthly']
            daily_exceeded = current_usage['daily'] >= service_limits['daily']
            
            result = {
                'success': True,
                'within_limits': not (monthly_exceeded or daily_exceeded),
                'plan': plan,
                'service_type': service_type,
                'limits': service_limits,
                'current_usage': current_usage,
                'monthly_exceeded': monthly_exceeded,
                'daily_exceeded': daily_exceeded,
                'remaining_monthly': max(0, service_limits['monthly'] - current_usage['monthly']),
                'remaining_daily': max(0, service_limits['daily'] - current_usage['daily'])
            }
            
            logger.info(f"Arcjet limit check for {organization.name} ({plan}): {result}")
            return result
            
        except Exception as e:
            logger.error(f"Arcjet limit check failed for {organization.name}: {str(e)}")
            # Return permissive result on error to avoid blocking legitimate requests
            return {
                'success': False,
                'within_limits': True,  # Allow request on error
                'error': str(e),
                'plan': 'unknown',
                'service_type': service_type
            }
    
    def increment_usage(self, organization: Organization, service_type: str) -> bool:
        """
        Increment usage counter for organization
        
        Args:
            organization: Organization instance
            service_type: Type of service
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # TODO: Implement actual Arcjet API integration
            # For now, just log the usage increment
            
            logger.info(f"Incrementing usage for {organization.name}: {service_type}")
            
            # In real implementation, this would make an API call to Arcjet
            # to increment the usage counter
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to increment usage for {organization.name}: {str(e)}")
            return False
    
    def get_usage_stats(self, organization: Organization) -> Dict[str, Any]:
        """
        Get usage statistics for organization
        
        Args:
            organization: Organization instance
            
        Returns:
            Dict with usage statistics
        """
        try:
            # TODO: Implement actual Arcjet API integration
            # For now, return mock data
            
            if hasattr(organization, 'plan'):
                plan = organization.plan
            else:
                plan = 'free'
            
            # Mock usage statistics
            stats = {
                'plan': plan,
                'services': {
                    'poster_generation': {
                        'monthly_used': 5,
                        'monthly_limit': 10 if plan == 'free' else 100,
                        'daily_used': 1,
                        'daily_limit': 2 if plan == 'free' else 20
                    },
                    'caption_generation': {
                        'monthly_used': 15,
                        'monthly_limit': 50 if plan == 'free' else 500,
                        'daily_used': 3,
                        'daily_limit': 10 if plan == 'free' else 100
                    },
                    'scheduled_posts': {
                        'monthly_used': 8,
                        'monthly_limit': 20 if plan == 'free' else 200,
                        'daily_used': 2,
                        'daily_limit': 5 if plan == 'free' else 50
                    }
                },
                'billing_period': {
                    'start_date': '2024-01-01',
                    'end_date': '2024-01-31',
                    'days_remaining': 15
                }
            }
            
            logger.info(f"Retrieved usage stats for {organization.name}: {plan}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get usage stats for {organization.name}: {str(e)}")
            return {
                'error': str(e),
                'plan': 'unknown',
                'services': {}
            }
