
import pickle
import html
import os
import openai
import streamlit as st
from streamlit_chat import message
from chain import get_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from streamlit import components
from utils import query_data_warehouse
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

openai.api_key = st.secrets["OPENAI_API_KEY"]
MAX_INPUTS = 3
# get current path 
current_path = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_chain():
    
    embeddings = OpenAIEmbeddings(openai_api_key = st.secrets["OPENAI_API_KEY"])
    vectorstore = FAISS.load_local("faiss_index", embeddings)
    return get_chain(vectorstore)
    
chain = load_chain()

st.title("snowChat")
st.caption("Chat with your Snowflake Data")

class SnowChat:
    def __init__(self):
        self.ddl_dict = self.load_ddls()

    @staticmethod
    def load_ddls():
        ddl_files = {
            "TRANSACTIONS": "sql/ddl_transactions.sql",
            "ORDER_DETAILS": "sql/ddl_orders.sql",
            "PAYMENTS": "sql/ddl_payments.sql",
            "PRODUCTS": "sql/ddl_products.sql",
            "CUSTOMER_DETAILS": "sql/ddl_customer.sql"
        }

        ddl_dict = {}
        for table_name, file_name in ddl_files.items():
            with open(file_name, "r") as f:
                ddl_dict[table_name] = f.read()
                # print(f"DDL for table loaded. {ddl_dict[table_name]} ")
        return ddl_dict

snow_chat = SnowChat()

# Display the DDL for the selected table
st.sidebar.markdown(f''' 
# SnowChat - Chat with Your Snowflake Data

SnowChat is an intuitive and user-friendly application that allows you to interact with your Snowflake data using natural language queries. Type in your questions or requests, and SnowChat will generate the appropriate SQL query and return the data you need. No more complex SQL queries or digging through tables - SnowChat makes it easy to access your data!

## Features

- **Natural Language Processing**: Understands your text queries and converts them into SQL queries.
- **Instant Results**: Fetches the data from your Snowflake database and displays the results quickly.
- **GEN AI models**: Uses OpenAI's GPT-4 and vector search to generate SQL queries.

Here are some example queries you can try with SnowChat:

- Show me the total revenue for each product category.
- Who are the top 10 customers by sales?
- What is the average order value for each region?
- How many orders were placed last week?
- Display the list of products with their prices.

'''
                    )
                    
# Create a sidebar with a dropdown menu
selected_table = st.sidebar.selectbox("Select a table:", options=list(snow_chat.ddl_dict.keys()))
st.sidebar.markdown(f"### DDL for {selected_table} table")
st.sidebar.code(snow_chat.ddl_dict[selected_table], language="sql")

def extract_code(text):
    # Use OpenAI's GPT-3 to extract the SQL code
    response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'user', 'content': f"Extract only the code do not add text or any apostrophes or any sql keywords \n\n{text}"},
    ],
    # stream=True  # this time, we set stream=True
    )

    # Extract the SQL code from the response
    sql_code = response.choices[0].message.content

    return sql_code

@st.cache_resource
def message(text, is_user=False, key=None, avatar_style="Adventurer"):
    text = html.escape(text)
    if is_user:
        avatar_url = f"https://avataaars.io/?avatarStyle=Circle&topType=ShortHairShortFlat&accessoriesType=Blank&hairColor=BrownDark&facialHairType=Blank&clotheType=Hoodie&clotheColor=Blue03&eyeType=Default&eyebrowType=Default&mouthType=Default&skinColor=Light"
        message_alignment = "flex-end"
        message_bg_color = "linear-gradient(135deg, #00B2FF 0%, #006AFF 100%)"
        avatar_class = "user-avatar"
        st.write(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
                    <div style="background: {message_bg_color}; color: white; border-radius: 20px; padding: 10px; margin-right: 5px; max-width: 75%;">
                        {text}
                    </div>
                            <img src="{avatar_url}" class="{avatar_class}" alt="avatar" />

                </div>
                """, unsafe_allow_html=True)
    else:
        avatar_url = f"https://avataaars.io/?avatarStyle=Circle&topType=LongHairBun&accessoriesType=Blank&hairColor=BrownDark&facialHairType=Blank&clotheType=BlazerShirt&eyeType=Default&eyebrowType=Default&mouthType=Default&skinColor=Light"
        message_alignment = "flex-start"
        message_bg_color = "#71797E"
        avatar_class = "bot-avatar"
        st.write(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
                    <img src="{avatar_url}" class="{avatar_class}" alt="avatar" />
                    <div style="background: {message_bg_color}; color: white; border-radius: 20px; padding: 10px; margin-right: 5px; max-width: 75%;">
                        {text}
                    </div>
                </div>
                """, unsafe_allow_html=True)

def reset_chat_history():
    st.session_state['generated'] = ["WOW 🤪"]
    st.session_state['past'] = ["Welcome to snowChat! I'm a chatbot designed to help you with Snowflake Database."]
    st.session_state["stored_session"] = []
    st.session_state['messages'] = [("Hello! I'm a chatbot designed to help you with Snowflake Database.")]

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
    st.session_state['generated'] = ["WOW 🤪"]
if 'past' not in st.session_state:
    st.session_state['past'] = ["Welcome to snowChat! I'm a chatbot designed to help you with Snowflake Database."]
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
        print("relevant doc: ",result['source_documents'])
        st.session_state.past.append(query)
        st.session_state.generated.append(result['result'])



with messages_container:
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="Adventurer")
            message(st.session_state["generated"][i], key=str(i), avatar_style="Adventurer")
            op = extract_code(st.session_state["generated"][i])
            try:
                if len(op) > 2:
                    with st.spinner("In progress..."):
                        # print("extracted sql is", op)
                        df = query_data_warehouse(op)                        
                        st.dataframe(df, use_container_width=True)
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