import json
from neo4j import Driver
import numpy as np

###########
# QUERIES #
###########

node_prop_update_query = """
    MATCH (d:Disease {DiseaseID: $disease_id})
    CALL apoc.create.setProperty(d, $embedding_prop, $embedding)
    YIELD node
    RETURN node
"""

batch_retrieve_query = """
    MATCH (d:Disease)
    RETURN d
    SKIP $skip LIMIT $limit
"""

###########
# HELPERS #
###########

def calculate_centroid(vectors: list) -> list:
    if not vectors:
        return None
    
    vectors_array = np.array(vectors)
    centroid = np.mean(vectors_array, axis=0)

    return centroid.tolist()

def batch_update_synonym_centorid_embeddings(driver: Driver, embedding_model_name: str, batch_size=100):
    embedding_prop = f"SynonymsCentroidEmbedding-{embedding_model_name.replace('.', '_').replace('/', '-')}"
    synonym_embeddings_prop = f"SynonymsEmbedding-{embedding_model_name.replace('.', '_').replace('/', '-')}"
    disease_embedding_prop = f"DiseaseEmbedding-{embedding_model_name.replace('.', '_').replace('/', '-')}"

    skip = 0
    
    with driver.session() as session:
        while True:
            result = session.run(batch_retrieve_query, skip=skip, limit=batch_size)
            nodes = list(result)

            # If no more nodes, break the loop
            if not nodes:
                break

            for record in nodes:
                node = record['d']
                disease_id = node['DiseaseID']
                synonym_embeddings_json = node.get(synonym_embeddings_prop, '[]')
                disease_embedding = node.get(disease_embedding_prop, None)

                # Decode the JSON-encoded embeddings
                synonym_embeddings = json.loads(synonym_embeddings_json)

                if synonym_embeddings:
                    centroid = calculate_centroid(synonym_embeddings)
                    embedding = centroid
                else:
                    # If no synonym embeddings, use the disease embedding
                    embedding = disease_embedding

                session.run(node_prop_update_query, disease_id=disease_id, embedding_prop=embedding_prop, embedding=embedding)

            # Increment the skip value to move to the next batch
            skip += batch_size