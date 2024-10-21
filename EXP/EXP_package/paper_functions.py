import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.stats import entropy as calc_entropy
from tqdm import tqdm
def calculate_localization_parameter(phi):
    """
    Calculate the localization parameter L.

    Parameters:
    - phi: a numpy array of values.

    Formula:
    - numerator = (np.sum(phi**2))**2: Sum of squares of phi, squared.
    - denominator = np.sum(phi**4): Sum of fourth powers of phi.
    - L = numerator / denominator: Ratio gives the value of L.

    Returns:
    - L: The localization parameter.
    """
    numerator = (np.sum(phi**2))**2
    denominator = np.sum(phi**4)
    if denominator == 0:  
        return np.nan  
    L = numerator / denominator
    return L



# Funzione per calcolare alpha (frequenza di interaction_len == 1)
def calculate_alpha(distribution):
    return (distribution == 1).sum() / len(distribution)

# Funzione per calcolare l'entropia della distribuzione
def calculate_entropy(distribution):
    return calc_entropy(distribution, base=2)

# Define a function to handle platform-specific configurations
def process_platform(platform, param='alpha'):
    # Define directories and filenames
    data_directory = f'/home/jacoponudo/Documents/Size_effects/DATA/{platform}/'
    output_directory = '/home/jacoponudo/Documents/Size_effects/PLT/7_temporal/'
    
    # Adjust filename based on platform
    filename = f'{platform}_labeled_data_unified.parquet' if platform != 'facebook' else 'facebook_snews.csv'
    
    # Define the column mapping based on platform
    if platform in ['reddit', 'voat']:
        column_mapping = {
            'root_submission': 'post_id',
            'user': 'user_id',
            'created_at': 'date'
        }
    elif platform == 'facebook':
        column_mapping = {
            'post_id': 'post_id',
            'user_id': 'user_id',
            'created_at': 'date'
        }
    elif platform == 'gab':
        column_mapping = {
            'post_id': 'post_id',
            'user': 'user_id',
            'created_at': 'date'
        }
    elif platform == 'usenet':
        column_mapping = {
            'thread_id': 'post_id',
            'author_id': 'user_id',
            'created_at': 'date'
        }
    
    # Load the dataset (you can adjust depending on the file type)
    if filename.endswith('.parquet'):
        data = pd.read_parquet(os.path.join(data_directory, filename))
    else:
        data = pd.read_csv(os.path.join(data_directory, filename))
    
    # Rename columns based on the mapping
    data.rename(columns=column_mapping, inplace=True)
    
    # Further processing based on the chosen parameter (param can be 'localizator', 'alpha', or 'entropy')
    # Add your data analysis logic here
    
    return data

def window_activity(df,platform, sample_size=1000,window=60):
    # Ensure the 'date' column is in datetime format
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Take a random sample of comments
    sample_df = df.sample(n=sample_size, random_state=1)  # Set random_state for reproducibility

    results = []

    # Use tqdm to show progress
    for index, row in tqdm(sample_df.iterrows(), total=sample_df.shape[0], desc="Analyzing comments "+platform ):
        post_id = row['post_id']
        user_id = row['user_id']
        comment_time = row['date']

        # Get comments within 10 minutes after the current comment
        comments_within_10min = df[(df['post_id'] == post_id) & 
                                     (df['date'] > comment_time) & 
                                     (df['date'] <= comment_time + pd.Timedelta(minutes=60))]
        num_comments_within_10min = len(comments_within_10min)

        # Check if the user has commented again in the same conversation
        user_returned = not df[(df['post_id'] == post_id) & 
                               (df['user_id'] == user_id) & 
                               (df['date'] > comment_time)].empty

        results.append({
            'post_id': post_id,
            'user_id': user_id,
            'comment_time': comment_time,
            'num_comments_within_10min': num_comments_within_10min,
            'user_returned': user_returned
        })

    return pd.DataFrame(results)

def filter_out_tail(df,size=100):
    # Ensure created_at is in datetime format
    df['created_at'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Sort the DataFrame by created_at
    df = df.sort_values(by=['post_id', 'created_at'])
    
    # Group by post_id and filter the first hour of conversation
    def filter_group(group):
        start_time = group['created_at'].min()
        return group[(group['created_at'] >= start_time) & 
                     (group['created_at'] < start_time + pd.Timedelta(hours=100))]

    filtered_df = df.groupby('post_id', group_keys=False).apply(filter_group)

    return filtered_df.reset_index(drop=True)