
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
import os

root = '/home/jacoponudo/Documents/Size_effects/'

platforms = ['reddit', 'twitter', 'usenet', 'voat', 'facebook','gab']

max_k = 200
max_d = 200
sample_size=1000000

for platform in tqdm(platforms):
    output_path = root + f'PAPER/output/2_section/density_matrix_{platform}.csv'
    if not os.path.exists(output_path):
        data = pd.read_parquet(root + 'DATA/' + platform + '/' + platform + '_raw_data.parquet', columns=columns_to_read[platform])
        data.columns = standard_columns
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        df = data.sort_values(by=['post_id', 'timestamp'])
        sampled_posts = np.random.choice(df['post_id'].unique(), min(len(df['post_id'].unique()), sample_size), replace=False)
        df = df[df['post_id'].isin(sampled_posts)]
        density_matrix = np.zeros((max_d // 2, max_k // 2))

        for post_id, group in tqdm(df.groupby('post_id'), desc=f"Processing {platform}"):
            group = group.sort_values(by='timestamp')
            for k in range(2, max_k + 1, 2):
                top_k_comments = group.head(k)
                if len(top_k_comments)==k:
                    distinct_users_count = top_k_comments['user_id'].nunique()
                    if distinct_users_count <= max_d:
                        density_matrix[(distinct_users_count - 1) // 2, (k - 1) // 2] += 1
                else:
                    continue

        density_matrix /= density_matrix.sum(axis=0, keepdims=True)

        density_df = pd.DataFrame(density_matrix, 
                                columns=[f"k={i}" for i in range(2, max_k + 1, 2)],
                                index=[f"d={i}" for i in range(2, max_d + 1, 2)])
        density_df.to_csv(root + f'PAPER/output/2_section/density_matrix_{platform}.csv', index=True)
    density_matrix = pd.read_csv(root + f'PAPER/output/2_section/density_matrix_{platform}.csv', index_col=0)
    plt.figure(figsize=(10, 10))
    platform_color = palette[platform]
    cmap = LinearSegmentedColormap.from_list("platform_to_white", ['white', platform_color], N=100)

    # Crea l'heatmap
    sns.heatmap(density_matrix, cmap=cmap,
                cbar_kws={'label': 'Density'},
                xticklabels=range(2, max_k + 1, 2),
                yticklabels=range(2, max_d + 1, 2))

    # Imposta i label degli assi con dimensioni maggiorate
    plt.xlabel("Thread prefix length (k)", fontsize=14)
    plt.ylabel("Number of users (d)", fontsize=14)
    plt.title(f"{platform.capitalize()}", fontsize=14)

    # Riduci il numero di etichette dell'asse x e y visualizzate e ingrandisci i tick
    plt.xticks(ticks=np.arange(0, max_k // 2, step=5),
            labels=[f"{i*2}" for i in range(0, max_k // 2, 5)], 
            rotation=45, fontsize=12)
    plt.yticks(ticks=np.arange(0, max_d // 2, step=5),
            labels=[f"{i*2}" for i in range(0, max_d // 2, 5)], 
            fontsize=12)

    # Inverti l'asse y per mantenere la convenzione della heatmap
    plt.gca().invert_yaxis()

    # Salva e mostra il grafico
    plt.savefig(f"/home/jacoponudo/Documents/Size_effects/PAPER/output/2_section/heatmap_{platform}.png")
    plt.show()

plt.close()  # Close the plot to free up memory
