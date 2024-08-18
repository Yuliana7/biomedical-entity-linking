from neo4j import Driver, GraphDatabase
from enum import Enum
import os
import re
from dotenv import load_dotenv
from typing import Literal, Union

load_dotenv()

def get_driver() -> Driver:
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


abbreviation_pattern = re.compile(r'\b(?!I{1,3}|IV|VI{0,3}|IX|X{1,3})[A-Z\.]{2,}s?\b') # excluding Roman numbers

def contains_abbreviation(description):
    return bool(abbreviation_pattern.search(description))

Models = Enum('Models', {
    'BAAI_BGE_SMALL_EN_V1_5': "BAAI/bge-small-en-v1.5",
    'LLAMA3': "llama3"
})

Vectors = Enum('Vectors', {
    "BAAI_DISEASE_NAME": "baaiVectorIndex",
    "BAAI_DISEASE_SYNONYMS_CENTROID": "baaiVectorIndex_combinedSynonym"
})
