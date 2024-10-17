import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.stats import entropy as calc_entropy

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
def process_platform(platform, param):
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

