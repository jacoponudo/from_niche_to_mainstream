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

root = '/home/jacoponudo/Documents/Size_effects/'

platforms = ['reddit', 'voat', 'facebook', 'twitter']
for platform in tqdm(platforms):
    data = read_and_rename(platform, root)
    df=data
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
    weekly_unique_users['smoothed_users_count'] = weekly_unique_users.groupby('page_id')['unique_users_count'].rolling(window=120, min_periods=1).mean().reset_index(level=0, drop=True)

    # Raggruppiamo per 'post_id' e 'page_id' e otteniamo il timestamp minimo per ogni gruppo
    posts = data.groupby(['post_id', 'page_id'])['timestamp'].min().reset_index()

    # Convertiamo 'timestamp' in formato datetime
    posts['timestamp'] = pd.to_datetime(posts['timestamp'])

    # Creiamo una colonna 'week' che rappresenta la settimana del 'timestamp'
    posts['week'] = posts['timestamp'].dt.to_period('d')

    # Raggruppiamo per 'user_id' e 'post_id' per calcolare il numero di commenti per ogni post
    comments = data.groupby(['user_id', 'post_id']).size().reset_index(name='comment_count')

    # Impostiamo un limite per i commenti (se ci sono più di 5 commenti, li limitamo a 5)
    comments['comment_count'] = comments['comment_count'].apply(lambda x: 5 if x > 5 else x)

    # Calcoliamo la distribuzione di probabilità dei commenti per ogni post
    prob_dist = comments.groupby(['post_id'])['comment_count'].value_counts(normalize=True)

    # Calcoliamo il parametro di localizzazione per ogni post_id
    localization_results = prob_dist.groupby(['post_id']).apply(lambda x: calculate_localization_parameter(x.values)).reset_index(name='localization_parameter')

    # Aggiungiamo la colonna 'localization_parameter' al DataFrame 'posts' tramite un merge su 'post_id'
    posts = posts.merge(localization_results[['post_id', 'localization_parameter']], on='post_id', how='left')
    merged_df = pd.merge(weekly_unique_users, posts, on=['page_id',  'week'], how='right')

    # 'how' può essere 'inner', 'left', 'right' o 'outer' a seconda di come vuoi che vengano gestiti i valori non corrispondenti

    # Mostriamo il risultato del merge
    print(merged_df)
    merged_df.to_csv(root + f'PAPER/output/4_section/5_size_effect_{platform}.csv')

    # Creazione dei bins logaritmici
    # Creazione dei bins logaritmici
    bin_start = 20
    bin_end = merged_df['smoothed_users_count'].max()

    # Calcolare i limiti dei bins utilizzando logaritmi (log base 10)
    bins = np.logspace(np.log10(bin_start), np.log10(bin_end), num=10)

    # Aggiunta di una colonna per il bin in cui si trova ogni valore
    merged_df['binned'] = pd.cut(merged_df['smoothed_users_count'], bins, right=False)

    # Filtriamo i bins che hanno meno di 100 osservazioni
    binned_counts = merged_df['binned'].value_counts()
    valid_bins = binned_counts[binned_counts >= 100].index

    # Ordiniamo i bins in base al limite sinistro
    valid_bins = sorted(valid_bins, key=lambda bin_: bin_.left)

    # Calcolo del valore medio e dei quantili (25° e 75°) per ogni bin valido
    mean_values = []
    lower_quantiles = []
    upper_quantiles = []

    for bin_ in valid_bins:
        bin_data = merged_df[merged_df['binned'] == bin_]['localization_parameter']
        mean_values.append(bin_data.quantile(0.75))
        lower_quantiles.append(bin_data.quantile(0.2))
        upper_quantiles.append(bin_data.quantile(0.8))

    # Creazione del line plot
    plt.figure(figsize=(10, 6))

    # Disegno del grafico a linee
    plt.plot(np.arange(len(valid_bins)), mean_values, marker='o', linestyle='-', color=palette[platform])

    # Aggiungi l'area per il intervallo di confidenza
    plt.fill_between(np.arange(len(valid_bins)), lower_quantiles, upper_quantiles, color=palette[platform], alpha=0.05)

    # Etichette per i bins
    bin_labels = [f'{int(bin_.left)} - {int(bin_.right)}' for bin_ in valid_bins]
    plt.xticks(np.arange(len(valid_bins)), bin_labels, rotation=45)

    # Aggiunta delle etichette agli assi
    plt.xlabel('Page outreach', fontsize=30)
    plt.ylabel('Localization', fontsize=30)
    plt.title(str(platform.capitalize()), fontsize=35)
    plt.ylim(1,2)

    # Mostra il grafico
    plt.tight_layout()
    plt.savefig(f"{root}PAPER/output/4_section/5_size_effect_{platform}.png")
    plt.show()