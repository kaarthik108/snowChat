
import pickle
import os
from langchain import FAISS
import openai
import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
from chain import get_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from streamlit import components

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

# embeddings = OpenAIEmbeddings()
# vectorstore = FAISS.load_local("faiss_index", embeddings)
with open("vectors.pkl", "rb") as f:
    print('Loading model...')
    vectorstore = pickle.load(f)
    
chain = get_chain(vectorstore)
# messages = []
# result = chain({"question": "how many records are thr in each table?", "chat_history": messages})
# print(result)
# print(result['answer'])
# print(result['chat_history'])
st.write("""
<link rel="preconnect" href="https://fonts.gstatic.com">
<link href="https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.0/css/all.min.css">
""", unsafe_allow_html=True)


st.write("""
<style>
    #input-container {
        position: fixed;
        bottom: 0;
        width: 100%;
        padding: 10px;
        background-color: white;
        z-index: 100;
    }
    .messages-container {
        height: calc(100vh - 180px);
        overflow-y: scroll;
        padding-bottom: 80px;
    }
    h1 {
        font-family: 'Roboto Slab', serif;
    }
    .user-icon {
        color: #3498db;
    }
    .bot-icon {
        color: #e74c3c;
    }
</style>
""", unsafe_allow_html=True)

st.title("snowChat")
st.subheader("Chat with Snowflake Database")

# model = st.selectbox(
#     "Select a model",
#     ("gpt-3.5-turbo", "gpt-4")
# )

if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Hello! I'm a chatbot designed to help you with Snowflake Database."]
if 'past' not in st.session_state:
    st.session_state['past'] = ["Welcome to snowChat!"]
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []

if 'messages' not in st.session_state:
    st.session_state['messages'] = [("Welcome to snowChat!", "Hello! I'm a chatbot designed to help you with Snowflake Database.")]


messages_container = st.container()

# Input container
input_container = st.container()
query = input_container.text_input("Query: ", key="input")
# messages = []

if 'messages' not in st.session_state:
    st.session_state['messages'] = []
    
if query:
    with st.spinner("generating..."):
        messages = st.session_state['messages']
        result = chain({"question": query, "chat_history": messages})
        print("result is", result)
        # chat_history = [(query, result["answer"])]
        messages.append((query, result["answer"]))
        # messages.append(result['answer'])

        st.session_state.past.append(query)
        st.session_state.generated.append(result['answer'])


with messages_container:
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
        # with st.expander("Show Messages"):
        #     st.write(messages)

# Create a custom div for the input container
st.markdown('<div id="input-container-placeholder"></div>', unsafe_allow_html=True)

# Move the input container to the custom div using JavaScript
components.v1.html(
    """
    <script>
    window.addEventListener('load', function() {
        const inputContainer = document.querySelector('.stTextInput');
        const inputContainerPlaceholder = document.getElementById('input-container-placeholder');
        inputContainer.id = 'input-container';
        inputContainerPlaceholder.appendChild(inputContainer);
        document.getElementById("input").focus();
    });
    </script>
    """,
    height=0,
)