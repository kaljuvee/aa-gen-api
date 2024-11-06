from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.llms import OpenAI
from sqlalchemy import create_engine, inspect
import pandas as pd
import os
from dotenv import load_dotenv
import openai

class TextToSQL:
    def __init__(self):
        load_dotenv()
        self.db_uri = os.getenv('DATABASE_URL')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.engine = None
        self.db = None
        self.llm = None
        self.db_chain = None
        
        if self.db_uri and self.openai_api_key:
            self.setup_connections()

    def setup_connections(self):
        """Initialize database and OpenAI connections"""
        self.engine = create_engine(self.db_uri)
        self.db = SQLDatabase.from_uri(self.db_uri)
        self.llm = OpenAI(temperature=0, api_key=self.openai_api_key)
        self.db_chain = create_sql_query_chain(self.llm, self.db)

    def get_schema(self):
        """Get database schema information"""
        if not self.engine:
            return None
        
        schema_info = []
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()
        
        for table_name in table_names:
            columns = inspector.get_columns(table_name)
            table_info = {
                'name': table_name,
                'columns': [{'name': col['name'], 'type': str(col['type'])} for col in columns]
            }
            schema_info.append(table_info)
        
        return schema_info

    def generate_sql(self, user_input):
        """Generate SQL from natural language"""
        if not self.db_chain:
            raise Exception("Database connection not initialized")
        
        try:
            result = self.db_chain.invoke({"question": user_input})
            return result
        except Exception as e:
            raise Exception(f"Error generating SQL: {str(e)}")

    def execute_sql(self, sql_query):
        """Execute SQL query and return results"""
        if not self.engine:
            raise Exception("Database connection not initialized")
        
        try:
            df = pd.read_sql_query(sql_query, self.engine)
            return df.to_dict('records')
        except Exception as e:
            raise Exception(f"Error executing SQL: {str(e)}")

    def __del__(self):
        """Cleanup database connections"""
        if self.engine:
            self.engine.dispose()
