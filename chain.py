import streamlit as st

from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from supabase.client import Client, create_client

template = """Considering the provided chat history and a subsequent question, rewrite the follow-up question to be an independent query. Alternatively, conclude the conversation if it appears to be complete.
Chat History:\"""
{chat_history}
\"""
Follow Up Input: \"""
{question}
\"""
Standalone question:"""

condense_question_prompt = PromptTemplate.from_template(template)

TEMPLATE = """ 
You're an AI assistant specializing in data analysis with Snowflake SQL. When providing responses, strive to exhibit friendliness and a tutor-like approach to help users learn. 

Based on the question provided, if it pertains to data analysis or SQL tasks, generate SQL code that is compatible with the Snowflake environment. Additionally, offer a brief explanation about how you arrived at the SQL code. If the required column isn't explicitly stated in the context, suggest an alternative using available columns, but do not assume the existence of any columns that are not mentioned. Also, do not modify the database in any way (no insert, update, or delete operations). You are only allowed to query the database. Refrain from using the information schema.

If the question or context does not clearly involve SQL or data analysis tasks, respond appropriately without generating SQL queries. 

Do not answer any question that is not related to SQL. If you don't know the answer, simply state, "I'm sorry, I don't know the answer to your question."

Write the SQL code in markdown format.

Question: ```{question}```
{context}

Answer:
"""


QA_PROMPT = PromptTemplate(template=TEMPLATE, input_variables=["question", "context"])

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_SERVICE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)


def get_chain(vectorstore):
    """
    Get a chain for chatting with a vector database.
    """
    q_llm = OpenAI(
        temperature=0,
        openai_api_key=st.secrets["OPENAI_API_KEY"],
        model_name="gpt-3.5-turbo-16k",
        max_tokens=500,
    )

    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo-16k",
        temperature=0,
        openai_api_key=st.secrets["OPENAI_API_KEY"],
        max_tokens=500,
        # streaming=True,
    )

    question_generator = LLMChain(llm=q_llm, prompt=condense_question_prompt)

    doc_chain = load_qa_chain(llm=llm, chain_type="stuff", prompt=QA_PROMPT)
    conv_chain = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(),
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
    )

    return conv_chain


def load_chain():
    """
    Load the chain from the local file system

    Returns:
        chain (Chain): The chain object

    """

    embeddings = OpenAIEmbeddings(
        openai_api_key=st.secrets["OPENAI_API_KEY"], model="text-embedding-ada-002"
    )
    vectorstore = SupabaseVectorStore(
        embedding=embeddings, client=supabase, table_name="documents"
    )
    return get_chain(vectorstore)
