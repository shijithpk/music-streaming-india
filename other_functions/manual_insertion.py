import pandas as pd
import copy
import numpy as np
from search_functions import *

# BELOW AM INSERTING MATCHES FROM MANUAL INSERTION 

expanded_grid_csv_path = 'data/match_grid_expanded_aug_6_after_removal.csv'
expanded_grid_df = pd.read_csv(expanded_grid_csv_path, dtype = str, index_col='index')

insertion_csv_path = 'data/for_manual_insertion_2022_08_06.csv'
insertion_df =  pd.read_csv(insertion_csv_path, dtype = str, index_col='index')
# will the fact that the index is duplicated sometimes in this df affect anything? 

# index	service	target_url	target_title	target_artist

service_dict = {
'apple': { 'domain': 'apple', 'function': get_artist_title_apple },
'jiosaavn': { 'domain': 'jiosaavn', 'function': get_artist_title_jiosaavn },
'spotify': { 'domain': 'spotify', 'function': get_artist_title_spotify },
'ytmusic': { 'domain': 'youtube', 'function': get_artist_title_ytmusic },
'amazon': { 'domain': 'amazon', 'function': get_artist_title_amazon },
'gaana': { 'domain': 'gaana', 'function': get_artist_title_gaana },
'hungama': { 'domain': 'hungama', 'function': get_artist_title_hungama },
'wynk': { 'domain': 'wynk', 'function': get_artist_title_wynk },
}

for index, row in insertion_df.iterrows():
	target_url = row['target_url']
	for service in service_dict:
		if service_dict[service]['domain'] in target_url:
			time_sleep(10,15)
			try:
				target_artist_title = service_dict[service]['function'](target_url,'')
				target_artist = target_artist_title[0]
				target_title = target_artist_title[1]
			except:
				target_artist = ''
				target_title = ''
				print('issue with ' + target_url)
			
			artist_col_name_grid_df = 'matched_artist_' + service
			title_col_name_grid_df = 'matched_title_' + service
			url_col_name_grid_df = 'matched_url_' + service

			expanded_grid_df.at[index, artist_col_name_grid_df] = target_artist
			expanded_grid_df.at[index, title_col_name_grid_df] = target_title
			expanded_grid_df.at[index, url_col_name_grid_df] = target_url

new_expanded_grid_csv_path = 'data/match_grid_expanded_aug_6_after_insertion.csv'
expanded_grid_df.to_csv(new_expanded_grid_csv_path, encoding='utf-8')

print('done and done')

# line for cron jobs
# cd /home/ubuntu/work/2022_03_17_music_app_remote && stdbuf -o0 -e0 /usr/bin/python3 ./manual_insertion.py >> /home/ubuntu/work/2022_03_17_music_app_remote/responses_logs/cron_logs/`date +\%Y-\%m-\%d-\%H:\%M`-manual_insertion-cron.log 2>&1