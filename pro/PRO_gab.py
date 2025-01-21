import pandas as pd
import os
from tqdm import tqdm

# Directory path
directory = '/home/jacoponudo/Documents/Size_effects/DATA/gab/'

# Nome del file da elaborare
file_name = 'gab_labeled_data_unified.parquet'

# Path completo del file
file_path = os.path.join(directory, file_name)

# Lista per memorizzare i DataFrame elaborati
dataframes = []

# Colonne da leggere
required_columns = ['user', 'post_id', 'created_at']

# Variabile per contare il totale delle righe
total_rows_count = 0

# Carica solo le colonne richieste dal file Parquet
try:
    data = pd.read_parquet(file_path, columns=required_columns)
except ValueError as e:
    print(f"Missing columns in file {file_name}: {e}")
else:
    data.columns=['author_id', 'post_id', 'created_at']
    # Estrai l'anno dalla colonna 'created_at' e crea la colonna 'year'
    data['month_year'] = pd.to_datetime(data['created_at'], errors='coerce').dt.to_period('M').astype(str)
    
    # Elimina la colonna 'created_at'
    data = data.drop(columns=['created_at'])
    
    # Incrementa il conteggio totale delle righe
    total_rows_count += data.shape[0]
    
    # Step 2: Conta quanti utenti unici ci sono per post
    users_per_post = data.groupby('post_id')['author_id'].nunique().reset_index()
    users_per_post.columns = ['post_id', 'post_size']
    
    # Step 3: Conta quante volte ogni autore appare per post
    author_post_count = data.groupby(['post_id', 'author_id','month_year']).size().reset_index(name='interaction_len')
    
    # Step 4: Unisci i due DataFrame su 'post_id'
    merged_data = pd.merge(users_per_post, author_post_count, on='post_id')
    
    # Aggiungi il DataFrame elaborato alla lista
    dataframes.append(merged_data)

# Concatenate all DataFrames into a single dataset
final_dataset = pd.concat(dataframes, ignore_index=True)

# Salva il dataset finale con la colonna 'year' come terza colonna
final_dataset[['post_size', 'interaction_len', 'month_year']].to_csv('/home/jacoponudo/Documents/Size_effects/DATA/gab/PRO_gab.csv', index=False)

# Conta il numero di post e di autori unici
num_posts = final_dataset['post_id'].nunique()
num_users = final_dataset['author_id'].nunique()

print(f"Number of posts: {num_posts}")
print(f"Number of unique users: {num_users}")
print(f"Total number of rows: {total_rows_count}")
