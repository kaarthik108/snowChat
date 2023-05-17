
import asyncio
import openai
import streamlit as st
from callback import (
    QuestionGenCallbackHandler,
    StreamingLLMCallbackHandler
)
from chain import get_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from streamlit import components
from utils.snowflake import query_data_warehouse
from langchain.vectorstores import FAISS
from utils.snowddl import Snowddl
from utils.snowchat_ui import reset_chat_history, extract_code, message_func, is_sql_query

openai.api_key = st.secrets["OPENAI_API_KEY"]
MAX_INPUTS = 3
chat_history = []

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
def load_chain(_question_handler ,_stream_handler):
    '''
    Load the chain from the local file system

    Returns:
        chain (Chain): The chain object

    '''

    embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["OPENAI_API_KEY"])
    vectorstore = FAISS.load_local("faiss_index", embeddings)
    return get_chain(vectorstore, stream_handler=_stream_handler, question_handler=_question_handler)

# Instantiate callback handlers
_question_handler = QuestionGenCallbackHandler()
_stream_handler = StreamingLLMCallbackHandler()

chain = load_chain(_question_handler ,_stream_handler)
snow_ddl = Snowddl()

st.title("snowChat")
st.caption("Talk your way through data")

with open("ui/sidebar.md", "r") as sidebar_file:
    sidebar_content = sidebar_file.read()

with open("ui/styles.md", "r") as styles_file:
    styles_content = styles_file.read()

# Display the DDL for the selected table
st.sidebar.markdown(sidebar_content)

# Create a sidebar with a dropdown menu
selected_table = st.sidebar.selectbox(
    "Select a table:", options=list(snow_ddl.ddl_dict.keys()))
st.sidebar.markdown(f"### DDL for {selected_table} table")
st.sidebar.code(snow_ddl.ddl_dict[selected_table], language="sql")

st.write(styles_content, unsafe_allow_html=True)

if 'generated' not in st.session_state:
    st.session_state['generated'] = [
        "Hey there, I'm Snowman ☃️ , your SQL-speaking sidekick, ready to chat up Snowflake and fetch answers faster than a snowball fight in summer! ❄️🔍"]
if 'past' not in st.session_state:
    st.session_state['past'] = ["Hey!"]
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []

if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        ("Hello! I'm a chatbot designed to help you with Snowflake Database.")]

if "query_count" not in st.session_state:
    st.session_state["query_count"] = 0

RESET = True
messages_container = st.container()

with st.form(key='my_form'):
    query = st.text_input("Query: ", key="input", value="",
                          placeholder="Type your query here...", label_visibility="hidden")
    submit_button = st.form_submit_button(label='Submit')
col1, col2 = st.columns([1, 3.2])
reset_button = col1.button("Reset Chat History")

if reset_button or st.session_state['query_count'] >= MAX_INPUTS and RESET:
    RESET = False
    st.session_state['query_count'] = 0
    reset_chat_history()

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

def update_progress_bar(value, prefix, progress_bar=None):
    if progress_bar is None:
        progress_bar = st.empty()

    key = f'{prefix}_progress_bar_value'
    if key not in st.session_state:
        st.session_state[key] = 0

    st.session_state[key] = value
    progress_bar.progress(st.session_state[key])
    if value == 100:
        st.session_state[key] = 0
        progress_bar.empty()

async def make_query():
    submit_progress_bar = st.empty()
    messages = st.session_state['messages']
    update_progress_bar(33, 'submit', submit_progress_bar)

    result = await chain.acall(
        {"question": query, "chat_history": chat_history}
    )
    # print("result -----",result)
    update_progress_bar(66, 'submit', submit_progress_bar)
    chat_history.append((result["question"], result["answer"]))
    st.session_state['query_count'] += 1
    messages.append((query, result["answer"]))
    st.session_state.past.append(query)
    st.session_state.generated.append(result['answer'])
    update_progress_bar(100, 'submit', submit_progress_bar)

if len(query) > 2 and submit_button:
    asyncio.run( make_query())


def generate_df(to_extract: str):
    '''
    Generate a dataframe from the query by querying the data warehouse.

    Args:
        to_extract (str): The query

    Returns:
        df (pandas.DataFrame): The dataframe generated from the query

    '''
    df = query_data_warehouse(to_extract)
    st.dataframe(df, use_container_width=True)


with messages_container:
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message_func(st.session_state['past'][i], is_user=True)
            message_func(st.session_state["generated"][i])
            if i > 0 and is_sql_query(st.session_state["generated"][i]):
                code = extract_code(st.session_state["generated"][i])
                try:
                    if code:
                        generate_df(code)
                except:  # noqa: E722
                    pass

if st.session_state['query_count'] == MAX_INPUTS and RESET:
    st.warning(
        "You have reached the maximum number of inputs. The chat history will be cleared after the next input.")

col2.markdown(
    f'<div style="line-height: 2.5;">{st.session_state["query_count"]}/{MAX_INPUTS}</div>', unsafe_allow_html=True)

st.markdown('<div id="input-container-placeholder"></div>',
            unsafe_allow_html=True)

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
