from django.db import models
from organizations.mixins import TenantScopedModel, TenantScopedManager
import uuid


class Design(TenantScopedModel):
    """
    Design model with tenant isolation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    design_type = models.CharField(
        max_length=50,
        choices=[
            ('poster', 'Poster'),
            ('banner', 'Banner'),
            ('flyer', 'Flyer'),
            ('business_card', 'Business Card'),
            ('logo', 'Logo'),
            ('other', 'Other'),
        ],
        default='poster'
    )
    
    # Design files
    image = models.ImageField(upload_to='designs/images/', blank=True, null=True)
    ai_prompt = models.TextField(blank=True, null=True)
    ai_generated = models.BooleanField(default=False)
    
    # Status and visibility
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ],
        default='draft'
    )
    is_public = models.BooleanField(default=False)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='created_designs'
    )
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'designs'
        verbose_name = 'Design'
        verbose_name_plural = 'Designs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'created_by']),
            models.Index(fields=['organization', 'design_type']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_ai_generated(self):
        return self.ai_generated
    
    def can_be_edited_by(self, user):
        """Check if user can edit this design."""
        from organizations.models import OrganizationMember
        
        try:
            membership = OrganizationMember.objects.get(
                user=user,
                organization=self.organization,
                is_active=True
            )
            # Admin and Manager can edit any design, Designer can edit their own
            return membership.role in ['admin', 'manager'] or self.created_by == user
        except OrganizationMember.DoesNotExist:
            return False


class DesignTemplate(TenantScopedModel):
    """
    Design template model with tenant isolation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    template_type = models.CharField(
        max_length=50,
        choices=[
            ('poster', 'Poster'),
            ('banner', 'Banner'),
            ('flyer', 'Flyer'),
            ('business_card', 'Business Card'),
            ('logo', 'Logo'),
            ('other', 'Other'),
        ]
    )
    
    # Template files
    preview_image = models.ImageField(upload_to='templates/previews/')
    template_file = models.FileField(upload_to='templates/files/')
    
    # Template settings
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='created_templates'
    )
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'design_templates'
        verbose_name = 'Design Template'
        verbose_name_plural = 'Design Templates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'template_type']),
            models.Index(fields=['organization', 'is_public']),
        ]
    
    def __str__(self):
        return self.name


class DesignCatalog(TenantScopedModel):
    """
    Design catalog model with tenant isolation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Catalog settings
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Design relationships
    designs = models.ManyToManyField(
        Design,
        through='DesignCatalogItem',
        related_name='catalogs'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='created_catalogs'
    )
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'design_catalogs'
        verbose_name = 'Design Catalog'
        verbose_name_plural = 'Design Catalogs'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class DesignCatalogItem(models.Model):
    """
    Through model for Design and DesignCatalog relationship.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    catalog = models.ForeignKey(DesignCatalog, on_delete=models.CASCADE)
    design = models.ForeignKey(Design, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='catalog_items_added'
    )
    
    class Meta:
        db_table = 'design_catalog_items'
        unique_together = ['catalog', 'design']
        ordering = ['order', '-added_at']
    
    def __str__(self):
        return f"{self.design.title} in {self.catalog.name}"
