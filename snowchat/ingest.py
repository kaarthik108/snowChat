from typing import Any, Dict
import hashlib
import streamlit as st
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import SupabaseVectorStore
from pydantic import BaseModel
from supabase.client import Client, create_client
import json

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

    def calculate_checksum(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()
    
    def process(self) -> Dict[str, Any]:
        data = self.loader.load()
        vector_store = SupabaseVectorStore(client=self.client)
        
        for doc_id, content in data.items():
            checksum = self.calculate_checksum(content)
            
            if vector_store.checksum_exists(checksum):
                print(f"Skipping {doc_id}, checksum {checksum} already exists.")
                continue
            
            # If not, proceed to split and embed the document
            texts = self.text_splitter.split_text(content)
            vector_store.add_document(doc_id, texts, checksum, self.embeddings)
        
        return vector_store


def run():
    secrets = Secrets(
        SUPABASE_URL=st.secrets["SUPABASE_URL"],
        SUPABASE_SERVICE_KEY=st.secrets["SUPABASE_SERVICE_KEY"],
        OPENAI_API_KEY=st.secrets["OPENAI_API_KEY"],
    )
    config = Config()
    doc_processor = DocumentProcessor(secrets, config)
    vector_store = doc_processor.process()
    result = json.dumps(vector_store.to_dict())
    return result


if __name__ == "__main__":
    run()
