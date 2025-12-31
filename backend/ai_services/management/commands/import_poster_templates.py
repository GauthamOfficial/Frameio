"""
Management command to import all poster templates from prompts.txt JSON file.
"""
import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from ai_services.models import PosterTemplate
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Import all poster templates from prompts.txt JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default=None,
            help='Path to prompts.txt file (default: frontend/public/Templates/prompts.txt)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing templates before importing',
        )

    def handle(self, *args, **options):
        # Determine file path
        if options['file']:
            file_path = options['file']
        else:
            # Default path relative to project root
            base_dir = settings.BASE_DIR
            # BASE_DIR is backend/, so go up one level to project root
            project_root = os.path.dirname(base_dir)
            file_path = os.path.join(project_root, 'frontend', 'public', 'Templates', 'prompts.txt')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        
        # Clear existing templates if requested
        if options['clear']:
            count = PosterTemplate.objects.all().count()
            PosterTemplate.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing templates'))
        
        # Get or create a system user for templates
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@framio.com',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        
        # Read and parse JSON file
        self.stdout.write(f'Reading templates from: {file_path}')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {e}'))
            return
        
        self.stdout.write(f'Found {len(templates_data)} templates to import')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for template_data in templates_data:
            try:
                # Extract data
                name = template_data.get('title', '')
                template_id = template_data.get('id', '')
                if not name:
                    self.stdout.write(self.style.WARNING(f'Skipping template with no title: {template_id or "unknown"}'))
                    skipped_count += 1
                    continue
                
                # Use ID or name+subcategory as unique identifier
                # Check if template already exists (by ID if available, otherwise by name+subcategory)
                subcategory = template_data.get('subcategory', '')
                if template_id:
                    existing = PosterTemplate.objects.filter(name=name, subcategory=subcategory).first()
                else:
                    existing = PosterTemplate.objects.filter(name=name, subcategory=subcategory).first()
                
                # Prepare template data
                prompt = template_data.get('caption', '')
                category = template_data.get('category', '')
                subcategory = template_data.get('subcategory', '')
                audience = template_data.get('audience', [])
                offer = template_data.get('offer', 'No Offer')
                image_filename = template_data.get('image', '')
                
                # Determine if featured (mark first few as featured)
                is_featured = created_count < 4
                
                template_fields = {
                    'description': f'{category} - {subcategory}' if category and subcategory else category or subcategory or '',
                    'prompt': prompt,
                    'category': category,
                    'subcategory': subcategory,
                    'audience': audience if isinstance(audience, list) else [],
                    'offer': offer,
                    'is_active': True,
                    'is_featured': is_featured,
                    'organization': None,  # Global templates
                    'created_by': system_user,
                }
                
                if existing:
                    # Update existing template
                    for key, value in template_fields.items():
                        if key != 'organization' and key != 'created_by':  # Don't change these
                            setattr(existing, key, value)
                    existing.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'↻ Updated: {name}'))
                else:
                    # Create new template
                    PosterTemplate.objects.create(
                        name=name,
                        **template_fields
                    )
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Created: {name}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing template {template_data.get("id", "unknown")}: {e}'))
                skipped_count += 1
                continue
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Import complete!'
            f'\n  Created: {created_count} templates'
            f'\n  Updated: {updated_count} templates'
            f'\n  Skipped: {skipped_count} templates'
            f'\n  Total in database: {PosterTemplate.objects.count()} templates'
        ))

