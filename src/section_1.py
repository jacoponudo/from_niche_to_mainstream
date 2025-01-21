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

    root = '/home/jacoponudo/documents/size/'
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
    plt.savefig(root + 'PAPER/output/1_section/1_users_in_thread_{}.png'.format(platform))

    '''
    # 2. Lifetime of a conversation
    output_path = root + 'PAPER/output/1_section/2_lifetime_thread_{}.csv'.format(platform)
    if not os.path.exists(output_path):
        calculate_lifetime_percentile(data, 80, output_path)
    # Plotting
    df = pd.read_csv(output_path, dtype={'post_id': str})
    df = df.dropna(subset=['duration_percentile', 'unique_user_count'])
    df['log_unique_users'] = df['unique_user_count'] + 1
    df['log_duration'] = df['duration_percentile'] + 1
    bin_edges = [1, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192] + [np.inf]
    df['user_bin'] = pd.cut(df['log_unique_users'], bins=bin_edges)
    bin_counts = df['user_bin'].value_counts()
    valid_bins = bin_counts[bin_counts >= 100].index
    filtered_df = df[df['user_bin'].isin(valid_bins)]
    stats = filtered_df.groupby('user_bin')['log_duration'].agg(
        median='median',
        q1=lambda x: x.quantile(0.3),
        q3=lambda x: x.quantile(0.7),
        p80=lambda x: x.quantile(0.8),
        p20=lambda x: x.quantile(0.2)
    ).reset_index()
    stats['user_bin_str'] = stats['user_bin'].astype(str)
    plt.figure(figsize=(12, 6))
    ax = plt.gca()
    sns.lineplot(data=stats, x='user_bin_str', y='median', marker='o', label='Median', color=palette[platform], ax=ax)
    ax.fill_between(
        x=range(len(stats)),
        y1=stats['q1'],
        y2=stats['q3'],
        alpha=0.3,
        color=palette[platform],
        label='IQR (30th-70th percentile)'
    )
    ax.fill_between(
        x=range(len(stats)),
        y1=stats['p80'],
        y2=stats['p20'],
        alpha=0.1,
        color=palette[platform],
        label='IQR (20th-80th percentile)'
    )
    ax.set_ylim(bottom=0)
    ax.set_title(f'{platform.capitalize()}')
    bin_intervals = filtered_df['user_bin'].cat.categories  # Get actual categories for filtered data
    x_labels = [str(int(interval.left)) for interval in bin_intervals]  # Display the left edge of each bin
    ax.set_xticks(range(len(bin_intervals)))  # Ensure ticks match the number of bins
    ax.set_xticklabels(x_labels, rotation=45)
    ax.set_xlabel('Number of users (logarithmic)')
    ax.set_ylabel('Lifetime (hours)')
    ax.legend()
    plt.tight_layout()
    plt.savefig(root + f'PAPER/output/1_section/2_lifetime_conversation_{platform}.png')
    plt.show()

    # 3. Concentration of the conversation
    csv_filename = root + f'PAPER/output/1_section/3_entrance_in_conversation_{platform}.csv'
    if not os.path.exists(csv_filename):
        df_sorted = data.sort_values(by=['timestamp'])
        first_comments = df_sorted.groupby(['post_id', 'user_id']).first().reset_index()
        first_post_comments = df_sorted.groupby('post_id').first().reset_index()
        df = pd.merge(first_comments, first_post_comments, on='post_id', suffixes=('', '_post'))
        df['time_difference_seconds'] = (df['timestamp'] - df['timestamp_post']).dt.total_seconds() / 3600
        df['num_users_per_post'] = df.groupby('post_id')['user_id'].transform('nunique')
        df = df.dropna(subset=['time_difference_seconds', 'num_users_per_post'])
        df['log_unique_users'] = df['num_users_per_post'] 
        df['log_duration'] = df['time_difference_seconds'] + 1
        bin_edges = [1, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192] + [np.inf]  # Define bins for user counts
        df['user_bin'] = pd.cut(df['log_unique_users'], bins=bin_edges)
        bin_counts = df['user_bin'].value_counts()
        valid_bins = bin_counts[bin_counts >= 200].index
        filtered_df = df[df['user_bin'].isin(valid_bins)]
        stats = filtered_df.groupby('user_bin')['log_duration'].agg(
            median='median',
            q1=lambda x: x.quantile(0.3),
            q3=lambda x: x.quantile(0.7),
            p80=lambda x: x.quantile(0.8),
            p20=lambda x: x.quantile(0.2)
        ).reset_index()
        stats['user_bin_str'] = stats['user_bin'].astype(str)
        stats.to_csv(csv_filename, index=False)
    # Plot
    stats = pd.read_csv(csv_filename)
    stats.loc[stats['median'] > 1000, stats.columns != 'user_bin'] = np.nan
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=stats, x='user_bin_str', y='median', marker='o', label='Median', color=palette[platform])
    plt.fill_between(
        x=range(len(stats)),
        y1=stats['q1'],
        y2=stats['q3'],
        alpha=0.3,
        color=palette[platform],
        label='IQR (30th-70th percentile)'
    )
    plt.fill_between(
        x=range(len(stats)),
        y1=stats['p80'],
        y2=stats['p20'],
        alpha=0.1,
        color=palette[platform],
        label='IQR (20th-80th percentile)'
    )
    plt.yscale('log')
    plt.ylim(0, 1000)
    plt.title(f'{platform.capitalize()}')

    plt.xlabel('Number of users (logarithmic)')
    bin_intervals = filtered_df['user_bin'].cat.categories  # Get actual categories for filtered data
    x_labels = [str(int(interval.left)) for interval in bin_intervals]  # Display the left edge of each bin
    plt.xticks(range(len(bin_intervals)), x_labels, rotation=45)

    plt.ylabel('Entrance (hours)')
    plot_filename = root + f'PAPER/output/1_section/3_entrance_in_conversation_{platform}.png'
    plt.tight_layout()
    plt.savefig(plot_filename)
    plt.close()  # Close the plot to save memory
'''
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
        valid_bins = result['user_count_bin'].value_counts()[result['user_count_bin'].value_counts() > 10000].index
        result = result[result['user_count_bin'].isin(valid_bins)]
        result['comment_count'] = result['comment_count'].apply(lambda x: 10 if x > 10 else x)
        balanced_result = result.groupby('user_count_bin').apply(
            lambda x: x.sample(n=min(len(x), 10000), random_state=42) if len(x) > 0 else x
        ).reset_index(drop=True)
        # Creazione dei sub-bins, dividendo ogni bin in 10 gruppi da 100
        balanced_result['subbin'] =balanced_result.groupby('user_count_bin').cumcount() // 250 + 1

        prob_dist = balanced_result.groupby(['user_count_bin','subbin'])['comment_count'].value_counts(normalize=True)
        localization_results = prob_dist.groupby(['user_count_bin','subbin']).apply(lambda x: calculate_localization_parameter(x.values)).reset_index(name='localization_parameter')
        alpha_results = prob_dist.groupby(['user_count_bin','subbin']).apply(lambda x: calculate_alpha_parameter(x.values)).reset_index(name='localization_parameter')
        localization_results.to_csv(root + f'PAPER/output/1_section/4_dialogue_level_{platform}.csv')
        alpha_results.to_csv(root + f'PAPER/output/1_section/4_dialogue_level_{platform}_alpha.csv')

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
