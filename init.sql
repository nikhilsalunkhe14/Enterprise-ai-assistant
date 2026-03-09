-- Initialize PostgreSQL database for Enterprise AI Assistant
-- This script runs when the PostgreSQL container starts

-- Create database if it doesn't exist
-- (PostgreSQL creates it automatically from POSTGRES_DB env var)

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set default permissions
GRANT ALL PRIVILEGES ON DATABASE enterprise_ai TO postgres;
