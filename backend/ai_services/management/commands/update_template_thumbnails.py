"""
Management command to update template thumbnails from existing image files.
"""
import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from ai_services.models import PosterTemplate

class Command(BaseCommand):
    help = 'Update template thumbnails from existing image files in Templates folder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default=None,
            help='Path to prompts.txt file (default: frontend/public/Templates/prompts.txt)',
        )
        parser.add_argument(
            '--templates-dir',
            type=str,
            default=None,
            help='Path to Templates directory with images (default: frontend/public/Templates/)',
        )

    def handle(self, *args, **options):
        # Determine file paths
        base_dir = settings.BASE_DIR
        project_root = os.path.dirname(base_dir)
        
        if options['file']:
            prompts_file = options['file']
        else:
            prompts_file = os.path.join(project_root, 'frontend', 'public', 'Templates', 'prompts.txt')
        
        if options['templates_dir']:
            templates_dir = options['templates_dir']
        else:
            templates_dir = os.path.join(project_root, 'frontend', 'public', 'Templates')
        
        if not os.path.exists(prompts_file):
            self.stdout.write(self.style.ERROR(f'File not found: {prompts_file}'))
            return
        
        if not os.path.exists(templates_dir):
            self.stdout.write(self.style.ERROR(f'Templates directory not found: {templates_dir}'))
            return
        
        # Read templates data
        self.stdout.write(f'Reading templates from: {prompts_file}')
        try:
            with open(prompts_file, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {e}'))
            return
        
        self.stdout.write(f'Found {len(templates_data)} templates to process')
        
        updated_count = 0
        skipped_count = 0
        not_found_count = 0
        
        for template_data in templates_data:
            try:
                name = template_data.get('title', '')
                image_filename = template_data.get('image', '')
                subcategory = template_data.get('subcategory', '')
                
                if not name or not image_filename:
                    skipped_count += 1
                    continue
                
                # Find template by name and subcategory (to handle duplicates)
                template = PosterTemplate.objects.filter(
                    name=name,
                    subcategory=subcategory
                ).first()
                
                if not template:
                    # Try without subcategory if not found
                    template = PosterTemplate.objects.filter(name=name).first()
                
                if not template:
                    self.stdout.write(self.style.WARNING(f'Template not found: {name} ({subcategory})'))
                    not_found_count += 1
                    continue
                
                # Check if template already has a thumbnail
                if template.thumbnail:
                    self.stdout.write(self.style.WARNING(f'Template already has thumbnail, skipping: {name}'))
                    skipped_count += 1
                    continue
                
                # Build image path
                image_path = os.path.join(templates_dir, image_filename)
                
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
                    self.stdout.write(self.style.SUCCESS(f'✓ Updated thumbnail: {name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error updating thumbnail for {name}: {e}'))
                    skipped_count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing template {template_data.get("id", "unknown")}: {e}'))
                skipped_count += 1
                continue
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Thumbnail update complete!'
            f'\n  Updated: {updated_count} templates'
            f'\n  Skipped: {skipped_count} templates (already have thumbnails or errors)'
            f'\n  Not found: {not_found_count} templates (template or image file not found)'
        ))

