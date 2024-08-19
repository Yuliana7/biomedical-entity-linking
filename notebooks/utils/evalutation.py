from matplotlib import pyplot as plt
from neo4j import Driver
import pandas as pd

###########
# QEURIES #
###########

get_shortest_path_query = """
    WITH $trueID AS startId, $predictedID AS endId

    MATCH (start:Disease)
    WHERE (start.DiseaseID IS NOT NULL AND ANY(id IN SPLIT(toString(start.DiseaseID), '|') WHERE id = startId))
    OR (start.AltDiseaseIDs IS NOT NULL AND ANY(altId IN SPLIT(toString(start.AltDiseaseIDs), '|') WHERE altId = startId))

    MATCH (end:Disease)
    WHERE (end.DiseaseID IS NOT NULL AND ANY(id IN SPLIT(toString(end.DiseaseID), '|') WHERE id = endId))
    OR (end.AltDiseaseIDs IS NOT NULL AND ANY(altId IN SPLIT(toString(end.AltDiseaseIDs), '|') WHERE altId = endId))

    MATCH p = shortestPath((start)-[*]-(end))

    RETURN length(p) AS distance
"""

###########
# HELPERS #
###########

def extract_ids(entry: dict) -> list:
    """
    Extracts unique IDs from a dictionary entry.

    Parameters:
        entry (dict): A dictionary containing 'MESH_ID' and 'AltDiseaseIDs' keys.

    Returns:
        list: A list of unique IDs extracted from the entry.
    """
    mesh_ids = entry['MESH_ID'].split('|') if entry['MESH_ID'] else []
    alt_disease_ids = []

    if 'AltDiseaseIDs' in entry.keys() and entry['AltDiseaseIDs'] is not None and not pd.isna(entry['AltDiseaseIDs']):
        alt_disease_ids = entry['AltDiseaseIDs'].split('|')

    all_ids = mesh_ids + alt_disease_ids
    unique_ids = list(set(all_ids)) 
    
    return unique_ids

def partial_match(true_labels: list, predicted_labels: list) -> bool:
    """
    Check if there is a partial match between the true labels and the predicted labels.

    Parameters:
        true_labels (list): A list of dictionaries representing the true labels.
        predicted_labels (list): A list of lists, where each inner list contains dictionaries representing the predicted labels.

    Returns:
        bool: True if there is a partial match between the true labels and the predicted labels, False otherwise.
    """
    true_set = set(extract_ids(true_labels))
    predicted_set = set(extract_ids(predicted_labels[0]))

    return not true_set.isdisjoint(predicted_set)

def custom_accuracy(true_values: list, predicted_values: list) -> float:
    """
    Calculates the custom accuracy score based on the true labels and predicted labels.

    Parameters:
        true_values (list): A list of dictionaries representing the true labels.
        predicted_values (list): A list of lists, where each inner list contains dictionaries representing the predicted labels.

    Returns:
        float: The custom accuracy score, which is the ratio of true positives to the total number of true labels.
              If the length of true_values is 0, returns 0.
    """
    true_positive = 0
    
    for true_labels, predicted_labels in zip(true_values, predicted_values):
        if partial_match(true_labels, predicted_labels):
            true_positive += 1
        
    return true_positive / len(true_values) if len(true_values) > 0 else 0

def mrr_score(disease_predictions: list) -> float:
    """
    Calculate the Mean Reciprocal Rank (MRR) for a list of disease predictions.
    
    Parameters:
        disease_predictions (list): A list of lists, where each inner list represents the predictions for a single disease.
            Each prediction is a dictionary with the following keys:
            - 'True MESH_ID' (str): The true MESH ID for the disease.
            - 'True Description' (str): The true description for the disease.
            - Other keys (str): Additional keys may be present in the dictionary, but they are not used in the calculation.
    
    Returns:
        float: The Mean Reciprocal Rank (MRR) score.
    """
    reciprocal_ranks = []
    
    for list_of_pred_for_single_disease in disease_predictions:
        rank = []
        found = False
        for i, entity in enumerate(list_of_pred_for_single_disease):
            predicted_ids = extract_ids(entity)
            if entity['True MESH_ID'] in predicted_ids:
                rank.append(1)
                reciprocal_rank = 1 / (i + 1)
                reciprocal_ranks.append(reciprocal_rank)
                found = True
                break  # Stop after the first correct prediction
            else:
                rank.append(0)
        
        if not found:
            reciprocal_ranks.append(0)  # If no correct prediction was found, add 0
    
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)

    return mrr

def hits_at_n_score(disease_predictions: list, n: int):
    """
    Calculate the Hits@N score given a list of ranks and the value of N.
    
    Parameters:
        disease_predictions (list): A list of lists, where each inner list represents the predictions for a single disease.
            Each prediction is a dictionary with the following keys:
            - 'True MESH_ID' (str): The true MESH ID for the disease.
            - 'True Description' (str): The true description for the disease.
            - Other keys (str): Additional keys may be present in the dictionary, but they are not used in the calculation.
                         If a query has no correct match, it should have a rank of 0 or be excluded.
        n (int): The value of N for Hits@N (e.g., Hits@1, Hits@5).
    
    Returns:
        float: The Hits@N score.
    """
    hits = 0
    
    for list_of_pred_for_single_disease in disease_predictions:
        for entity in list_of_pred_for_single_disease[:n]:
            predicted_ids = extract_ids(entity)
            if entity['True MESH_ID'] in predicted_ids:
                hits += 1
                break  # Stop once the correct prediction is found within the top N

    hits_at_n_score = hits / len(disease_predictions)

    return hits_at_n_score

def mark_predictions_with_shortest_path(disease_predictions: list, driver: Driver) -> list:
    with driver.session() as session:
        for candidates_for_single_disease in disease_predictions:
            for candidate in candidates_for_single_disease:
                true_id = candidate['True MESH_ID']
                predicted_ids = extract_ids(candidate)
                # Mark whether the prediction is correct
                if true_id in predicted_ids:
                    candidate['is_correct'] = True
                    candidate['shortest_path'] = 0  # Direct match
                else:
                    candidate['is_correct'] = False
                    predicted_id = candidate['MESH_ID']
                    
                    # If the predicted ID is not "Unknown", calculate the shortest path
                    if predicted_id != "Unknown":
                        result = session.run(get_shortest_path_query, trueID=true_id, predictedID=predicted_id)
                        single_result = result.single()

                        if single_result is not None:
                            candidate['shortest_path'] = single_result[0]
                        else:
                            candidate['shortest_path'] = -1  # No path found
                    else:
                        candidate['shortest_path'] = -2  # Unknown prediction

    return disease_predictions

def display_shortest_path_predictions(shortest_path_predictions: list):
    bins = list(range(min(shortest_path_predictions), max(shortest_path_predictions) + 2))

    plt.figure(figsize=(10, 6))
    n, bins, patches = plt.hist(shortest_path_predictions, bins=bins, edgecolor='black', color='blue', alpha=0.7)

    # Change color for specific bars (-1 and -2)
    for i, bin_edge in enumerate(bins[:-1]):
        if bin_edge == -1:
            patches[i].set_facecolor('red')
            plt.text(bin_edge + 0.5, n[i] + 10, 'No path found', ha='center', va='bottom', color='black', fontsize=10)
        elif bin_edge == -2:
            patches[i].set_facecolor('orange')
            plt.text(bin_edge + 0.5, n[i] + 10, 'No predicted ID', ha='center', va='bottom', color='black', fontsize=10)

    plt.title('Distribution of Shortest Path Distances')
    plt.xlabel('Distance')
    plt.ylabel('Frequency')
    plt.show()