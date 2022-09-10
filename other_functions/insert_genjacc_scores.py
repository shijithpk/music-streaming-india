import pandas as pd
import copy
import numpy as np

from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

from search_functions import *

def insert_genjacc_score_columns(service_list, round_num):
	for service in service_list:
		partial_csv_path = 'data/round_' + round_num + '/matches_' + service +\
									 '_round_' + round_num + '_partial.csv'
		partial_df = pd.read_csv(partial_csv_path, dtype = str, index_col='index')
		for index,row in partial_df.iterrows():
			source_title = row['title']
			source_artist = row['artist']
			source_artist_title_combined = source_artist + source_title
			for match_num in ['1','2','3','4','5']:
				target_artist_col_name = 'match_artist_' + service + '_' +\
										match_num
				target_title_col_name = 'match_title_' + service + '_' +\
										match_num
				try:
					target_artist = row[target_artist_col_name]
				except:
					break
				target_title = row[target_title_col_name]
				#if a NaN value, break loop
				if ((isinstance(target_title, float) and  np.isnan(target_title)) or\
				(isinstance(target_artist, float) and  np.isnan(target_artist))):
					break
				target_artist_title_combined = target_artist + target_title
				#below we get the similiarity score acc to an algo called 
					# generalized jaccard
				score_raw = get_genjacc_score_jarowink(source_artist_title_combined,
										target_artist_title_combined)
				score = round(score_raw,1)
				score_col_name = 'genjacc_score_' + service + '_match_' + str(match_num)
				partial_df.loc[index, score_col_name] = score

		partial_df_with_scores_path = 'data/round_' + round_num + '/matches_' +\
				service + '_round_' + round_num + '_partial_with_genjacc_scores.csv'
		partial_df.to_csv(partial_df_with_scores_path, encoding='utf-8')

service_list = [
				'amazon',
				# 'apple',
				# 'gaana',
				# 'hungama',
				# 'jiosaavn',
				# 'spotify',
				# 'wynk',
				# 'ytmusic',
				]

round_num = '09'
insert_genjacc_score_columns(service_list, round_num)
