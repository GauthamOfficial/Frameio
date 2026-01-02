"""
Management command to add thumbnails for the 4 seed templates.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from ai_services.models import PosterTemplate

class Command(BaseCommand):
    help = 'Add thumbnails for seed templates (Wedding Frock, Men\'s Denim Shirt, Elegant Silk Saree, Men\'s Casual T-shirt)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update thumbnails even if they already exist',
        )

    def handle(self, *args, **options):
        force_update = options.get('force', False)
        # Map template names to image filenames
        template_image_map = {
            'Wedding Frock': 'Wedding Frock.jpg',
            "Men's Denim Shirt": 'Men Shirt.png',
            'Elegant Silk Saree': 'Saaree.jpg',
            "Men's Casual T-shirt": 'T_shirt.png',
        }
        
        # Get project root and image directory
        base_dir = settings.BASE_DIR
        project_root = os.path.dirname(base_dir)
        images_dir = os.path.join(project_root, 'frontend', 'public')
        
        if not os.path.exists(images_dir):
            self.stdout.write(self.style.ERROR(f'Images directory not found: {images_dir}'))
            return
        
        updated_count = 0
        skipped_count = 0
        not_found_count = 0
        
        for template_name, image_filename in template_image_map.items():
            try:
                self.stdout.write(f'\nProcessing: {template_name}')
                
                # Find template by name (try exact match first, then case-insensitive)
                template = PosterTemplate.objects.filter(name=template_name).first()
                if not template:
                    # Try case-insensitive search
                    template = PosterTemplate.objects.filter(name__iexact=template_name).first()
                    if template:
                        self.stdout.write(self.style.WARNING(f'  Found template with different case: "{template.name}"'))
                
                if not template:
                    # List similar template names
                    similar = PosterTemplate.objects.filter(name__icontains=template_name.split()[0]).values_list('name', flat=True)[:5]
                    self.stdout.write(self.style.ERROR(f'  ✗ Template not found: {template_name}'))
                    if similar:
                        self.stdout.write(self.style.WARNING(f'  Similar templates found: {list(similar)}'))
                    not_found_count += 1
                    continue
                
                self.stdout.write(self.style.SUCCESS(f'  ✓ Template found: {template.name} (ID: {template.id})'))
                
                # Check if template already has a thumbnail
                if template.thumbnail and not force_update:
                    self.stdout.write(self.style.WARNING(f'  Template already has thumbnail, skipping (use --force to update)'))
                    skipped_count += 1
                    continue
                
                if template.thumbnail and force_update:
                    self.stdout.write(self.style.WARNING(f'  Template has thumbnail, will force update'))
                
                # Build image path
                image_path = os.path.join(images_dir, image_filename)
                self.stdout.write(f'  Looking for image: {image_path}')
                
                if not os.path.exists(image_path):
                    # List files in the directory to help debug
                    if os.path.exists(images_dir):
                        files = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
                        similar_files = [f for f in files if any(word.lower() in f.lower() for word in template_name.split())]
                        self.stdout.write(self.style.ERROR(f'  ✗ Image file not found: {image_path}'))
                        if similar_files:
                            self.stdout.write(self.style.WARNING(f'  Similar files in directory: {similar_files[:5]}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'  ✗ Images directory does not exist: {images_dir}'))
                    not_found_count += 1
                    continue
                
                self.stdout.write(self.style.SUCCESS(f'  ✓ Image file found'))
                
                # Open and save the image
                try:
                    with open(image_path, 'rb') as f:
                        django_file = File(f, name=image_filename)
                        template.thumbnail.save(image_filename, django_file, save=True)
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Updated thumbnail: {template_name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error updating thumbnail for {template_name}: {e}'))
                    skipped_count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing template {template_name}: {e}'))
                skipped_count += 1
                continue
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Thumbnail update complete!'
            f'\n  Updated: {updated_count} templates'
            f'\n  Skipped: {skipped_count} templates (already have thumbnails or errors)'
            f'\n  Not found: {not_found_count} templates (template or image file not found)'
        ))

