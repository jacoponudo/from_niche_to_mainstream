# Import packages
from tools.to_read import *
from tools.to_plot import *
from tools.to_do import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# Set up
root = '/home/jacoponudo/Documents/Size_effects/'
platforms = ['gab', 'reddit', 'twitter', 'usenet', 'voat', 'facebook']
unique_counts = {}
temporal_ranges = {}

for platform in tqdm(platforms):
    # Carica i dati
    data = pd.read_parquet(root + 'DATA/' + platform + '/' + platform + '_raw_data.parquet', columns=columns_to_read[platform])
    data.columns = standard_columns
    df = data
    df['created_at'] = pd.to_datetime(df['timestamp'])
    
    # Crea una tabella di conteggio per ogni colonna
    unique_counts[platform] = {col: df[col].nunique() for col in df.columns}
    
    # Calcola il range temporale
    temporal_ranges[platform] = {
        'start_date': df['created_at'].min(),
        'end_date': df['created_at'].max()
    }

# Crea il DataFrame con i risultati
unique_counts_df = pd.DataFrame(unique_counts).T
unique_counts_df.index.name = 'Piattaforma'
unique_counts_df.fillna(0, inplace=True)  # Sostituisci NaN con 0 se ci sono colonne mancanti in alcune piattaforme

# Crea il DataFrame per i range temporali
temporal_ranges_df = pd.DataFrame(temporal_ranges).T
temporal_ranges_df.index.name = 'Piattaforma'

# Unisci i risultati e visualizza
results_df = pd.concat([unique_counts_df, temporal_ranges_df], axis=1)
print(results_df)

results_df = pd.concat([unique_counts_df, temporal_ranges_df], axis=1)

results_df['start_date'] = results_df['start_date'].astype(str).str.slice(0, 10)

results_df['end_date'] = results_df['end_date'].astype(str).str.slice(0, 10)

results_df=results_df.reset_index()
results_df[['Piattaforma','user_id', 'post_id', 'timestamp', 'start_date', 'end_date']].to_clipboard(index=False)