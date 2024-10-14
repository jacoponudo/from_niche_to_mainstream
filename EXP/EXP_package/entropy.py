import pandas as pd
import numpy as np
from scipy.stats import entropy
import matplotlib.pyplot as plt

def calculate_len_entropy(group):
    len_counts = group['len'].value_counts(normalize=True)
    return entropy(len_counts)



def calculate_entropy_by_class(df, max_size=500, step=10):
    # Mantieni solo le colonne richieste
    df = df[['author_id', 'post_id', 'created_at', 'len', 'size']]
    
    # Definisci i bin (gli intervalli)
    bins = list(range(0, max_size + 1, step)) + [np.inf]

    # Definisci le etichette per ogni bin
    labels = [f"{i}-{i + step}" for i in range(0, max_size, step)] + [str(max_size)+"+"]

    # Crea una nuova colonna 'size_grouped' con i valori raggruppati
    df['size_grouped'] = pd.cut(df['size'], bins=bins, labels=labels, right=False)

    # Conta il numero di elementi in ogni gruppo
    group_counts = df['size_grouped'].value_counts()

    # Filtra i gruppi con meno di 10 elementi
    filtered_groups = group_counts[group_counts >= 100].index

    # Filtra il DataFrame per mantenere solo i gruppi validi
    df_filtered = df[df['size_grouped'].isin(filtered_groups)]

    # Funzione per calcolare l'entropia della distribuzione di 'len'
    def calculate_len_entropy(group):
        # Calcola la distribuzione dei valori di 'len'
        value_counts = group['len'].value_counts(normalize=True)
        # Calcola l'entropia
        return entropy(value_counts)

    # Calcola l'entropia di 'len' per ogni classe di 'size_grouped' nei gruppi filtrati
    entropy_by_class = df_filtered.groupby('size_grouped').apply(calculate_len_entropy)

    

    return entropy_by_class

import matplotlib.pyplot as plt

def plot_entropy(entropy_by_class, platform):
    # Define colors
    reddit_color = '#FF5700'
    voat_color = '#800080'
    facebook_color = '#3b5998'
    gab_color = '#00c853'
    twitter_color = '#1DA1F2'  # Example color for Twitter
    usenet_color = '#7D7D7D'    # Example color for Usenet

    # Select the color based on the platform
    if platform == 'reddit':
        color = reddit_color
    elif platform == 'voat':
        color = voat_color
    elif platform == 'facebook':
        color = facebook_color
    elif platform == 'gab':
        color = gab_color
    elif platform == 'twitter':
        color = twitter_color
    elif platform == 'usenet':
        color = usenet_color
    else:
        color = '#000000'  # Default to black if platform is unknown

    # Plotting the entropy for each class
    plt.figure(figsize=(10, 6))
    entropy_by_class.plot(kind='bar', color=color, edgecolor='black')  # Customized color
    plt.title(f'{platform.capitalize()} - Entropy of Probability Distribution of Progressive Number of Comments', fontsize=14)
    plt.xlabel('Size Grouped Classes', fontsize=12)
    plt.ylabel('Entropy', fontsize=12)
    plt.xticks(rotation=90)
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # Added grid
    plt.tight_layout()

    # Define the path and filename
    save_path = f'/home/jacoponudo/Documents/Size_effects/PLT/5_dynamic_entropy/{platform}_dynamic_entropy.png'

    # Save the plot
    plt.savefig(save_path)

    # Show the plot
    plt.show()
