from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import ChatVectorDBChain
from langchain.document_loaders import DirectoryLoader
from langchain.vectorstores import FAISS
from langchain.prompts.prompt import PromptTemplate

template = """Write either sql code in snowflake database based on the following question or answer questions about the company Laybuy.
If you don't know the answer, just say "Hmm, I'm not sure. I am trained only to answer sql related queries. Please try again." Don't try to make up an answer.
Use snowflake database documentation https://docs.snowflake.com/sql-reference-commands for writing sql code.

Laybuy is a FinTech company that provides a buy now, pay later service to customers.
Customers can use Laybuy to purchase goods from online retailers and pay for them in 6 equal instalments over six weeks.

Question: {question}
{context}
Answer in code format:"""
QA_PROMPT = PromptTemplate(template=template, input_variables=["question", "context"])


def get_chain(vectorstore):
    llm = OpenAI(model_name='gpt-4', top_p = 1)
    qa = ChatVectorDBChain.from_llm(llm=llm, vectorstore=vectorstore, qa_prompt=QA_PROMPT, verbose=True, return_source_documents=True)
    return qa