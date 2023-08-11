import streamlit as st

from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI, Replicate
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from supabase.client import Client, create_client


template = """You are an AI chatbot having a conversation with a human.

Chat History:\"""
{chat_history}
\"""
Human Input: \"""
{question}
\"""
AI:"""

condense_question_prompt = PromptTemplate.from_template(template)

TEMPLATE = """ 
You're an AI assistant specializing in data analysis with Snowflake SQL. When providing responses, strive to exhibit friendliness and adopt a conversational tone, similar to how a friend or tutor would communicate.

When asked about your capabilities, provide a general overview of your ability to assist with data analysis tasks using Snowflake SQL, instead of performing specific SQL queries. 

Based on the question provided, if it pertains to data analysis or SQL tasks, generate SQL code that is compatible with the Snowflake environment. Additionally, offer a brief explanation about how you arrived at the SQL code. If the required column isn't explicitly stated in the context, suggest an alternative using available columns, but do not assume the existence of any columns that are not mentioned. Also, do not modify the database in any way (no insert, update, or delete operations). You are only allowed to query the database. Refrain from using the information schema.
**You are only required to write one SQL query per question.**

If the question or context does not clearly involve SQL or data analysis tasks, respond appropriately without generating SQL queries. 

When the user expresses gratitude or says "Thanks", interpret it as a signal to conclude the conversation. Respond with an appropriate closing statement without generating further SQL queries.

If you don't know the answer, simply state, "I'm sorry, I don't know the answer to your question."

Write your response in markdown format.

Question: ```{question}```
{context}

Answer:
"""

LLAMA_TEMPLATE = """
You're specialized with Snowflake SQL. When providing answers, strive to exhibit friendliness and adopt a conversational tone, similar to how a friend or tutor would communicate.

If the question or context does not clearly involve SQL or data analysis tasks, respond appropriately without generating SQL queries. 

If you don't know the answer, simply state, "I'm sorry, I don't know the answer to your question."

Write SQL code for this Question based on the below context details:  {question}

context: \n {context}

WRITE RESPONSES IN MARKDOWN FORMAT and code in ```sql  ```

Answer:

"""

QA_PROMPT = PromptTemplate(template=TEMPLATE, input_variables=["question", "context"])
LLAMA_PROMPT = PromptTemplate(
    template=LLAMA_TEMPLATE, input_variables=["question", "context"]
)

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_SERVICE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)

VERSION = "2a7f981751ec7fdf87b5b91ad4db53683a98082e9ff7bfd12c8cd5ea85980a52"
LLAMA = "a16z-infra/llama13b-v2-chat:{}".format(VERSION)


def get_chain_replicate(vectorstore, callback_handler=None):
    """
    Get a chain for chatting with a vector database.
    """
    q_llm = Replicate(
        # streaming=True,
        # callbacks=[callback_handler],
        model=LLAMA,
        input={"temperature": 0.75, "max_length": 200, "top_p": 1},
        replicate_api_token=st.secrets["REPLICATE_API_TOKEN"],
    )
    llm = Replicate(
        # streaming=True,
        # callbacks=[callback_handler],
        model=LLAMA,
        input={"temperature": 0.75, "max_length": 200, "top_p": 1},
        replicate_api_token=st.secrets["REPLICATE_API_TOKEN"],
    )

    question_generator = LLMChain(llm=q_llm, prompt=condense_question_prompt)

    doc_chain = load_qa_chain(llm=llm, chain_type="stuff", prompt=QA_PROMPT)
    conv_chain = ConversationalRetrievalChain(
        callbacks=[callback_handler],
        retriever=vectorstore.as_retriever(),
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
    )

    return conv_chain


def get_chain_gpt(vectorstore, callback_handler=None):
    """
    Get a chain for chatting with a vector database.
    """
    q_llm = OpenAI(
        temperature=0.1,
        openai_api_key=st.secrets["OPENAI_API_KEY"],
        model_name="gpt-3.5-turbo-16k",
        max_tokens=500,
    )

    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.5,
        openai_api_key=st.secrets["OPENAI_API_KEY"],
        max_tokens=500,
        callbacks=[callback_handler],
        streaming=True,
    )
    question_generator = LLMChain(llm=q_llm, prompt=condense_question_prompt)

    doc_chain = load_qa_chain(llm=llm, chain_type="stuff", prompt=QA_PROMPT)
    conv_chain = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(),
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
    )

    return conv_chain


def load_chain(model_name="GPT-3.5", callback_handler=None):
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
    return (
        get_chain_gpt(vectorstore, callback_handler=callback_handler)
        if model_name == "GPT-3.5"
        else get_chain_replicate(vectorstore, callback_handler=callback_handler)
    )
