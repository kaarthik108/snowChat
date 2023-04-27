
import os
import openai
import streamlit as st
from chain import get_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from streamlit import components
from utils import query_data_warehouse
from langchain.vectorstores import FAISS
from snowchat import SnowChat
from snowchat_ui import reset_chat_history, extract_code, message_func

openai.api_key = st.secrets["OPENAI_API_KEY"]
MAX_INPUTS = 3
# get current path 
current_path = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="snowChat",
    page_icon="❄️",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
        'Report a bug': "https://github.com/kaarthik108/snowChat",
        'About': '''snowChat is a chatbot designed to help you with Snowflake Database. It is built using OpenAI's GPT-4 and Streamlit. 
            Go to the GitHub repo to learn more about the project. https://github.com/kaarthik108/snowChat 
            '''
}
)

@st.cache_resource
def load_chain():
    '''
    Load the chain from the local file system
    
    Returns:
        chain (Chain): The chain object
    
    '''
    
    embeddings = OpenAIEmbeddings(openai_api_key = st.secrets["OPENAI_API_KEY"])
    vectorstore = FAISS.load_local("faiss_index", embeddings)
    return get_chain(vectorstore)
    
chain = load_chain()
snow_chat = SnowChat()

st.title("snowChat")
st.caption("Chat with your Snowflake Data")

with open("ui/sidebar.md", "r") as sidebar_file:
    sidebar_content = sidebar_file.read()

with open("ui/styles.md", "r") as styles_file:
    styles_content = styles_file.read()

# Display the DDL for the selected table
st.sidebar.markdown(sidebar_content)
                    
# Create a sidebar with a dropdown menu
selected_table = st.sidebar.selectbox("Select a table:", options=list(snow_chat.ddl_dict.keys()))
st.sidebar.markdown(f"### DDL for {selected_table} table")
st.sidebar.code(snow_chat.ddl_dict[selected_table], language="sql")

st.write(styles_content, unsafe_allow_html=True)

if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Hey there, I'm Chatty McQueryFace, your SQL-speaking sidekick, ready to chat up Snowflake and fetch answers faster than a snowball fight in summer! ❄️🔍"]
if 'past' not in st.session_state:
    st.session_state['past'] = ["Hey!"]
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []

if 'messages' not in st.session_state:
    st.session_state['messages'] = [("Hello! I'm a chatbot designed to help you with Snowflake Database.")]

RESET = True
messages_container = st.container()

with st.form(key='my_form'):
    query = st.text_input("Query: ", key="input", placeholder="Type your query here...", label_visibility="hidden")
    submit_button = st.form_submit_button(label='Submit')
reset_button = st.button("Reset Chat History")

if len(st.session_state['past']) >= MAX_INPUTS and not RESET:
    st.warning("You have reached the maximum number of inputs. The chat history will be cleared after the next input.")

if reset_button:
    RESET = False
    reset_chat_history()
    
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if len(query) > 2 and submit_button:
    with st.spinner("generating..."):
        messages = st.session_state['messages']
        result = chain({"query": query})
        messages.append((query, result["result"]))
        # print("relevant doc: ", result['source_documents'])
        st.session_state.past.append(query)
        st.session_state.generated.append(result['result'])

@st.cache_resource
def generate_df(op):
    '''
    Generate a dataframe from the query by querying the data warehouse.
    
    Args:
        op (str): The query
        
    Returns:
        df (pandas.DataFrame): The dataframe generated from the query
    
    '''
    df = query_data_warehouse(op)
    st.dataframe(df, use_container_width=True)

with messages_container:
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            print("for loop i is", i)
            message_func(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="Adventurer")
            message_func(st.session_state["generated"][i], key=str(i), avatar_style="Adventurer")
            op = extract_code(st.session_state["generated"][i])
            try:
                if len(op) > 5:
                    with st.spinner("In progress..."):
                        generate_df(op)
            except:
                pass
            

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