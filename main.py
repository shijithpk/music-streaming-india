#!/usr/bin/python3

from search_functions import *
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

logger = create_logger()

service_dict = {
				'amazon':find_matches_amazon,
				'apple':find_matches_apple,
				'gaana':find_matches_gaana,
				# 'hungama':find_matches_hungama,
				'jiosaavn':find_matches_jiosaavn,
				'spotify':find_matches_spotify,
				'wynk':find_matches_wynk,
				'ytmusic':find_matches_ytmusic,
				}

orig_data_path = 'data/all_data_v14.csv'

# for first run of code, put input_csv_path = None here
input_csv_path = 'data/match_grid_expanded_sep_23_wynk_update_rights_holder_final.csv'


def create_holding_dict(service_dict, orig_data_path, input_csv_path):
	holding_dict = {}
	
	orig_df = pd.read_csv(orig_data_path, dtype = str, index_col='index')
	if not input_csv_path: #ie. if input_csv_path=None for first run of code
		grid_df = copy.deepcopy(orig_df)
		for service in service_dict:
			url_column_name = 'matched_url_' + service
			title_column_name = 'matched_title_' + service
			artist_column_name = 'matched_artist_' + service
			grid_df[url_column_name] = np.nan
			grid_df[title_column_name] = np.nan
			grid_df[artist_column_name] = np.nan
	else:
		grid_df = pd.read_csv(input_csv_path, dtype = str, index_col='index')

	for service in service_dict:
		url_column_name = 'matched_url_' + service
		index_df_for_searching = grid_df[grid_df[url_column_name].isnull()]
		index_list_for_searching = index_df_for_searching.index.tolist()

		service_df = orig_df[orig_df.index.isin(index_list_for_searching)]
		holding_dict[service] = copy.deepcopy(service_df)

	return holding_dict


holding_dict = create_holding_dict(service_dict, orig_data_path, input_csv_path)

#for first run put round_num = '01'
round_num = '10'

# searching on services for albums that havent gotten a match
with ThreadPoolExecutor(max_workers=8) as pool:
	futures = []
	for service in service_dict:
		output_csv = 'round_' + round_num + '/matches_' + service +\
										 '_round_' + round_num + '_partial.csv'
		function = service_dict[service]
		futures.append(pool.submit(
								function,
								# below are function parameters 
								albums_df=holding_dict[service],
								csv_name=output_csv,
								min_matched=5,
								min_checked=25,
								min_combos=6
								))

	for future in as_completed(futures):
		try:
			future.result()
		except Exception as e:
			logger.exception(e, stack_info=True)


# insert columns with generalised jaccard scores in partial csvs
os.system('python3 other_functions/insert_genjacc_scores.py')
print('insertion of gen jacc scores done')

# find match with highest gen jacc score from five possibilities 
os.system('python3 other_functions/choose_genjacc_match.py')
print('choosing best gen jacc match done')

# optional -- print text file to double check chosen match manually
os.system('python3 other_functions/create_txt_false_pos_check.py')
print('creation of txt for false positive check done')

# merge partial csvs together
os.system('python3 other_functions/integrate_partial_csvs.py')
print('merging of csvs done')

# download google results with links from infocards to albums on various services
os.system('python3 other_functions/download_google_results.py')
print('downloading google results done')

# extract links from google infocards 
os.system('python3 other_functions/extract_google_links.py')
print('extracting links from downloaded results done')

# find title and artist information for links received from google infocards 
os.system('python3 other_functions/extract_google_titles_artists.py')
print('extracting titles and artists for album links done')

# creating txt to check google results for false positives 
	# if the album's not a match, just remove the pre-filled 'yes'
os.system('python3 other_functions/create_txt_false_pos_check_google.py')
print('checking google results for false positives done')

# integrate results from google infocards
os.system('python3 other_functions/integrate_google_results.py')
print('integrating google results done done')

# next two scripts need to be reworked, commenting them out for now 

# # check if albums are playable/ are inactive / have less than 80% of tracks
# os.system('python3 other_functions/check_playability.py')
# print('checking playability of albums done')

# # remove albums that arent playable, targets taken from for_manual_removal.csv 
# os.system('python3 other_functions/manual_removal.py')
# print('removal of unplayable albums done')

# find copyright and label info for matches
os.system('python3 other_functions/find_label_info.py')
print('finding label info done')

# come up with options for rights holder based on different criteria 
os.system('python3 other_functions/find_rights_holders.py')
print('presenting options for rights holder done')

# choose a rights holder from different options 
os.system('python3 other_functions/choose_rights_holder.py')
print('choosing rights holder done')

# calculate ratings and other scores 
os.system('python3 other_functions/calculate_scores.py')
print('calculation of ratings and other scores done')

# make graphics for each genre based on scores 
os.system('python3 other_functions/create_graphics.py')
print('creation of graphics done')

# calculating what percentage of a label's albums does a service have
os.system('python3 other_functions/guess_label_tieups.py')
print('creation of label_coverage.csv done')

# put % coverage of a label's albums in terms of ratings points
os.system('python3 other_functions/translate_coverage_into_ratings.py')
print('translation of label coverage into ratings points done')

# print out the one music group deal that'll most move needle for each service
os.system('python3 other_functions/print_must_do_deals.py')
print('printing of critical deals done')


# line for cron and at jobs on linux system
# cd /absolute/path/to/folder && stdbuf -o0 -e0 /usr/bin/python3 ./main.py >> /absolute/path/to/folder/responses_logs/cron_logs/`date +\%Y-\%m-\%d-\%H:\%M`-music-search-cron.log 2>&1
