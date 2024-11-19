import pandas as pd
import matplotlib.pyplot as plt


from tools.to_read import *
from tools.to_plot import *
from tools.to_do import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.image as mpimg

platform='facebook'
root = '/home/jacoponudo/Documents/Size_effects/'
data = pd.read_parquet(root + 'DATA/' + platform + '/' + platform + '_raw_data.parquet')
data.rename(columns={
    'page_id': 'page_id',
    'from_id': 'user_id',  # This remains the same
    'post_id': 'post_id',  # This remains the same
    'created_time': 'timestamp'
}, inplace=True)
df=data
# Simulazione dei dati per esempio
# df dovrebbe essere un DataFrame che include almeno 'timestamp' (data del commento), 'user_id' e 'page_id'
# df = pd.read_csv("tuo_file.csv")

# Assicurati che la colonna 'timestamp' sia di tipo datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Aggiungi una colonna 'week' che rappresenta la settimana dell'anno
df['week'] = df['timestamp'].dt.to_period('d')

# Raggruppa per 'page_id', 'week' e calcola il numero di utenti univoci per ogni combinazione
weekly_unique_users = df.groupby(['page_id', 'week'])['user_id'].nunique().reset_index()

# Rinominare la colonna per maggiore chiarezza
weekly_unique_users.rename(columns={'user_id': 'unique_users_count'}, inplace=True)

# Ordinare per 'page_id' e 'week' (assicurarsi che i dati siano in ordine)
weekly_unique_users = weekly_unique_users.sort_values(by=['page_id', 'week'])

# Aggiungere la media mobile a 3 settimane (o a una finestra che preferisci)
weekly_unique_users['smoothed_users_count'] = weekly_unique_users.groupby('page_id')['unique_users_count'].rolling(window=15, min_periods=1).mean().reset_index(level=0, drop=True)

# Mostrare i primi risultati
print(weekly_unique_users.head())

weekly_unique_users.to_csv("/home/jacoponudo/Documents/Size_effects/PAPER/output/4_section/ts_outreach.csv", index=False)
