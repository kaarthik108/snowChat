import os
import re
import warnings

import streamlit as st
from snowflake.snowpark.exceptions import SnowparkSQLException

from snowchat import (
    load_chain,
    SnowflakeConnection,
    StreamlitUICallbackHandler,
    message_func,
    Snowddl,
)

warnings.filterwarnings("ignore")

chat_history = []
snow_ddl = Snowddl()

st.title("snowChat")
st.caption("Talk your way through data")

# Define the path to the docs folder
DOCS_PATH = 'docs/'

# Get a list of all .md and .mdx files in the docs folder
doc_files = [f for f in os.listdir(DOCS_PATH) if f.endswith(('.md', '.mdx'))]


# Create three columns
col1, col2, col3 = st.columns([2,1,2])

# Place the toggle in the middle column
with col2:
    chat = st.toggle("Chat-mode")  # Changed from st.toggle to st.button as st.toggle is not a valid Streamlit function

st.divider()
if chat:
    model = st.radio(
        "",
        options=["✨ GPT-3.5", "🐐 code-LLama"],
        index=0,
        horizontal=True,
    )

    st.session_state["model"] = model

    INITIAL_MESSAGE = [
        {"role": "user", "content": "Hi!"},
        {
            "role": "assistant",
            "content": "Hey there, I'm Chatty McQueryFace, your SQL-speaking sidekick, ready to chat up Snowflake and fetch answers faster than a snowball fight in summer! ❄️🔍",
        },
    ]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sidebar_path = os.path.join(script_dir, "ui", "sidebar.md")
    styles_path = os.path.join(script_dir, "ui", "styles.md")

    # Add a reset button
    if st.sidebar.button("Reset Chat"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.session_state["messages"] = INITIAL_MESSAGE
        st.session_state["history"] = []


    print(st.session_state.keys())
    # Initialize the chat messages history
    if "messages" not in st.session_state:
        st.session_state["messages"] = INITIAL_MESSAGE

    if "history" not in st.session_state:
        st.session_state["history"] = []

    if "model" not in st.session_state:
        st.session_state["model"] = model

    # Prompt for user input and save
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})

    for message in st.session_state.messages:
        message_func(
            message["content"],
            True if message["role"] == "user" else False,
            True if message["role"] == "data" else False,
        )

    callback_handler = StreamlitUICallbackHandler()

    chain = load_chain(st.session_state["model"], callback_handler)


    def append_chat_history(question, answer):
        st.session_state["history"].append((question, answer))


    def get_sql(text):
        sql_match = re.search(r"```sql\n(.*)\n```", text, re.DOTALL)
        return sql_match.group(1) if sql_match else None


    def append_message(content, role="assistant", display=False):
        message = {"role": role, "content": content}
        if model == "LLama-2":  # unable to get streaming working with LLama-2
            message_func(content, False, display)
        st.session_state.messages.append(message)
        if role != "data":
            append_chat_history(st.session_state.messages[-2]["content"], content)

        if callback_handler.has_streaming_ended:
            callback_handler.has_streaming_ended = False
            return


    def handle_sql_exception(query, conn, e, retries=2):
        append_message("Uh oh, I made an error, let me try to fix it..")
        error_message = (
            "You gave me a wrong SQL. FIX The SQL query by searching the schema definition:  \n```sql\n"
            + query
            + "\n```\n Error message: \n "
            + str(e)
        )
        new_query = chain({"question": error_message, "chat_history": ""})["answer"]
        append_message(new_query)
        if get_sql(new_query) and retries > 0:
            return execute_sql(get_sql(new_query), conn, retries - 1)
        else:
            append_message("I'm sorry, I couldn't fix the error. Please try again.")
            return None


    def execute_sql(query, conn, retries=2):
        if re.match(r"^\s*(drop|alter|truncate|delete|insert|update)\s", query, re.I):
            append_message("Sorry, I can't execute queries that can modify the database.")
            return None
        try:
            return conn.sql(query).collect()
        except SnowparkSQLException as e:
            return handle_sql_exception(query, conn, e, retries)


    if st.session_state.messages[-1]["role"] != "assistant":
        content = st.session_state.messages[-1]["content"]
        if isinstance(content, str):
            result = chain(
                {"question": content, "chat_history": st.session_state["history"]}
            )["answer"]
            # print(result)
            append_message(result)
            if get_sql(result):
                conn = SnowflakeConnection().get_session()
                df = execute_sql(get_sql(result), conn)
                if df is not None:
                    callback_handler.display_dataframe(df)
                    append_message(df, "data", True)

else:
    # Display radio buttons in containers in the sidebar for selecting the documentation file
    if 'selected_doc' not in st.session_state:
        st.session_state['selected_doc'] = doc_files[0]

    for doc_file in doc_files:
        with st.sidebar.container():
            if st.radio("", options=[doc_file], key=doc_file) == doc_file:
                st.session_state['selected_doc'] = doc_file

    # Read and render the content of the selected file
    with open(os.path.join(DOCS_PATH, st.session_state['selected_doc']), 'r') as file:
        content = file.read()
    st.markdown(content, unsafe_allow_html=True)
