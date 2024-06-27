import os
import pandas as pd

def load_belb_data(corpora_dir):
    data = []
    for file_name in os.listdir(corpora_dir):
        file_path = os.path.join(corpora_dir, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            data.append(text)
    return pd.DataFrame(data, columns=['text'])

def preprocess_data(df):
    df['text'] = df['text'].apply(lambda x: x.lower())
    return df

def save_processed_data(df, output_path):
    df.to_csv(output_path, index=False)
