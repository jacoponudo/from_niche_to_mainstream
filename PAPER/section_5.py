from tools.to_read import *
from tools.to_plot import *
from tools.to_do import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.image as mpimg
import os

root = '/home/jacoponudo/Documents/Size_effects/'
platforms = ['voat','usenet','gab','twitter','reddit','facebook']

s=1000 # number of users studied
k=20 # number of comments observed
m=6 # consider born user just if not in the first m months 

for platform in tqdm(platforms):
    output_path = root + f'PAPER/output/5_section/{platform}_regression_parameters.csv'
    if not os.path.exists(output_path):
        data = read_and_rename(platform, root)
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        excluded_users = data.loc[data['timestamp'] < data['timestamp'].min() + pd.DateOffset(months=m), 'user_id'].unique()
        data = data[~data['user_id'].isin(excluded_users)]
        
        # Prendi solo i primi 10 utenti (unici)
        unique_users = data['user_id'].drop_duplicates().head(s)

        # Filtra i dati per mantenere solo quelli relativi a questi utenti
        data = data[data['user_id'].isin(unique_users)]

        # Ordinare i dati
        data = data.sort_values(by=['page_id', 'user_id', 'timestamp'])
        data['interaction_len'] = data.groupby(['post_id', 'user_id'])['post_id'].transform('size')

        data['posts_commented'] = 0

        # Abilitare la barra di progresso per i gruppi di page_id e user_id
        for (page, user), group in tqdm(data.groupby(['page_id', 'user_id'])):
            post_count = 0
            previous_post_id = None  # Variabile per tracciare l'ID del post precedente
            
            # Aggiungere una barra di progresso per l'iterazione sulle righe del gruppo
            for i, row in group.iterrows():
                # Incrementa il contatore se l'ID del post è diverso dal precedente
                if row['post_id'] != previous_post_id:
                    post_count += 1
                    previous_post_id = row['post_id']
                
                # Assegna il conteggio dei post commentati
                data.loc[row.name, 'posts_commented'] = post_count

        # Filtro per mantenere solo gli utenti con almeno k commenti
        data_filtered = data[data['user_id'].isin(data.groupby('user_id')['posts_commented'].max()[data.groupby('user_id')['posts_commented'].max() > k].index)]

        data_filtered = data_filtered[data_filtered['posts_commented'] <k]
        # Visualizzare il risultato
        print(data_filtered[['user_id','post_id','interaction_len','posts_commented']].drop_duplicates())
        from scipy.stats import linregress

        # Supponiamo che tu abbia già il DataFrame 'data' caricato

        # Selezioniamo le colonne e rimuoviamo i duplicati
        df_filtered = data_filtered[['user_id', 'post_id', 'interaction_len', 'posts_commented']].drop_duplicates()

        # Un elenco di utenti unici
        user_ids = df_filtered['user_id'].unique()

        # Creiamo una lista per memorizzare i risultati
        results = []

        # Impostiamo il numero di righe e colonne per i subplot (puoi modificarlo in base al numero di utenti)
        n_users = len(user_ids)


        # Cicliamo su ciascun utente e tracciamo la regressione
        for i, user_id in enumerate(user_ids):
            # Filtriamo i dati per l'utente corrente
            user_data = df_filtered[df_filtered['user_id'] == user_id]
            
            # Calcoliamo la regressione lineare per ottenere slope e intercept
            slope, intercept, r_value, p_value, std_err = linregress(user_data['posts_commented'], user_data['interaction_len'])
            
            # Salviamo i risultati in una lista
            results.append({'user_id': user_id, 'slope': slope, 'intercept': intercept})
            
        # Creiamo un DataFrame con i risultati
        results_df = pd.DataFrame(results)
        results_df.to_csv(output_path)
    else:
        print('skip calculation')

    # Assumendo che 'output_path' e 'palette' siano già definiti
    results_df = pd.read_csv(output_path)

    # Calcola il centroide come media delle coordinate x e y
    centroid_x = results_df['slope'].median()  # Media della colonna 'slope'
    centroid_y = results_df['intercept'].median()  # Media della colonna 'intercept'

    # Imposta la figura
    plt.figure(figsize=(6, 6))

    # Crea il grafico a dispersione
    sns.scatterplot(data=results_df, x='slope', y='intercept', color=palette[platform])

    # Aggiungi un titolo e le etichette degli assi
    plt.xlabel('Slope', fontsize=30)
    plt.ylabel('Intercept', fontsize=30)
    plt.title(str(platform.capitalize()), fontsize=35)
    plt.xlim(-1, 1)
    plt.ylim(-10, 10)

    # Aggiungi le linee orizzontali e verticali per gli assi con un colore più scuro
    plt.axhline(0, color='black', linestyle='--', linewidth=2)  # Asse y = 0, più scuro
    plt.axvline(0, color='black', linestyle='--', linewidth=2)  # Asse x = 0, più scuro

    # Aggiungi il punto del centroide con lo stesso colore delle linee degli assi
    plt.scatter(centroid_x, centroid_y, color=palette[platform], zorder=5, s=100, label=f'Median: (Slope={centroid_x:.2f}, Intercept={centroid_y:.2f})', edgecolor='black')

    # Aggiungi una griglia tratteggiata
    plt.grid(True, which='both', axis='both', color='gray', linestyle='--', linewidth=1)

    # Aggiungi una legenda per il centroide
    plt.legend(fontsize=10)

    # Salva il grafico come file PNG
    plt.savefig('scatterplot_results.png', dpi=300, bbox_inches='tight')

    # Mostra il grafico
    plt.show()

