import pandas as pd
import copy
import numpy as np
from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

from search_functions import *

def integrate_google_results(input_csv_path, round_num, output_csv_path, 
							services_taken, services_ignored):

	old_expanded_grid_df = pd.read_csv(input_csv_path, dtype = str, 
															index_col='index')
	old_expanded_grid_df.sort_index(axis = 0, inplace=True)

	combined_service_list = services_taken + services_ignored

	old_expanded_grid_df_column_names =\
									old_expanded_grid_df.columns.values.tolist()
	basic_column_name_list = []
	for column_name in old_expanded_grid_df_column_names:
		if not any(substring in column_name for substring in combined_service_list):
			basic_column_name_list.append(column_name)

	new_expanded_grid_df_raw = old_expanded_grid_df[basic_column_name_list]
	new_expanded_grid_df = copy.deepcopy(new_expanded_grid_df_raw)

	for service in combined_service_list:
		service_column_name_list =\
				 [x for x in old_expanded_grid_df_column_names if service in x]
		service_df_raw = old_expanded_grid_df[service_column_name_list]
		service_df = copy.deepcopy(service_df_raw)

		if service in services_taken:
			google_matches_csv_path = 'data/round_' + round_num +\
				'/artists_titles_for_' + service + '_playable_corrected.csv'
			google_matches_df = pd.read_csv(google_matches_csv_path, dtype = str, 
															index_col='index')
			google_matches_df_relevant =\
					 google_matches_df[google_matches_df['correct']=='yes']
			index_list = google_matches_df_relevant.index.tolist()
			
			service_df_culled = service_df[~service_df.index.isin(index_list)]
			
			google_matches_df_relevant.rename(columns = {
										service + '_link': 'matched_url_' + service, 
										service + '_artist': 'matched_artist_' + service,
										service + '_title': 'matched_title_' + service,
										}, inplace = True)
			
			# rearrange both dfs in same column order 
			service_df_google_matches =\
				google_matches_df_relevant[service_column_name_list]

			#POSSBILITY OF INDEX MISMATCH, CHECK 

			# below we're changing the object service_df variable is attached to 
			service_df = pd.concat([service_df_culled, service_df_google_matches],
																		 axis=0)
			# dont think we need to sort, just being on safe side
			service_df.sort_index(axis = 0, inplace=True)			
		
		new_expanded_grid_df = new_expanded_grid_df.join(service_df)

	new_expanded_grid_df.to_csv(output_csv_path, encoding='utf-8')


round_num = '09'
input_csv_path = 'data/match_grid_expanded_sep_04_after_integration.csv'
output_csv_path = 'data/match_grid_expanded_sep_04_after_google_integration.csv'

services_ignored = ['amazon','wynk',]
services_taken = [ 'apple','gaana','hungama','jiosaavn','spotify','ytmusic']

integrate_google_results(input_csv_path, round_num, output_csv_path, 
							services_taken, services_ignored)
