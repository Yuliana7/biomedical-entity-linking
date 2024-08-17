import pandas as pd

def extract_ids(entry):
    """
    Extracts unique IDs from a dictionary entry.

    Args:
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

def partial_match(true_labels, predicted_labels):
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

def custom_accuracy(true_values, predicted_values):
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

def mrr_score(ranks):
    """
    Calculate the Mean Reciprocal Rank (MRR) given a list of ranks.
    
    Parameters:
    ranks (list of int): A list of ranks (1-based) where the correct entity was found in each query. 
                         If a query has no correct match, it should have a rank of 0 or be excluded.
    
    Returns:
    float: The Mean Reciprocal Rank (MRR) score.
    """
    reciprocal_ranks = [1.0 / rank for rank in ranks if rank > 0]
    return sum(reciprocal_ranks) / len(ranks) if ranks else 0.0

def hits_at_n_score(ranks, n):
    """
    Calculate the Hits@N score given a list of ranks and the value of N.
    
    Parameters:
    ranks (list of int): A list of ranks (1-based) where the correct entity was found in each query.
                         If a query has no correct match, it should have a rank of 0 or be excluded.
    n (int): The value of N for Hits@N (e.g., Hits@1, Hits@5).
    
    Returns:
    float: The Hits@N score.
    """
    hits = sum(1 for rank in ranks if 0 < rank <= n)
    return hits / len(ranks) if ranks else 0.0

