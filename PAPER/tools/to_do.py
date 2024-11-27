from tqdm import tqdm
import pandas as pd
import numpy as np

def calculate_percentile_lifetime(group, percentile):
    # Ordiniamo per timestamp
    group = group.sort_values('timestamp')
    # Prendiamo il primo percentile percentuale dei commenti
    cutoff_index = int(len(group) * (percentile / 100))
    filtered_group = group.iloc[:cutoff_index]
    # Calcoliamo la differenza di tempo tra il primo e l'ultimo commento
    duration = (filtered_group['timestamp'].max() - filtered_group['timestamp'].min()).total_seconds() / 3600  # Convertiamo in ore
    return duration

# Funzione per calcolare il percentile specificato di lifetime e restituire un dataset
def calculate_lifetime_percentile(data, percentile, output_path):
    # Convertiamo i 'post_id' in stringhe
    data['post_id'] = data['post_id'].astype(str)
    
    # Rimuoviamo i valori NaN dalle colonne rilevanti
    data = data.dropna(subset=['timestamp'])
    
    # Inizializzare una lista per memorizzare i risultati
    durations_percentile = []
    post_ids = []
    unique_user_counts = []  # Lista per il conteggio degli utenti univoci

    # Applicare la funzione per ogni 'post_id' con una barra di progresso
    for post_id, group in tqdm(data.groupby('post_id'), desc=f"Calcolando durata {percentile}° percentile per ogni post", total=data['post_id'].nunique()):
        # Calcoliamo la durata per il percentile
        duration = calculate_percentile_lifetime(group, percentile)
        # Calcoliamo il numero di utenti univoci per ogni post
        unique_user_count = group['user_id'].nunique()
        
        durations_percentile.append(duration)
        post_ids.append(post_id)
        unique_user_counts.append(unique_user_count)

    # Creiamo un DataFrame con i risultati
    result_df = pd.DataFrame({
        'post_id': post_ids,
        'duration_percentile': durations_percentile,
        'unique_user_count': unique_user_counts  # Aggiungiamo il conteggio degli utenti univoci
    })

    # Salviamo il DataFrame come CSV nel percorso specificato
    result_df.to_csv(output_path, index=False)

# Function to calculate localization parameter
def calculate_localization_parameter(phi):
    """
    Calculate the localization parameter L.

    Parameters:
    - phi: a numpy array of values.

    Formula:
    - numerator = (np.sum(phi**2))**2: Sum of squares of phi, squared.
    - denominator = np.sum(phi**4): Sum of fourth powers of phi.
    - L = numerator / denominator: Ratio gives the value of L.

    Returns:
    - L: The localization parameter.
    """
    numerator = (np.sum(phi**2))**2
    denominator = np.sum(phi**4)
    if denominator == 0:  
        return np.nan  
    L = numerator / denominator
    return L

def calculate_alpha_parameter(phi):
    if sum(phi)==1:
        return phi[0]
    else:
        return None