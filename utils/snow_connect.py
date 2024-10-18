from typing import Any, Dict
import json
import requests
import streamlit as st
from snowflake.snowpark.session import Session


class SnowflakeConnection:
    """
    This class is used to establish a connection to Snowflake and execute queries with optional caching.

    Attributes
    ----------
    connection_parameters : Dict[str, Any]
        A dictionary containing the connection parameters for Snowflake.
    session : snowflake.snowpark.Session
        A Snowflake session object.

    Methods
    -------
    get_session()
        Establishes and returns the Snowflake connection session.
    execute_query(query: str, use_cache: bool = True)
        Executes a Snowflake SQL query with optional caching.
    """

    def __init__(self):
        self.connection_parameters = self._get_connection_parameters_from_env()
        self.session = None
        self.cloudflare_account_id = st.secrets["CLOUDFLARE_ACCOUNT_ID"]
        self.cloudflare_namespace_id = st.secrets["CLOUDFLARE_NAMESPACE_ID"]
        self.cloudflare_api_token = st.secrets["CLOUDFLARE_API_TOKEN"]
        self.headers = {
            "Authorization": f"Bearer {self.cloudflare_api_token}",
            "Content-Type": "application/json"
        }

    @staticmethod
    def _get_connection_parameters_from_env() -> Dict[str, Any]:
        return {
            "account": st.secrets["ACCOUNT"],
            "user": st.secrets["USER_NAME"],
            "password": st.secrets["PASSWORD"],
            "warehouse": st.secrets["WAREHOUSE"],
            "database": st.secrets["DATABASE"],
            "schema": st.secrets["SCHEMA"],
            "role": st.secrets["ROLE"],
        }

    def get_session(self):
        """
        Establishes and returns the Snowflake connection session.
        Returns:
            session: Snowflake connection session.
        """
        if self.session is None:
            self.session = Session.builder.configs(self.connection_parameters).create()
            self.session.sql_simplifier_enabled = True
        return self.session

    def _construct_kv_url(self, key: str) -> str:
        return f"https://api.cloudflare.com/client/v4/accounts/{self.cloudflare_account_id}/storage/kv/namespaces/{self.cloudflare_namespace_id}/values/{key}"

    def get_from_cache(self, key: str) -> str:
        url = self._construct_kv_url(key)
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            print("\n\n\nCache hit\n\n\n")
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Cache miss or error: {e}")
        return None

    def set_to_cache(self, key: str, value: str) -> None:
        url = self._construct_kv_url(key)
        serialized_value = json.dumps(value)
        try:
            response = requests.put(url, headers=self.headers, data=serialized_value)
            response.raise_for_status()
            print("Cache set successfully")
        except requests.exceptions.RequestException as e:
            print(f"Failed to set cache: {e}")

    def execute_query(self, query: str, use_cache: bool = True) -> str:
        """
        Execute a Snowflake SQL query with optional caching.
        """
        if use_cache:
            cached_response = self.get_from_cache(query)
            if cached_response:
                return json.loads(cached_response)

        session = self.get_session()
        result = session.sql(query).collect()
        result_list = [row.as_dict() for row in result]

        if use_cache:
            self.set_to_cache(query, result_list)

        return result_list
