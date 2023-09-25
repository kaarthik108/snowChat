import hashlib
import json
import os

import streamlit as st
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma, SupabaseVectorStore  # Import Chroma
from pydantic import BaseModel
from supabase.client import Client, create_client


class Secrets(BaseModel):
    SUPABASE_URL: str = None
    SUPABASE_SERVICE_KEY: str = None
    OPENAI_API_KEY: str
    VECTOR_STORE_TYPE: str = "chroma"


class Config(BaseModel):
    chunk_size: int = 1000
    chunk_overlap: int = 0
    docs_dir: str = "docs/"
    docs_glob: str = "**/*.md"
    checksum_file: str = "checksums.json"


class DocumentProcessor:
    def __init__(self, secrets: Secrets, config: Config):
        self.config = config
        self.loader = DirectoryLoader(config.docs_dir, glob=config.docs_glob)
        self.text_splitter = CharacterTextSplitter(
            chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
        )
        self.embeddings = OpenAIEmbeddings(openai_api_key=secrets.OPENAI_API_KEY)
        self.checksums = self.load_checksums()

        # Initialize vector store based on environment variable
        self.vector_store_type = secrets.VECTOR_STORE_TYPE
        if self.vector_store_type == "supabase":
            self.client: Client = create_client(
                secrets.SUPABASE_URL, secrets.SUPABASE_SERVICE_KEY
            )

    def load_checksums(self):
        if os.path.exists(self.config.checksum_file):
            with open(self.config.checksum_file, "r") as f:
                checksums = json.load(f)
                return checksums
        else:
            print("No checksum file found, starting with an empty dictionary.")
            return {}

    def save_checksums(self):
        with open(self.config.checksum_file, "w") as f:
            json.dump(self.checksums, f)

    def calculate_checksum(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def process(self):
        documents = self.loader.load()
        docs = self.text_splitter.split_documents(documents)

        new_docs = []
        for doc in docs:
            doc_id = doc.metadata["source"]
            content = doc.page_content
            checksum = self.calculate_checksum(content)

            if checksum in self.checksums.values():
                print(f"Skipping {doc_id}, embeded already.")
                continue

            new_docs.append(doc)
            self.checksums[doc_id] = checksum
            self.save_checksums()

        if not new_docs:
            print("No new documents found to embed.")
            return

        print(f"Found {len(new_docs)} new documents to embed.")
        if self.vector_store_type == "chroma":
            self.vector_store = Chroma.from_documents(
                new_docs, self.embeddings, persist_directory="chroma_db"
            )
            self.vector_store.persist()
        elif self.vector_store_type == "supabase":
            self.vector_store = SupabaseVectorStore.from_documents(
                new_docs, self.embeddings, client=self.client, table_name="ex_documents"
            )


def run():
    vector_store_type = st.secrets["VECTOR_STORE_TYPE"]

    # Initialize secrets based on the chosen vector store type
    if vector_store_type == "supabase":
        secrets = Secrets(
            SUPABASE_URL=st.secrets["SUPABASE_URL"],
            SUPABASE_SERVICE_KEY=st.secrets["SUPABASE_SERVICE_KEY"],
            OPENAI_API_KEY=st.secrets["OPENAI_API_KEY"],
            VECTOR_STORE_TYPE=vector_store_type,
        )
    elif vector_store_type == "chroma":
        secrets = Secrets(
            OPENAI_API_KEY=st.secrets["OPENAI_API_KEY"],
            VECTOR_STORE_TYPE=vector_store_type,
        )
    else:
        raise ValueError(f"Unsupported vector store type: {vector_store_type}")

    config = Config()
    doc_processor = DocumentProcessor(secrets, config)
    doc_processor.process()


if __name__ == "__main__":
    run()
