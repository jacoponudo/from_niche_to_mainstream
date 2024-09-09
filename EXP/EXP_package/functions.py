import pandas as pd
import numpy as np

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


def calculate_gini_for_posts(df):
    """Calcola l'indice di concentrazione di Gini per ogni post_id basato sul numero di righe per utente."""
    gini_results = []
    
    # Raggruppa i dati per post_id
    grouped = df.groupby('post_id')
    
    for post_id, group in tqdm(grouped):
        # Conta il numero di righe per ogni utente
        user_counts = group['user_id'].value_counts()
        # Calcola l'indice di Gini per questi conteggi
        gini_index = gini_coefficient(user_counts.values)
        gini_results.append({'post_id': post_id, 'gini_index': gini_index})
    
    return pd.DataFrame(gini_results)
