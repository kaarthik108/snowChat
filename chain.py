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
        valid_model_types = ["qwen", "llama", "claude", "mixtral8x7b", "arctic"]
        if v not in valid_model_types:
            raise ValueError(f"Unsupported model type: {v}")
        return v


class ModelWrapper:
    def __init__(self, config: ModelConfig):
        self.model_type = config.model_type
        self.secrets = config.secrets
        self.callback_handler = config.callback_handler
        self.llm = self._setup_llm()

    def _setup_llm(self):
        model_config = {
            "qwen": {
                "model_name": "qwen/qwen-2-72b-instruct",
                "api_key": self.secrets["OPENROUTER_API_KEY"],
                "base_url": "https://openrouter.ai/api/v1",
            },
            "claude": {
                "model_name": "anthropic/claude-3-haiku",
                "api_key": self.secrets["OPENROUTER_API_KEY"],
                "base_url": "https://openrouter.ai/api/v1",
            },
            "mixtral8x7b": {
                "model_name": "mixtral-8x7b-32768",
                "api_key": self.secrets["GROQ_API_KEY"],
                "base_url": "https://api.groq.com/openai/v1",
            },
            "llama": {
                "model_name": "meta-llama/llama-3-70b-instruct",
                "api_key": self.secrets["OPENROUTER_API_KEY"],
                "base_url": "https://openrouter.ai/api/v1",
            },
            "arctic": {
                "model_name": "snowflake/snowflake-arctic-instruct",
                "api_key": self.secrets["OPENROUTER_API_KEY"],
                "base_url": "https://openrouter.ai/api/v1",
            },
        }

        config = model_config[self.model_type]

        return ChatOpenAI(
            model_name=config["model_name"],
            temperature=0.1,
            api_key=config["api_key"],
            max_tokens=700,
            callbacks=[self.callback_handler],
            streaming=True,
            base_url=config["base_url"],
            default_headers={
                "HTTP-Referer": "https://snowchat.streamlit.app/",
                "X-Title": "Snowchat",
            },
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
        "qwen 2-72b": "qwen",
        "mixtral 8x7b": "mixtral8x7b",
        "claude-3 haiku": "claude",
        "llama 3-70b": "llama",
        "snowflake arctic": "arctic",
    }

    model_type = model_type_mapping.get(model_name.lower())
    if model_type is None:
        raise ValueError(f"Unsupported model name: {model_name}")

    config = ModelConfig(
        model_type=model_type, secrets=st.secrets, callback_handler=callback_handler
    )
    model = ModelWrapper(config)
    return model.get_chain(vectorstore)
