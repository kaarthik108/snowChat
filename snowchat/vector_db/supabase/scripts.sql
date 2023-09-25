
CREATE extension vector;

CREATE TABLE ex_documents (
   id UUID PRIMARY KEY,
   content text,
   metadata jsonb,
   embedding vector(1536)
);

-- CREATE INDEX ON ex_documents
-- USING hnsw (embedding vector_ip_ops);

CREATE OR REPLACE FUNCTION match_ex_documents(query_embedding vector(1536), match_count int)
           RETURNS TABLE(
               id UUID,
               content text,
               metadata jsonb,
               -- we return matched vectors to enable maximal marginal relevance searches
               embedding vector(1536),
               similarity float)
           LANGUAGE plpgsql
           AS $$
           # variable_conflict use_column
       BEGIN
           RETURN query
           SELECT
               id,
               content,
               metadata,
               embedding,
               1 -(ex_documents.embedding <=> query_embedding) AS similarity
           FROM
               ex_documents
           ORDER BY
               ex_documents.embedding <=> query_embedding
           LIMIT match_count;
       END;
       $$;
