
from langchain.callbacks.base import (
    AsyncCallbackHandler, 
)
import streamlit as st
from typing import Any, Dict, List

from utils.snowchat_ui import message_func

class StreamingLLMCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses."""
    def __init__(self):
        pass
    
    def set_messages_container(self, message_container):
        self.messages_container = message_container

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        print(token, end ="")
        
        # if (self.messages_container):
        #     with self.messages_container:
        #         i = len(st.session_state["generated"]) - 1
        #         st.session_state["generated"][0] += token
        #         message_func(st.session_state["generated"][0])


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