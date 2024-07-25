from neo4j import GraphDatabase
from enum import Enum
import os
from dotenv import load_dotenv
from typing import Literal, Union

load_dotenv()

def get_driver():
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME')
    password = os.getenv('NEO4J_PASSWORD')

    return GraphDatabase.driver(uri, auth=(username, password))

def get_credentials(type: Literal['uri', 'username', 'password']) -> Union[str, None]:
    if type == 'uri':
        return os.getenv('NEO4J_URI')
    elif type == 'username':
        return os.getenv('NEO4J_USERNAME')
    elif type == 'password':
        return os.getenv('NEO4J_PASSWORD')
    else:
        return None

Models = Enum('Models', {
    'BAAI_BGE_SMALL_EN_V1_5': "BAAI/bge-small-en-v1.5",
    'LLAMA3': "llama3"
})
