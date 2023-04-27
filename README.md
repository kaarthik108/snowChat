# snowChat 🗨️❄️

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![OpenAI](https://img.shields.io/badge/-OpenAI-412991?style=flat-square&logo=openai&logoColor=white)
![Snowflake](https://img.shields.io/badge/-Snowflake-29BFFF?style=flat-square&logo=snowflake&logoColor=white)

snowChat is an interactive chatbot that helps you access and explore data from your Snowflake Database. It understands natural language queries and retrieves the requested information using advanced natural language processing techniques.

![pika-1682575152623-1x](https://user-images.githubusercontent.com/53030784/234772753-228ad22b-3939-47a5-a4cc-c2aa7c08577a.jpeg)


## Features

- Interactive and user-friendly interface
- Integration with Snowflake Data Warehouse
- Utilizes OpenAI's GPT-4 technology for natural language processing

## Installation

1. Clone this repository:
   git clone https://github.com/yourusername/snowchat.git

2. Install the required packages:
   cd snowchat
   pip install -r requirements.txt

3. Set up your `OPENAI_API_KEY`, `ACCOUNT`, `USER_NAME`, `PASSWORD`, `ROLE`, `DATABASE`, `SCHEMA` and `WAREHOUSE` in project directory `secrets.toml`.

4. Make you're schema.md that matches you're database.

5. Run `python ingest.py` to get convert to embeddings and store as an index file.

6. Run the Streamlit app:
   streamlit run main.py

## Usage

1. Launch the app by visiting the URL provided by Streamlit.
2. Type your query in natural language or SQL format in the input box.
3. Press "Submit" to generate the response.
4. The chatbot will generate a response based on your query and display the result, including any relevant data or SQL code.

## Contributing

Feel free to contribute to this project by submitting a pull request or opening an issue. Your feedback and suggestions are greatly appreciated!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
