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
        'facebook': ['created_time', 'post_id', 'from_id'],
        'voat': ['user', 'root_submission', 'created_at'],
        'gab': ['user', 'post_id', 'created_at'],
        'twitter': ['author_id', 'post_id', 'created_at'],
        'usenet': ['thread_id', 'author_id', 'created_at'],
    }
    
    try:
        if platform == 'reddit':
            data = pd.read_parquet(file_paths[platform], columns=required_columns[platform])
            data.columns = ['author_id', 'post_id', 'created_at']
        
        elif platform == 'facebook':
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
            data=data[[ 'thread_id', 'author_id','created_at']]
            data.columns = ['author_id', 'post_id', 'created_at']

        else:
            raise ValueError("Platform not recognized")
    
    except ValueError as e:
        print(f"Missing columns or file error for {platform}: {e}")
        return None
    
    return data

# Esempio di utilizzo
