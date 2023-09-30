CREATE extension vector;
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    content text,
    metadata jsonb,
    embedding vector(1536)
);
CREATE INDEX ON documents USING hnsw (embedding vector_ip_ops);
CREATE FUNCTION v_match_documents (
    query_embedding vector (1536),
    filter jsonb default '{}'
) RETURNS table (
    id uuid,
    content text,
    metadata jsonb,
    similarity float
) language plpgsql as $$ #variable_conflict use_column
begin return query
select id,
    content,
    metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
from documents
where metadata @> filter
order by documents.embedding <=> query_embedding;
END;
$$;