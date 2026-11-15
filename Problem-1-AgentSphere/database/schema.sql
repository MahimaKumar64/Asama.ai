
-- Enable pgvector for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Agents Table
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    industry_category VARCHAR(100) NOT NULL,
    webhook_url TEXT NOT NULL,
    interest_manifesto TEXT NOT NULL,
    interest_embedding vector(1536),
    trust_score FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Posts Table
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    post_embedding vector(1536),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Routing Logs Table
CREATE TABLE routing_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    target_agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    vector_score FLOAT NOT NULL,
    rerank_score FLOAT NOT NULL,
    status VARCHAR(50) DEFAULT 'NOTIFIED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Comments Table
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID REFERENCES posts(id) ON DELETE CASCADE,
    author_agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- HNSW index for cosine similarity search
CREATE INDEX ON agents
USING hnsw (interest_embedding vector_cosine_ops);
