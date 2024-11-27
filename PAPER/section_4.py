import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from tqdm import tqdm
from tools.to_read import *
from tools.to_do import *
from tools.to_plot import *

# Define root path for saving results
root = '/home/jacoponudo/Documents/Size_effects/'

# Platform types and index categories
platforms = ['reddit', 'usenet', 'voat', 'gab', 'facebook', 'twitter']
types = ['_localization', '_alpha']

# Parameters for data filtering and processing
ignore_under = 50  # Minimum outreach threshold to avoid U-shaped trends
group_size = 1000  # Number of interactions per bin
time_window = 12  # Time window for smoothing the time series (weeks)
correction = 5  # Maximum value of interaction count for corrections

# Iterate over the different platform types and index types
for platform in tqdm(platforms):
    for type in types:
        output_path = f'{root}PAPER/output/4_section/5_size_effect_{platform}{type}.csv'
        
        # If the output file does not exist, process and generate data
        if not os.path.exists(output_path):
            # Load and preprocess data for the platform
            df = read_and_rename(platform, root)
            df['timestamp'] = pd.to_datetime(df['timestamp'])  # Convert timestamp to datetime
            df['week'] = df['timestamp'].dt.to_period('W')  # Extract the week from timestamp

            # Group by 'page_id' and 'week' to count unique users
            weekly_unique_users = df.groupby(['page_id', 'week'])['user_id'].nunique().reset_index()
            weekly_unique_users.rename(columns={'user_id': 'unique_users_count'}, inplace=True)
            weekly_unique_users = weekly_unique_users.sort_values(by=['page_id', 'week'])
            
            # Apply a moving average for smoothing
            weekly_unique_users['smoothed_users_count'] = (
                weekly_unique_users.groupby('page_id')['unique_users_count']
                .rolling(window=time_window, min_periods=1)
                .mean().reset_index(level=0, drop=True)
            )

            # Filter out entries with outreach lower than the threshold
            weekly_unique_users = weekly_unique_users[weekly_unique_users['unique_users_count'] > ignore_under]

            # Create logarithmic bins based on user count
            bins = pd.qcut(weekly_unique_users['unique_users_count'], 
                           q=weekly_unique_users['unique_users_count'].sum() // group_size, 
                           retbins=True, duplicates='drop')[1]
            weekly_unique_users['binned'] = pd.cut(weekly_unique_users['smoothed_users_count'], bins, right=False)

            # Group by 'user_id', 'post_id', 'page_id' and calculate interaction counts
            interactions = df.groupby(['user_id', 'post_id', 'page_id'])['timestamp'].agg(['min', 'count']).reset_index()
            interactions['timestamp'] = pd.to_datetime(interactions['min'])
            interactions['week'] = interactions['timestamp'].dt.to_period('W')

            # Apply correction for interaction counts
            interactions['count'] = interactions['count'].apply(lambda x: min(x, correction))

            # Merge interactions with weekly unique users data
            interactions = interactions.merge(weekly_unique_users[['page_id', 'week', 'binned', 'smoothed_users_count']], on=['page_id', 'week'])

            # Calculate the probability distribution of comment counts for each post
            prob_dist = interactions.groupby(['binned'])['count'].value_counts(normalize=True)

            # Calculate localization or alpha parameter
            if type == '_alpha':
                localization_results = prob_dist.groupby(['binned']).apply(lambda x: calculate_alpha_parameter(x.values)).reset_index(name='localization_parameter')
            else:
                localization_results = prob_dist.groupby(['binned']).apply(lambda x: calculate_localization_parameter(x.values)).reset_index(name='localization_parameter')

            # Save the results to CSV
            localization_results.to_csv(output_path)

        # Load the preprocessed data
        merged_df = pd.read_csv(root + f'PAPER/output/4_section/5_size_effect_{platform+type}.csv')


        color ='grey'# palette[platform]

        # Estrai e arrotonda la colonna 'binned_lower'
        merged_df['binned_lower'] = merged_df['binned'].apply(lambda x: float(x.split(',')[0][1:])).round()

        # Filtra righe con valori NaN o Inf
        merged_df = merged_df.dropna(subset=['binned_lower', 'localization_parameter'])
        merged_df = merged_df[np.isfinite(merged_df['localization_parameter'])]

        # Dati per l'interpolazione
        x = merged_df['binned_lower']
        y = merged_df['localization_parameter']

        # Assicurati che x e y siano numerici
        x = pd.to_numeric(x, errors='coerce')
        y = pd.to_numeric(y, errors='coerce')

        # Rimuovi righe non valide
        valid_idx = (~x.isna()) & (x > 0) & (~y.isna())
        x = x[valid_idx]
        y = y[valid_idx]

        # Applica logaritmo a x
        log_x = np.log(x)

        # Stima la retta di regressione tra y e log(x)
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_x, y)

        # Calcola R^2
        r2 = r_value ** 2

        # Calcola l'intervallo di confidenza al 95% per la pendenza (slope) e l'intercetta (intercept)
        n = len(x)  # numero di dati validi
        t_value = stats.t.ppf(0.975, df=n-2)  # valore t per il 95% di intervallo di confidenza
        slope_ci = t_value * std_err  # intervallo di confidenza per la pendenza
        intercept_ci = t_value * std_err  # intervallo di confidenza per l'intercetta

        # Creazione del grafico
        plt.figure(figsize=(d1, d2))

        # Punti originali
        plt.scatter(x, y, color=color, zorder=5, alpha=0.5, edgecolors=palette[platform])

        # Aggiungi la retta di regressione
        plt.plot(x, slope * log_x + intercept, color='grey', label=f'Fit: y = {slope:.2f} * log(x) + {intercept:.2f}', zorder=10)

        # Aggiungi le bande di confidenza per la pendenza e l'intercetta
        plt.fill_between(x, slope * log_x + intercept - slope_ci, slope * log_x + intercept + slope_ci, color=palette[platform], alpha=0.2)

        plt.xlabel('Page outreach', fontsize=xl)
        if type == '_alpha':
            plt.ylabel('Probability of 1 comment', fontsize=xl)
        else:
            plt.ylabel('Localization', fontsize=xl)
        plt.title(f'{platform.capitalize()} (R² = {r2:.2f})', fontsize=T)  # Include R² in the title
        plt.tick_params(axis='both', which='major', labelsize=t)

        plt.legend()
        plt.tight_layout()
        if platform in ['twitter','facebook']:
            plt.xscale('log')

        plt.savefig(f"{root}PAPER/output/4_section/5_size_effect_{platform+type}.png")
        plt.show()
