import pandas as pd
import copy
import numpy as np

from pathlib import Path
import sys
root = Path(__file__).parent.parent
sys.path.append(str(root))

from search_functions import *

def choose_genjacc_match(service_list, round_num):
	for service in service_list:
		scores_csv_path = 'data/round_' + round_num + '/matches_' + service +\
			'_round_' + round_num + '_partial_with_genjacc_scores.csv'
		scores_df = pd.read_csv(scores_csv_path, dtype = str, index_col='index')

		df_for_saving_all_columns = copy.deepcopy(scores_df)
		df_for_saving = df_for_saving_all_columns[['title', 'artist']]

		for index,row in scores_df.iterrows():
			highest_genjacc_score = 0
			df_for_saving.loc[index, service] = np.nan
			for match_num in ['1','2','3','4','5']:
				target_title_col_name = 'match_title_' + service + '_' +\
										match_num
				target_artist_col_name = 'match_artist_' + service + '_' +\
										match_num
				try:
					target_title = row[target_title_col_name]
				except:
					break
				target_artist = row[target_artist_col_name]

				if ((isinstance(target_title, float) and math.isnan(target_title)) or\
					(isinstance(target_artist, float) and math.isnan(target_artist))):
					break
				genjacc_score_col_name = 'genjacc_score_' + service + '_match_' + match_num
				genjacc_score_raw = row[genjacc_score_col_name]
				genjacc_score = float(genjacc_score_raw)
				if genjacc_score > highest_genjacc_score:
					highest_genjacc_score = genjacc_score
					df_for_saving.loc[index, service] = match_num

		# saving it again incase we need to correct one manually, keep one intact
		filepath_orig = 'data/round_' + round_num + '/matches_' + service +\
			'_round_' + round_num + '_chosen_match.csv'
		filepath_dupli = 'data/round_' + round_num + '/matches_' + service +\
			'_round_' + round_num + '_chosen_match_corrected.csv'
		
		df_for_saving.to_csv(filepath_orig, encoding='utf-8')
		df_for_saving.to_csv(filepath_dupli, encoding='utf-8')

service_list = [
				# 'amazon',
				# 'apple',
				# 'gaana',
				# 'hungama',
				'jiosaavn',
				# 'spotify',
				# 'wynk',
				'ytmusic',
				]

round_num = '10'

choose_genjacc_match(service_list, round_num)
