from langchain.prompts.prompt import PromptTemplate
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import (
    ConversationalRetrievalChain,
    LLMChain
)
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks.base import (
    AsyncCallbackHandler, 
    AsyncCallbackManager
)
import streamlit as st
from langchain.chat_models import ChatOpenAI

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


def get_chain(vectorstore, question_handler, stream_handler):
    ## Async Managers
    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([question_handler])
    stream_manager = AsyncCallbackManager([stream_handler])

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
