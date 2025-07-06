-- BigCapitalPy Database Initialization
-- This script runs when the PostgreSQL container starts for the first time

-- Create additional databases if needed
-- CREATE DATABASE bigcapitalpy_test;

-- Create extensions that might be useful for accounting software
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create additional users if needed
-- CREATE USER bigcapital_readonly WITH PASSWORD 'readonly123';
-- GRANT CONNECT ON DATABASE bigcapitalpy TO bigcapital_readonly;
-- GRANT USAGE ON SCHEMA public TO bigcapital_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO bigcapital_readonly;

-- Set timezone (adjust as needed)
SET timezone = 'UTC';

-- Create initial schema or tables here if needed
-- Example:
-- CREATE TABLE IF NOT EXISTS app_info (
--     id SERIAL PRIMARY KEY,
--     version VARCHAR(50),
--     initialized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- Insert initial data
-- INSERT INTO app_info (version) VALUES ('1.0.0') ON CONFLICT DO NOTHING;

COMMIT;
