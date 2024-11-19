columns_to_read= {
    'usenet': ['thread_id', 'author_id', 'created_at'],
    'reddit': [ 'post_id', 'user_id','date'],
    'gab': ['post_id','user',  'created_at'],
    'twitter':[ 'post_id','author_id', 'created_at'],
    'voat':[ 'root_submission','user', 'created_at'],'facebook':['post_id',	'from_id',	'created_time']}


standard_columns=['post_id','user_id','timestamp']


import pandas as pd

# Define column renaming rules for each platform
column_renaming = {
    'facebook': {
        'topic': 'page_id',
        'from_id': 'user_id',
        'post_id': 'post_id',
        'created_time': 'timestamp'
    },
    'twitter': {
        'topic': 'page_id',
        'author_id': 'user_id',
        'post_id': 'post_id',
        'created_at': 'timestamp'
    },
    'reddit': {
        'topic': 'page_id',
        'user_id': 'user_id',
        'post_id': 'post_id',
        'date': 'timestamp'
    },
    'voat': {
        'topic': 'page_id',
        'user': 'user_id',
        'root_submission': 'post_id',
        'created_at': 'timestamp'
    }
}

# Function to read and rename columns based on platform
def read_and_rename(platform, root):
    # Read the data for the specific platform
    if platform == 'reddit':
        df = pd.read_parquet(root + 'DATA/' + platform + '/' + platform + '_raw_data.parquet', columns=['topic', 'user_id', 'post_id', 'date'])
    elif platform == 'voat':
        df = pd.read_parquet(root + 'DATA/' + platform + '/' + platform + '_raw_data.parquet', columns=['topic', 'user', 'root_submission', 'created_at'])
    else:
        df = pd.read_parquet(root + 'DATA/' + platform + '/' + platform + '_raw_data.parquet')
    
    # Rename the columns according to the dictionary
    df.rename(columns=column_renaming[platform], inplace=True)
    
    return df
