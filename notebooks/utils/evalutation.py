import pandas as pd

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

