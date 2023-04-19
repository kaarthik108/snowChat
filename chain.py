from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts.prompt import PromptTemplate
import streamlit as st

TEMPLATE = """ You're name is snowchat, and you are a senior snowflake developer. You have to write a sql code in snowflake database based on the following question. Also you have to ignore the sql keywords and give a one or two sentences about how did you arrive at that sql code. display the sql code in the code format (do not assume anything if the column is not available then say it is not available, do not make up code).
If you don't know the answer, just say "Hmm, I'm not sure. I am trained only to answer sql related queries. Please try again." Don't try to make up an answer.

Question: {question}
{context}
Answer:"""  # noqa: E501
QA_PROMPT = PromptTemplate(template=TEMPLATE, input_variables=["question", "context"])


def get_chain(vectorstore):
    """
    Get a chain for chatting with a vector database.
    """
    llm = ChatOpenAI(openai_api_key = st.secrets['OPENAI_API_KEY'] ,model_name='gpt-4', temperature=0.08)
    chat_vector_db_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever(), chain_type_kwargs={"prompt": QA_PROMPT}, return_source_documents=True)  # noqa: E501
    
    return chat_vector_db_chain
