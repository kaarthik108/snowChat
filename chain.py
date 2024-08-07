from typing import Any, Callable, Dict, Optional

import streamlit as st
from langchain_community.chat_models import ChatOpenAI
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
from langchain_anthropic import ChatAnthropic

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_SERVICE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)


class ModelConfig(BaseModel):
    model_type: str
    secrets: Dict[str, Any]
    callback_handler: Optional[Callable] = None


class ModelWrapper:
    def __init__(self, config: ModelConfig):
        self.model_type = config.model_type
        self.secrets = config.secrets
        self.callback_handler = config.callback_handler
        self.llm = self._setup_llm()

    def _setup_llm(self):
        model_config = {
            "gpt-4o-mini": {
                "model_name": "gpt-4o-mini",
                "api_key": self.secrets["OPENAI_API_KEY"],
            },
            "gemma2-9b": {
                "model_name": "gemma2-9b-it",
                "api_key": self.secrets["GROQ_API_KEY"],
                "base_url": "https://api.groq.com/openai/v1",
            },
            "claude3-haiku": {
                "model_name": "claude-3-haiku-20240307",
                "api_key": self.secrets["ANTHROPIC_API_KEY"],
            },
            "mixtral-8x22b": {
                "model_name": "accounts/fireworks/models/mixtral-8x22b-instruct",
                "api_key": self.secrets["FIREWORKS_API_KEY"],
                "base_url": "https://api.fireworks.ai/inference/v1",
            },
            "llama-3.1-405b": {
                "model_name": "accounts/fireworks/models/llama-v3p1-405b-instruct",
                "api_key": self.secrets["FIREWORKS_API_KEY"],
                "base_url": "https://api.fireworks.ai/inference/v1",
            },
        }

        config = model_config[self.model_type]

        return (
            ChatOpenAI(
                model_name=config["model_name"],
                temperature=0.1,
                api_key=config["api_key"],
                max_tokens=700,
                callbacks=[self.callback_handler],
                streaming=True,
                base_url=config["base_url"]
                if config["model_name"] != "gpt-4o-mini"
                else None,
                default_headers={
                    "HTTP-Referer": "https://snowchat.streamlit.app/",
                    "X-Title": "Snowchat",
                },
            )
            if config["model_name"] != "claude-3-haiku-20240307"
            else (
                ChatAnthropic(
                    model=config["model_name"],
                    temperature=0.1,
                    max_tokens=700,
                    timeout=None,
                    max_retries=2,
                    callbacks=[self.callback_handler],
                    streaming=True,
                )
            )
        )

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


def load_chain(model_name="qwen", callback_handler=None):
    embeddings = OpenAIEmbeddings(
        openai_api_key=st.secrets["OPENAI_API_KEY"], model="text-embedding-ada-002"
    )
    vectorstore = SupabaseVectorStore(
        embedding=embeddings,
        client=supabase,
        table_name="documents",
        query_name="v_match_documents",
    )

    model_type_mapping = {
        "gpt-4o-mini": "gpt-4o-mini",
        "gemma2-9b": "gemma2-9b",
        "claude3-haiku": "claude3-haiku",
        "mixtral-8x22b": "mixtral-8x22b",
        "llama-3.1-405b": "llama-3.1-405b",
    }

    model_type = model_type_mapping.get(model_name.lower())
    if model_type is None:
        raise ValueError(f"Unsupported model name: {model_name}")

    config = ModelConfig(
        model_type=model_type, secrets=st.secrets, callback_handler=callback_handler
    )
    model = ModelWrapper(config)
    return model.get_chain(vectorstore)
