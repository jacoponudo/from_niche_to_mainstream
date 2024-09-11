import pandas as pd
import numpy as np
from tqdm import tqdm
def gini_coefficient(values):
    if len(values) == 0:
        return np.nan  # O un valore che hai scelto per i casi senza dati
    sorted_values = np.sort(values)
    cumulative_values = np.cumsum(sorted_values)
    
    # Aggiungi un controllo per evitare problemi con array troppo piccoli
    if len(cumulative_values) == 1:
        return 0  # O un valore che hai scelto per i casi con un solo elemento
    
    lorenz_curve = cumulative_values / cumulative_values[-1]
    gini_index = 1 - 2 * np.trapz(lorenz_curve, dx=1/len(lorenz_curve))
    return gini_index


import pandas as pd
from tqdm import tqdm

def gini_coefficient(values):
    """Calcola l'indice di Gini dato un array di valori."""
    sorted_values = sorted(values)
    n = len(sorted_values)
    cumulative_sum = sum((i + 1) * v for i, v in enumerate(sorted_values))
    gini_index = (2 * cumulative_sum) / (n * sum(sorted_values)) - (n + 1) / n
    return gini_index

def calculate_gini_for_posts(df, outreach_df, count_lurcker=False):
    """Calcola l'indice di concentrazione di Gini per ogni post_id basato sul numero di righe per utente."""
    gini_results = []
    
    # Raggruppa i dati per post_id
    grouped = df.groupby('post_id')
    
    for post_id, group in tqdm(grouped):
        # Conta il numero di righe per ogni utente
        user_counts = group['user_id'].value_counts().reset_index()
        user_counts.columns = ['user_id', 'count']
        
        # Ottieni la dimensione totale degli utenti nella finestra temporale
        size = int(outreach_df.loc[outreach_df['post_id'] == post_id, 'users_one_month_window'].iloc[0])
        
        if count_lurcker:
            # Trova tutti gli utenti nella finestra temporale
            all_users = pd.Series(range(size), name='user_id')
            
            # Crea un DataFrame con gli utenti che non hanno commentato
            commenting_users = set(user_counts['user_id'])
            non_commenting_users = set(all_users) - commenting_users
            non_commenting_counts = pd.DataFrame(non_commenting_users, columns=['user_id'])
            non_commenting_counts['count'] = 0
            
            # Unisci i conteggi degli utenti che hanno commentato con quelli che non hanno commentato
            full_user_counts = pd.concat([user_counts, non_commenting_counts], ignore_index=True)
        else:
            full_user_counts = user_counts
        
        # Calcola l'indice di Gini per questi conteggi
        gini_index = gini_coefficient(full_user_counts['count'].values)
        gini_results.append({'post_id': post_id, 'gini_index': gini_index})
    
    return pd.DataFrame(gini_results)


def count_unique_users_within_period(post_date, period):
    # Ensure 'post_date' is in datetime format
    post_date_value = pd.to_datetime(post_date['post_date'])
    
    # Define the time window around the post date
    start_time = post_date_value - pd.Timedelta(days=period)
    end_time = post_date_value + pd.Timedelta(days=period)

    # Filter comments within the time window and matching the author
    relevant_comments = social[(social['created_at'] >= start_time) & 
                               (social['created_at'] <= end_time) & 
                               (social['autore'] == post_date['autore'])]
    
    # Count unique users commenting within the time window
    unique_users = relevant_comments['user_id'].nunique()
    return unique_users
