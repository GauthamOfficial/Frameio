#!/usr/bin/env python3
"""Create MySQL database for Frameio"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join('backend', '.env'))

db_name = os.getenv('DB_NAME', 'frameio_db')
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', '')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = int(os.getenv('DB_PORT', '3306'))

print(f"Creating database '{db_name}'...")

try:
    # Try mysql-connector-python first
    try:
        import mysql.connector
        from mysql.connector import Error
        
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {db_name} "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            print(f"✓ Database '{db_name}' created successfully")
            
            cursor.execute(f"USE {db_name}")
            cursor.execute(
                "SELECT DATABASE() as db, "
                "@@character_set_database as charset, "
                "@@collation_database as collation"
            )
            result = cursor.fetchone()
            print(f"  - Database: {result[0]}")
            print(f"  - Character Set: {result[1]}")
            print(f"  - Collation: {result[2]}")
            
            cursor.close()
            connection.close()
            exit(0)
    except ImportError:
        # Fall back to MySQLdb (mysqlclient)
        import MySQLdb
        
        connection = MySQLdb.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            passwd=db_password
        )
        
        cursor = connection.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {db_name} "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        print(f"✓ Database '{db_name}' created successfully")
        
        cursor.execute(f"USE {db_name}")
        cursor.execute(
            "SELECT DATABASE() as db, "
            "@@character_set_database as charset, "
            "@@collation_database as collation"
        )
        result = cursor.fetchone()
        print(f"  - Database: {result[0]}")
        print(f"  - Character Set: {result[1]}")
        print(f"  - Collation: {result[2]}")
        
        cursor.close()
        connection.close()
        exit(0)
        
except Exception as e:
    print(f"✗ Error: {e}")
    print(f"  Error type: {type(e).__name__}")
    exit(1)

