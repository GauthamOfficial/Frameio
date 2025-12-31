"""
Management command to seed initial poster templates from hardcoded templates.
"""
from django.core.management.base import BaseCommand
from ai_services.models import PosterTemplate
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed initial poster templates'

    def handle(self, *args, **options):
        self.stdout.write('Seeding poster templates...')
        
        # Get or create a system user for templates
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@framio.com',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        
        templates_data = [
            {
                'name': 'Wedding Frock',
                'description': 'Moody outdoor style for wedding frocks',
                'prompt': "Create a stylish product post featuring a dummy model wearing the uploaded white party frock. Set the background in a moody, misty outdoor atmosphere with soft cinematic lighting. Add the text 'AVAILABLE NOW' and 'Contact Us' in a nice cinematic font, positioned around two-thirds from the top edge of the image. Do not include any other text or contact details.",
                'category': 'Fashion',
                'subcategory': 'Wedding',
                'audience': ['Women'],
                'offer': 'No Offer',
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': "Men's Denim Shirt",
                'description': 'Urban Casual Style for men\'s shirts',
                'prompt': "Create a stylish product post featuring a real man wearing the uploaded shirt. Set the background with cinematic buildings and dramatic lighting for a modern, urban look. Add the text 'AVAILABLE NOW' and 'Contact Us' in a nice cinematic font, positioned around two-thirds from the top edge of the image. Do not include any other text or contact details.",
                'category': 'Fashion',
                'subcategory': 'Casual',
                'audience': ['Men'],
                'offer': 'No Offer',
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': 'Elegant Silk Saree',
                'description': 'Premium Luxurious Style for sarees',
                'prompt': "Create a stylish product post featuring a dummy model wearing the uploaded saree. Set the background in a premium, elegant environment with cinematic lighting for a luxurious look. Add the text 'AVAILABLE NOW' and 'Contact Us' in a nice cinematic font, positioned around two-thirds from the top edge of the image. Do not include any other text or contact details.",
                'category': 'Fashion',
                'subcategory': 'Traditional',
                'audience': ['Women'],
                'offer': 'No Offer',
                'is_active': True,
                'is_featured': True,
            },
            {
                'name': "Men's Casual T-shirt",
                'description': 'Premium dress shop style for casual wear',
                'prompt': "Create a stylish product post featuring a dummy wearing the uploaded men's T-shirt. Set the background at a cinematic premium dress shop. Add the text 'AVAILABLE NOW' and 'Contact Us' in a nice cinematic font, positioned around two-thirds from the top edge of the image. Do not include any other text or contact details.",
                'category': 'Fashion',
                'subcategory': 'Casual',
                'audience': ['Men'],
                'offer': 'No Offer',
                'is_active': True,
                'is_featured': True,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for template_data in templates_data:
            template, created = PosterTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'description': template_data['description'],
                    'prompt': template_data['prompt'],
                    'category': template_data['category'],
                    'subcategory': template_data['subcategory'],
                    'audience': template_data['audience'],
                    'offer': template_data['offer'],
                    'is_active': template_data['is_active'],
                    'is_featured': template_data['is_featured'],
                    'organization': None,  # Global templates
                    'created_by': system_user,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created template: {template.name}'))
            else:
                # Update existing template
                for key, value in template_data.items():
                    if key != 'name':
                        setattr(template, key, value)
                template.save()
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated template: {template.name}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Seeding complete! Created {created_count} templates, updated {updated_count} templates.'
        ))

