from langchain.vectorstores import Chroma
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain, ChatVectorDBChain
# from langchain.document_loaders import DirectoryLoader
# from langchain.vectorstores import FAISS
from langchain.prompts.prompt import PromptTemplate
# from langchain.chat_models import ChatOpenAI

TEMPLATE = """Write either sql code in snowflake database based on the following question.
If you don't know the answer, just say "Hmm, I'm not sure. I am trained only to answer sql related queries. Please try again." Don't try to make up an answer.
Use snowflake database documentation https://docs.snowflake.com/sql-reference-commands for writing sql code.

Question: {question}
{context}
Answer in code format:"""
QA_PROMPT = PromptTemplate(template=TEMPLATE, input_variables=["question", "context"])


def get_chain(vectorstore):
    """
    Get a chain for chatting with a vector database.
    """
    llm = ChatOpenAI(model_name='gpt-4', temperature=0.2)
    chat_vector_db_chain = ChatVectorDBChain.from_llm(llm=llm, vectorstore=vectorstore, qa_prompt=QA_PROMPT, verbose=True)
    
    return chat_vector_db_chain
