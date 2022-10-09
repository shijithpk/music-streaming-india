import pandas as pd
import copy
import numpy as np

from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

from search_functions import *

# this code is for integration of matches from corrected grids 

def integrate_partial_csvs(old_csv_path, round_num, 
							services_taken, services_ignored, new_csv_path):

	services_combined = services_taken + services_ignored

	old_csv_path = old_csv_path
	expanded_grid_df = pd.read_csv(old_csv_path, dtype = str, index_col='index')

	# this section of code just for first run 
	expanded_grid_df_column_names = expanded_grid_df.columns.values.tolist()
	for service in services_combined:
		url_column_name = 'matched_url_' + service
		title_column_name = 'matched_title_' + service
		artist_column_name = 'matched_artist_' + service
		if url_column_name not in expanded_grid_df_column_names:
			expanded_grid_df[url_column_name] = np.nan
		if title_column_name not in expanded_grid_df_column_names:
			expanded_grid_df[title_column_name] = np.nan
		if artist_column_name not in expanded_grid_df_column_names:
			expanded_grid_df[artist_column_name] = np.nan

	expanded_grid_df_column_names = expanded_grid_df.columns.values.tolist()
	basic_column_name_list = []
	for column_name in expanded_grid_df_column_names:
		if not any(substring in column_name for substring in services_combined):
			basic_column_name_list.append(column_name)

	new_expanded_grid_df_raw = expanded_grid_df[basic_column_name_list]
	new_expanded_grid_df = copy.deepcopy(new_expanded_grid_df_raw)

	for service in services_combined:
		service_column_name_list =\
			[x for x in expanded_grid_df_column_names if service in x]
		service_df_raw = expanded_grid_df[service_column_name_list]
		service_df = copy.deepcopy(service_df_raw)

		if service in services_taken:

			corrected_grid_csv_path ='data/round_' + round_num + '/matches_' +\
				 service + '_round_' + round_num + '_chosen_match_corrected.csv'
			corrected_grid_df = pd.read_csv(corrected_grid_csv_path, 
												dtype = str, index_col='index')

			matches_partial_csv_path = 'data/round_' + round_num + '/matches_' +\
							 service + '_round_' + round_num + '_partial.csv'
			matches_partial_df = pd.read_csv(matches_partial_csv_path,
												 dtype = str, index_col='index')

			corrected_grid_df_relevant =\
				corrected_grid_df[corrected_grid_df[service].notnull()]
			# will there be index mismatch here?
			for index, row in corrected_grid_df_relevant.iterrows():
				match_num = row[service]
				artist_col_name_partials =\
					'match_artist_' + service + '_' + str(match_num)
				title_col_name_partials =\
					'match_title_' + service + '_' + str(match_num)
				url_col_name_partials =\
					'match_url_' + service + '_' + str(match_num)
				target_artist =\
					matches_partial_df.at[index, artist_col_name_partials]
				target_title =\
					matches_partial_df.at[index, title_col_name_partials]
				target_url =\
					matches_partial_df.at[index, url_col_name_partials]

				artist_col_name_service_df = 'matched_artist_' + service
				title_col_name_service_df = 'matched_title_' + service
				url_col_name_service_df = 'matched_url_' + service

				service_df.at[index, artist_col_name_service_df] = target_artist
				service_df.at[index, title_col_name_service_df] = target_title
				service_df.at[index, url_col_name_service_df] = target_url

		new_expanded_grid_df = new_expanded_grid_df.join(service_df)

	new_expanded_grid_csv_path = new_csv_path
	new_expanded_grid_df.to_csv(new_expanded_grid_csv_path, encoding='utf-8')

# for first run of code put old_csv_path = all_data_v??.csv
old_csv_path = 'data/match_grid_expanded_sep_23_after_amazon_insertion.csv'
new_csv_path = 'data/match_grid_expanded_sep_23_after_wynk_update.csv'
round_num = '10'

services_taken = [
					# 'amazon',
					# 'apple',
					# 'gaana',
					# 'hungama',
					# 'jiosaavn',
					# 'spotify',
					'wynk',
					# 'ytmusic',
					]

services_ignored = [
					'amazon',
					'apple',
					'gaana',
					'hungama',
					'jiosaavn',
					'spotify',
					# 'wynk',
					'ytmusic',
					]

integrate_partial_csvs(	old_csv_path=old_csv_path, 
						round_num=round_num, 
						services_taken=services_taken, 
						services_ignored=services_ignored, 
						new_csv_path=new_csv_path
						)


# cd /home/ubuntu/work/2022_03_17_music_app_remote/ && stdbuf -o0 -e0 /usr/bin/python3 ./other_functions/integrate_partial_csvs.py >> /home/ubuntu/work/2022_03_17_music_app_remote/responses_logs/cron_logs/`date +\%Y-\%m-\%d-\%H:\%M`-partial-csv-integration-cron.log 2>&1