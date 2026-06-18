-- Creates the dedicated test database alongside the main database.
-- Executed by PostgreSQL on first container start via docker-entrypoint-initdb.d.
CREATE DATABASE aarogya_test;
GRANT ALL PRIVILEGES ON DATABASE aarogya_test TO postgres;
