import snowflake.connector
import pandas as pd
import streamlit as st

conn = snowflake.connector.connect(
    user=st.secrets["USER_NAME"],
    password=st.secrets["PASSWORD"],
    account=st.secrets["ACCOUNT"],
    warehouse=st.secrets["WAREHOUSE"],
    role=st.secrets["ROLE"],
    database=st.secrets["DATABASE"],
    schema=st.secrets["SCHEMA"],
)

# Create a cursor object.
cur = conn.cursor()


# function - run sql query and return data
def query_data_warehouse(sql: str, parameters=None) -> any:
    """
    Executes snowflake sql query and returns result as data as dataframe.
    Example of parameters
    :param sql: sql query to be executed
    :param parameters: named parameters used in the sql query (defaulted as None)
    :return: dataframe
    """    
    if parameters is None:
        parameters = {}
    query = sql
    
    try:
        cur.execute("USE DATABASE " + st.secrets["DATABASE"])
        cur.execute("USE SCHEMA " + st.secrets["SCHEMA"])
        cur.execute(query, parameters)
        all_rows = cur.fetchall()
        field_names = [i[0] for i in cur.description]
        
    except snowflake.connector.errors.ProgrammingError as e:
        # print(f"Error in query_data_warehouse: {e}")
        return e
    
    finally:
        print("closing cursor")

    df = pd.DataFrame(all_rows)
    df.columns = field_names
    return df
