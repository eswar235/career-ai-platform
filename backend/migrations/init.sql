-- Career Assistant SaaS Database Initialization Script
-- Run this script when initializing the PostgreSQL database

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;

-- Comments
COMMENT ON DATABASE career_ai_db IS 'Career Assistant SaaS Platform Database';

