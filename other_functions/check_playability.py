



# ALL CODE BELOW NEEDS TO BE REWORKED, PLEASE DONT USE AS IS 





import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

from search_functions import *

# this file removes albums that aren't playable and logs names of albums 
	# whose track counts are more in spotify/apple than in other services 
	# meaning sthing fishy is going on, so check it out 


input_csv_path = 'data/match_grid_expanded_aug_4_after_insertion.csv'
save_csv_path = 'data/for_manual_removal_after_activity_check_v2.csv'

def check_playability(input_csv_path, save_csv_path):

	headings = ['index','title','artist','target_url','tracks_count_target','tracks_count_target_playable',
				'spotify_url','spotify_title','tracks_count_spotify', 'apple_url','apple_title','tracks_count_apple','statement']

	with open(save_csv_path, "w") as filem:   
		wr = csv.writer(filem, delimiter = ',' , quotechar = '"' )
		wr.writerow(headings)

	def write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
				spotify_url, spotify_title, tracks_count_spotify, apple_url, apple_title, tracks_count_apple,statement):
		with open(save_csv_path, "a") as filen:
			wrz = csv.writer(filen, delimiter = ',' , quotechar = '"' )
			wrz.writerow([index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
				spotify_url, spotify_title, tracks_count_spotify, apple_url, apple_title, tracks_count_apple,statement])
			filen.flush()

	logger = create_logger()
	
	expanded_grid_df = pd.read_csv(input_csv_path, dtype = str, index_col='index')

	# index,year,title,artist,source,canon_contemp,genre,list_name,matched_artist_amazon,matched_title_amazon,matched_url_amazon,matched_artist_gaana,matched_title_gaana,matched_url_gaana,matched_artist_wynk,matched_title_wynk,matched_url_wynk,matched_artist_apple,matched_title_apple,matched_url_apple,matched_artist_jiosaavn,matched_title_jiosaavn,matched_url_jiosaavn,matched_artist_spotify,matched_title_spotify,matched_url_spotify,matched_artist_ytmusic,matched_title_ytmusic,matched_url_ytmusic,matched_artist_hungama,matched_title_hungama,matched_url_hungama

	expanded_grid_df_culled = expanded_grid_df[(expanded_grid_df['matched_url_spotify'].notnull())|\
								(expanded_grid_df['matched_url_apple'].notnull())]

	service_dict = {
	'amazon': { 'domain': 'amazon', 'function': get_activity_tracks_amazon },
	'gaana': { 'domain': 'gaana', 'function': get_activity_tracks_gaana },
	'hungama': { 'domain': 'hungama', 'function': get_activity_tracks_hungama },
	'jiosaavn': { 'domain': 'jiosaavn', 'function': get_activity_tracks_jiosaavn },
	'wynk': { 'domain': 'wynk', 'function': get_activity_tracks_wynk },
	'ytmusic': { 'domain': 'youtube', 'function': get_activity_tracks_ytmusic },
	}

	# for index, row in expanded_grid_df_culled.sample(n=20).iterrows(): # for testing
	for index, row in expanded_grid_df_culled.iterrows():

		title = row['title']
		artist = row['artist']
		spotify_title = row['matched_title_spotify']
		apple_title =  row['matched_title_apple']
		
		tracks_count_target = np.nan
		tracks_count_target_playable = np.nan
		tracks_count_spotify = np.nan
		tracks_count_apple = np.nan
		tracks_count_apple_actual = np.nan
		tracks_count_spotify_actual = np.nan

		time_sleep(10,15)

		spotify_url = expanded_grid_df_culled.at[index, 'matched_url_spotify']
		apple_url = expanded_grid_df_culled.at[index, 'matched_url_apple']

		if (isinstance(spotify_url, float) and np.isnan(spotify_url)):
			tracks_count_spotify = 1000
		else:
			target_url = spotify_url

			try:
				activity_tracks_dict_spotify = get_activity_tracks_spotify(spotify_url)
			except:
				statement = 'Redo row for all services. Issue with ' + spotify_url
				print(statement)
				write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
					spotify_url, spotify_title, tracks_count_spotify, apple_url, apple_title, tracks_count_apple,statement)
				continue
			
			tracks_count_spotify_actual =  activity_tracks_dict_spotify['tracks_count']

			if activity_tracks_dict_spotify['activity_status'] == 'inactive without a doubt':
				statement = 'for index ' + str(index).zfill(4) + ' and service spotify, album is inactive without a doubt.'
				print(statement)
				write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
					spotify_url, spotify_title, tracks_count_spotify_actual, apple_url, apple_title, tracks_count_apple,statement)
				tracks_count_spotify = 1000

			# internal threshold is >= math.floor(0.8*total_tracks_on_album)
			elif activity_tracks_dict_spotify['activity_status'] == 'possibly inactive: below internal threshold':
				statement = 'for index ' + str(index).zfill(4) + ' and service spotify, album is possibly inactive: below internal threshold.'
				print(statement)
				write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
					spotify_url, spotify_title, tracks_count_spotify_actual, apple_url, apple_title, tracks_count_apple,statement)
				tracks_count_spotify = activity_tracks_dict_spotify['tracks_count']

			elif activity_tracks_dict_spotify['activity_status'] == 'possibly inactive: but over internal threshold':
				statement = 'for index ' + str(index).zfill(4) + ' and service spotify, album is possibly inactive: but over internal threshold.'
				print(statement)
				write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
					spotify_url, spotify_title, tracks_count_spotify_actual, apple_url, apple_title, tracks_count_apple,statement)
				tracks_count_spotify = activity_tracks_dict_spotify['tracks_count']

			elif activity_tracks_dict_spotify['activity_status'] == 'possibly active':
				tracks_count_spotify = activity_tracks_dict_spotify['tracks_count']
		

		if (isinstance(apple_url, float) and np.isnan(apple_url)):
			tracks_count_apple = 1000
		else:
			target_url = apple_url

			try:
				activity_tracks_dict_apple = get_activity_tracks_apple(apple_url)
			except:
				statement = 'Redo row for all services. Issue with ' + apple_url
				print(statement)
				write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
					spotify_url, spotify_title, tracks_count_spotify, apple_url, apple_title, tracks_count_apple,statement)
				continue
			
			tracks_count_apple_actual = activity_tracks_dict_apple['tracks_count']

			if activity_tracks_dict_apple['activity_status'] == 'inactive without a doubt':
				statement = 'for index ' + str(index).zfill(4) + ' and service apple, album is inactive without a doubt.'
				print(statement)
				write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
					spotify_url, spotify_title, tracks_count_spotify, apple_url, apple_title, tracks_count_apple_actual,statement)
				tracks_count_apple = 1000

			elif activity_tracks_dict_apple['activity_status'] == 'possibly inactive: below internal threshold':
				statement = 'for index ' + str(index).zfill(4) + ' and service apple, album is possibly inactive: below internal threshold.'
				print(statement)
				write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
					spotify_url, spotify_title, tracks_count_spotify, apple_url, apple_title, tracks_count_apple_actual,statement)
				tracks_count_apple = activity_tracks_dict_apple['tracks_count']

			elif activity_tracks_dict_apple['activity_status'] == 'possibly inactive: but over internal threshold':
				statement = 'for index ' + str(index).zfill(4) + ' and service apple, album is possibly inactive: but over internal threshold.'
				print(statement)
				write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
					spotify_url, spotify_title, tracks_count_spotify, apple_url, apple_title, tracks_count_apple_actual,statement)
				tracks_count_apple = activity_tracks_dict_apple['tracks_count']

			elif activity_tracks_dict_apple['activity_status'] == 'possibly active':
				tracks_count_apple = activity_tracks_dict_apple['tracks_count']

		tracks_count_ideal = min(tracks_count_spotify, tracks_count_apple)

		def log_errors(service):
			global tracks_count_target
			global tracks_count_target_playable

			url_column_name = 'matched_url_' + service
			target_url = expanded_grid_df_culled.at[index, url_column_name]
			if (isinstance(target_url, float) and np.isnan(target_url)):
				return None

			try:
				activity_tracks_dict = service_dict[service]['function'](target_url)
				activity_status_target = activity_tracks_dict['activity_status']
				tracks_count_target = activity_tracks_dict['tracks_count']
				tracks_count_target_playable = activity_tracks_dict['tracks_count_playable']
			except:
				statement = 'issue with ' + target_url
				print(statement)
				write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
					spotify_url, spotify_title, tracks_count_spotify_actual, apple_url, apple_title, tracks_count_apple_actual,statement)
				return None

			if activity_status_target == 'redo the check, had an issue':
				statement = 'for index ' + str(index).zfill(4) + ' and service ' + service + ', redo the check, had an issue.'
				print(statement)
				write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
					spotify_url, spotify_title, tracks_count_spotify_actual, apple_url, apple_title, tracks_count_apple_actual,statement)
				return None

			if activity_status_target == 'inactive without a doubt':
				statement = 'for index ' + str(index).zfill(4) + ' and service ' + service + ', album is inactive without a doubt.'
				print(statement)
				write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
					spotify_url, spotify_title, tracks_count_spotify_actual, apple_url, apple_title, tracks_count_apple_actual,statement)
				return None

			threshold_ideal = 0.8 * tracks_count_ideal

			if tracks_count_ideal > tracks_count_target_playable >= threshold_ideal:
				statement = 'for index ' + str(index).zfill(4) + ' and service ' + service + ', album is possibly inactive: but over ideal threshold.'
				print(statement)
				write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
					spotify_url, spotify_title, tracks_count_spotify_actual, apple_url, apple_title, tracks_count_apple_actual,statement)
				return None

			elif tracks_count_target_playable < threshold_ideal:
				statement = 'for index ' + str(index).zfill(4) + ' and service ' + service + ', album is possibly inactive: below ideal threshold.'
				print(statement)
				write_row(index,title,artist,target_url,tracks_count_target,tracks_count_target_playable,
					spotify_url, spotify_title, tracks_count_spotify_actual, apple_url, apple_title, tracks_count_apple_actual,statement)
				return None

		with ThreadPoolExecutor(max_workers=8) as pool:
			futures = []
			for service in service_dict:
				futures.append(pool.submit(log_errors, service))
			for future in as_completed(futures):
				try:
					future.result()
				except Exception as e:
					logger.exception(e, stack_info=True)

		
print('done and done')


