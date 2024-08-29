# Biomedial Entity Linking

The rapid growth of the healthcare sector has led to an explosion of biomedical data from sources like literature, electronic medical records (EMRs), clinical trials, and genomic databases. While this data offers valuable insights, it also presents challenges for researchers and healthcare professionals. Advances in machine learning have revolutionized data analysis, introducing powerful algorithms capable of mining and interpreting biomedical information with unprecedented accuracy.

However, challenges remain, such as ambiguous terminology, abbreviations, misspellings, and varied medical jargon, making it difficult to extract accurate information. To address this, robust Biomedical Entity Linking (BM-EL) methods are crucial for linking terms to their correct concepts within a knowledge base, ensuring accurate data interpretation and informed decision-making in healthcare.

BM-EL not only improves information retrieval from biomedical texts but also integrates and correlates data across different sources. By resolving ambiguities and standardizing terms, BM-EL enhances precision in research, supporting personalized medicine, clinical decision-making, and biomedical research. As biomedical data continues to grow, refining BM-EL techniques becomes increasingly important.

This research focuses on building a Biomedical Entity Linking system using a Knowledge Graph. This is later used by a simple RAG system that acts as a medical assistant.

## Project setup

When starting with this repository, you should download the data used in this project and setup Neo4J on your local machine.

Please use `requirements.txt` to install the dependecies.

### Data aquisition

We used CTD Knowledge Base for the Knowledge Graph and NCBI Disease Dataset for annotated disease entities.

[Download CTD Knowledge Base](https://ctdbase.org/reports/CTD_diseases.csv.gz)

[Download NCBI Disease Corpus - train](https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/NCBItrainset_corpus.zip)

[Download NCBI Disease Corpus - dev](https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/NCBIdevelopset_corpus.zip)

[Download NCBI Disease Corpus - test](https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/NCBItestset_corpus.zip)


After loading these - please place them in [data/row](data/raw) folder. It should have the following structure:

```
├── data/
│   ├── raw/
|   |   └── NCBI_corpus/
|   |   |   └── NCBIdevelopset_corpus.txt
|   |   |   └── NCBItestset_corpus.txt
|   |   |   └── NCBItrainset_corpus.txt
|   |   └── CTD_diseases.csv
│   └── processed/
```

**NB:** During the Llama3 embedding experiment we extend the annotation dataset with Llama3 embedding, however due to the high dimentionality of vectors this file exeeds the GitHub file size limit, thus the copy saved in this repository contains only BAAI embeddings.

### Tooling setup

We used Docker Desktop to run Neo4j instance locally, please refer to the official [Docker documentation](https://www.docker.com/products/docker-desktop/) for installation instructions. `docker-compose.yml` should be used for Docker settings.

[db/conf](db/conf) folder contains configuration needed for Neo4j to run. The credentials should be placed into `.env` file on your local machine.

Llama3 embeddings and LLM used in this project were served from a local ollama server. Please refer to [Ollama](https://ollama.com/) documentation for the installation instructions.

## Project structure

This project consist of a set of experiments conducted in dedicated Jupyter notebooks.

**[Part 1. Data processing](notebooks/data_processing.ipynb)**

This part covers
- the EDA and data processing for CTD knowledge base and NCBI dataset
- setup knowledge graph with Neo4j
- create embeddings for disease names and synonyms with two embedding models
- cross-validate the disease IDs in the knowledge base and the dataset

**[Part 2. Cypher index](notebooks/cypher_index.ipynb)**

This part of the research will focus on experiments with fulltext index and vector index on BAAI embeddings.

**[Part 3. Combined search strategy](notebooks/candidates_ranking.ipynb)**

In this part we:
- run fulltext, vector and combined vector indices queries with more limit and threshold
- calculate mrr and hit@k
- calculate string distance for fulltext index results
- combine into a single search function with candidates ranking
  
**[Part 4. Experiment with a different embedding model](notebooks/embedding_model_experiments.ipynb)**

In this part we will recreate the experiment with LLAMA3 embeddings and compare the performance.

**[Part 5. Augumenting search results](notebooks/augumented_search_results.ipynb)**
This is a final part of this research. This notebook includes additional retrieval functions and a simple RAG setup using a local ollama server.

**[untils](notebooks/utils)** folder contains re-usable code for creating/updating and using different search strategies as well as enums for safeguarding against typos when conducting these experiments.

**[media](notebooks/media)** folder holds media assets used in the research analysis sections.

