import pandas as pd
from neo4j import GraphDatabase

# Function to create disease nodes
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
def get_disease_name(tx):
    result = tx.run("""
        MATCH (d:Disease) 
        RETURN d.DiseaseID AS DiseaseID, d.DiseaseName AS DiseaseName
    """)
    return result.data()

# Function to update disease embeddings
def update_disease_embeddings(tx, disease_id, embedding, embedding_model_name):
    disease_embedding = f"DiseaseEmbedding-{embedding_model_name.replace('.', '_').replace('/', '_')}"

    query = """
        MATCH (d:Disease {DiseaseID: $DiseaseID})
        CALL apoc.create.setProperty(d, $disease_embedding, $embedding)
        YIELD node
        RETURN node;
    """

    tx.run(query, DiseaseID=disease_id, embedding=embedding, disease_embedding=disease_embedding)