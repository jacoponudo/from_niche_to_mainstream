from tools.to_read import *
from tools.to_plot import *
from tools.to_do import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import os
from tqdm import tqdm
from scipy.interpolate import make_interp_spline

root = '/home/jacoponudo/Documents/Size_effects/'

platforms = ['twitter','reddit','facebook','voat','gab','usenet']
for platform in tqdm(platforms):
    output_path = root + f'PAPER/output/4_section/5_size_effect_{platform}.csv'
    if not os.path.exists(output_path):
        df = read_and_rename(platform, root)
        # Assicurati che la colonna 'timestamp' sia di tipo datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Aggiungi una colonna 'week' che rappresenta la settimana dell'anno
        df['week'] = df['timestamp'].dt.to_period('d')

        # Raggruppa per 'page_id', 'week' e calcola il numero di utenti univoci per ogni combinazione
        weekly_unique_users = df.groupby(['page_id', 'week'])['user_id'].nunique().reset_index()

        # Rinominare la colonna per maggiore chiarezza
        weekly_unique_users.rename(columns={'user_id': 'unique_users_count'}, inplace=True)

        # Ordinare per 'page_id' e 'week' (assicurarsi che i dati siano in ordine)
        weekly_unique_users = weekly_unique_users.sort_values(by=['page_id', 'week'])

        # Aggiungere la media mobile a 3 settimane (o a una finestra che preferisci)
        weekly_unique_users['smoothed_users_count'] = weekly_unique_users.groupby('page_id')['unique_users_count'].rolling(window=30, min_periods=1).mean().reset_index(level=0, drop=True)
        
        # Creazione dei bins logaritmici
        bin_start = 10
        bin_end = 25000

        # Calcolare i limiti dei bins utilizzando logaritmi (log base 10)
        bins = np.logspace(np.log10(bin_start), np.log10(bin_end), num=20)

        # Aggiunta di una colonna per il bin in cui si trova ogni valore
        weekly_unique_users['binned'] = pd.cut(weekly_unique_users['smoothed_users_count'], bins, right=False)

        # Raggruppiamo per 'post_id' e 'page_id' e otteniamo il timestamp minimo per ogni gruppo
        interactions = df.groupby(['user_id', 'post_id', 'page_id'])['timestamp'].agg(['min', 'count']).reset_index()
        # Convertiamo 'timestamp' in formato datetime
        interactions['timestamp'] = pd.to_datetime(interactions['min'])

        # Creiamo una colonna 'week' che rappresenta la settimana del 'timestamp'
        interactions['week'] = interactions['timestamp'].dt.to_period('d')

        # Impostiamo un limite per i commenti (se ci sono più di 5 commenti, li limitamo a 5)
        interactions['count'] = interactions['count'].apply(lambda x: 20 if x > 20 else x)
        # Esegui la fusione tra i due DataFrame
        interactions = interactions.merge(weekly_unique_users[['page_id', 'week', 'binned', 'smoothed_users_count']], on=['page_id', 'week'])

        # Conta il numero di righe per ogni valore della colonna 'binned'
        binned_counts = interactions['binned'].value_counts()

        # Seleziona i valori di 'binned' che hanno 100 o più righe
        valid_binned = binned_counts[binned_counts >= 200].index

        # Filtra il DataFrame per tenere solo le righe con 'binned' valido
        interactions = interactions[interactions['binned'].isin(valid_binned)]
        # Calcoliamo la distribuzione di probabilità dei commenti per ogni post
        prob_dist = interactions.groupby(['binned'])['count'].value_counts(normalize=True)

        # Calcoliamo il parametro di localizzazione per ogni post_id
        localization_results = prob_dist.groupby(['binned']).apply(lambda x: calculate_localization_parameter(x.values)).reset_index(name='localization_parameter')

        # Mostriamo il risultato del merge
        localization_results.to_csv(root + f'PAPER/output/4_section/5_size_effect_{platform}.csv')

    # Carica i dati
    merged_df = pd.read_csv(root + f'PAPER/output/4_section/5_size_effect_{platform}.csv')

    # Definisce il colore dalla palette
    color = palette[platform]

    # Estrai e arrotonda la colonna 'binned_lower'
    merged_df['binned_lower'] = merged_df['binned'].apply(lambda x: float(x.split(',')[0][1:])).round()

    # Check for NaN or Inf values and remove rows with such values
    merged_df = merged_df.dropna(subset=['binned_lower', 'localization_parameter'])  # Remove rows with NaN
    merged_df = merged_df[np.isfinite(merged_df['localization_parameter'])]  # Remove rows with Inf

    # Data for spline interpolation
    x = merged_df['binned_lower']
    y = merged_df['localization_parameter']

    # Make sure x and y are numeric (in case there's still some non-numeric data)
    x = pd.to_numeric(x, errors='coerce')
    y = pd.to_numeric(y, errors='coerce')

    # Remove rows that have become NaN after conversion
    merged_df = merged_df.dropna(subset=['binned_lower', 'localization_parameter'])

    # Create a cubic spline (k=3)
    spl = make_interp_spline(x, y, k=3)

    # Generate a smooth curve
    x_smooth = np.linspace(x.min(), x.max(), 500)
    y_smooth = spl(x_smooth)

    # Plot the smoothed line
    plt.plot(x_smooth, y_smooth, color=color, label='Smoothed line')

    # Add the original points as scatter plot
    plt.scatter(x, y, color=color, zorder=5)

    # Add axis labels and title
    plt.xlabel('Page outreach', fontsize=30)
    plt.ylabel('Localization', fontsize=30)
    plt.title(str(platform.capitalize()), fontsize=35)

    # Additional settings
    plt.tight_layout()
    plt.ylim(1, 1.3)

    # Save and show the plot
    plt.savefig(f"{root}PAPER/output/4_section/5_size_effect_{platform}.png")
    plt.show()