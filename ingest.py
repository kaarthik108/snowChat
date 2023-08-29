from typing import Any, Dict

import streamlit as st
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import SupabaseVectorStore
from pydantic import BaseModel
from supabase.client import Client, create_client


class Secrets(BaseModel):
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    OPENAI_API_KEY: str


class Config(BaseModel):
    chunk_size: int = 1000
    chunk_overlap: int = 0
    docs_dir: str = "docs/"
    docs_glob: str = "**/*.md"


class DocumentProcessor:
    def __init__(self, secrets: Secrets, config: Config):
        self.client: Client = create_client(
            secrets.SUPABASE_URL, secrets.SUPABASE_SERVICE_KEY
        )
        self.loader = DirectoryLoader(config.docs_dir, glob=config.docs_glob)
        self.text_splitter = CharacterTextSplitter(
            chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=secrets.OPENAI_API_KEY)

    def process(self) -> Dict[str, Any]:
        data = self.loader.load()
        texts = self.text_splitter.split_documents(data)
        vector_store = SupabaseVectorStore.from_documents(
            texts, self.embeddings, client=self.client
        )
        return vector_store


def run():
    secrets = Secrets(
        SUPABASE_URL=st.secrets["SUPABASE_URL"],
        SUPABASE_SERVICE_KEY=st.secrets["SUPABASE_SERVICE_KEY"],
        OPENAI_API_KEY=st.secrets["OPENAI_API_KEY"],
    )
    config = Config()
    doc_processor = DocumentProcessor(secrets, config)
    result = doc_processor.process()
    return result


if __name__ == "__main__":
    run()
