#!/usr/bin/python3

from search_functions import *
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = create_logger()

# albums_df = pd.read_csv('data/all_data_v10.csv', dtype = str, index_col='index')

# test_df = albums_df.loc[950:1000]

# service_list = ['amazon','apple','gaana',
# 				'hungama',
# 				'jiosaavn','spotify','wynk','ytmusic']

#the concurrent code below could be simpler, pool.submit is enough
	# but am doing futures.append & future.result so error messages get displayed
# with ThreadPoolExecutor(max_workers=8) as pool:
# 	futures = []
# 	futures.append(pool.submit(find_matches_amazon, albums_df,
# 								'round_01/matches_amazon_round_01.csv',3,10,3))
# 	futures.append(pool.submit(find_matches_apple, albums_df,
# 								'round_01/matches_apple_round_01.csv',3,10,1))
# 	futures.append(pool.submit(find_matches_gaana, albums_df,
# 								'round_01/matches_gaana_round_01.csv',3,10,3))
# 	futures.append(pool.submit(find_matches_hungama, albums_df,
# 								'round_01/matches_hungama_round_01.csv',3,10,3))
# 	futures.append(pool.submit(find_matches_jiosaavn, albums_df,
# 								'round_01/matches_jiosaavn_round_01.csv',3,10,3))
# 	futures.append(pool.submit(find_matches_spotify, albums_df,
# 								'round_01/matches_spotify_round_01.csv',3,10,3))
# 	futures.append(pool.submit(find_matches_wynk, albums_df,
# 								'round_01/matches_wynk_round_01.csv',3,10,3))
# 	futures.append(pool.submit(find_matches_ytmusic, albums_df,
# 								'round_01/matches_ytmusic_round_01.csv',3,10,3))
# 	for future in as_completed(futures):
# 		try:
# 			future.result()
# 		except Exception as e:
# 			# print(e)
# 			logger.exception(e, stack_info=True)


# #for each service, creating dataframes of albums that dont have a single match
# second_round_df_dict = {}
# for service in service_list:
# 	service_csv_path = 'data/round_01/matches_' + service + '_round_01.csv'
# 	service_df = pd.read_csv(service_csv_path, dtype = str, 
# 							index_col='index')
# 	title_col_name = 'match_title_' + service + '_1'
# 	service_df_culled = service_df[service_df[title_col_name].isnull()]
# 	second_round_df_dict[service] = service_df_culled

#another round of searching on services for albums that havent gotten a match
# with ThreadPoolExecutor(max_workers=8) as pool:
# 	futures = []
# 	futures.append(pool.submit(find_matches_amazon, 
# 							second_round_df_dict['amazon'],
# 							'round_02/matches_amazon_round_02_culled.csv',
# 							3,30,12))
# 	futures.append(pool.submit(find_matches_apple, 
# 							second_round_df_dict['apple'],
# 							'round_02/matches_apple_round_02_culled.csv',
# 							3,30,12))
# 	futures.append(pool.submit(find_matches_gaana, 
# 							second_round_df_dict['gaana'],
# 							'round_02/matches_gaana_round_02_culled.csv',
# 							3,30,12))
# 	futures.append(pool.submit(find_matches_hungama,
# 							second_round_df_dict['hungama'],
# 							'round_02/matches_hungama_round_02_culled.csv',
# 							3,30,12))
# 	futures.append(pool.submit(find_matches_jiosaavn, 
# 							second_round_df_dict['jiosaavn'],
# 							'round_02/matches_jiosaavn_round_02_culled.csv',
# 							3,30,12))
# 	futures.append(pool.submit(find_matches_spotify, 
# 							second_round_df_dict['spotify'],
# 							'round_02/matches_spotify_round_02_culled.csv',
# 							3,30,12))
# 	futures.append(pool.submit(find_matches_wynk, 
# 							second_round_df_dict['wynk'],
# 							'round_02/matches_wynk_round_02_culled.csv',
# 							3,30,12))
# 	futures.append(pool.submit(find_matches_ytmusic, 
# 							second_round_df_dict['ytmusic'],
# 							'round_02/matches_ytmusic_round_02_culled.csv',
# 							3,30,12))
# 	for future in as_completed(futures):
# 		try:
# 			future.result()
# 		except Exception as e:
# 			# print(e)
# 			logger.exception(e, stack_info=True)

# merge_round_csvs(service_list)

# HAVE CODE HERE ABOUT COPYING HUNGAMA OVER TO 2ND ROUND , TAKES TOO LONG 
	# SKIPPED 2ND ROUND, BE HONEST ABOUT IT, GIVE REASONS WHY 

# merge_service_csvs()

# insert_genjacc_score_columns()

# insert_tokenset_score_columns()

#WEDNESDAY WORK BELOW

# create_txt_false_positive_check('for_manually_checking_false_positives.txt')

# explain why we're creating csvs for manual correction, and what actually we're manually correcting
# create_csvs_manual_correction()

# albums_df_round3 = pd.read_csv('data/all_data_v10_culled_round3.csv', 
# 								dtype = str, index_col='index')

# with ThreadPoolExecutor(max_workers=8) as pool:
# 	futures = []
# 	futures.append(pool.submit(find_matches_amazon, albums_df_round3,
# 								'round_03/matches_amazon_round_03.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_apple, albums_df_round3,
# 								'round_03/matches_apple_round_03.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_gaana, albums_df_round3,
# 								'round_03/matches_gaana_round_03.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_jiosaavn, albums_df_round3,
# 								'round_03/matches_jiosaavn_round_03.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_spotify, albums_df_round3,
# 								'round_03/matches_spotify_round_03.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_wynk, albums_df_round3,
# 								'round_03/matches_wynk_round_03.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_ytmusic, albums_df_round3,
# 								'round_03/matches_ytmusic_round_03.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_hungama, albums_df_round3,
# 								'round_03/matches_hungama_round_03.csv',
# 								'albums_processed.csv', 5,15,5))
# 	for future in as_completed(futures):
# 		try:
# 			future.result()
# 		except Exception as e:
# 			# print(e)
# 			logger.exception(e, stack_info=True)


# albums_df_round_04 = pd.read_csv('data/all_data_v11_culled_for_round_04.csv', 
# 								dtype = str, index_col='index')

# with ThreadPoolExecutor(max_workers=8) as pool:
# 	futures = []
# 	futures.append(pool.submit(find_matches_amazon, albums_df_round_04,
# 								'round_04/matches_amazon_round_04_select.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_apple, albums_df_round_04,
# 								'round_04/matches_apple_round_04_select.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_gaana, albums_df_round_04,
# 								'round_04/matches_gaana_round_04_select.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_jiosaavn, albums_df_round_04,
# 								'round_04/matches_jiosaavn_round_04_select.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_spotify, albums_df_round_04,
# 								'round_04/matches_spotify_round_04_select.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_wynk, albums_df_round_04,
# 								'round_04/matches_wynk_round_04_select.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_ytmusic, albums_df_round_04,
# 								'round_04/matches_ytmusic_round_04_select.csv',5,15,5))
# 	futures.append(pool.submit(find_matches_hungama, albums_df_round_04,
# 								'round_04/matches_hungama_round_04_select.csv',
# 								'albums_processed.csv', 5,15,5))
# 	for future in as_completed(futures):
# 		try:
# 			future.result()
# 		except Exception as e:
# 			logger.exception(e, stack_info=True)

# # UNCOMMENT ALL LINES BELOW FOR ROUND 5 
# # for round 5, no apple, spotify or hungama 

# # #for each service, creating dataframes of albums that dont have a single match
# def create_holding_dict_oneoff(all_data_csv_name,service_list):
# 	holding_dict = {}

# 	all_data_csv_path = 'data/' + all_data_csv_name
# 	albums_df = pd.read_csv(all_data_csv_path, dtype = str, index_col='index')

# 	index_csv_path = 'data/all_data_v11_culled_for_round_04.csv'
# 	index_df = pd.read_csv(index_csv_path, dtype = str, index_col='index')
# 	index_list = index_df.index.tolist()
	
# 	merged_corrected_csv_path = 'data/matches_corrected_after_round_03_local_all.csv'
# 	merged_corrected_df = pd.read_csv(merged_corrected_csv_path, dtype = str, index_col='index')
# 	merged_corrected_df_culled = merged_corrected_df[~merged_corrected_df.index.isin(index_list)]

# 	for service in service_list:
# 		index_df_for_searching = merged_corrected_df_culled[merged_corrected_df_culled[service].isnull()]
# 		index_list_for_searching = index_df_for_searching.index.tolist()
# 		service_df = albums_df[albums_df.index.isin(index_list_for_searching)]
# 		holding_dict[service] = copy.deepcopy(service_df)

# 	return holding_dict

# service_list = ['amazon','gaana','jiosaavn','wynk','ytmusic']

# holding_dict = create_holding_dict_oneoff(all_data_csv_name='all_data_v11.csv', 
# 					service_list=service_list)

# # #another round of searching on services for albums that havent gotten a match
# with ThreadPoolExecutor(max_workers=8) as pool:
# 	futures = []
# 	futures.append(pool.submit(find_matches_amazon, 
# 							holding_dict['amazon'],
# 							'round_05/matches_amazon_round_05_partial.csv',
# 							5,15,5))
# 	futures.append(pool.submit(find_matches_gaana, 
# 							holding_dict['gaana'],
# 							'round_05/matches_gaana_round_05_partial.csv',
# 							5,15,5))
# 	futures.append(pool.submit(find_matches_jiosaavn, 
# 							holding_dict['jiosaavn'],
# 							'round_05/matches_jiosaavn_round_05_partial.csv',
# 							5,15,5))
# 	futures.append(pool.submit(find_matches_wynk, 
# 							holding_dict['wynk'],
# 							'round_05/matches_wynk_round_05_partial.csv',
# 							5,15,5))
# 	futures.append(pool.submit(find_matches_ytmusic, 
# 							holding_dict['ytmusic'],
# 							'round_05/matches_ytmusic_round_05_partial.csv',
# 							5,15,5))
# 	for future in as_completed(futures):
# 		try:
# 			future.result()
# 		except Exception as e:
# 			logger.exception(e, stack_info=True)

# #for each service, creating dataframes of albums that dont have a single match
def create_holding_dict_oneoff_round_07(service_list):
	holding_dict = {}
	
	all_data_csv_path = 'data/all_data_v12.csv'
	all_data_df = pd.read_csv(all_data_csv_path, dtype = str, index_col='index')

	grid_csv_path = 'data/match_grid_expanded_after_round_06_updated.csv'
	grid_df = pd.read_csv(grid_csv_path, dtype = str, index_col='index')

	for service in service_list:
		service_column_name = 'matched_url_' + service
		index_df_for_searching = grid_df[grid_df[service_column_name].isnull()]
		index_list_for_searching = index_df_for_searching.index.tolist()

		service_df = all_data_df[all_data_df.index.isin(index_list_for_searching)]
		holding_dict[service] = copy.deepcopy(service_df)

	return holding_dict

service_list = ['amazon','gaana','wynk']
holding_dict = create_holding_dict_oneoff_round_07(service_list)

# #another round of searching on services for albums that havent gotten a match
with ThreadPoolExecutor(max_workers=8) as pool:
	futures = []
	futures.append(pool.submit(
						find_matches_amazon, 
							albums_df=holding_dict['amazon'],
							csv_name='round_07/matches_amazon_round_07_partial.csv',
							min_matched=5,
							min_checked=25,
							min_combos=6,
							threshold=80
							))
	futures.append(pool.submit(
						find_matches_gaana, 
							albums_df=holding_dict['gaana'],
							csv_name='round_07/matches_gaana_round_07_partial.csv',
							min_matched=5,
							min_checked=25,
							min_combos=6,
							threshold=80
							))

	futures.append(pool.submit(
						find_matches_wynk, 
							albums_df=holding_dict['wynk'],
							csv_name='round_07/matches_wynk_round_07_partial.csv',
							min_matched=5,
							min_checked=25,
							min_combos=6,
							threshold=80
							))

	for future in as_completed(futures):
		try:
			future.result()
		except Exception as e:
			logger.exception(e, stack_info=True)


# need code on merging these partial csvs 
# need code on inserting genjacc columns 
# need code for making a match grid 
# need code for making a text readout 
# manual step of correcing match grid by hand 
# need code for combinging partial csvs with rest 
	# this will be tricky, this is just 5 services, not all 8 
# need code for taking corrected match grid and merging it with rest 


#DO PLAYABLE_ON_SERVICE CODE HERE?


# CHECK FOR GHOST ALBUMS?


# line for cron jobs
# cd /home/ubuntu/work/2022_03_17_music_app_remote && stdbuf -o0 -e0 /usr/bin/python3 ./main.py >> /home/ubuntu/work/2022_03_17_music_app_remote/responses_logs/cron_logs/`date +\%Y-\%m-\%d-\%H:\%M`-music-search-cron.log 2>&1 