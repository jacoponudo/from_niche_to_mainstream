from tqdm import tqdm
import os

platforms = ['reddit', 'usenet', 'voat','gab', 'facebook','twitter']
for platform in tqdm(platforms):
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
    root = '/home/jacoponudo/documents/from_niche_to_mainstream/'
    data = pd.read_parquet(root + 'data/' + platform + '/' + platform + '_raw_data.parquet', columns=columns_to_read[platform])
    data.columns = standard_columns
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # 1. Numero di utenti coinvolti in una conversazione
    
    output_path = root + 'src/output/1_section/1_users_in_thread_{}.csv'.format(platform)
    if not os.path.exists(output_path):
        unique_users_per_post = data.groupby('post_id')['user_id'].nunique().reset_index()
        unique_users_per_post.columns = ['post_id', 'unique_users_count']
        unique_users_per_post.to_csv(output_path)

    # Plotting
    unique_users_per_post = pd.read_csv(output_path)
    distribution = unique_users_per_post['unique_users_count'].value_counts().sort_index()
    percentile_90 = np.percentile(unique_users_per_post['unique_users_count'], 90)
    print(f"Il 90° percentile : {platform}-{percentile_90}")
    xl=40
    yl=40
    plt.figure(figsize=(d1, d1))
    plt.scatter(distribution.index, distribution.values, color=palette[platform], alpha=0.3,s=160)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlim(1, 10**5)
    plt.ylim(1, 10**6)
    plt.xlabel('Number of users', fontsize=xl)
    plt.ylabel('Number of posts', fontsize=yl)
    plt.title(str(platform.capitalize()), fontsize=T)
    plt.grid(False)
    plt.tight_layout()
    plt.subplots_adjust(left=0.15, right=0.9, bottom=-0.1) 
    

    # Set tick parameters
    plt.tick_params(axis='both', which='major', labelsize=t)
    plt.subplots_adjust( bottom=0.2, left=0.2,hspace=0.2, wspace=0.2)
    plt.savefig(root + 'src/output/1_section/1_users_in_thread_{}.png'.format(platform))


    from tools.to_plot import *
    # 4. Level of dialogue
    output_path = root + f'src/output/1_section/4_dialogue_level_{platform}.csv'
    if not os.path.exists(output_path):
        grouped = data.groupby(['user_id', 'post_id']).size().reset_index(name='comment_count')
        user_count = data.groupby('post_id')['user_id'].nunique().reset_index(name='user_count')
        result = grouped.merge(user_count, on='post_id', how='left')
        bin_start = 10
        bin_end = 500

        bins = np.logspace(np.log10(bin_start), np.log10(bin_end), num=12)
        result['user_count_bin'] = pd.cut(result['user_count'], bins=bins, right=False)
        valid_bins = result['user_count_bin'].value_counts()[result['user_count_bin'].value_counts() > 1000].index
        result = result[result['user_count_bin'].isin(valid_bins)]
        result['comment_count'] = result['comment_count'].apply(lambda x: 10 if x > 10 else x)
        balanced_result = result.groupby('user_count_bin').apply(
            lambda x: x.sample(n=min(len(x), 1000), random_state=42) if len(x) > 0 else x
        ).reset_index(drop=True)
        # Creazione dei sub-bins, dividendo ogni bin in 10 gruppi da 100
        balanced_result['subbin'] =balanced_result.groupby('user_count_bin').cumcount() // 100 + 1

        prob_dist = balanced_result.groupby(['user_count_bin','subbin'])['comment_count'].value_counts(normalize=True)
        localization_results = prob_dist.groupby(['user_count_bin','subbin']).apply(lambda x: calculate_localization_parameter(x.values)).reset_index(name='localization_parameter')
        alpha_results = prob_dist.groupby(['user_count_bin','subbin']).apply(lambda x: calculate_alpha_parameter(x.values)).reset_index(name='localization_parameter')
        localization_results.to_csv(root + f'src/output/1_section/4_dialogue_level_{platform}.csv')
        alpha_results.to_csv(root + f'src/output/1_section/4_dialogue_level_{platform}_alpha.csv')

    # Plotting

    localization_results = pd.read_csv(f"{root}src/output/1_section/4_dialogue_level_{platform}.csv")

    median_values = localization_results.groupby('user_count_bin')['localization_parameter'].median().reset_index()
    q1_values = localization_results.groupby('user_count_bin')['localization_parameter'].quantile(0.25).reset_index()
    q3_values = localization_results.groupby('user_count_bin')['localization_parameter'].quantile(0.75).reset_index()

    conf_interval = pd.merge(median_values, q1_values[['user_count_bin', 'localization_parameter']], on='user_count_bin', suffixes=('', '_Q1'))
    conf_interval = pd.merge(conf_interval, q3_values[['user_count_bin', 'localization_parameter']], on='user_count_bin', suffixes=('', '_Q3'))

    localization_results['bin_lower_bound'] = localization_results['user_count_bin'].str.extract(r'(\d+)').astype(float)

    conf_interval = conf_interval.merge(localization_results[['user_count_bin', 'bin_lower_bound']].drop_duplicates(), on='user_count_bin')
    conf_interval = conf_interval.sort_values(by='bin_lower_bound').reset_index(drop=True)

    plt.figure(figsize=(d1, d2))

    # Set x-axis labels
    if 'user_count_bin' in locals() and 'user_count_bin' in localization_results.columns:
        bin_intervals = localization_results['user_count_bin'].cat.categories
        x_labels = [str(int(interval.left)) for interval in bin_intervals]
    else:
        x_labels = conf_interval['bin_lower_bound'].astype(int).astype(str).tolist()

    plt.xticks(ticks=range(len(x_labels)), labels=x_labels,fontsize=t-6,rotation=45)
    plt.yticks(fontsize=t)

    # Plotting
    plt.fill_between(conf_interval['user_count_bin'], conf_interval['localization_parameter_Q1'], conf_interval['localization_parameter_Q3'], color=palette[platform], alpha=0.2, label='Confidence Band (IQR)')
    plt.plot(conf_interval['user_count_bin'], conf_interval['localization_parameter'], marker='o', color=palette[platform], label='Median per Bin')

    # Set labels and legend
    plt.xlim(0, 11)
    plt.ylim(1, 1.15)
    if platform=='usenet':
        plt.ylim(1, 2.1)
    plt.legend(fontsize=t-10)

    # Set tick parameters for both axes
    plt.xlabel('Crowd Size', fontsize=xl)
    plt.ylabel(r'$L$', fontsize=yl)
    plt.title(str(platform.capitalize()), fontsize=T)
    plt.subplots_adjust( bottom=0.2, left=0.2,hspace=0.2, wspace=0.2)

    # Save and show the plot
    plt.savefig(f"{root}src/output/1_section/4_dialogue_level_{platform}.png")

    print('Done for ' + platform + '!')
    
    localization_results = pd.read_csv(f"{root}src/output/1_section/4_dialogue_level_{platform}_alpha.csv")

    median_values = localization_results.groupby('user_count_bin')['localization_parameter'].median().reset_index()
    q1_values = localization_results.groupby('user_count_bin')['localization_parameter'].quantile(0.25).reset_index()
    q3_values = localization_results.groupby('user_count_bin')['localization_parameter'].quantile(0.75).reset_index()

    conf_interval = pd.merge(median_values, q1_values[['user_count_bin', 'localization_parameter']], on='user_count_bin', suffixes=('', '_Q1'))
    conf_interval = pd.merge(conf_interval, q3_values[['user_count_bin', 'localization_parameter']], on='user_count_bin', suffixes=('', '_Q3'))

    localization_results['bin_lower_bound'] = localization_results['user_count_bin'].str.extract(r'(\d+)').astype(float)

    conf_interval = conf_interval.merge(localization_results[['user_count_bin', 'bin_lower_bound']].drop_duplicates(), on='user_count_bin')
    conf_interval = conf_interval.sort_values(by='bin_lower_bound').reset_index(drop=True)

    plt.figure(figsize=(d1, d2))

    # Set x-axis labels
    if 'user_count_bin' in locals() and 'user_count_bin' in localization_results.columns:
        bin_intervals = localization_results['user_count_bin'].cat.categories
        x_labels = [str(int(interval.left)) for interval in bin_intervals]
    else:
        x_labels = conf_interval['bin_lower_bound'].astype(int).astype(str).tolist()

    plt.xticks(ticks=range(len(x_labels)), labels=x_labels, fontsize=t-12,rotation=45)
    plt.yticks(fontsize=t)

    # Plotting
    plt.fill_between(conf_interval['user_count_bin'], conf_interval['localization_parameter_Q1'], conf_interval['localization_parameter_Q3'], color=palette[platform], alpha=0.2, label='Confidence Band (IQR)')
    plt.plot(conf_interval['user_count_bin'], conf_interval['localization_parameter'], marker='o', color=palette[platform], label='Median per Bin')

    # Set labels and legend
    plt.xlim(0, 11)
    plt.ylim(0.35,1)

    # Set tick parameters for both axes
    plt.xlabel('Crowd Size', fontsize=xl)
    plt.ylabel(r'$\alpha$', fontsize=yl)
    plt.title(str(platform.capitalize()), fontsize=T)
    plt.tight_layout()
    plt.subplots_adjust( bottom=0.2, left=0.2,hspace=0.2, wspace=0.2)
    plt.legend(fontsize=t-10)
    # Save and show the plot
    plt.savefig(f"{root}src/output/1_section/4_dialogue_level_{platform}_alpha.png")

    print('Done for ' + platform + '!')
