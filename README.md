# Biomedial Entity Linking

Introduction tbd

## Project setup

When starting with this repository, you should download the data used in this project and setup Neo4J on your local machine.

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

**[untils](notebooks/utils)** folder contains re-usable code for creating/updating and using different search strategies as well as enums for safeguarding against typos when conducting these experiments.

**[media](notebooks/media)** folder holds media assets used in the research analysis sections.

