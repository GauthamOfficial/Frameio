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

    def handle(self, *args, **options):
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
                # Find template by name
                template = PosterTemplate.objects.filter(name=template_name).first()
                
                if not template:
                    self.stdout.write(self.style.WARNING(f'Template not found: {template_name}'))
                    not_found_count += 1
                    continue
                
                # Check if template already has a thumbnail
                if template.thumbnail:
                    self.stdout.write(self.style.WARNING(f'Template already has thumbnail, skipping: {template_name}'))
                    skipped_count += 1
                    continue
                
                # Build image path
                image_path = os.path.join(images_dir, image_filename)
                
                if not os.path.exists(image_path):
                    self.stdout.write(self.style.WARNING(f'Image file not found: {image_path}'))
                    not_found_count += 1
                    continue
                
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

