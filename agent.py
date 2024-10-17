import os
import streamlit as st
from dataclasses import dataclass
from typing import Annotated, Sequence, Optional

from langchain.callbacks.base import BaseCallbackHandler
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

from template import TEMPLATE
from tools import retriever_tool


@dataclass
class MessagesState:
    messages: Annotated[Sequence[BaseMessage], add_messages]


memory = MemorySaver()


@dataclass
class ModelConfig:
    model_name: str
    api_key: str
    base_url: Optional[str] = None


def create_agent(callback_handler: BaseCallbackHandler, model_name: str):
    model_configurations = {
        "gpt-4o": ModelConfig(
            model_name="gpt-4o", api_key=os.getenv("OPENAI_API_KEY")
        ),
        "Gemini Flash 1.5 8B": ModelConfig(
            model_name="google/gemini-flash-1.5-8b",
            api_key=st.secrets["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
        ),
        "claude3-haiku": ModelConfig(
            model_name="claude-3-haiku-20240307", api_key=os.getenv("ANTHROPIC_API_KEY")
        ),
        "llama-3.2-3b": ModelConfig(
            model_name="accounts/fireworks/models/llama-v3p2-3b-instruct",
            api_key=os.getenv("FIREWORKS_API_KEY"),
            base_url="https://api.fireworks.ai/inference/v1",
        ),
        "llama-3.1-405b": ModelConfig(
            model_name="accounts/fireworks/models/llama-v3p1-405b-instruct",
            api_key=os.getenv("FIREWORKS_API_KEY"),
            base_url="https://api.fireworks.ai/inference/v1",
        ),
    }
    config = model_configurations.get(model_name)
    if not config:
        raise ValueError(f"Unsupported model name: {model_name}")

    sys_msg = SystemMessage(
        content="""You're an AI assistant specializing in data analysis with Snowflake SQL. When providing responses, strive to exhibit friendliness and adopt a conversational tone, similar to how a friend or tutor would communicate.
        Call the tool "Database_Schema" to search for database schema details when needed to generate the SQL code.
        """
    )

    llm = (
        ChatOpenAI(
            model=config.model_name,
            api_key=config.api_key,
            callbacks=[callback_handler],
            streaming=True,
            base_url=config.base_url,
        )
        if config.model_name != "claude-3-haiku-20240307"
        else ChatAnthropic(
            model=config.model_name,
            api_key=config.api_key,
            callbacks=[callback_handler],
            streaming=True,
        )
    )

    tools = [retriever_tool]

    llm_with_tools = llm.bind_tools(tools)

    def reasoner(state: MessagesState):
        return {"messages": [llm_with_tools.invoke([sys_msg] + state.messages)]}

    # Build the graph
    builder = StateGraph(MessagesState)
    builder.add_node("reasoner", reasoner)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "reasoner")
    builder.add_conditional_edges("reasoner", tools_condition)
    builder.add_edge("tools", "reasoner")

    react_graph = builder.compile(checkpointer=memory)

    return react_graph
