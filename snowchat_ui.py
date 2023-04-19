import html
import streamlit as st
import openai

@st.cache
def message_func(text, is_user=False, key=None, avatar_style="Adventurer"):
    text = html.escape(text)
    if is_user:
        avatar_url = "https://avataaars.io/?avatarStyle=Circle&topType=ShortHairShortFlat&accessoriesType=Blank&hairColor=BrownDark&facialHairType=Blank&clotheType=Hoodie&clotheColor=Blue03&eyeType=Default&eyebrowType=Default&mouthType=Default&skinColor=Light"
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
        avatar_url = "https://avataaars.io/?avatarStyle=Circle&topType=LongHairBun&accessoriesType=Blank&hairColor=BrownDark&facialHairType=Blank&clotheType=BlazerShirt&eyeType=Default&eyebrowType=Default&mouthType=Default&skinColor=Light"
        message_alignment = "flex-start"
        message_bg_color = "#71797E"
        avatar_class = "bot-avatar"
        st.write(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
                    <img src="{avatar_url}" class="{avatar_class}" alt="avatar" />
                    <div style="background: {message_bg_color}; color: white; border-radius: 20px; padding: 10px; margin-right: 5px; max-width: 75%;">
                        {text} \n </div>
                </div>
                """, unsafe_allow_html=True)


def reset_chat_history():
    st.session_state['generated'] = ["WOW 🤪"]
    st.session_state['past'] = ["Welcome to snowChat! I'm a chatbot designed to help you with Snowflake Database."]
    st.session_state["stored_session"] = []
    st.session_state['messages'] = [("Hello! I'm a chatbot designed to help you with Snowflake Database.")]



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
