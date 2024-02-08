from typing import Any, Callable, Dict, Optional

import boto3
import streamlit as st
from langchain.chat_models import BedrockChat, ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.vectorstores import SupabaseVectorStore
from pydantic import BaseModel, validator
from supabase.client import Client, create_client

from template import CONDENSE_QUESTION_PROMPT, QA_PROMPT

from operator import itemgetter

from langchain.prompts.prompt import PromptTemplate
from langchain.schema import format_document
from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_SERVICE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)


class ModelConfig(BaseModel):
    model_type: str
    secrets: Dict[str, Any]
    callback_handler: Optional[Callable] = None

    @validator("model_type", pre=True, always=True)
    def validate_model_type(cls, v):
        if v not in ["gpt", "codellama", "mistral"]:
            raise ValueError(f"Unsupported model type: {v}")
        return v


class ModelWrapper:
    def __init__(self, config: ModelConfig):
        self.model_type = config.model_type
        self.secrets = config.secrets
        self.callback_handler = config.callback_handler
        account_tag = self.secrets["CF_ACCOUNT_TAG"]
        self.gateway_url = (
            f"https://gateway.ai.cloudflare.com/v1/{account_tag}/k-1-gpt/openai"
        )
        self.setup()

    def setup(self):
        if self.model_type == "gpt":
            self.setup_gpt()
        elif self.model_type == "codellama":
            self.setup_codellama()
        elif self.model_type == "mistral":
            self.setup_mixtral()

    def setup_gpt(self):
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo-0125",
            temperature=0.2,
            api_key=self.secrets["OPENAI_API_KEY"],
            max_tokens=500,
            callbacks=[self.callback_handler],
            streaming=True,
            base_url=self.gateway_url,
        )

    def setup_mixtral(self):
        self.llm = ChatOpenAI(
            model_name="mistralai/mistral-medium",
            temperature=0.2,
            api_key=self.secrets["OPENROUTER_API_KEY"],
            max_tokens=500,
            callbacks=[self.callback_handler],
            streaming=True,
            base_url="https://openrouter.ai/api/v1",
        )

    def setup_codellama(self):
        self.llm = ChatOpenAI(
            model_name="codellama/codellama-70b-instruct",
            temperature=0.2,
            api_key=self.secrets["OPENROUTER_API_KEY"],
            max_tokens=500,
            callbacks=[self.callback_handler],
            streaming=True,
            base_url="https://openrouter.ai/api/v1",
        )

    # def setup_claude(self):
    #     bedrock_runtime = boto3.client(
    #         service_name="bedrock-runtime",
    #         aws_access_key_id=self.secrets["AWS_ACCESS_KEY_ID"],
    #         aws_secret_access_key=self.secrets["AWS_SECRET_ACCESS_KEY"],
    #         region_name="us-east-1",
    #     )
    #     parameters = {
    #         "max_tokens_to_sample": 1000,
    #         "stop_sequences": [],
    #         "temperature": 0,
    #         "top_p": 0.9,
    #     }
    #     self.q_llm = BedrockChat(
    #         model_id="anthropic.claude-instant-v1", client=bedrock_runtime
    #     )

    #     self.llm = BedrockChat(
    #         model_id="anthropic.claude-instant-v1",
    #         client=bedrock_runtime,
    #         callbacks=[self.callback_handler],
    #         streaming=True,
    #         model_kwargs=parameters,
    #     )

    def get_chain(self, vectorstore):
        def _combine_documents(
            docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
        ):
            doc_strings = [format_document(doc, document_prompt) for doc in docs]
            return document_separator.join(doc_strings)

        _inputs = RunnableParallel(
            standalone_question=RunnablePassthrough.assign(
                chat_history=lambda x: get_buffer_string(x["chat_history"])
            )
            | CONDENSE_QUESTION_PROMPT
            | OpenAI()
            | StrOutputParser(),
        )
        _context = {
            "context": itemgetter("standalone_question")
            | vectorstore.as_retriever()
            | _combine_documents,
            "question": lambda x: x["standalone_question"],
        }
        conversational_qa_chain = _inputs | _context | QA_PROMPT | self.llm

        return conversational_qa_chain


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

    if "codellama" in model_name.lower():
        model_type = "codellama"
    elif "GPT-3.5" in model_name:
        model_type = "gpt"
    elif "mistral" in model_name.lower():
        model_type = "mistral"
    else:
        raise ValueError(f"Unsupported model name: {model_name}")

    config = ModelConfig(
        model_type=model_type, secrets=st.secrets, callback_handler=callback_handler
    )
    model = ModelWrapper(config)
    return model.get_chain(vectorstore)
