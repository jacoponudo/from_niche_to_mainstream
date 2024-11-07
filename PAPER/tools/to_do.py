# Funzione per calcolare il lifetime nel percentile specificato dei commenti ordinati per timestamp

from tqdm import tqdm 
import pandas as pd
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
    # Rimuoviamo i valori NaN dalle colonne rilevanti
    data = data.dropna(subset=['timestamp'])
    
    # Inizializzare una lista per memorizzare i risultati
    durations_percentile = []
    post_ids = []

    # Applicare la funzione per ogni 'post_id' con una barra di progresso
    for post_id, group in tqdm(data.groupby('post_id'), desc=f"Calcolando durata {percentile}° percentile per ogni post", total=data['post_id'].nunique()):
        duration = calculate_percentile_lifetime(group, percentile)
        durations_percentile.append(duration)
        post_ids.append(post_id)

    # Creiamo un DataFrame con i risultati
    result_df = pd.DataFrame({
        'post_id': post_ids,
        'duration_percentile': durations_percentile
    })

    # Salviamo il DataFrame come CSV nel percorso specificato
    result_df.to_csv(output_path, index=False)
    print(f"File salvato in: {output_path}")