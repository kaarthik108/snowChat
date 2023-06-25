from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import streamlit as st

template = """Considering the provided chat history and a subsequent question, rewrite the follow-up question to be an independent query. Alternatively, conclude the conversation if it appears to be complete.
Chat History:\"""
{chat_history}
\"""
Follow Up Input: \"""
{question}
\"""
Standalone question:"""

condense_question_prompt = PromptTemplate.from_template(template)

TEMPLATE = """ You're a helpful AI assistant who is specialized in data analysis using SQL. You have to write sql code in snowflake database based on the following question. Give a one or two sentences about how did you arrive at that sql code. (do not assume anything if the column is not available then say it is not available, do not make up code). Write the sql code in markdown format.

Question: {question}
{context}

Answer:

"""
QA_PROMPT = PromptTemplate(template=TEMPLATE, input_variables=["question", "context"])


def get_chain(vectorstore):
    """
    Get a chain for chatting with a vector database.
    """
    q_llm = OpenAI(
        temperature=0,
        openai_api_key=st.secrets["OPENAI_API_KEY"],
        model_name="gpt-3.5-turbo-16k",
    )

    llm = OpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=st.secrets["OPENAI_API_KEY"],
    )

    question_generator = LLMChain(llm=q_llm, prompt=condense_question_prompt)

    doc_chain = load_qa_chain(llm=llm, chain_type="stuff", prompt=QA_PROMPT)
    chain = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(),
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
    )
    return chain
