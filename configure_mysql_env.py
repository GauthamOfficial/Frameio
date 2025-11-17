#!/usr/bin/env python3
"""
Quick script to configure MySQL in backend/.env file
"""

import os
from getpass import getpass

def main():
    env_path = os.path.join('backend', '.env')
    
    print("=" * 70)
    print("MySQL Configuration for Frameio")
    print("=" * 70)
    print("\nEnter your MySQL credentials:")
    
    db_name = input("Database Name [frameio_db]: ").strip() or "frameio_db"
    db_user = input("MySQL User [root]: ").strip() or "root"
    db_password = getpass("MySQL Password: ")
    db_host = input("MySQL Host [localhost]: ").strip() or "localhost"
    db_port = input("MySQL Port [3306]: ").strip() or "3306"
    
    # Read existing .env if it exists
    env_content = ""
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()
    
    # Update or add database configuration
    lines = env_content.split('\n') if env_content else []
    new_lines = []
    skip_db_section = False
    db_section_added = False
    
    for line in lines:
        if line.startswith('# DATABASE CONFIGURATION') or line.startswith('# MySQL Database Configuration'):
            skip_db_section = True
            new_lines.append('# =============================================================================')
            new_lines.append('# DATABASE CONFIGURATION')
            new_lines.append('# =============================================================================')
            new_lines.append('# MySQL Database Configuration')
            new_lines.append(f'DB_NAME={db_name}')
            new_lines.append(f'DB_USER={db_user}')
            new_lines.append(f'DB_PASSWORD={db_password}')
            new_lines.append(f'DB_HOST={db_host}')
            new_lines.append(f'DB_PORT={db_port}')
            new_lines.append('USE_SQLITE_FALLBACK=False')
            db_section_added = True
        elif skip_db_section and (line.startswith('DB_') or line.startswith('USE_SQLITE_FALLBACK')):
            continue
        elif skip_db_section and line.strip() == '':
            continue
        elif skip_db_section:
            skip_db_section = False
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add database section if it wasn't found
    if not db_section_added:
        if new_lines and new_lines[-1].strip():
            new_lines.append('')
        new_lines.append('# =============================================================================')
        new_lines.append('# DATABASE CONFIGURATION')
        new_lines.append('# =============================================================================')
        new_lines.append('# MySQL Database Configuration')
        new_lines.append(f'DB_NAME={db_name}')
        new_lines.append(f'DB_USER={db_user}')
        new_lines.append(f'DB_PASSWORD={db_password}')
        new_lines.append(f'DB_HOST={db_host}')
        new_lines.append(f'DB_PORT={db_port}')
        new_lines.append('USE_SQLITE_FALLBACK=False')
    
    # Ensure backend directory exists
    os.makedirs('backend', exist_ok=True)
    
    # Write .env file
    with open(env_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"\n✓ Configuration saved to {env_path}")
    print("\nNext steps:")
    print("1. Make sure MySQL service is running")
    print("2. Create the database: mysql -u root -p -e 'CREATE DATABASE frameio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;'")
    print("3. Run migrations: cd backend && python manage.py migrate")
    print("4. Start server: cd backend && python manage.py runserver")

if __name__ == "__main__":
    main()

