from typing import Any, Callable, Dict, Optional

import boto3
import streamlit as st
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI, Replicate
from langchain.llms.bedrock import Bedrock
from langchain.vectorstores import SupabaseVectorStore
from pydantic import BaseModel, validator
from supabase.client import Client, create_client

from template import CONDENSE_QUESTION_PROMPT, LLAMA_PROMPT, QA_PROMPT

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_SERVICE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)

VERSION = "1f01a52ff933873dff339d5fb5e1fd6f24f77456836f514fa05e91c1a42699c7"
LLAMA = "meta/codellama-13b-instruct:{}".format(VERSION)


class ModelConfig(BaseModel):
    model_type: str
    secrets: Dict[str, Any]
    callback_handler: Optional[Callable] = None

    @validator("model_type", pre=True, always=True)
    def validate_model_type(cls, v):
        if v not in ["code-llama", "gpt", "claude"]:
            raise ValueError(f"Unsupported model type: {v}")
        return v


class ModelWrapper:
    def __init__(self, config: ModelConfig):
        self.model_type = config.model_type
        self.secrets = config.secrets
        self.callback_handler = config.callback_handler
        self.setup()

    def setup(self):
        if self.model_type == "code-llama":
            self.setup_llama()
        elif self.model_type == "gpt":
            self.setup_gpt()
        elif self.model_type == "claude":
            self.setup_claude()

    def setup_llama(self):
        self.q_llm = Replicate(
            model=LLAMA,
            input={"temperature": 0.2, "max_length": 200, "top_p": 1},
            replicate_api_token=self.secrets["REPLICATE_API_TOKEN"],
        )
        self.llm = Replicate(
            streaming=True,
            callbacks=[self.callback_handler],
            model=LLAMA,
            input={"temperature": 0.2, "max_length": 300, "top_p": 1},
            replicate_api_token=self.secrets["REPLICATE_API_TOKEN"],
        )

    def setup_gpt(self):
        self.q_llm = OpenAI(
            temperature=0.1,
            openai_api_key=self.secrets["OPENAI_API_KEY"],
            model_name="gpt-3.5-turbo-16k",
            max_tokens=500,
        )

        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo-16k",
            temperature=0.5,
            openai_api_key=self.secrets["OPENAI_API_KEY"],
            max_tokens=500,
            callbacks=[self.callback_handler],
            streaming=True,
        )

    def setup_claude(self):
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            aws_access_key_id=self.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=self.secrets["AWS_SECRET_ACCESS_KEY"],
            region_name="us-east-1",
        )
        parameters = {
            "max_tokens_to_sample": 1000,
            "stop_sequences": [],
            "temperature": 0,
            "top_p": 0.9,
        }
        self.q_llm = Bedrock(
            model_id="anthropic.claude-instant-v1", client=bedrock_runtime
        )
        self.llm = Bedrock(
            model_id="anthropic.claude-instant-v1",
            client=bedrock_runtime,
            callbacks=[self.callback_handler],
            streaming=True,
            model_kwargs=parameters,
        )

    def get_chain(self, vectorstore):
        if not self.q_llm or not self.llm:
            raise ValueError("Models have not been properly initialized.")
        question_generator = LLMChain(llm=self.q_llm, prompt=CONDENSE_QUESTION_PROMPT)
        doc_chain = load_qa_chain(llm=self.llm, chain_type="stuff", prompt=QA_PROMPT)
        conv_chain = ConversationalRetrievalChain(
            retriever=vectorstore.as_retriever(),
            combine_docs_chain=doc_chain,
            question_generator=question_generator,
        )
        return conv_chain


def load_chain(model_name="GPT-3.5", callback_handler=None):
    embeddings = OpenAIEmbeddings(
        openai_api_key=st.secrets["OPENAI_API_KEY"], model="text-embedding-ada-002"
    )
    vectorstore = SupabaseVectorStore(
        embedding=embeddings,
        client=supabase,
        table_name="documents",
        query_name="v_match_documents",
    )

    if "claude" in model_name.lower():
        model_type = "claude"
    elif "GPT-3.5" in model_name:
        model_type = "gpt"
    else:
        model_type = "code-llama"

    config = ModelConfig(
        model_type=model_type, secrets=st.secrets, callback_handler=callback_handler
    )
    model = ModelWrapper(config)
    return model.get_chain(vectorstore)
