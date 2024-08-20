import json
import re
from typing import Dict, List, Literal
from neo4j import Driver
from pandas import DataFrame
from rapidfuzz import fuzz, distance

from utils.generic import Models, Vectors, contains_abbreviation


###########
# QUERIES #
###########

fulltext_index_query = """
    CALL db.index.fulltext.queryNodes('diseaseIndex', $disease_name)
    YIELD node, score
    RETURN node.DiseaseID AS MESH_ID, node.AltDiseaseIDs as AltDiseaseIDs, node.DiseaseName AS Description, node.Synonyms AS Synonyms, score
    LIMIT $limit
"""

vector_index_query = """
    CALL db.index.vector.queryNodes($index, $limit, $embedding)
    YIELD node, score
    with node, score
    WHERE score > $threshold
    RETURN node.DiseaseName AS Description,
        node.DiseaseID AS MESH_ID,
        node.AltDiseaseIDs AS AltDiseaseIDs,
        node.Synonyms AS Synonyms,
        score
"""

###########
# HELPERS #
###########

def fulltext_search(
        query: str,
        disease_name: str,
        driver: Driver,
        limit=1
        ) -> list:
    with driver.session() as session:
        disease_name_re = re.sub('[^A-Za-z0-9 ]+', '', disease_name) # to address the limitation of the fulltext index

        result = session.run(query, disease_name=disease_name_re, limit=limit)

        return [{
            'MESH_ID': record['MESH_ID'],
            'Description': record['Description'],
            'Synonyms': record['Synonyms'],
            'AltDiseaseIDs': record['AltDiseaseIDs'],
            'score': record['score']} for record in result
        ]

def get_embedding_col_name(
        model: Models,
        prop: Literal['SynonymsCentroidEmbedding','DiseaseEmbedding' ,'SynonymsEmbedding']
        ) -> str:
    return f"{prop}-{model.value.replace('.', '_').replace('/', '-')}"

def vector_index_search(
        driver: Driver,
        query: str,
        embedding: list,
        index: str,
        limit=1, 
        threshold=0.80
        ) -> list:
    with driver.session() as session:
        result = session.run(query, index=index, embedding=embedding, limit=limit, threshold=threshold)

        return [{
            'MESH_ID': record['MESH_ID'],
            'Description': record['Description'],
            'Synonyms': record['Synonyms'],
            'AltDiseaseIDs': record['AltDiseaseIDs'],
            'score': record['score']} for record in result
        ]

def predict_with_vector_index(
        dataset: DataFrame,
        query: str,
        index: str,
        embedding_col: str,
        driver: Driver,
        limit=1,
        threshold=0.80
        ) -> list:
    predicted_values = []

    for _, row in dataset.iterrows():
        disease_name = row['Description']
        true_mesh_id = row['MESH ID']
        embedding = row[embedding_col]
        
        search_results = vector_index_search(driver, query, json.loads(embedding), index, limit, threshold)

        for item in search_results:
            item['True MESH_ID'] = true_mesh_id
            item['True Description'] = disease_name
        
        predicted_values.append(search_results if len(search_results) > 0 else [{
            "MESH_ID": "Unknown", 
            "AltDiseaseIDs": "Unknown", 
            "Description": "Unknown",
            "True MESH_ID": true_mesh_id,
            "True Description": disease_name
            }]
        )

    return predicted_values

def predict_with_fulltext_index(
        dataset: DataFrame,
        driver: Driver,
        limit=1
        ) -> list:
    predicted_values = []

    for _, row in dataset.iterrows():
        disease_name = row['Description']
        true_mesh_id = row['MESH ID']
        
        search_results = fulltext_search(fulltext_index_query, disease_name, driver, limit)
        for item in search_results:
            item['True MESH_ID'] = true_mesh_id
            item['True Description'] = disease_name
        
        predicted_values.append(search_results if len(search_results) > 0 else [{
            "MESH_ID": "Unknown", 
            "AltDiseaseIDs": "Unknown", 
            "Description": "Unknown",
            "True MESH_ID": true_mesh_id,
            "True Description": disease_name
            }]
        )

    return predicted_values

def get_combined_search_for_df(dataset: DataFrame, embedding_col: str, driver: Driver) -> list:
    predicted_values = []

    for _, row in dataset.iterrows():
        disease_name = row['Description']
        true_mesh_id = row['MESH ID']
        embedding = row[embedding_col]
        
        search_results = combined_search(disease_name=disease_name, embedding=json.loads(embedding), driver=driver)

        for item in search_results:
            item['True MESH_ID'] = true_mesh_id
            item['True Description'] = disease_name
        
        predicted_values.append(search_results if len(search_results) > 0 else [{
            "MESH_ID": "Unknown", 
            "AltDiseaseIDs": "Unknown", 
            "Description": "Unknown",
            "True MESH_ID": true_mesh_id,
            "True Description": disease_name
            }]
        )

    return predicted_values

def calculate_string_similarity(candidates_list: List[str], disease_name: str) -> Dict[str, float]:
    similarity_metrics = {
        "weighted_ratio": 0,
        "token_set_ratio": 0,
        "JaroWinkler_distance": 0,
        "LCSseq_distance": 0
    }

    for candidate in candidates_list:
        similarity_metrics["weighted_ratio"] = max(similarity_metrics["weighted_ratio"], fuzz.WRatio(candidate, disease_name))
        similarity_metrics["token_set_ratio"] = max(similarity_metrics["token_set_ratio"], fuzz.token_set_ratio(candidate, disease_name))
        similarity_metrics["JaroWinkler_distance"] = max(similarity_metrics["JaroWinkler_distance"], distance.JaroWinkler.similarity(candidate, disease_name))
        similarity_metrics["LCSseq_distance"] = max(similarity_metrics["LCSseq_distance"], distance.LCSseq.similarity(candidate, disease_name))

    return similarity_metrics

def custom_sort_key(candidate: dict, disease_name: str) -> tuple:
    abbrev = contains_abbreviation(disease_name)

    # Original scoring metrics
    primary_metric = candidate['weighted_ratio'] if abbrev else candidate['token_set_ratio']
    secondary_metric = candidate['token_set_ratio'] if abbrev else candidate['weighted_ratio']
    tertiary_metric = candidate['JaroWinkler_distance']
    quaternary_metric = candidate['LCSseq_distance']

    # New scoring logic for prioritizing exact matches and subtypes
    exact_match = 0
    subtype_penalty = 0

    # Prioritize exact match
    if candidate['Description'].strip().lower() == disease_name.strip().lower():
        exact_match = 1

    # Penalize broader matches that miss subtype details
    if 'type' in disease_name.lower() and 'type' not in candidate['Description'].lower():
        subtype_penalty = -1
    

    # Return a tuple with the original metrics and the new factors
    return (
        -exact_match,                 # Higher priority for exact matches
        subtype_penalty,              # Penalize missing subtype information
        -primary_metric, 
        -secondary_metric, 
        -tertiary_metric, 
        -quaternary_metric
    )

def process_predictions(predictions: list, disease_name: str) -> list:
    for prediction in predictions:
        synonyms = prediction['Synonyms'] if isinstance(prediction['Synonyms'], str) else ""
        combined_names = synonyms.split('|') + [prediction['Description']]

        ranking = calculate_string_similarity(combined_names, disease_name)
        prediction.update(ranking)

    return sorted(predictions, key=lambda candidate: custom_sort_key(candidate, disease_name))

def find_all_direct_vector_hits(candidates: list) -> list:
    return [d for d in candidates if d.get('score') == 1.0]

def combined_search(
        disease_name: str,
        embedding: list,
        driver: Driver,
        limit: 100,
        name_vec_index=Vectors.BAAI_DISEASE_NAME.value,
        centoid_vec_index=Vectors.BAAI_DISEASE_SYNONYMS_CENTROID.value) -> dict:
    fulltext_predictions = fulltext_search(
        query=fulltext_index_query,
        disease_name=disease_name,
        driver=driver,
        limit=100
    )

    name_vector_predictions = vector_index_search(
        driver=driver,
        query=vector_index_query,
        embedding=embedding,
        index=name_vec_index,
        limit=100,
        threshold=0.80
    )
    
    centroid_synonyms_vector_predictions = vector_index_search(
        driver=driver,
        query=vector_index_query,
        embedding=embedding,
        index=centoid_vec_index,
        limit=100,
        threshold=0.80
    )

    name_vec_direct_hits = find_all_direct_vector_hits(name_vector_predictions)
    centroid_direct_hits = find_all_direct_vector_hits(centroid_synonyms_vector_predictions)

    if len(name_vec_direct_hits) > 0 or len(centroid_direct_hits) > 0:
        return name_vec_direct_hits + centroid_direct_hits
    else:
        fulltext_predictions = process_predictions(fulltext_predictions, disease_name)
        name_vector_predictions = process_predictions(name_vector_predictions, disease_name)
        centroid_synonyms_vector_predictions = process_predictions(centroid_synonyms_vector_predictions, disease_name)

        # Combine all predictions and sort
        combined = fulltext_predictions + name_vector_predictions + centroid_synonyms_vector_predictions
        combined = sorted(combined, key=lambda candidate: custom_sort_key(candidate, disease_name))

        return combined[0:limit]
    
def get_combined_search_for_df(dataset: DataFrame,
                               embedding_col: str,
                               driver: Driver,
                               limit: 100,
                               name_vec_index: Vectors.BAAI_DISEASE_NAME.value,
                               centoid_vec_index: Vectors.BAAI_DISEASE_SYNONYMS_CENTROID.value
                               ) -> list:
    predicted_values = []

    for _, row in dataset.iterrows():
        disease_name = row['Description']
        true_mesh_id = row['MESH ID']
        embedding = row[embedding_col]
        
        search_results = combined_search(
            disease_name=disease_name,
            embedding=json.loads(embedding),
            driver=driver,
            limit=limit,
            name_vec_index=name_vec_index,
            centoid_vec_index=centoid_vec_index
            )

        for item in search_results:
            item['True MESH_ID'] = true_mesh_id
            item['True Description'] = disease_name
        
        predicted_values.append(search_results if len(search_results) > 0 else [{
            "MESH_ID": "Unknown", 
            "AltDiseaseIDs": "Unknown", 
            "Description": "Unknown",
            "True MESH_ID": true_mesh_id,
            "True Description": disease_name
            }]
        )

    return predicted_values