# snowChat 💬❄️

[![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/-OpenAI-412991?style=flat-square&logo=openai&logoColor=white)](https://openai.com/)
[![Snowflake](https://img.shields.io/badge/-Snowflake-29BFFF?style=flat-square&logo=snowflake&logoColor=white)](https://www.snowflake.com/en/)
[![Supabase](https://img.shields.io/badge/-Supabase-00C04A?style=flat-square&logo=supabase&logoColor=white)](https://www.supabase.io/)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://snowchat.streamlit.app/)

**snowChat** is an intuitive and user-friendly application that allows users to interact with their Snowflake data using natural language queries. Type in your questions or requests, and SnowChat will generate the appropriate SQL query and return the data you need. No more complex SQL queries or digging through tables - SnowChat makes it easy to access your data! By bringing data one step closer, SnowChat empowers users to make data-driven decisions faster and more efficiently, reducing the barriers between users and the insights they seek.

#

![pika-1682575152623-1x](https://user-images.githubusercontent.com/53030784/234772753-228ad22b-3939-47a5-a4cc-c2aa7c08577a.jpeg)

## 🌟 Features

- Interactive and user-friendly interface
- Integration with Snowflake Data Warehouse
- Utilizes OpenAI's GPT-3.5-turbo-16k and text-embedding-ada-002
- Uses Supabase PG-vector Vector Database for storing and searching through vectors

## 🛠️ Installation

1. Clone this repository:
   git clone https://github.com/yourusername/snowchat.git

2. Install the required packages:
   cd snowchat
   pip install -r requirements.txt

3. Set up your `OPENAI_API_KEY`, `ACCOUNT`, `USER_NAME`, `PASSWORD`, `ROLE`, `DATABASE`, `SCHEMA`,  `WAREHOUSE`, `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in project directory `secrets.toml`.

4. Make you're schemas and store them in docs folder that matches you're database.

5. Create supabase extention, table and function from the supabase/scripts.sql.

6. Run `python ingest.py` to get convert to embeddings and store as an index file.

7. Run the Streamlit app to start chatting:
   streamlit run main.py

## 📚 Usage

1. Launch the app by visiting the URL provided by Streamlit.
2. Type your query in natural language or SQL format in the input box.
3. Press "Submit" to generate the response.
4. The chatbot will generate a response based on your query and display the result, including any relevant data or SQL code.

## 🚀 Additional Enhancements

1. **Automation**: Create a generalized script that retrieves schema information from Snowflake automatically.
2. **Platform Integration**: Connect snowChat with popular communication platforms like Slack or Discord for seamless interaction.
3. **Voice Integration**: Implement voice recognition and text-to-speech functionality to make the chatbot more interactive and user-friendly.
4. **Advanced Analytics**: Integrate with popular data visualization libraries like Plotly or Matplotlib to generate interactive visualizations based on the user's queries (AutoGPT).

## 🤝 Contributing

Feel free to contribute to this project by submitting a pull request or opening an issue. Your feedback and suggestions are greatly appreciated!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://choosealicense.com/licenses/mit/) file for details.
