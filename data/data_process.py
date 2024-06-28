# Function to create disease nodes
import pandas as pd

def create_disease_nodes(tx, disease):
    tx.run("""
        MERGE (d:Disease {DiseaseID: $DiseaseID})
        SET d.DiseaseName = $DiseaseName, d.AltDiseaseIDs = $AltDiseaseIDs,
            d.Definition = $Definition, d.TreeNumbers = $TreeNumbers,
            d.ParentTreeNumbers = $ParentTreeNumbers, d.Synonyms = $Synonyms,
            d.SlimMappings = $SlimMappings
    """, 
    DiseaseID=disease['DiseaseID'],
    DiseaseName=disease['DiseaseName'],
    AltDiseaseIDs=disease['AltDiseaseIDs'],
    Definition=disease['Definition'],
    TreeNumbers=disease['TreeNumbers'],
    ParentTreeNumbers=disease['ParentTreeNumbers'],
    Synonyms=disease['Synonyms'],
    SlimMappings=disease['SlimMappings'])

# Function to create hierarchical relationships
def create_hierarchy(tx, disease):
    if pd.notna(disease['ParentIDs']):
        parent_ids = disease['ParentIDs'].split('|')
        for parent_id in parent_ids:
            tx.run("""
                MATCH (d:Disease {DiseaseID: $DiseaseID})
                MATCH (p:Disease {DiseaseID: $ParentID})
                MERGE (d)-[:SUB_CATEGORY_OF]->(p)
            """, DiseaseID=disease['DiseaseID'], ParentID=parent_id)

# Function to get disease descriptions
def get_disease_descriptions(tx):
    result = tx.run("""
        MATCH (d:Disease) 
        RETURN d.DiseaseID AS DiseaseID, d.DiseaseName AS DiseaseName, d.Definition AS Definition
    """)
    return result.data()

# Function to update disease embeddings
def update_disease_embeddings(tx, disease_id, embedding):
    tx.run("""
        MATCH (d:Disease {DiseaseID: $DiseaseID}) 
        SET d.DiseaseEmbedding = $embedding
    """, DiseaseID=disease_id, embedding=embedding)