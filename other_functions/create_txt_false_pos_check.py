import pandas as pd
import copy
import numpy as np
import os
from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

from search_functions import *

def create_txt_false_positive_check(service_list, round_num):
	for service in service_list:
		print_filepath='data/round_' + round_num +\
			'/for_manually_checking_false_positives_after_round_' + round_num +\
			'_' + service + '.txt'
		if os.path.exists(print_filepath):
			os.remove(print_filepath)
		f = open(print_filepath,'a')

		scores_csv_path = 'data/round_' + round_num + '/matches_' + service +\
			'_round_' + round_num + '_partial_with_genjacc_scores.csv'
		scores_df = pd.read_csv(scores_csv_path, dtype = str, index_col='index')

		for index,row in scores_df.iterrows():
			source_artist = row['artist']
			source_title = row['title']
			statement_A = '\n' +\
				'INDEX_NUMBER: ' + str(index) + '\n' +\
				'SOURCE_TITLE: ' + source_title + ' * SOURCE_ARTIST: ' + source_artist
			print(statement_A, file=f)
			for match_num in ['1','2','3','4','5']:
				target_title_col_name = 'match_title_' + service + '_' +\
										match_num
				target_artist_col_name = 'match_artist_' + service + '_' +\
										match_num
				target_url_col_name = 'match_url_' + service + '_' +\
										match_num

				try:
					target_title = row[target_title_col_name]
				except:
					break
				target_artist = row[target_artist_col_name]
				target_url = row[target_url_col_name]
				
				if ((isinstance(target_title, float) and  np.isnan(target_title)) or\
					(isinstance(target_artist, float) and  np.isnan(target_artist))):
					break
				genjacc_score_col_name = 'genjacc_score_' + service + '_match_' + match_num
				genjacc_score = row[genjacc_score_col_name]
				statement_B = '\n' +\
					'		MATCH_NUM: ' + match_num + '\n' +\
					'		TARGET_TITLE: ' + target_title + ' * TARGET_ARTIST: ' + target_artist + '\n' +\
					'		TARGET_URL: ' + target_url + '\n' +\
					'		GENJACC_SCORE: ' + str(genjacc_score)
				print(statement_B, file=f)

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
create_txt_false_positive_check(service_list, round_num)
