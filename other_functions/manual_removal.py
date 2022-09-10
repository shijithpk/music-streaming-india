import pandas as pd
import copy
import numpy as np
from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

from search_functions import *


# BELOW AM REMOVING MATCHES

# defining function
def remove_matches(	expanded_grid_csv_path,
					removal_csv_path,
					save_path
					):
	expanded_grid_df = pd.read_csv(expanded_grid_csv_path, dtype = str, 
															index_col='index')
	removal_df =  pd.read_csv(removal_csv_path, dtype = str, index_col='index')

	# columns in removal_df are [index, target_url]

	service_dict = {
	'apple': { 'domain': 'apple'},
	'jiosaavn': { 'domain': 'jiosaavn'},
	'spotify': { 'domain': 'spotify'},
	'ytmusic': { 'domain': 'youtube'},
	'amazon': { 'domain': 'amazon'},
	'gaana': { 'domain': 'gaana'},
	'hungama': { 'domain': 'hungama'},
	'wynk': { 'domain': 'wynk'},
	}

	all_cols = expanded_grid_df.columns.values.tolist()

	for index, row in removal_df.iterrows():
		target_url = row['target_url']
		for service in service_dict:
			if service_dict[service]['domain'] in target_url:
				cols_for_removal = [x for x in all_cols if service in x]
				for col in cols_for_removal:
					expanded_grid_df.at[index, col] = np.nan

	expanded_grid_df.to_csv(save_path, encoding='utf-8')

# setting paths
expanded_grid_csv_path = root/'data/match_grid_expanded_aug_06_with_rights_holder_final.csv'
removal_csv_path = root/'data/for_manual_removal_2022_09_01.csv'
save_path = root/'data/match_grid_expanded_sep_02_after_removal.csv'

# running function 
remove_matches(	expanded_grid_csv_path,
					removal_csv_path,
					save_path
					)


