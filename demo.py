import asyncio
from langchain.prompts.prompt import PromptTemplate
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.chains import (
    ConversationalRetrievalChain,
    LLMChain
)
from langchain.callbacks.base import (
    AsyncCallbackHandler, 
    AsyncCallbackManager
)

from typing import Any, Dict, List

import streamlit as st

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

template = """Considering the provided chat history and a subsequent question, rewrite the follow-up question to be an independent query. Alternatively, conclude the conversation if it appears to be complete.
Chat History:
{chat_history}
Follow Up Input: \"""
{question}
\"""
Standalone question:"""

template = """Considering the provided chat history and a subsequent question, rewrite the follow-up question to be an independent query. Alternatively, conclude the conversation if it appears to be complete.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
 
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(template)

prompt_template = """ You're a senior SQL developer. You have to write sql code in snowflake database based on the following question. Also you have to ignore the sql keywords and give a one or two sentences about how did you arrive at that sql code. display the sql code in the code format (do not assume anything if the column is not available then say it is not available, do not make up code).
If you don't know the answer, just say "Hmm, I'm not sure. I am trained only to answer sql related queries. Please try again." Don't try to make up an answer.

Question: {question}
{context}
Answer:"""  
STREAMING_TEXT_PROMPT = PromptTemplate(template=prompt_template, input_variables=["question", "context"])


class StreamingLLMCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses."""
    def __init__(self):
        pass

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        print(token, end ="")


class QuestionGenCallbackHandler(AsyncCallbackHandler):
    """Callback handler for question generation."""

    def __init__(self):
        pass

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        print('Synthesizing question..')

def get_streaming_chain(vectorstore):
    ## Async Managers
    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([QuestionGenCallbackHandler()])
    stream_manager = AsyncCallbackManager([StreamingLLMCallbackHandler()])

    ## LLM Models
    question_gen_llm = OpenAI(
        temperature=0,
        verbose=True,
        callback_manager=question_manager,
    )
    streaming_llm = OpenAI(
        streaming=True,
        callback_manager=stream_manager,
        verbose=True,
        temperature=0,
    )
    question_generator = LLMChain(
        llm=question_gen_llm, prompt=CONDENSE_QUESTION_PROMPT, callback_manager=manager
    )
    doc_chain = load_qa_chain(
        streaming_llm, chain_type="stuff", prompt=STREAMING_TEXT_PROMPT, callback_manager=manager
    )

    chain = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(),
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
        callback_manager=manager,
    )
    return chain

#### Loader

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS

def load_streaming_chain():
    '''
    Load the chain from the local file system

    Returns:
        chain (Chain): The chain object

    '''
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = FAISS.load_local('faiss_index', embeddings)

    return get_streaming_chain(vectorstore)

streaming_chain = load_streaming_chain()    

async def run_streaming_text_2_sql_demo(query=''):
    chat_history = []

    while True:
        # Receive and send back the client message
        if query:
            question = 'Show me the total revenue for each product category.'
        else:
            question = input('---\n\nQuestion (enter to quit):\n')
        if question=='' or query != '':
            break
        # Construct a response
        result = await streaming_chain.acall({"question": question, "chat_history": chat_history})
        chat_history.append((question, result["answer"]))

if __name__ == "__main__":
    asyncio.run(run_streaming_text_2_sql_demo())