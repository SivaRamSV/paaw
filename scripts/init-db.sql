-- PAAW Database Initialization
-- PostgreSQL tables (non-graph data)
-- Graph data is in init-graph.sql

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- CONVERSATIONS (chat history for context windows)
-- =============================================================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,  -- References graph User node
    channel TEXT NOT NULL DEFAULT 'cli',
    messages JSONB NOT NULL DEFAULT '[]',
    summary TEXT,
    token_count INT DEFAULT 0,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_active ON conversations(active) WHERE active = true;
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);

-- =============================================================================
-- ACTIONS (audit log - append only)
-- =============================================================================
CREATE TABLE IF NOT EXISTS actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT,  -- References graph User node
    action_type TEXT NOT NULL,
    input JSONB,
    output JSONB,
    tool_used TEXT,
    model_used TEXT,
    channel TEXT,
    status TEXT DEFAULT 'success' CHECK (status IN ('success', 'failed', 'pending')),
    error TEXT,
    duration_ms INT,
    node_ids TEXT[] DEFAULT '{}',  -- Graph nodes involved
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_actions_user_id ON actions(user_id);
CREATE INDEX IF NOT EXISTS idx_actions_created_at ON actions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_actions_action_type ON actions(action_type);

-- =============================================================================
-- UPDATES (audit trail for mental model changes)
-- =============================================================================
CREATE TABLE IF NOT EXISTS updates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    node_id TEXT NOT NULL,
    field TEXT NOT NULL,
    old_value JSONB,
    new_value JSONB,
    reason TEXT NOT NULL,  -- correction, new_info, status_change, consolidation
    source TEXT NOT NULL,  -- conversation, manual, scheduler
    conversation_id UUID REFERENCES conversations(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_updates_node_id ON updates(node_id);
CREATE INDEX IF NOT EXISTS idx_updates_created_at ON updates(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_updates_reason ON updates(reason);

-- =============================================================================
-- SCHEDULED TASKS
-- =============================================================================
CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT,
    name TEXT NOT NULL,
    description TEXT,
    cron_expression TEXT NOT NULL,
    task_type TEXT NOT NULL,
    task_params JSONB DEFAULT '{}',
    enabled BOOLEAN DEFAULT true,
    last_run TIMESTAMPTZ,
    next_run TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_next_run ON scheduled_tasks(next_run) WHERE enabled = true;

-- =============================================================================
-- FUNCTIONS
-- =============================================================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- GRANTS
-- =============================================================================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO paaw;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO paaw;
