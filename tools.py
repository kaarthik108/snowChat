import streamlit as st
from supabase.client import Client, create_client
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools import DuckDuckGoSearchRun
from utils.snow_connect import SnowflakeConnection

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_SERVICE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)

embeddings = OpenAIEmbeddings(
    openai_api_key=st.secrets["OPENAI_API_KEY"], model="text-embedding-ada-002"
)
vectorstore = SupabaseVectorStore(
    embedding=embeddings,
    client=supabase,
    table_name="documents",
    query_name="v_match_documents",
)

retriever_tool = create_retriever_tool(
    vectorstore.as_retriever(),
    name="Database_Schema",
    description="Search for database schema details",
)

search = DuckDuckGoSearchRun()

def sql_executor_tool(query: str, use_cache: bool = True) -> str:
    """
    Execute snowflake sql queries with optional caching.
    """
    conn = SnowflakeConnection()
    return conn.execute_query(query, use_cache)

# if __name__ == "__main__":
#     print(sql_executor_tool("select * from STREAM_HACKATHON.STREAMLIT.CUSTOMER_DETAILS"))
