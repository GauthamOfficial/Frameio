-- ============================================================================
-- Frameio MySQL Database Setup Script
-- ============================================================================
-- This script sets up the MySQL database for Frameio application
-- Run this script as MySQL root user or a user with appropriate privileges
-- 
-- Usage:
--   mysql -u root -p < setup_mysql.sql
-- ============================================================================

-- Create the database with UTF-8 support (utf8mb4 for full Unicode including emojis)
CREATE DATABASE IF NOT EXISTS frameio_db 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Optional: Create a dedicated user for the application (recommended for production)
-- Uncomment and modify the password below if you want to use a dedicated user
-- CREATE USER IF NOT EXISTS 'frameio_user'@'localhost' IDENTIFIED BY 'your_secure_password_here';
-- GRANT ALL PRIVILEGES ON frameio_db.* TO 'frameio_user'@'localhost';

-- For remote database connections (use with caution, only in trusted networks)
-- CREATE USER IF NOT EXISTS 'frameio_user'@'%' IDENTIFIED BY 'your_secure_password_here';
-- GRANT ALL PRIVILEGES ON frameio_db.* TO 'frameio_user'@'%';

-- Apply the privilege changes
FLUSH PRIVILEGES;

-- Select the database
USE frameio_db;

-- Show database info
SELECT 
    'Database created successfully!' AS Status,
    DATABASE() AS 'Current Database',
    @@character_set_database AS 'Character Set',
    @@collation_database AS 'Collation';

-- ============================================================================
-- MySQL Configuration Recommendations for Django
-- ============================================================================
-- Add these to your MySQL configuration file (my.cnf or my.ini):
--
-- [mysqld]
-- # Character set and collation
-- character-set-server = utf8mb4
-- collation-server = utf8mb4_unicode_ci
--
-- # InnoDB settings for better performance
-- innodb_buffer_pool_size = 1G
-- innodb_log_file_size = 256M
-- innodb_flush_log_at_trx_commit = 2
-- innodb_flush_method = O_DIRECT
--
-- # Connection settings
-- max_connections = 500
-- max_allowed_packet = 64M
--
-- # Query cache (for MySQL 5.7 and earlier)
-- query_cache_type = 1
-- query_cache_size = 64M
--
-- [client]
-- default-character-set = utf8mb4
-- ============================================================================

-- ============================================================================
-- Verify the setup
-- ============================================================================
-- Show all databases
SHOW DATABASES;

-- Show user privileges (run this to verify)
-- SHOW GRANTS FOR 'frameio_user'@'localhost';

