-- =============================================================================
-- Genesis — PostgreSQL Initialization Script
-- Version: 0.1.0
--
-- This script runs once when the PostgreSQL container is first created.
-- It enables required extensions for the genesis database.
--
-- Extensions:
--   uuid-ossp  — UUID generation (uuid_generate_v4())
--   pgcrypto   — Cryptographic functions (gen_random_uuid(), crypt())
--   citext     — Case-insensitive text type (for email fields)
-- =============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable cryptographic functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enable case-insensitive text (useful for email/username lookups)
CREATE EXTENSION IF NOT EXISTS "citext";

-- =============================================================================
-- Future schema migrations will be applied by the API service via a migration
-- tool (e.g., golang-migrate, Flyway, or Prisma Migrate).
-- This init script only handles one-time extension setup.
-- =============================================================================

-- Log initialization
DO $$
BEGIN
  RAISE NOTICE 'Genesis database initialized successfully.';
  RAISE NOTICE 'Extensions: uuid-ossp, pgcrypto, citext';
END $$;
