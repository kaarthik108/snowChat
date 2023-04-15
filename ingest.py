import pickle
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader
from langchain.vectorstores import FAISS
from dotenv import load_dotenv
# import pandas as pd
load_dotenv()

PERSIST_DIRECTORY = 'store'

loader = DirectoryLoader('./', glob="*.txt")
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(data)

embeddings = OpenAIEmbeddings(openai_api_key = os.getenv("OPENAI_API_KEY"))
docsearch = FAISS.from_documents(texts, embeddings)

# docsearch.save_local("faiss_index")

with open("vectors.pkl", "wb") as f:
    pickle.dump(docsearch, f)