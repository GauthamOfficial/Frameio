"""
Management command to seed default roles and permissions.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from organizations.models import Organization, OrganizationMember
from users.models import User
from users.permissions import create_role_permissions


class Command(BaseCommand):
    help = 'Seed default roles and permissions for the system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-sample-org',
            action='store_true',
            help='Create a sample organization for testing',
        )
        parser.add_argument(
            '--create-sample-users',
            action='store_true',
            help='Create sample users for testing',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Seeding roles and permissions...')
        
        # Create role permissions
        create_role_permissions()
        self.stdout.write(
            self.style.SUCCESS('✓ Role permissions created')
        )
        
        # Create sample organization if requested
        if options['create_sample_org']:
            self.create_sample_organization()
        
        # Create sample users if requested
        if options['create_sample_users']:
            self.create_sample_users()
        
        self.stdout.write(
            self.style.SUCCESS('✓ Roles and permissions seeded successfully')
        )
    
    def create_sample_organization(self):
        """Create a sample organization for testing."""
        org, created = Organization.objects.get_or_create(
            name='Sample Organization',
            defaults={
                'slug': 'sample-org',
                'description': 'A sample organization for testing',
                'industry': 'Technology',
                'subscription_plan': 'premium',
                'subscription_status': 'active',
                'ai_generations_limit': 1000
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created sample organization: {org.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠ Sample organization already exists: {org.name}')
            )
    
    def create_sample_users(self):
        """Create sample users for testing."""
        sample_users = [
            {
                'username': 'admin@sample.com',
                'email': 'admin@sample.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin'
            },
            {
                'username': 'manager@sample.com',
                'email': 'manager@sample.com',
                'first_name': 'Manager',
                'last_name': 'User',
                'role': 'manager'
            },
            {
                'username': 'designer@sample.com',
                'email': 'designer@sample.com',
                'first_name': 'Designer',
                'last_name': 'User',
                'role': 'designer'
            }
        ]
        
        # Get or create sample organization
        try:
            org = Organization.objects.get(slug='sample-org')
        except Organization.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Sample organization not found. Run with --create-sample-org first.')
            )
            return
        
        for user_data in sample_users:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['username'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_verified': True
                }
            )
            
            if created:
                # Create organization membership
                OrganizationMember.objects.create(
                    organization=org,
                    user=user,
                    role=user_data['role'],
                    can_invite_users=user_data['role'] in ['admin', 'manager'],
                    can_manage_billing=user_data['role'] == 'admin',
                    can_export_data=user_data['role'] in ['admin', 'manager']
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created user: {user.email} ({user_data["role"]})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ User already exists: {user.email}')
                )
