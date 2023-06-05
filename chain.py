from langchain.prompts.prompt import PromptTemplate
from langchain.chains import (
    RetrievalQA
)
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
import streamlit as st

TEMPLATE = """ You're a senior SQL developer. You have to write sql code in snowflake database based on the following question. Give a one or two sentences about how did you arrive at that sql code. display the sql code in the SQL code format (do not assume anything if the column is not available, do not make up code). ALSO if you are asked to FIX the sql code, then look what was the error and try to fix that by searching the schema definition.
If you don't know the answer, just say "Hmm, I'm not sure. I am trained only to answer sql related queries. Please try again." Don't try to make up an answer.

{history}

Question: {question}
{context}
SQL: ```sql ``` \n
Explanation: """
QA_PROMPT = PromptTemplate(template=TEMPLATE, input_variables=["history", "question", "context"])

chain_type_kwargs = {"prompt": QA_PROMPT,
                     "memory": ConversationBufferMemory(
                        memory_key="history",
                        input_key="question"), 
                    }


def get_chain(vectorstore):
    """
    Get a chain for chatting with a vector database.
    """
    
    streaming_llm = OpenAI(
        model_name='gpt-3.5-turbo',
        streaming=False, # Not working yet
        # callback_manager=CallbackManager([
        #     StreamingStdOutCallbackHandler()
        # ]),
        max_tokens=1000,
        temperature=0.1,
        openai_api_key=st.secrets["OPENAI_API_KEY"]
    )
    
    chain = RetrievalQA.from_chain_type(
                llm=streaming_llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(),
                chain_type_kwargs=chain_type_kwargs,
                )
    return chain
