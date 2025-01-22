columns_to_read= {
    'usenet': ['thread_id', 'author_id', 'created_at'],
    'reddit': [ 'post_id', 'user_id','date'],
    'gab': ['post_id','user',  'created_at'],
    'twitter':[ 'post_id','author_id', 'created_at'],
    'voat':[ 'root_submission','user', 'created_at'],'facebook':['post_id',	'from_id',	'created_time']}


standard_columns=['post_id','user_id','timestamp']

root = '/home/jacoponudo/documents/from_niche_to_mainstream/' 
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
    },
        'gab': {
        'topic': 'page_id',
        'user': 'user_id',
        'post_id': 'post_id',
        'created_at': 'timestamp'
    }
,
        'usenet': {
        'topic': 'page_id',
        'author_id': 'user_id',
        'thread_id': 'post_id',
        'created_at': 'timestamp'
    }
}

# Function to read and rename columns based on platform
def read_and_rename(platform, root):
    if platform=='facebook':
        df = pd.read_parquet(root + 'data/' + platform + '/' + platform + '_raw_data.parquet')
    else:
        df = pd.read_parquet(root + 'data/' + platform + '/' + platform + '_raw_data.parquet', columns=list(column_renaming[platform].keys()))
    
    # Rename the columns according to the dictionary
    df.rename(columns=column_renaming[platform], inplace=True)
    
    return df
