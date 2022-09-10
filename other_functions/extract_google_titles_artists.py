import pandas as pd
import copy
import numpy as np
from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

from search_functions import *
from concurrent.futures import ThreadPoolExecutor, as_completed

### HARD-CODED PATHS HERE ####

round_num = '09'
links_csv_path = 'data/round_' + round_num + '/google_links_extracted.csv'
input_csv_path = 'data/match_grid_expanded_sep_04_after_integration.csv'



##############################


logger = create_logger()

services_ignored = ['amazon','wynk',]
services_taken = [ 'apple','gaana','hungama','jiosaavn','spotify','ytmusic']
service_list = services_taken + services_ignored

links_df = pd.read_csv(links_csv_path, dtype = str, index_col='index')

matches_merged_df = pd.read_csv(input_csv_path, dtype = str, index_col='index')

links_df_column_names = links_df.columns.values.tolist()
basic_column_name_list = []
for column_name in links_df_column_names:
	if not any(substring in column_name for substring in service_list):
		basic_column_name_list.append(column_name)

function_dict = { 	
				'apple': get_artist_title_apple,
				'gaana': get_artist_title_gaana,
				'hungama': get_artist_title_hungama,
				'jiosaavn': get_artist_title_jiosaavn,
				'spotify': get_artist_title_spotify,
				'ytmusic': get_artist_title_ytmusic,
				}

def fill_artist_title(service):
	service_column_name = service + '_link'
	column_name_list = basic_column_name_list + [service_column_name]
	df_for_saving_raw = links_df[column_name_list]
	df_for_saving = copy.deepcopy(df_for_saving_raw)

	matches_missing_index_list = matches_merged_df[matches_merged_df[service].isnull()].index.tolist()

	# will i get f***d over by index mismatch in the line below? Check
	df_for_saving_relevant = df_for_saving[df_for_saving.index.isin(matches_missing_index_list)]
	df_for_saving_has_links = df_for_saving_relevant[df_for_saving_relevant[service_column_name].notnull()]

	# for index, row  in df_for_saving_has_links.head(3).iterrows(): # for testing
	for index, row  in df_for_saving_has_links.iterrows():
		print(str(index).zfill(4) + ' ' + service)
		genre = row['genre']
		url = row[service_column_name]
		time_sleep(18,22)
		try:
			artist_title_list = function_dict[service](url, genre)
		except:
			print('redo artist and title extraction for index number ' + str(index) + ' for service ' + service)
			continue
		artist = artist_title_list[0]
		title =  artist_title_list[1]
		artist_column_name = service + '_artist'
		df_for_saving_has_links.loc[index, artist_column_name] = artist
		title_column_name = service + '_title'
		df_for_saving_has_links.loc[index, title_column_name] = title
		
	# adding column for manual correction, pre-filled with 'yes' string 
	df_for_saving_has_links['correct'] = 'yes'
	save_path = 'data/round_' + round_num + '/artists_titles_for_' + service + '.csv'
	df_for_saving_has_links.to_csv(save_path, encoding='utf-8')

with ThreadPoolExecutor(max_workers=6) as pool:
	futures = []
	for service in services_taken:
		futures.append(pool.submit(fill_artist_title, service))
	for future in as_completed(futures):
		try:
			future.result()
		except Exception as e:
			logger.exception(e, stack_info=True)

