import pandas as pd
import os
from tqdm import tqdm

# Directory path
directory = '/media/jacoponudo/Elements/usenet/merged'

# List of files to process
files = [
    'usenet_alt.politics.csv',
    'usenet_current-events.csv',
    'usenet_conspiracy.csv',
    'usenet_talk.csv'
]

# List to store the processed DataFrames
dataframes = []

# Columns to read
required_columns = ['thread_id', 'author_id']

# Variable to count total rows
total_rows_count = 0

# Process each file
for file in tqdm(files):
    # Read the CSV file, checking if the required columns are present
    file_path = os.path.join(directory, file)
    
    # Load only the required columns and handle missing columns
    try:
        data = pd.read_csv(file_path, usecols=required_columns)
    except ValueError as e:
        print(f"Missing columns in file {file}: {e}")
        continue
    
    # Increment total rows count
    total_rows_count += data.shape[0]
    
    # Step 2: Count how many unique users are in each thread
    users_per_thread = data.groupby('thread_id')['author_id'].nunique().reset_index()
    users_per_thread.columns = ['thread_id', 'post_size']
    
    # Step 3: Count how many times each user appears in each thread
    user_thread_count = data.groupby(['thread_id', 'author_id']).size().reset_index(name='interaction_len')
    
    # Step 4: Merge the two DataFrames on 'thread_id'
    merged_data = pd.merge(users_per_thread,user_thread_count, on='thread_id')
    
    # Append the processed DataFrame to the list
    dataframes.append(merged_data)

# Concatenate all DataFrames into a single dataset
final_dataset = pd.concat(dataframes, ignore_index=True)

# Save the final dataset
final_dataset[['post_size','interaction_len']].to_csv('/home/jacoponudo/Documents/Size_effects/DATA/usenet/PRO_usenet.csv', index=False)

# Count the number of posts and unique users
num_posts = final_dataset['thread_id'].nunique()
num_users = final_dataset['author_id'].nunique()

print(f"Number of posts: {num_posts}")
print(f"Number of unique users: {num_users}")
print(f"Total number of rows across all datasets: {total_rows_count}")
