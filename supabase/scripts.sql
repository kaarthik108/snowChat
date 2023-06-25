
CREATE extension vector;

CREATE TABLE documents (
   id UUID PRIMARY KEY,
   content text,
   metadata jsonb,
   embedding vector(1536)
);

CREATE OR REPLACE FUNCTION match_documents(query_embedding vector(1536), match_count int)
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
               1 -(documents.embedding <=> query_embedding) AS similarity
           FROM
               documents
           ORDER BY
               documents.embedding <=> query_embedding
           LIMIT match_count;
       END;
       $$;
