import re
import warnings

import streamlit as st
from snowflake.snowpark.exceptions import SnowparkSQLException

from chain import load_chain

# from utils.snow_connect import SnowflakeConnection
from utils.snowchat_ui import StreamlitUICallbackHandler, message_func
from utils.snowddl import Snowddl

warnings.filterwarnings("ignore")
chat_history = []
snow_ddl = Snowddl()

gradient_text_html = """
<style>
.gradient-text {
    font-weight: bold;
    background: -webkit-linear-gradient(left, red, orange);
    background: linear-gradient(to right, red, orange);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline;
    font-size: 3em;
}
</style>
<div class="gradient-text">snowChat</div>
"""

st.markdown(gradient_text_html, unsafe_allow_html=True)

st.caption("Talk your way through data")

model_options = {
    "gpt-4o-mini": "GPT-4o Mini",
    "llama-3.1-405b": "Llama 3.1 405B",
    "gemma2-9b": "Gemma 2 9B",
    "claude3-haiku": "Claude 3 Haiku",
    "mixtral-8x22b": "Mixtral 8x22B",
}

model = st.radio(
    "Choose your AI Model:",
    options=list(model_options.keys()),
    format_func=lambda x: model_options[x],
    index=0,
    horizontal=True,
)
st.session_state["model"] = model

if "toast_shown" not in st.session_state:
    st.session_state["toast_shown"] = False

if "rate-limit" not in st.session_state:
    st.session_state["rate-limit"] = False

# Show the toast only if it hasn't been shown before
if not st.session_state["toast_shown"]:
    st.toast("The snowflake data retrieval is disabled for now.", icon="👋")
    st.session_state["toast_shown"] = True

# Show a warning if the model is rate-limited
if st.session_state["rate-limit"]:
    st.toast("Probably rate limited.. Go easy folks", icon="⚠️")
    st.session_state["rate-limit"] = False

if st.session_state["model"] == "Mixtral 8x7B":
    st.warning("This is highly rate-limited. Please use it sparingly", icon="⚠️")

INITIAL_MESSAGE = [
    {"role": "user", "content": "Hi!"},
    {
        "role": "assistant",
        "content": "Hey there, I'm Chatty McQueryFace, your SQL-speaking sidekick, ready to chat up Snowflake and fetch answers faster than a snowball fight in summer! ❄️🔍",
    },
]

with open("ui/sidebar.md", "r") as sidebar_file:
    sidebar_content = sidebar_file.read()

with open("ui/styles.md", "r") as styles_file:
    styles_content = styles_file.read()

st.sidebar.markdown(sidebar_content)

selected_table = st.sidebar.selectbox(
    "Select a table:", options=list(snow_ddl.ddl_dict.keys())
)
st.sidebar.markdown(f"### DDL for {selected_table} table")
st.sidebar.code(snow_ddl.ddl_dict[selected_table], language="sql")

# Add a reset button
if st.sidebar.button("Reset Chat"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state["messages"] = INITIAL_MESSAGE
    st.session_state["history"] = []

st.sidebar.markdown(
    "**Note:** <span style='color:red'>The snowflake data retrieval is disabled for now.</span>",
    unsafe_allow_html=True,
)

st.write(styles_content, unsafe_allow_html=True)

# Initialize the chat messages history
if "messages" not in st.session_state.keys():
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
        model,
    )

callback_handler = StreamlitUICallbackHandler(model)

chain = load_chain(st.session_state["model"], callback_handler)


def append_chat_history(question, answer):
    st.session_state["history"].append((question, answer))


def get_sql(text):
    sql_match = re.search(r"```sql\n(.*)\n```", text, re.DOTALL)
    return sql_match.group(1) if sql_match else None


def append_message(content, role="assistant"):
    """Appends a message to the session state messages."""
    if content.strip():
        st.session_state.messages.append({"role": role, "content": content})


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


if (
    "messages" in st.session_state
    and st.session_state["messages"][-1]["role"] != "assistant"
):
    user_input_content = st.session_state["messages"][-1]["content"]

    if isinstance(user_input_content, str):
        callback_handler.start_loading_message()

        result = chain.invoke(
            {
                "question": user_input_content,
                "chat_history": [h for h in st.session_state["history"]],
            }
        )
        append_message(result.content)

if (
    st.session_state["model"] == "Mixtral 8x7B"
    and st.session_state["messages"][-1]["content"] == ""
):
    st.session_state["rate-limit"] = True

    # if get_sql(result):
    #     conn = SnowflakeConnection().get_session()
    #     df = execute_sql(get_sql(result), conn)
    #     if df is not None:
    #         callback_handler.display_dataframe(df)
    #         append_message(df, "data", True)
