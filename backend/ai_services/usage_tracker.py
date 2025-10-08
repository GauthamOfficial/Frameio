"""
Usage Tracking and Billing System for Phase 1 Week 4
Advanced usage quotas, billing integration with Stripe, and usage analytics
"""
import logging
import stripe
from typing import Dict, List, Any, Optional
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum, Count, Avg
from datetime import timedelta, datetime

from .models import AIGenerationRequest, AIUsageQuota, AIProvider
from organizations.models import Organization

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else None


class UsageTracker:
    """Advanced usage tracking and quota management system"""
    
    def __init__(self):
        self.stripe_configured = bool(stripe.api_key)
        if not self.stripe_configured:
            logger.warning("Stripe not configured - billing features will be limited")
    
    def track_usage(self,
                   organization: Organization,
                   user,
                   generation_type: str,
                   cost: float = 0.0,
                   provider_name: str = 'nanobanana') -> Dict[str, Any]:
        """
        Track AI usage and update quotas
        
        Args:
            organization: Organization instance
            user: User instance
            generation_type: Type of AI generation
            cost: Cost of the generation
            provider_name: Name of the AI provider
            
        Returns:
            Dictionary containing tracking results
        """
        try:
            with transaction.atomic():
                # Get or create provider
                provider = self._get_or_create_provider(provider_name)
                
                # Update monthly quota
                monthly_result = self._update_quota(
                    organization=organization,
                    provider=provider,
                    generation_type=generation_type,
                    quota_type='monthly',
                    cost=cost
                )
                
                # Update daily quota
                daily_result = self._update_quota(
                    organization=organization,
                    provider=provider,
                    generation_type=generation_type,
                    quota_type='daily',
                    cost=cost
                )
                
                # Update hourly quota
                hourly_result = self._update_quota(
                    organization=organization,
                    provider=provider,
                    generation_type=generation_type,
                    quota_type='hourly',
                    cost=cost
                )
                
                # Check if any quota is exceeded
                quota_exceeded = (
                    monthly_result['quota_exceeded'] or
                    daily_result['quota_exceeded'] or
                    hourly_result['quota_exceeded']
                )
                
                # Log usage for analytics
                self._log_usage_analytics(organization, user, generation_type, cost, provider)
                
                result = {
                    'success': True,
                    'quota_exceeded': quota_exceeded,
                    'monthly_quota': monthly_result,
                    'daily_quota': daily_result,
                    'hourly_quota': hourly_result,
                    'total_cost': cost,
                    'provider': provider_name,
                    'generation_type': generation_type
                }
                
                # If quota exceeded, trigger billing workflow
                if quota_exceeded:
                    billing_result = self._handle_quota_exceeded(organization, result)
                    result['billing_action'] = billing_result
                
                logger.info(f"Usage tracked for {organization.name}: {generation_type} - ${cost}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to track usage: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'quota_exceeded': False
            }
    
    def check_quota(self,
                   organization: Organization,
                   generation_type: str,
                   provider_name: str = 'nanobanana') -> Dict[str, Any]:
        """
        Check current quota status without updating
        
        Args:
            organization: Organization instance
            generation_type: Type of AI generation
            provider_name: Name of the AI provider
            
        Returns:
            Dictionary containing quota status
        """
        try:
            provider = self._get_or_create_provider(provider_name)
            
            # Check all quota types
            quotas = {}
            for quota_type in ['monthly', 'daily', 'hourly']:
                quota = AIUsageQuota.objects.filter(
                    organization=organization,
                    provider=provider,
                    generation_type=generation_type,
                    quota_type=quota_type
                ).first()
                
                if quota:
                    quotas[quota_type] = {
                        'current_requests': quota.current_requests,
                        'max_requests': quota.max_requests,
                        'current_cost': float(quota.current_cost),
                        'max_cost': float(quota.max_cost),
                        'quota_exceeded': quota.is_quota_exceeded(),
                        'reset_at': quota.reset_at,
                        'usage_percentage': {
                            'requests': (quota.current_requests / quota.max_requests) * 100,
                            'cost': (quota.current_cost / quota.max_cost) * 100
                        }
                    }
                else:
                    # No quota set - unlimited
                    quotas[quota_type] = {
                        'current_requests': 0,
                        'max_requests': float('inf'),
                        'current_cost': 0.0,
                        'max_cost': float('inf'),
                        'quota_exceeded': False,
                        'reset_at': None,
                        'usage_percentage': {
                            'requests': 0,
                            'cost': 0
                        }
                    }
            
            # Overall quota status
            any_exceeded = any(q['quota_exceeded'] for q in quotas.values())
            
            return {
                'success': True,
                'quota_exceeded': any_exceeded,
                'quotas': quotas,
                'organization': organization.name,
                'generation_type': generation_type,
                'provider': provider_name
            }
            
        except Exception as e:
            logger.error(f"Failed to check quota: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'quota_exceeded': False
            }
    
    def get_usage_analytics(self,
                          organization: Organization,
                          days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive usage analytics
        
        Args:
            organization: Organization instance
            days: Number of days to analyze
            
        Returns:
            Dictionary containing usage analytics
        """
        try:
            start_date = timezone.now() - timedelta(days=days)
            
            # Get all requests in date range
            requests = AIGenerationRequest.objects.filter(
                organization=organization,
                created_at__gte=start_date
            )
            
            # Basic metrics
            total_requests = requests.count()
            successful_requests = requests.filter(status='completed').count()
            failed_requests = requests.filter(status='failed').count()
            success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
            
            # Cost metrics
            total_cost = requests.aggregate(total=Sum('cost'))['total'] or 0
            avg_cost_per_request = requests.filter(cost__isnull=False).aggregate(avg=Avg('cost'))['avg'] or 0
            
            # Usage by generation type
            usage_by_type = {}
            for gen_type in AIGenerationRequest.GENERATION_TYPES:
                type_requests = requests.filter(generation_type=gen_type[0])
                usage_by_type[gen_type[0]] = {
                    'count': type_requests.count(),
                    'cost': float(type_requests.aggregate(total=Sum('cost'))['total'] or 0),
                    'success_rate': (type_requests.filter(status='completed').count() / type_requests.count() * 100) if type_requests.count() > 0 else 0
                }
            
            # Usage by provider
            usage_by_provider = {}
            providers = requests.values('provider__name').distinct()
            for provider_data in providers:
                provider_name = provider_data['provider__name']
                provider_requests = requests.filter(provider__name=provider_name)
                usage_by_provider[provider_name] = {
                    'count': provider_requests.count(),
                    'cost': float(provider_requests.aggregate(total=Sum('cost'))['total'] or 0),
                    'success_rate': (provider_requests.filter(status='completed').count() / provider_requests.count() * 100) if provider_requests.count() > 0 else 0
                }
            
            # Daily usage trends
            daily_usage = []
            for i in range(days):
                date = start_date + timedelta(days=i)
                day_requests = requests.filter(created_at__date=date.date())
                daily_usage.append({
                    'date': date.date().isoformat(),
                    'requests': day_requests.count(),
                    'cost': float(day_requests.aggregate(total=Sum('cost'))['total'] or 0),
                    'successful': day_requests.filter(status='completed').count()
                })
            
            # Top users
            top_users = requests.values('user__email', 'user__first_name', 'user__last_name').annotate(
                request_count=Count('id'),
                total_cost=Sum('cost')
            ).order_by('-request_count')[:10]
            
            # Processing time analytics
            processing_times = requests.filter(
                status='completed',
                processing_time__isnull=False
            ).values_list('processing_time', flat=True)
            
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            analytics = {
                'success': True,
                'period_days': days,
                'start_date': start_date.date().isoformat(),
                'end_date': timezone.now().date().isoformat(),
                'summary': {
                    'total_requests': total_requests,
                    'successful_requests': successful_requests,
                    'failed_requests': failed_requests,
                    'success_rate': round(success_rate, 2),
                    'total_cost': float(total_cost),
                    'avg_cost_per_request': float(avg_cost_per_request),
                    'avg_processing_time': round(avg_processing_time, 2)
                },
                'usage_by_type': usage_by_type,
                'usage_by_provider': usage_by_provider,
                'daily_trends': daily_usage,
                'top_users': list(top_users),
                'quota_status': self._get_quota_status(organization)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get usage analytics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_billing_invoice(self,
                             organization: Organization,
                             amount: float,
                             description: str = "AI Usage Charges") -> Dict[str, Any]:
        """
        Create billing invoice using Stripe
        
        Args:
            organization: Organization instance
            amount: Amount to charge
            description: Description of the charge
            
        Returns:
            Dictionary containing invoice creation results
        """
        try:
            if not self.stripe_configured:
                return {
                    'success': False,
                    'error': 'Stripe not configured',
                    'mock_invoice': {
                        'id': f'mock_invoice_{organization.id}_{int(timezone.now().timestamp())}',
                        'amount': amount,
                        'description': description,
                        'status': 'mock'
                    }
                }
            
            # Get or create Stripe customer
            customer = self._get_or_create_stripe_customer(organization)
            
            # Create invoice item
            invoice_item = stripe.InvoiceItem.create(
                customer=customer.id,
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                description=description
            )
            
            # Create invoice
            invoice = stripe.Invoice.create(
                customer=customer.id,
                auto_advance=True,
                collection_method='charge_automatically'
            )
            
            # Finalize and pay invoice
            invoice.finalize_invoice()
            invoice.pay()
            
            result = {
                'success': True,
                'invoice_id': invoice.id,
                'amount': amount,
                'currency': 'usd',
                'status': invoice.status,
                'paid': invoice.paid,
                'description': description,
                'customer_id': customer.id
            }
            
            logger.info(f"Billing invoice created for {organization.name}: ${amount}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create billing invoice: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_quota(self,
                     organization: Organization,
                     provider: AIProvider,
                     generation_type: str,
                     quota_type: str,
                     cost: float) -> Dict[str, Any]:
        """Update specific quota"""
        try:
            # Calculate reset time based on quota type
            now = timezone.now()
            if quota_type == 'monthly':
                reset_at = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32)
            elif quota_type == 'daily':
                reset_at = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            else:  # hourly
                reset_at = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            
            # Get or create quota
            quota, created = AIUsageQuota.objects.get_or_create(
                organization=organization,
                provider=provider,
                generation_type=generation_type,
                quota_type=quota_type,
                defaults={
                    'max_requests': self._get_default_max_requests(quota_type),
                    'max_cost': self._get_default_max_cost(quota_type),
                    'reset_at': reset_at
                }
            )
            
            # Check if quota needs reset
            if now >= quota.reset_at:
                quota.reset_usage()
                quota.reset_at = reset_at
                quota.save()
            
            # Increment usage
            quota.increment_usage(cost=cost)
            
            return {
                'quota_exceeded': quota.is_quota_exceeded(),
                'current_requests': quota.current_requests,
                'max_requests': quota.max_requests,
                'current_cost': float(quota.current_cost),
                'max_cost': float(quota.max_cost),
                'reset_at': quota.reset_at,
                'usage_percentage': {
                    'requests': (quota.current_requests / quota.max_requests) * 100,
                    'cost': (quota.current_cost / quota.max_cost) * 100
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to update quota: {str(e)}")
            return {
                'quota_exceeded': False,
                'error': str(e)
            }
    
    def _get_or_create_provider(self, provider_name: str) -> AIProvider:
        """Get or create AI provider"""
        provider, created = AIProvider.objects.get_or_create(
            name=provider_name,
            defaults={
                'api_key': '',
                'api_url': '',
                'is_active': True,
                'rate_limit_per_minute': 60,
                'rate_limit_per_hour': 1000
            }
        )
        return provider
    
    def _get_default_max_requests(self, quota_type: str) -> int:
        """Get default max requests based on quota type"""
        defaults = {
            'monthly': 1000,
            'daily': 100,
            'hourly': 20
        }
        return defaults.get(quota_type, 100)
    
    def _get_default_max_cost(self, quota_type: str) -> Decimal:
        """Get default max cost based on quota type"""
        defaults = {
            'monthly': Decimal('100.00'),
            'daily': Decimal('10.00'),
            'hourly': Decimal('2.00')
        }
        return defaults.get(quota_type, Decimal('10.00'))
    
    def _log_usage_analytics(self,
                           organization: Organization,
                           user,
                           generation_type: str,
                           cost: float,
                           provider: AIProvider):
        """Log usage for analytics (could be extended to external analytics service)"""
        try:
            # This could be extended to send data to external analytics services
            # For now, we just log the usage
            logger.info(f"Usage logged: {organization.name} - {user.email} - {generation_type} - ${cost} - {provider.name}")
            
        except Exception as e:
            logger.error(f"Failed to log usage analytics: {str(e)}")
    
    def _handle_quota_exceeded(self, organization: Organization, usage_result: Dict) -> Dict[str, Any]:
        """Handle quota exceeded scenario"""
        try:
            # Check if organization has billing enabled
            billing_enabled = getattr(organization, 'billing_enabled', False)
            
            if billing_enabled and self.stripe_configured:
                # Create automatic invoice for overage
                overage_amount = self._calculate_overage_amount(organization, usage_result)
                
                if overage_amount > 0:
                    invoice_result = self.create_billing_invoice(
                        organization=organization,
                        amount=overage_amount,
                        description=f"AI Usage Overage - {usage_result['generation_type']}"
                    )
                    
                    return {
                        'action': 'billing_invoice_created',
                        'overage_amount': overage_amount,
                        'invoice_result': invoice_result
                    }
            
            # If no billing, just log the overage
            return {
                'action': 'quota_exceeded_logged',
                'message': 'Quota exceeded - billing not enabled',
                'overage_amount': 0
            }
            
        except Exception as e:
            logger.error(f"Failed to handle quota exceeded: {str(e)}")
            return {
                'action': 'error',
                'error': str(e)
            }
    
    def _calculate_overage_amount(self, organization: Organization, usage_result: Dict) -> float:
        """Calculate overage amount for billing"""
        try:
            # Simple overage calculation - could be more sophisticated
            monthly_quota = usage_result.get('monthly_quota', {})
            current_cost = monthly_quota.get('current_cost', 0)
            max_cost = monthly_quota.get('max_cost', 0)
            
            overage = max(0, current_cost - max_cost)
            return overage
            
        except Exception as e:
            logger.error(f"Failed to calculate overage amount: {str(e)}")
            return 0.0
    
    def _get_quota_status(self, organization: Organization) -> Dict[str, Any]:
        """Get current quota status for all generation types"""
        try:
            quotas = AIUsageQuota.objects.filter(
                organization=organization,
                quota_type='monthly'
            ).select_related('provider')
            
            quota_status = {}
            for quota in quotas:
                key = f"{quota.provider.name}_{quota.generation_type}"
                quota_status[key] = {
                    'provider': quota.provider.name,
                    'generation_type': quota.generation_type,
                    'current_requests': quota.current_requests,
                    'max_requests': quota.max_requests,
                    'current_cost': float(quota.current_cost),
                    'max_cost': float(quota.max_cost),
                    'quota_exceeded': quota.is_quota_exceeded(),
                    'reset_at': quota.reset_at
                }
            
            return quota_status
            
        except Exception as e:
            logger.error(f"Failed to get quota status: {str(e)}")
            return {}
    
    def _get_or_create_stripe_customer(self, organization: Organization):
        """Get or create Stripe customer for organization"""
        try:
            # Check if organization has Stripe customer ID
            customer_id = getattr(organization, 'stripe_customer_id', None)
            
            if customer_id:
                try:
                    customer = stripe.Customer.retrieve(customer_id)
                    return customer
                except stripe.error.InvalidRequestError:
                    # Customer doesn't exist, create new one
                    pass
            
            # Create new Stripe customer
            customer = stripe.Customer.create(
                name=organization.name,
                email=getattr(organization, 'billing_email', None),
                metadata={
                    'organization_id': str(organization.id),
                    'organization_name': organization.name
                }
            )
            
            # Save customer ID to organization (would need to add this field)
            # organization.stripe_customer_id = customer.id
            # organization.save()
            
            return customer
            
        except Exception as e:
            logger.error(f"Failed to get or create Stripe customer: {str(e)}")
            raise


class BillingManager:
    """Advanced billing management system"""
    
    def __init__(self):
        self.usage_tracker = UsageTracker()
    
    def setup_organization_billing(self, organization: Organization, billing_info: Dict[str, Any]) -> Dict[str, Any]:
        """Setup billing for organization"""
        try:
            if not self.usage_tracker.stripe_configured:
                return {
                    'success': False,
                    'error': 'Stripe not configured'
                }
            
            # Create Stripe customer
            customer = stripe.Customer.create(
                name=organization.name,
                email=billing_info.get('email'),
                phone=billing_info.get('phone'),
                address={
                    'line1': billing_info.get('address_line1'),
                    'line2': billing_info.get('address_line2'),
                    'city': billing_info.get('city'),
                    'state': billing_info.get('state'),
                    'postal_code': billing_info.get('postal_code'),
                    'country': billing_info.get('country', 'US')
                },
                metadata={
                    'organization_id': str(organization.id),
                    'organization_name': organization.name
                }
            )
            
            # Create payment method if provided
            payment_method = None
            if billing_info.get('payment_method_id'):
                payment_method = stripe.PaymentMethod.attach(
                    billing_info['payment_method_id'],
                    customer=customer.id
                )
                
                # Set as default payment method
                stripe.Customer.modify(
                    customer.id,
                    invoice_settings={
                        'default_payment_method': payment_method.id
                    }
                )
            
            result = {
                'success': True,
                'customer_id': customer.id,
                'payment_method_id': payment_method.id if payment_method else None,
                'message': 'Billing setup completed successfully'
            }
            
            logger.info(f"Billing setup completed for {organization.name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to setup organization billing: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_billing_summary(self, organization: Organization) -> Dict[str, Any]:
        """Get billing summary for organization"""
        try:
            if not self.usage_tracker.stripe_configured:
                return {
                    'success': False,
                    'error': 'Stripe not configured'
                }
            
            # Get usage analytics
            usage_analytics = self.usage_tracker.get_usage_analytics(organization, 30)
            
            # Get quota status
            quota_status = self.usage_tracker._get_quota_status(organization)
            
            # Calculate projected monthly cost
            current_month_cost = usage_analytics.get('summary', {}).get('total_cost', 0)
            days_in_month = 30
            days_remaining = days_in_month - (timezone.now().day - 1)
            projected_cost = (current_month_cost / (days_in_month - days_remaining)) * days_in_month if days_remaining > 0 else current_month_cost
            
            summary = {
                'success': True,
                'organization': organization.name,
                'current_month': {
                    'cost': current_month_cost,
                    'requests': usage_analytics.get('summary', {}).get('total_requests', 0),
                    'projected_cost': round(projected_cost, 2)
                },
                'quota_status': quota_status,
                'billing_enabled': getattr(organization, 'billing_enabled', False),
                'last_updated': timezone.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get billing summary: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

