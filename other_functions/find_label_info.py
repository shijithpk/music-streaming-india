import pandas as pd
import numpy as np
from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

from search_functions import *

def is_nan(valuex):
	if ((isinstance(valuex, float) and np.isnan(valuex))):
		return True
	else:
		return False


def find_label_info(input_csv_path, service_dict, output_csv_path):

	expanded_grid_df = pd.read_csv(input_csv_path, dtype = str, 
															index_col='index')

	# creating empty columns if they arent there already, the first run of code 
	label_copyright_cols = []
	for service in service_dict:
		label_column_name = 'matched_label_' + service
		label_copyright_cols.append(label_column_name)
		copyright_column_name = 'matched_copyright_' + service
		label_copyright_cols.append(copyright_column_name)
	present_cols = expanded_grid_df.columns.values.tolist()
	for col in label_copyright_cols:
		if col not in present_cols:
			expanded_grid_df[col] = np.nan

	# for index, row in expanded_grid_df.sample(n=5).iterrows(): # for testing
	for index, row in expanded_grid_df.iterrows():
		for service in service_dict:
			label_column_name = 'matched_label_' + service
			copyright_column_name = 'matched_copyright_' + service
			label_value = row[label_column_name]
			copyright_value = row[copyright_column_name]

			# if value -- or empty string -- already there, move on 
			if not (is_nan(label_value) and is_nan(copyright_value)): continue

			url_column_name = 'matched_url_' + service
			target_url = row[url_column_name]
			if is_nan(target_url):	continue

			time_sleep(2,3)
			try:
				label_copyright = service_dict[service]['function'](target_url)
				label = label_copyright[0]
				copyright = label_copyright[1]
			except:
				label = ''
				copyright = ''
				print('issue with ' + target_url)

			expanded_grid_df.at[index, label_column_name] = label
			expanded_grid_df.at[index, copyright_column_name] = copyright

	expanded_grid_df.to_csv(output_csv_path, encoding='utf-8')


# not taking hungama & youtube below, ytmusicapi doesnt return copyright info
service_dict = {
'apple': { 'domain': 'apple', 'function': get_label_copyright_apple },
'jiosaavn': { 'domain': 'jiosaavn', 'function': get_label_copyright_jiosaavn },
'spotify': { 'domain': 'spotify', 'function': get_label_copyright_spotify },
'amazon': { 'domain': 'amazon', 'function': get_label_copyright_amazon },
'gaana': { 'domain': 'gaana', 'function': get_label_copyright_gaana },
'wynk': { 'domain': 'wynk', 'function': get_label_copyright_wynk },
}

input_csv_path = 'data/match_grid_expanded_sep_27_after_jiosaavn_insertion.csv'
output_csv_path = 'data/match_grid_expanded_sep_27_after_jiosaavn_label_info.csv'

find_label_info(input_csv_path=input_csv_path, 
				service_dict=service_dict, 
				output_csv_path=output_csv_path
				)


# cd /home/ubuntu/work/2022_03_17_music_app_remote/ && stdbuf -o0 -e0 /usr/bin/python3 ./other_functions/find_label_info.py >> /home/ubuntu/work/2022_03_17_music_app_remote/responses_logs/cron_logs/`date +\%Y-\%m-\%d-\%H:\%M`-find-label-info-cron.log 2>&1