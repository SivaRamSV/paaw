-- PAAW Graph Database Initialization (Apache AGE)
-- Mental Model stored as a graph

-- Enable Apache AGE extension
CREATE EXTENSION IF NOT EXISTS age;

-- Load AGE into the search path
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- =============================================================================
-- CREATE THE MENTAL MODEL GRAPH
-- =============================================================================
SELECT create_graph('mental_model');

-- =============================================================================
-- GRANTS
-- =============================================================================
GRANT USAGE ON SCHEMA ag_catalog TO paaw;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ag_catalog TO paaw;
