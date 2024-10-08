import pandas as pd
import os
from tqdm import tqdm
import seaborn as sns
import matplotlib.pyplot as plt

def load_reddit_data(directory, file_name):
    """Load Reddit data from a Parquet file."""
    file_path = os.path.join(directory, file_name)
    required_columns = ['user_id', 'post_id', 'date']
    
    try:
        data = pd.read_parquet(file_path, columns=required_columns)
        data.columns = ['author_id', 'post_id', 'created_at']
        return data
    except ValueError as e:
        print(f"Missing columns in file {file_name}: {e}")
        return None

def load_facebook_data(file_name, posts_file):
    """Load Facebook data from CSV files."""
    try:
        data = pd.read_csv(file_name, usecols=['created_time', 'post_id', 'from_id'], encoding='ISO-8859-1')
        data.rename(columns={'from_id': 'author_id'}, inplace=True)
        
        posts = pd.read_csv(posts_file, usecols=['page_id', 'post_id'], encoding='ISO-8859-1')
        posts_dict = posts.set_index('post_id').T.to_dict()
        data['page_id'] = data['post_id'].map(lambda x: posts_dict.get(x, {}).get('page_id', None))
        
        data.columns = ['author_id', 'post_id', 'created_at', 'page_id']
        return data
    except ValueError as e:
        print(f"Missing columns in file {file_name}: {e}")
        return None

def load_usenet_data(directory, files):
    """Load Usenet data from multiple CSV files."""
    dataframes = []
    required_columns = ['thread_id', 'author_id', 'created_at']
    
    for file in tqdm(files):
        file_path = os.path.join(directory, file)
        
        try:
            data = pd.read_csv(file_path, usecols=required_columns)
            data['month_year'] = pd.to_datetime(data['created_at'], errors='coerce').dt.to_period('M').astype(str)
            data.drop(columns=['created_at'], inplace=True)
            dataframes.append(data)
        except ValueError as e:
            print(f"Missing columns in file {file}: {e}")
    
    if dataframes:
        return pd.concat(dataframes, ignore_index=True).rename(columns={'thread_id': 'post_id'})
    else:
        return None

def load_voat_data(directory, file_name):
    """Load Voat data from a Parquet file."""
    file_path = os.path.join(directory, file_name)
    required_columns = ['user', 'root_submission', 'created_at']
    
    try:
        data = pd.read_parquet(file_path, columns=required_columns)
        data.columns = ['author_id', 'post_id', 'created_at']
        return data
    except ValueError as e:
        print(f"Missing columns in file {file_name}: {e}")
        return None

def load_twitter_data(directory, file_name):
    """Load Twitter data from a Parquet file."""
    file_path = os.path.join(directory, file_name)
    try:
        data = pd.read_parquet(file_path)
        return data
    except ValueError as e:
        print(f"Missing columns in file {file_name}: {e}")
        return None

def read(platform):
    """Read data based on the specified platform."""
    if platform == 'reddit':
        directory = '/home/jacoponudo/Documents/Size_effects/DATA/reddit/'
        file_name = 'reddit_labeled_data_unified.parquet'
        return load_reddit_data(directory, file_name)

    elif platform == 'facebook':
        file_name = '/home/jacoponudo/Documents/Size_effects/DATA/facebook/sample_comments.csv'
        posts_file = '/home/jacoponudo/Documents/Size_effects/DATA/facebook/sample_posts.csv'
        return load_facebook_data(file_name, posts_file)

    elif platform == 'usenet':
        directory = '/media/jacoponudo/Elements/usenet/merged'
        files = [
            'usenet_alt.politics.csv',
            'usenet_current-events.csv',
            'usenet_conspiracy.csv',
            'usenet_talk.csv'
        ]
        return load_usenet_data(directory, files)

    elif platform == 'voat':
        directory = '/home/jacoponudo/Documents/Size_effects/DATA/voat/'
        file_name = 'voat_labeled_data_unified.parquet'
        return load_voat_data(directory, file_name)

    elif platform == 'twitter':
        directory = '/media/jacoponudo/Elements/da spostare'
        file_name = 'twitter_labeled_data_unified.parquet'
        return load_twitter_data(directory, file_name)

    else:
        print("Platform not supported.")
        return None

def plot_comment_distribution(data, platform):
    # Calculate the number of comments for each author
    conversation_size_author = data.groupby('author_id')['author_id'].count().reset_index(name='comment_count')

    # Count how many authors have a certain number of comments
    post_count_author = conversation_size_author.groupby('comment_count').size().reset_index(name='user_count')

    # Draw scatter plot with logarithmic scale on both axes for authors
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=post_count_author, x='comment_count', y='user_count', alpha=0.5, color='skyblue')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim(1, 10000)  # Set x-axis limits
    plt.title(f'{platform} - Scatter plot of comments per author (log-log scale)')
    plt.xlabel('Number of comments')
    plt.ylabel('Number of authors')
    plt.grid(False)
    plt.show()

    # Calculate the number of comments for each post
    conversation_size_post = data.groupby('post_id')['post_id'].count().reset_index(name='comment_count')

    # Count how many posts have a certain number of comments
    post_count_post = conversation_size_post.groupby('comment_count').size().reset_index(name='post_count')

    # Draw scatter plot with logarithmic scale on both axes for posts
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=post_count_post, x='comment_count', y='post_count', alpha=0.5, color='skyblue')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim(1, 10000)  # Set x-axis limits
    plt.title(f'{platform} - Scatter plot of comments per post (log-log scale)')
    plt.xlabel('Number of comments')
    plt.ylabel('Number of posts')
    plt.grid(False)
    plt.show()
