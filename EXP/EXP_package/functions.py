
import pandas as pd
import numpy as np

def gini_coefficient(values):
    """Calcola l'indice di concentrazione di Gini per una serie di valori."""
    sorted_values = np.sort(values)
    cumulative_values = np.cumsum(sorted_values)
    lorenz_curve = cumulative_values / cumulative_values[-1]
    gini_index = 1 - 2 * np.trapz(lorenz_curve, dx=1/len(lorenz_curve))
    return gini_index

def calculate_gini_for_posts(df):
    """Calcola l'indice di concentrazione di Gini per ogni post_id."""
    gini_results = []
    
    # Raggruppa i dati per post_id
    grouped = df.groupby('post_id')
    
    for post_id, group in grouped:
        # Calcola l'attività per ogni utente
        user_activity = group.groupby('from_id')['activity'].sum()
        # Calcola l'indice di Gini per questa attività
        gini_index = gini_coefficient(user_activity.values)
        gini_results.append({'post_id': post_id, 'gini_index': gini_index})
    
    return pd.DataFrame(gini_results)
