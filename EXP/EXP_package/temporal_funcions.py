import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
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
    L = numerator / denominator
    return L
def process_file(data_directory, filename):
    if filename.endswith('.csv'):
        data = pd.read_csv(os.path.join(data_directory, filename)).drop_duplicates(subset='comment_code')
    elif filename.endswith('.parquet'):
        data = pd.read_parquet(os.path.join(data_directory, filename)).drop_duplicates(subset='comment_code')

    unique_user_counts = data.groupby('post_id')['user_id'].nunique().rename('size')
    data = data.merge(unique_user_counts, left_on='post_id', right_index=True, how='left')
    data = data.groupby(['user_id', 'post_id', 'size']).agg(interaction_len=('id', 'count')).reset_index()

    max_size = int(data['size'].max())
    bins = range(0, max_size + 20, 20)
    data['size_bin'] = pd.cut(data['size'], bins=bins, right=False)

    data['interaction_len'] = data['interaction_len'].clip(upper=10)
    location_params = data.groupby('size_bin')['interaction_len'].apply(
        lambda x: calculate_localization_parameter(x.value_counts(normalize=True))
    )

    valid_bins = data['size_bin'].value_counts()
    plot_data = location_params.copy()
    plot_data[valid_bins < 1000] = None

    return plot_data, filename

# Function to create plots for all files
def plot_location_parameters(data_directory, output_directory, files_to_process, platform):
    plt.figure(figsize=(12, 8))
    colors = plt.cm.Set1.colors
    
    for i, filename in enumerate(files_to_process):
        plot_data, label = process_file(data_directory, filename)
        plt.plot(plot_data.index.astype(str), plot_data, marker='o', linestyle='-', 
                 markersize=5, label=label.split('.')[0], color=colors[i % len(colors)])

    plt.xlabel('Size Bin')
    plt.ylabel('Location Parameter')
    plt.title('Location Parameter by Size Bin for Different Categories')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid()
    plt.legend(title='Categories', bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)
    plt.savefig(os.path.join(output_directory, platform + '_location_plot_subreddit.png'), bbox_inches='tight')
    plt.close()

# Function for processing raw data and plotting
def process_raw_data(data_directory, files_to_process):
    combined_data = pd.DataFrame()

    for i, filename in enumerate(files_to_process):
        if filename.endswith('.csv'):
            data = pd.read_csv(os.path.join(data_directory, filename)).drop_duplicates(subset='id')
        elif filename.endswith('.parquet'):
            data = pd.read_parquet(os.path.join(data_directory, filename)).drop_duplicates(subset='id')

        data['year'] = pd.to_datetime(data['date']).dt.year
        unique_user_counts = data.groupby('post_id')['user_id'].nunique().rename('size')
        data = data.merge(unique_user_counts, left_on='post_id', right_index=True, how='left')
        data = data.groupby(['user_id', 'post_id', 'year', 'size']).agg(interaction_len=('id', 'nunique')).reset_index()
        combined_data = pd.concat([combined_data, data], ignore_index=True)

    combined_data.drop_duplicates(subset=['user_id', 'post_id'], inplace=True)
    return combined_data

# Function to plot location parameters by year
def plot_location_parameters_by_year(combined_data, output_directory, platform):
    years = combined_data['year'].unique()
    plt.figure(figsize=(12, 8))
    colors = plt.cm.Set1.colors

    for i, year in enumerate(sorted(years)):
        year_data = combined_data[combined_data['year'] == year]
        max_size = int(year_data['size'].max())
        bins = range(0, max_size + 25, 25)
        year_data['size_bin'] = pd.cut(year_data['size'], bins=bins, right=False)
        year_data['interaction_len'] = year_data['interaction_len'].clip(upper=10)

        location_params = year_data.groupby('size_bin')['interaction_len'].apply(
            lambda x: calculate_localization_parameter(x.value_counts(normalize=True))
        )

        valid_bins = year_data['size_bin'].value_counts()
        plot_data = location_params.copy()
        plot_data[valid_bins < 250] = None

        plt.plot(plot_data.index.astype(str), plot_data, marker='o', linestyle='-', 
                 markersize=5, label=f'Year: {year}', color=colors[i % len(colors)])

    plt.xlabel('Size Bin')
    plt.ylabel('Location Parameter')
    plt.title('Location Parameter by Size Bin for Different Years')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid()
    plt.legend(title='Years')
    plt.savefig(os.path.join(output_directory, platform + '_location_plot_year.png'), bbox_inches='tight')
    plt.close()
