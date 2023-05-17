
import asyncio
import random
from langchain.callbacks.base import (
    AsyncCallbackHandler, 
)
import streamlit as st
from typing import Any, Dict, List

from utils.snowchat_ui import format_response, message_func

class StreamingLLMCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses."""
    def __init__(self, placeholder):
        self.async_text_memory = ''
        self.placeholder = placeholder

        # Handle styling
        self.ended_sql_portion = False
        self.effective_text_len = 0
        pass
    
    def set_messages_container(self, message_container):
        self.messages_container = message_container

    def reset_block(self, placeholder):
        self.async_text_memory = ''
        self.placeholder = placeholder
        self.ended_sql_portion = False
        self.effective_text_len = 0
        print('updated!')

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        print('start')

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        print(token, end ="")
        
        self.async_text_memory+=token
        self.placeholder.text(self.async_text_memory)

class QuestionGenCallbackHandler(AsyncCallbackHandler):
    """Callback handler for question generation."""

    def __init__(self):
        pass
    
    def set_messages_container(self, message_container):
        self.messages_container = message_container
        

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        text = 'Synthesizing question..'
        print(text)
        
        # if (self.messages_container):
            # with self.messages_container:
                # st.session_state["generated"].append(text)

async def type_effect(text, placeholder):
    for i in range(len(text)):
        st.session_state['generated'][0] = text[:i]
        placeholder.text(st.session_state['generated'][0])
        await asyncio.sleep(random.randint(1,2000)/100000)