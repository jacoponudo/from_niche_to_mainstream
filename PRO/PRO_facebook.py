import pandas as pd
import os
from tqdm import tqdm

# Nome del file da elaborare
file_name = '/home/jacoponudo/Documents/Size_effects/DATA/sample_comments.csv'

# Lista per memorizzare i DataFrame elaborati
dataframes = []

# Variabile per contare il totale delle righe
total_rows_count = 0

# Carica solo le colonne richieste dal file CSV
try:
    data = pd.read_csv(file_name, usecols=['created_time', 'post_id', 'from_id'], encoding='ISO-8859-1')
    data.rename(columns={'from_id': 'author_id'}, inplace=True)
    posts = pd.read_csv('/home/jacoponudo/Documents/Size_effects/DATA/sample_posts.csv', usecols=['page_id', 'post_id'], encoding='ISO-8859-1')
    posts_dict = posts.set_index('post_id').T.to_dict()
    data['page_id'] = data['post_id'].map(lambda x: posts_dict.get(x, {}).get('page_id', None))

except ValueError as e:
    print(f"Missing columns in file {file_name}: {e}")

else:
    # Estrai mese e anno dalla colonna 'created_time' e crea la colonna 'month_year'
    data['month_year'] = pd.to_datetime(data['created_time'], errors='coerce').dt.to_period('M').astype(str)
    
    # Elimina la colonna 'created_time'
    data = data.drop(columns=['created_time'])
    
    # Incrementa il conteggio totale delle righe
    total_rows_count += data.shape[0]
    
    # Step 2: Conta quanti utenti unici ci sono per post
    users_per_post = data.groupby('post_id')['author_id'].nunique().reset_index()
    users_per_post.columns = ['post_id', 'post_size']
    
    # Step 3: Conta quante volte ogni autore appare per post
    author_post_count = data.groupby(['post_id', 'author_id']).size().reset_index(name='interaction_len')
    
    # Aggiungi la colonna 'month_year' al conteggio degli autori
    author_post_count = pd.merge(author_post_count, data[['post_id', 'month_year']].drop_duplicates(), on='post_id')
    
    # Step 4: Unisci i due DataFrame su 'post_id'
    merged_data = pd.merge(users_per_post, author_post_count, on='post_id')
    
    # Aggiungi il DataFrame elaborato alla lista
    dataframes.append(merged_data)

# Concatenate all DataFrames into a single dataset
final_dataset = pd.concat(dataframes, ignore_index=True)

# Salva il dataset finale con la colonna 'month_year' come terza colonna
final_dataset[['post_size', 'interaction_len', 'month_year']].to_csv('/home/jacoponudo/Documents/Size_effects/DATA/facebook/PRO_facebook.csv', index=False)

# Conta il numero di post e di autori unici
num_posts = final_dataset['post_id'].nunique()
num_users = final_dataset['author_id'].nunique()

print(f"Number of posts: {num_posts}")
print(f"Number of unique users: {num_users}")
print(f"Total number of rows: {total_rows_count}")
