"""
Management command to set up user permissions and roles.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from users.permissions import create_role_permissions
from organizations.models import Organization, OrganizationMember
from users.models import User, UserProfile
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set up user permissions and roles for multi-tenant system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-demo-data',
            action='store_true',
            help='Create demo organizations and users for testing',
        )

    def handle(self, *args, **options):
        self.stdout.write('Setting up user permissions and roles...')
        
        # Create role permissions
        try:
            create_role_permissions()
            self.stdout.write(
                self.style.SUCCESS('✓ Role permissions created successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating role permissions: {e}')
            )
            return
        
        # Create demo data if requested
        if options['create_demo_data']:
            self.create_demo_data()
        
        self.stdout.write(
            self.style.SUCCESS('User permissions setup completed successfully!')
        )

    def create_demo_data(self):
        """Create demo organizations and users for testing."""
        self.stdout.write('Creating demo data...')
        
        try:
            # Create demo organizations
            org1, created = Organization.objects.get_or_create(
                slug='demo-company',
                defaults={
                    'name': 'Demo Company',
                    'description': 'A demo organization for testing',
                    'industry': 'Technology',
                    'subscription_plan': 'premium',
                    'subscription_status': 'active',
                    'ai_generations_limit': 1000
                }
            )
            
            org2, created = Organization.objects.get_or_create(
                slug='test-org',
                defaults={
                    'name': 'Test Organization',
                    'description': 'Another demo organization',
                    'industry': 'Design',
                    'subscription_plan': 'basic',
                    'subscription_status': 'active',
                    'ai_generations_limit': 100
                }
            )
            
            # Create demo users
            admin_user, created = User.objects.get_or_create(
                email='admin@demo.com',
                defaults={
                    'username': 'admin',
                    'first_name': 'Admin',
                    'last_name': 'User',
                    'is_verified': True,
                    'is_staff': True,
                }
            )
            
            manager_user, created = User.objects.get_or_create(
                email='manager@demo.com',
                defaults={
                    'username': 'manager',
                    'first_name': 'Manager',
                    'last_name': 'User',
                    'is_verified': True,
                }
            )
            
            designer_user, created = User.objects.get_or_create(
                email='designer@demo.com',
                defaults={
                    'username': 'designer',
                    'first_name': 'Designer',
                    'last_name': 'User',
                    'is_verified': True,
                }
            )
            
            # Create user profiles
            UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={
                    'current_organization': org1,
                    'job_title': 'System Administrator',
                    'department': 'IT',
                    'company_size': '51-200',
                }
            )
            
            UserProfile.objects.get_or_create(
                user=manager_user,
                defaults={
                    'current_organization': org1,
                    'job_title': 'Project Manager',
                    'department': 'Operations',
                    'company_size': '51-200',
                }
            )
            
            UserProfile.objects.get_or_create(
                user=designer_user,
                defaults={
                    'current_organization': org1,
                    'job_title': 'Graphic Designer',
                    'department': 'Creative',
                    'company_size': '51-200',
                }
            )
            
            # Create organization memberships
            OrganizationMember.objects.get_or_create(
                organization=org1,
                user=admin_user,
                defaults={
                    'role': 'admin',
                    'can_invite_users': True,
                    'can_manage_billing': True,
                    'can_export_data': True,
                }
            )
            
            OrganizationMember.objects.get_or_create(
                organization=org1,
                user=manager_user,
                defaults={
                    'role': 'manager',
                    'can_invite_users': True,
                    'can_manage_billing': False,
                    'can_export_data': True,
                }
            )
            
            OrganizationMember.objects.get_or_create(
                organization=org1,
                user=designer_user,
                defaults={
                    'role': 'designer',
                    'can_invite_users': False,
                    'can_manage_billing': False,
                    'can_export_data': False,
                }
            )
            
            # Add admin to second organization as well
            OrganizationMember.objects.get_or_create(
                organization=org2,
                user=admin_user,
                defaults={
                    'role': 'admin',
                    'can_invite_users': True,
                    'can_manage_billing': True,
                    'can_export_data': True,
                }
            )
            
            self.stdout.write(
                self.style.SUCCESS('✓ Demo data created successfully')
            )
            self.stdout.write(f'  - Organizations: {org1.name}, {org2.name}')
            self.stdout.write(f'  - Users: {admin_user.email}, {manager_user.email}, {designer_user.email}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating demo data: {e}')
            )

