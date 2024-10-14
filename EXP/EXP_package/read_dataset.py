import pandas as pd
import os

def read_data(platform):
    # Definizione dei percorsi e dei nomi dei file per ciascuna piattaforma
    file_paths = {
        'reddit': '/home/jacoponudo/Documents/Size_effects/DATA/reddit/reddit_labeled_data_unified.parquet',
        'facebook_comments': '/home/jacoponudo/Documents/Size_effects/DATA/facebook/sample_comments.csv',
        'facebook_posts': '/home/jacoponudo/Documents/Size_effects/DATA/facebook/sample_posts.csv',
        'voat': '/home/jacoponudo/Documents/Size_effects/DATA/voat/voat_labeled_data_unified.parquet',
        'gab': '/home/jacoponudo/Documents/Size_effects/DATA/gab/gab_labeled_data_unified.parquet',
        'twitter': '/media/jacoponudo/Elements/da spostare/twitter_labeled_data_unified.parquet',
        'usenet': '/media/jacoponudo/Elements/usenet/merged/usenet_alt.politics.csv',  # Puoi modificare se necessario
    }
    
    required_columns = {
        'reddit': ['user_id', 'post_id', 'date'],
        'facebook_comments': ['created_time', 'post_id', 'from_id'],
        'voat': ['user', 'root_submission', 'created_at'],
        'gab': ['user', 'post_id', 'created_at'],
        'twitter': ['author_id', 'post_id', 'created_at'],
        'usenet': ['thread_id', 'author_id', 'created_at'],
    }
    
    try:
        if platform == 'reddit':
            data = pd.read_parquet(file_paths[platform], columns=required_columns[platform])
            data.columns = ['author_id', 'post_id', 'created_at']
        
        elif platform == 'facebook_comments':
            data = pd.read_csv(file_paths['facebook_comments'], usecols=required_columns[platform], encoding='ISO-8859-1')
            data.rename(columns={'from_id': 'author_id'}, inplace=True)
            posts = pd.read_csv(file_paths['facebook_posts'], usecols=['page_id', 'post_id'], encoding='ISO-8859-1')
            posts_dict = posts.set_index('post_id').T.to_dict()
            data['page_id'] = data['post_id'].map(lambda x: posts_dict.get(x, {}).get('page_id', None))
            data = data[['author_id', 'post_id', 'created_time']]
            data.columns = ['author_id', 'post_id', 'created_at']
        
        elif platform == 'voat':
            data = pd.read_parquet(file_paths[platform], columns=required_columns[platform])
            data.columns = ['author_id', 'post_id', 'created_at']

        elif platform == 'gab':
            print('c')
            data = pd.read_parquet(file_paths[platform], columns=required_columns[platform])
            data.columns = ['author_id', 'post_id', 'created_at']
        
        elif platform == 'twitter':
            data = pd.read_parquet(file_paths[platform], columns=required_columns[platform])
            data.columns = ['author_id', 'post_id', 'created_at']

        elif platform == 'usenet':
            dataframes = []
            # Modifica per leggere più file se necessario
            usenet_files = [
                'usenet_alt.politics.csv',
                'usenet_current-events.csv',
                'usenet_conspiracy.csv',
                'usenet_talk.csv'
            ]
            for file in usenet_files:
                file_path = os.path.join('/media/jacoponudo/Elements/usenet/merged', file)
                try:
                    temp_data = pd.read_csv(file_path, usecols=required_columns[platform])
                    dataframes.append(temp_data)
                except ValueError as e:
                    print(f"Missing columns in file {file}: {e}")
            data = pd.concat(dataframes, ignore_index=True)

        else:
            raise ValueError("Platform not recognized")
    
    except ValueError as e:
        print(f"Missing columns or file error for {platform}: {e}")
        return None
    
    return data

# Esempio di utilizzo
import pandas as pd
import os
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def plot_comment_distribution(data, platform):
    # Definisci i colori per ciascuna piattaforma
    platform_colors = {
        'Reddit': '#FF5700',
        'Voat': '#800080',
        'Facebook': '#3b5998',
        'Gab': '#00c853',
        'Twitter': '#1DA1F2',  # Colore esempio per Twitter
        'Usenet': '#7D7D7D'    # Colore esempio per Usenet
    }
    
    # Seleziona il colore in base alla piattaforma
    color = platform_colors.get(platform, 'skyblue')  # Usa 'skyblue' come colore predefinito se la piattaforma non è specificata
    
    # Percorso di salvataggio
    base_path = "/home/jacoponudo/Documents/Size_effects/PLT/6_activity"
    
    # Calcola il numero di commenti per ogni autore
    conversation_size_author = data.groupby(['author_id', 'post_id'])['author_id'].count().reset_index(name='comment_count')
    
    # Conta quanti autori hanno un certo numero di commenti
    post_count_author = conversation_size_author.groupby('comment_count').size().reset_index(name='user_count')
    
    # Disegna lo scatter plot con scala logaritmica su entrambi gli assi per gli autori
    plt.figure(figsize=(12, 8))
    plt.scatter(post_count_author['comment_count'], post_count_author['user_count'], alpha=0.5, color=color)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim(1, 1000000)  # Imposta i limiti dell'asse x
    plt.title(f'{platform} Interaction Length Distribution')
    plt.xlabel('Number of comments')
    plt.ylabel('Number of interactions')
    plt.grid(False)
    interaction_len_path = f"{base_path}/{platform}_interaction_len_distribution.png"
    plt.savefig(interaction_len_path, dpi=300)
    plt.close()
    
    # Calcola il numero di commenti per ogni post
    conversation_size_post = data.groupby('post_id')['post_id'].count().reset_index(name='comment_count')
    
    # Conta quanti post hanno un certo numero di commenti
    post_count_post = conversation_size_post.groupby('comment_count').size().reset_index(name='post_count')
    
    # Disegna lo scatter plot con scala logaritmica su entrambi gli assi per i post
    plt.figure(figsize=(12, 8))
    plt.scatter(post_count_post['comment_count'], post_count_post['post_count'], alpha=0.5, color=color)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim(1, 1000000)  # Imposta i limiti dell'asse x
    plt.title(f'{platform} Post Size Distribution')
    plt.xlabel('Number of comments')
    plt.ylabel('Number of posts')
    plt.grid(False)
    post_size_path = f"{base_path}/{platform}_post_size_distribution.png"
    plt.savefig(post_size_path, dpi=300)
    plt.close()
