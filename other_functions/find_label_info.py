import pandas as pd
from search_functions import *
import numpy as np

expanded_grid_csv_path = 'data/match_grid_expanded_aug_06_after_insertion.csv'
expanded_grid_df = pd.read_csv(expanded_grid_csv_path, dtype = str, index_col='index')

service_dict = {
'apple': { 'domain': 'apple', 'function': get_label_copyright_apple },
'jiosaavn': { 'domain': 'jiosaavn', 'function': get_label_copyright_jiosaavn },
'spotify': { 'domain': 'spotify', 'function': get_label_copyright_spotify },
'amazon': { 'domain': 'amazon', 'function': get_label_copyright_amazon },
'gaana': { 'domain': 'gaana', 'function': get_label_copyright_gaana },
'wynk': { 'domain': 'wynk', 'function': get_label_copyright_wynk },
}
# not taking hungama & youtube, ytmusicapi package doesnt return copyright info

# for index, row in expanded_grid_df.sample(n=5).iterrows(): # for testing
for index, row in expanded_grid_df.iterrows():
	for service in service_dict:
		url_column_name = 'matched_url_' + service
		target_url = expanded_grid_df.at[index, url_column_name]
		if (isinstance(target_url, float) and np.isnan(target_url)):
			continue
		time_sleep(2,3)
		try:
			label_copyright = service_dict[service]['function'](target_url)
			label = label_copyright[0]
			copyright = label_copyright[1]
		except:
			label = ''
			copyright = ''
			print('issue with ' + target_url)
			
		label_column_name = 'matched_label_' + service
		copyright_column_name = 'matched_copyright_' + service
		expanded_grid_df.at[index, label_column_name] = label
		expanded_grid_df.at[index, copyright_column_name] = copyright

new_expanded_grid_csv_path = 'data/match_grid_expanded_aug_06_with_label_info.csv'
expanded_grid_df.to_csv(new_expanded_grid_csv_path, encoding='utf-8')


# line for cron jobs
# cd /home/ubuntu/work/2022_03_17_music_app_remote && stdbuf -o0 -e0 /usr/bin/python3 ./find_label_info.py >> /home/ubuntu/work/2022_03_17_music_app_remote/responses_logs/cron_logs/`date +\%Y-\%m-\%d-\%H:\%M`-label_info-cron.log 2>&1