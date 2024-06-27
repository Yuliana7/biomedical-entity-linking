# My RAG Project

This project implements a Retrieval-Augmented Generation (RAG) model using Mistral.

## Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/your_username/my_rag_project.git
    cd my_rag_project
    ```

2. Download the BelB dataset:
    ```bash
    cd data/raw/
    git clone https://github.com/sg-wbi/belb.git
    cd belb
    # Follow any additional instructions from the BelB repository to set up the data
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Project structure
```
├── README.md
├── requirements.txt
├── setup.py
├── .gitignore
├── data/
│   ├── raw/
|   |   └── belb/
│   └── processed/
├── notebooks/
│   └── ...
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── data_loader.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── rag_model.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── main.py
└── tests/
    ├── __init__.py
    └── test_rag.py
```

