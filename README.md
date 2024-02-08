# snowChat 💬❄️

[![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/-OpenAI-412991?style=flat-square&logo=openai&logoColor=white)](https://openai.com/)
[![Snowflake](https://img.shields.io/badge/-Snowflake-29BFFF?style=flat-square&logo=snowflake&logoColor=white)](https://www.snowflake.com/en/)
[![Supabase](https://img.shields.io/badge/-Supabase-00C04A?style=flat-square&logo=supabase&logoColor=white)](https://www.supabase.io/)
[![AWS](https://img.shields.io/badge/-AWS-232F3E?style=flat-square&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Langchain](https://img.shields.io/badge/-Langchain-gray?style=flat-square)](https://www.langchain.com/)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://snowchat.streamlit.app/)

![156shots_so](https://github.com/kaarthik108/snowChat/assets/53030784/7538d25b-a2d4-4a2c-9601-fb4c7db3c0b6)

**snowChat** is an intuitive and user-friendly application that allows users to interact with their Snowflake data using natural language queries. Type in your questions or requests, and SnowChat will generate the appropriate SQL query and return the data you need. No more complex SQL queries or digging through tables - SnowChat makes it easy to access your data! By bringing data one step closer, SnowChat empowers users to make data-driven decisions faster and more efficiently, reducing the barriers between users and the insights they seek.

## Supported LLM's

- GPT-3.5-turbo-0125
- CodeLlama-70B
- Mistral Medium

#

https://github.com/kaarthik108/snowChat/assets/53030784/24105e23-69d3-4676-b6d6-d8157dd1580a

#

## 🌟 Features

- **Conversational AI**: Harnesses ChatGPT to translate natural language into precise SQL queries.
- **Conversational Memory**: Retains context for interactive, dynamic responses.
- **Snowflake Integration**: Offers seamless, real-time data insights straight from your Snowflake database.
- **Self-healing SQL**: Proactively suggests solutions for SQL errors, streamlining data access.
- **Interactive User Interface**: Transforms data querying into an engaging conversation, complete with a chat reset option.

## 🛠️ Installation

1. Clone this repository:
   git clone https://github.com/yourusername/snowchat.git

2. Install the required packages:
   cd snowchat
   pip install -r requirements.txt

3. Set up your `OPENAI_API_KEY`, `ACCOUNT`, `USER_NAME`, `PASSWORD`, `ROLE`, `DATABASE`, `SCHEMA`, `WAREHOUSE`, `SUPABASE_URL` , `SUPABASE_SERVICE_KEY` and `REPLICATE_API_TOKEN` in project directory `secrets.toml`.

4. Make you're schemas and store them in docs folder that matches you're database.

5. Create supabase extention, table and function from the supabase/scripts.sql.

6. Run `python ingest.py` to get convert to embeddings and store as an index file.

7. Run the Streamlit app to start chatting:
   streamlit run main.py

## 🚀 Additional Enhancements

1. **Platform Integration**: Connect snowChat with popular communication platforms like Slack or Discord for seamless interaction.
2. **Voice Integration**: Implement voice recognition and text-to-speech functionality to make the chatbot more interactive and user-friendly.
3. **Advanced Analytics**: Integrate with popular data visualization libraries like Plotly or Matplotlib to generate interactive visualizations based on the user's queries (AutoGPT).

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=kaarthik108/snowChat&type=Date)]

## 🤝 Contributing

Feel free to contribute to this project by submitting a pull request or opening an issue. Your feedback and suggestions are greatly appreciated!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://choosealicense.com/licenses/mit/) file for details.
