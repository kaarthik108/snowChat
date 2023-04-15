
import os
import snowflake.connector
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

conn = snowflake.connector.connect(
    user=os.getenv("USER_NAME"),
    password=os.getenv("PASSWORD"),
    account=os.getenv("ACCOUNT"),
    warehouse=os.getenv("WAREHOUSE"),
    role=os.getenv("ROLE"),
    database=os.getenv("DATABASE"),
    schema=os.getenv("SCHEMA"),
)

# Create a cursor object.
cur = conn.cursor()


# function - run sql query and return data
def query_data_warehouse(sql: str, parameters=None) -> any:
    """
    Executes snowflake sql query and returns result as data as dataframe.
    Example of parameters
    {"order_date": '2022-07-13', "customer_region": 1} can be used to reference variable in sql query %(order_date)s
     and %(customer_region)s.
    :param sql: sql query to be executed
    :param parameters: named parameters used in the sql query (defaulted as None)
    :return: dataframe
    """
    if parameters is None:
        parameters = {}
    query = sql

    try:
        cur.execute("USE DATABASE " + os.getenv("DATABASE"))
        cur.execute(query, parameters)
        print("executing query")
        all_rows = cur.fetchall()
        field_names = [i[0] for i in cur.description]
    finally:
        print("closing cursor")

    df = pd.DataFrame(all_rows)
    df.columns = field_names
    return df

# query_data_warehouse("SELECT * FROM STREAMLIT.CUSTOMER_DETAILS")