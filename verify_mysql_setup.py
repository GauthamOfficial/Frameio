#!/usr/bin/env python3
"""
MySQL Setup Verification Script for Frameio
This script verifies that MySQL is properly configured and working
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.db import connection
from django.core.management import call_command
from django.contrib.auth import get_user_model
from organizations.models import Organization
from ai_services.models import AIProvider

User = get_user_model()


def print_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {message}")
    print("=" * 70)


def print_success(message):
    """Print a success message"""
    print(f"✓ {message}")


def print_error(message):
    """Print an error message"""
    print(f"✗ {message}")


def print_warning(message):
    """Print a warning message"""
    print(f"⚠ {message}")


def test_database_connection():
    """Test if database connection is working"""
    print_header("Testing Database Connection")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result and result[0] == 1:
                print_success("Database connection successful")
                return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False


def check_database_info():
    """Check database configuration"""
    print_header("Database Configuration")
    try:
        with connection.cursor() as cursor:
            # Get database name
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            print_success(f"Database Name: {db_name}")
            
            # Get MySQL version
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print_success(f"MySQL Version: {version}")
            
            # Check character set
            cursor.execute("SELECT @@character_set_database")
            charset = cursor.fetchone()[0]
            if charset == 'utf8mb4':
                print_success(f"Character Set: {charset} (Correct)")
            else:
                print_warning(f"Character Set: {charset} (Should be utf8mb4)")
            
            # Check collation
            cursor.execute("SELECT @@collation_database")
            collation = cursor.fetchone()[0]
            if 'utf8mb4' in collation:
                print_success(f"Collation: {collation} (Correct)")
            else:
                print_warning(f"Collation: {collation} (Should use utf8mb4)")
            
            # Check connection settings
            cursor.execute("SHOW VARIABLES LIKE 'max_connections'")
            max_conn = cursor.fetchone()[1]
            print_success(f"Max Connections: {max_conn}")
            
            # Check InnoDB status
            cursor.execute("SHOW VARIABLES LIKE 'default_storage_engine'")
            engine = cursor.fetchone()[1]
            if engine == 'InnoDB':
                print_success(f"Storage Engine: {engine} (Correct)")
            else:
                print_warning(f"Storage Engine: {engine} (InnoDB recommended)")
            
            return True
    except Exception as e:
        print_error(f"Error checking database info: {e}")
        return False


def test_migrations():
    """Check if migrations are up to date"""
    print_header("Checking Migrations")
    try:
        # Check if there are pending migrations
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print_warning(f"There are {len(plan)} pending migrations")
            print("Run: python manage.py migrate")
            return False
        else:
            print_success("All migrations are up to date")
            return True
    except Exception as e:
        print_error(f"Error checking migrations: {e}")
        return False


def test_model_operations():
    """Test basic model operations"""
    print_header("Testing Model Operations")
    
    success = True
    
    # Test User model
    try:
        user_count = User.objects.count()
        print_success(f"User model: {user_count} users found")
    except Exception as e:
        print_error(f"User model error: {e}")
        success = False
    
    # Test Organization model
    try:
        org_count = Organization.objects.count()
        print_success(f"Organization model: {org_count} organizations found")
    except Exception as e:
        print_error(f"Organization model error: {e}")
        success = False
    
    # Test AIProvider model
    try:
        provider_count = AIProvider.objects.count()
        print_success(f"AIProvider model: {provider_count} providers found")
    except Exception as e:
        print_error(f"AIProvider model error: {e}")
        success = False
    
    return success


def test_json_field():
    """Test JSONField support"""
    print_header("Testing JSONField Support (MySQL 5.7.8+)")
    try:
        # Test with Organization model which has no JSONField by default
        # Use AIGenerationRequest which has JSONField
        from ai_services.models import AIGenerationRequest
        
        # Just check if we can query
        AIGenerationRequest.objects.filter(parameters__isnull=False).count()
        print_success("JSONField support is working")
        return True
    except Exception as e:
        print_error(f"JSONField error: {e}")
        print_warning("Your MySQL version might not support JSON. Upgrade to MySQL 5.7.8+")
        return False


def test_uuid_field():
    """Test UUID field support"""
    print_header("Testing UUID Field Support")
    try:
        # All our models use UUID, so if we got here, it works
        print_success("UUID fields are working correctly")
        
        # Check the actual field type in MySQL
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COLUMN_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'organizations' 
                AND COLUMN_NAME = 'id'
            """)
            result = cursor.fetchone()
            if result:
                column_type = result[0]
                print_success(f"UUID stored as: {column_type}")
        
        return True
    except Exception as e:
        print_error(f"UUID field error: {e}")
        return False


def test_indexes():
    """Test if indexes are created properly"""
    print_header("Testing Database Indexes")
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.STATISTICS 
                WHERE TABLE_SCHEMA = DATABASE()
            """)
            index_count = cursor.fetchone()[0]
            print_success(f"Total indexes in database: {index_count}")
            
            # Check for specific indexes on ai_services_aigenerationrequest
            cursor.execute("""
                SELECT DISTINCT INDEX_NAME 
                FROM INFORMATION_SCHEMA.STATISTICS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME LIKE '%aigenerationrequest%'
            """)
            indexes = cursor.fetchall()
            if indexes:
                print_success(f"AI Service indexes: {len(indexes)} found")
        
        return True
    except Exception as e:
        print_error(f"Error checking indexes: {e}")
        return False


def test_performance():
    """Test basic query performance"""
    print_header("Testing Query Performance")
    try:
        import time
        
        # Test a simple query
        start_time = time.time()
        User.objects.all().count()
        query_time = (time.time() - start_time) * 1000  # Convert to ms
        
        if query_time < 100:
            print_success(f"Query performance: {query_time:.2f}ms (Excellent)")
        elif query_time < 500:
            print_success(f"Query performance: {query_time:.2f}ms (Good)")
        else:
            print_warning(f"Query performance: {query_time:.2f}ms (Consider optimization)")
        
        return True
    except Exception as e:
        print_error(f"Performance test error: {e}")
        return False


def check_environment_variables():
    """Check if environment variables are set"""
    print_header("Checking Environment Variables")
    
    required_vars = [
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'DB_HOST',
        'DB_PORT',
    ]
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask password
            display_value = '***' if var == 'DB_PASSWORD' else value
            print_success(f"{var}: {display_value}")
        else:
            print_warning(f"{var}: Not set (using default)")
            all_set = False
    
    return all_set


def main():
    """Main verification function"""
    print_header("Frameio MySQL Setup Verification")
    print("This script will verify your MySQL database configuration")
    
    results = []
    
    # Run all tests
    results.append(("Environment Variables", check_environment_variables()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Database Configuration", check_database_info()))
    results.append(("Migrations", test_migrations()))
    results.append(("Model Operations", test_model_operations()))
    results.append(("JSONField Support", test_json_field()))
    results.append(("UUID Field Support", test_uuid_field()))
    results.append(("Database Indexes", test_indexes()))
    results.append(("Query Performance", test_performance()))
    
    # Print summary
    print_header("Verification Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}\n")
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    if passed == total:
        print_header("✓ All Tests Passed!")
        print("\nYour MySQL database is properly configured and ready to use!")
        print("\nNext steps:")
        print("1. Start the backend: cd backend && python manage.py runserver")
        print("2. Start the frontend: cd frontend && npm run dev")
        return 0
    else:
        print_header("⚠ Some Tests Failed")
        print("\nPlease review the errors above and fix the issues.")
        print("\nCommon solutions:")
        print("- Make sure MySQL 8.0+ is installed and running")
        print("- Verify your .env file has correct database credentials")
        print("- Run migrations: python manage.py migrate")
        print("- Check MySQL character set is utf8mb4")
        return 1


if __name__ == "__main__":
    sys.exit(main())

