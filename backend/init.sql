-- ===========================================
-- NeuroCron Database Initialization
-- ===========================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- TimescaleDB for time-series analytics
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create schemas for better organization
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA analytics TO neurocron;
GRANT ALL PRIVILEGES ON SCHEMA audit TO neurocron;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'NeuroCron database initialized successfully!';
END $$;

