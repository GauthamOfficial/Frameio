"""
Mixins for tenant-scoped data access patterns.
"""
from django.db import models
from django.core.exceptions import PermissionDenied
from organizations.middleware import get_current_organization


class TenantScopedModel(models.Model):
    """
    Abstract base model that automatically scopes data to the current organization.
    All models that need tenant isolation should inherit from this.
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='%(class)s_set'
    )
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Automatically set organization if not provided."""
        if not self.organization_id:
            current_org = get_current_organization()
            if current_org:
                self.organization = current_org
            else:
                raise PermissionDenied("No organization context available")
        super().save(*args, **kwargs)


class TenantScopedManager(models.Manager):
    """
    Manager that automatically filters querysets by the current organization.
    """
    
    def get_queryset(self):
        """Filter queryset by current organization."""
        current_org = get_current_organization()
        if current_org:
            return super().get_queryset().filter(organization=current_org)
        return super().get_queryset().none()
    
    def for_organization(self, organization):
        """Get queryset for a specific organization."""
        return super().get_queryset().filter(organization=organization)
    
    def all_organizations(self):
        """Get queryset across all organizations (use with caution)."""
        return super().get_queryset()


class TenantScopedViewSetMixin:
    """
    Mixin for ViewSets that automatically filter by organization.
    """
    
    def get_queryset(self):
        """Filter queryset by current organization."""
        current_org = getattr(self.request, 'organization', None)
        if current_org:
            return super().get_queryset().filter(organization=current_org)
        return super().get_queryset().none()
    
    def perform_create(self, serializer):
        """Automatically set organization when creating objects."""
        current_org = getattr(self.request, 'organization', None)
        if current_org:
            serializer.save(organization=current_org)
        else:
            raise PermissionDenied("No organization context available")
    
    def check_organization_permission(self, obj):
        """Check if user has permission to access this object."""
        current_org = getattr(self.request, 'organization', None)
        if not current_org or obj.organization != current_org:
            raise PermissionDenied("Access denied to this organization's data")
    
    def get_object(self):
        """Override get_object to check organization permission."""
        obj = super().get_object()
        self.check_organization_permission(obj)
        return obj


class TenantScopedSerializerMixin:
    """
    Mixin for serializers that automatically handle organization context.
    """
    
    def create(self, validated_data):
        """Automatically set organization when creating objects."""
        request = self.context.get('request')
        if request and hasattr(request, 'organization'):
            validated_data['organization'] = request.organization
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Ensure organization cannot be changed during update."""
        if 'organization' in validated_data:
            del validated_data['organization']
        return super().update(instance, validated_data)


def get_tenant_queryset(model_class, organization=None):
    """
    Helper function to get a tenant-scoped queryset for any model.
    """
    if organization:
        return model_class.objects.filter(organization=organization)
    
    current_org = get_current_organization()
    if current_org:
        return model_class.objects.filter(organization=current_org)
    
    return model_class.objects.none()


def ensure_tenant_access(user, organization):
    """
    Ensure user has access to the organization.
    """
    from organizations.models import OrganizationMember
    
    if not OrganizationMember.objects.filter(
        user=user,
        organization=organization,
        is_active=True
    ).exists():
        raise PermissionDenied("User does not have access to this organization")
    
    return True

