
import pickle
import re
import os
from langchain import FAISS
import openai
import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
from chain import get_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from streamlit import components
from utils import query_data_warehouse
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

with open("vectors.pkl", "rb") as f:
    print('Loading model...')
    vectorstore = pickle.load(f)
    
chain = get_chain(vectorstore)

st.title("snowChat")
st.subheader("Chat with Snowflake Database")

ddl_transactions = '''
CREATE OR REPLACE TABLE TRANSACTIONS (
    TRANSACTION_ID NUMBER(38,0) NOT NULL,
    ORDER_ID NUMBER(38,0),
    PRODUCT_ID NUMBER(38,0),
    QUANTITY NUMBER(38,0),
    PRICE NUMBER(10,2),
    PRIMARY KEY (TRANSACTION_ID),
    FOREIGN KEY (ORDER_ID) REFERENCES STREAM_HACKATHON.STREAMLIT.ORDER_DETAILS(ORDER_ID)
);
'''

# Add more DDLs for other tables here
# ddl_table2 = '''...'''
# ddl_table3 = '''...'''

# Create a dictionary to store the table names and their corresponding DDLs
ddl_dict = {
    "TRANSACTIONS": ddl_transactions,
    # "TABLE2": ddl_table2,
    # "TABLE3": ddl_table3,
}

# Create a sidebar with a dropdown menu
selected_table = st.sidebar.selectbox("Select a table:", options=list(ddl_dict.keys()))

# Display the DDL for the selected table
st.sidebar.markdown(f"### DDL for {selected_table} table")
st.sidebar.code(ddl_dict[selected_table], language="sql")

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
    h1 {
        font-family: 'Roboto Slab', serif;
    }
    .user-avatar {
        float: right;
        width: 40px;
        height: 40px;
        margin-left: 5px;
        margin-bottom: -10px;
        border-radius: 50%;
        object-fit: cover;
    }
    .bot-avatar {
        float: left;
        width: 40px;
        height: 40px;
        margin-right: 5px;
        border-radius: 50%;
        object-fit: cover;
    }
</style>
""", unsafe_allow_html=True)


if 'generated' not in st.session_state:
    st.session_state['generated'] = ["WOW :smile:"]
if 'past' not in st.session_state:
    st.session_state['past'] = ["Welcome to snowChat! I'm a chatbot designed to help you with Snowflake Database."]
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []

if 'messages' not in st.session_state:
    st.session_state['messages'] = [("Hello! I'm a chatbot designed to help you with Snowflake Database.")]

def extract_code(text):
    # Use OpenAI's GPT-3 to extract the SQL code
    response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'user', 'content': f"Extract the SQL code from the following text snippet ignore baptics and sql keyword:\n\n{text}"},
    ],
    # stream=True  # this time, we set stream=True
    )

    # Extract the SQL code from the response
    sql_code = response.choices[0].message.content

    return sql_code

messages_container = st.container()

# Add a button inside the container to get the value of the text input widget
# Input container
# input_container = st.container()
# form = st.form()

# query = input_container.text_input("", key="input", placeholder="Type your query here...", label_visibility="hidden")
with st.form(key='my_form'):
    query = st.text_input("", key="input", placeholder="Type your query here...", label_visibility="hidden")
    submit_button = st.form_submit_button(label='Submit')

# messages = []

if 'messages' not in st.session_state:
    st.session_state['messages'] = []
    
if len(query) > 2 and submit_button:
    with st.spinner("generating..."):
        messages = st.session_state['messages']
        result = chain({"question": query, "chat_history": []})
        print("result is", result)
        # chat_history = [(query, result["answer"])]
        messages.append((query, result["answer"]))
        # messages.append(result['answer'])

        st.session_state.past.append(query)
        st.session_state.generated.append(result['answer'])

def message(text, is_user=False, key=None, avatar_style="Adventurer"):
    if is_user:
        avatar_url = f"https://avataaars.io/?avatarStyle=Circle&topType=ShortHairShortFlat&accessoriesType=Blank&hairColor=BrownDark&facialHairType=Blank&clotheType=Hoodie&clotheColor=Blue03&eyeType=Default&eyebrowType=Default&mouthType=Default&skinColor=Light"
        message_alignment = "flex-end"
        message_bg_color = "linear-gradient(135deg, #ff5f6d 0%, #ffc371 100%)"
        avatar_class = "user-avatar"
        st.write(f"""
    <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
        <div style="background: {message_bg_color}; color: white; border-radius: 5px; padding: 10px; margin-right: 5px; max-width: 75%;">
            {text}
        </div>
                <img src="{avatar_url}" class="{avatar_class}" alt="avatar" />

    </div>
    """, unsafe_allow_html=True)
    else:
        avatar_url = f"https://avataaars.io/?avatarStyle=Circle&topType=LongHairBun&accessoriesType=Blank&hairColor=BrownDark&facialHairType=Blank&clotheType=BlazerShirt&eyeType=Default&eyebrowType=Default&mouthType=Default&skinColor=Light"
        message_alignment = "flex-start"
        message_bg_color = "linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%)"
        avatar_class = "bot-avatar"
        st.write(f"""
    <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
        <img src="{avatar_url}" class="{avatar_class}" alt="avatar" />
        <div style="background: {message_bg_color}; color: white; border-radius: 5px; padding: 10px; margin-right: 5px; max-width: 75%;">
            {text}
        </div>
    </div>
    """, unsafe_allow_html=True)
    


with messages_container:
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="Adventurer")
            message(st.session_state["generated"][i], key=str(i), avatar_style="Adventurer")
            op = extract_code(st.session_state["generated"][i])
            try:
                if len(op) > 6:
                    print("op is", op)
                    df = query_data_warehouse(op)
                    st.spinner("Loading data...")
                    st.dataframe(df)
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