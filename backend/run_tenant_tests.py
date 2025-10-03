#!/usr/bin/env python
"""
Test runner for tenant isolation and role-based permissions.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frameio_backend.settings")
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run specific test modules
    test_modules = [
        'users.test_tenant_isolation',
        'organizations.test_organization_management',
        'users.test_permissions',
        'users.test_user_management',
        'organizations.test_tenant_isolation'
    ]
    
    failures = test_runner.run_tests(test_modules)
    
    if failures:
        sys.exit(bool(failures))
    else:
        print("\n✓ All tenant isolation and role-based permission tests passed!")
        sys.exit(0)
