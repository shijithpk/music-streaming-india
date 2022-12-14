import pandas as pd 
import numpy as np
import copy 

from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

service_list = ['amazon','apple','gaana',
				'hungama',
				'jiosaavn','spotify','wynk','ytmusic']

def guess_label_tieups(input_csv_path, output_csv_path):
	rights_holder_df = pd.read_csv(input_csv_path, dtype = str, index_col='index')

	# make sure we aren't counting duplicates 

	rights_holder_uniques = list(rights_holder_df['matched_group_final'].dropna().unique())

	new_df = pd.DataFrame({'label_group': rights_holder_uniques})

	for label_group in rights_holder_uniques:
		relevant_df =\
			rights_holder_df[rights_holder_df['matched_group_final']==label_group]
		relevant_df_deep = copy.deepcopy(relevant_df)
		relevant_df_deep.drop_duplicates(subset=['title','artist'], inplace=True)
		
		num_unique_albums = len(relevant_df_deep)

		for service in service_list:
			service_col_name = 'matched_url_' + service
			relevant_df_service =\
				relevant_df_deep[relevant_df_deep[service_col_name].notnull()]
			num_albums_service = len(relevant_df_service)
			percent_albums_service =\
				round((100*num_albums_service/num_unique_albums),1)
			new_df.loc[(new_df['label_group'] == label_group), service] =\
															percent_albums_service
			
	new_df.to_csv(output_csv_path, encoding='utf-8', index=False)


input_csv_path = 'data/match_grid_expanded_sep_27_after_jiosaavn_rights_holder_final.csv'
output_csv_path = 'data/analysis/label_coverage.csv'

guess_label_tieups(input_csv_path, output_csv_path)
