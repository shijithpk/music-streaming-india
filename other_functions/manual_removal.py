import pandas as pd
import copy
import numpy as np
from search_functions import *

# BELOW AM REMOVING MATCHES

expanded_grid_csv_path = 'data/match_grid_expanded_aug_4_after_insertion.csv'
expanded_grid_df = pd.read_csv(expanded_grid_csv_path, dtype = str, index_col='index')

removal_csv_path = 'data/for_manual_removal_2022_08_06.csv'
removal_df =  pd.read_csv(removal_csv_path, dtype = str, index_col='index')

# columns in removal_df are [index, target_url]

# service_list = ['amazon','apple','gaana',
# 				'hungama',
# 				'jiosaavn','spotify','wynk','ytmusic']

service_dict = {
'apple': { 'domain': 'apple'},
'jiosaavn': { 'domain': 'jiosaavn'},
'spotify': { 'domain': 'spotify'},
'ytmusic': { 'domain': 'youtube'},
'amazon': { 'domain': 'amazon'},
'gaana': { 'domain': 'gaana'},
'hungama': { 'domain': 'hungama'},
'wynk': { 'domain': 'wynk'},
}


for index, row in removal_df.iterrows():
	target_url = row['target_url']
	for service in service_dict:
		if service_dict[service]['domain'] in target_url:
			artist_col_name_grid_df = 'matched_artist_' + service
			title_col_name_grid_df = 'matched_title_' + service
			url_col_name_grid_df = 'matched_url_' + service

			expanded_grid_df.at[index, artist_col_name_grid_df] = np.nan
			expanded_grid_df.at[index, title_col_name_grid_df] = np.nan
			expanded_grid_df.at[index, url_col_name_grid_df] = np.nan

new_expanded_grid_csv_path = 'data/match_grid_expanded_aug_6_after_removal.csv'
expanded_grid_df.to_csv(new_expanded_grid_csv_path, encoding='utf-8')

print('done and done')

# line for cron jobs
# cd /home/ubuntu/work/2022_03_17_music_app_remote && stdbuf -o0 -e0 /usr/bin/python3 ./manual_removal.py >> /home/ubuntu/work/2022_03_17_music_app_remote/responses_logs/cron_logs/`date +\%Y-\%m-\%d-\%H:\%M`-manual_removal-cron.log 2>&1