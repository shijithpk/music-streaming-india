import pandas as pd
import numpy as np
from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

def is_nan(valuex):
	if ((isinstance(valuex, float) and np.isnan(valuex))):
		return True
	else:
		return False


def choose_rights_holder(input_csv_path, output_csv_path):

	raw_df = pd.read_csv(input_csv_path, dtype = str, index_col='index')

	for index, row in raw_df.iterrows():
		sp_ap_string_value = row['matched_group_sp_ap']
		all_string_value = row['matched_group_all']

		if (is_nan(sp_ap_string_value) and (is_nan(all_string_value))):
			final_value = np.nan
		elif (is_nan(sp_ap_string_value) and (not is_nan(all_string_value))):
			final_value = all_string_value
		else:
			final_value = sp_ap_string_value
		
		raw_df.loc[index, 'matched_group_final'] = final_value

	columns_to_drop = ['matched_group_sp_ap', 'matched_group_all']
	raw_df.drop(columns=columns_to_drop, axis=1, inplace = True)

	raw_df.to_csv(output_csv_path, encoding='utf-8')


input_csv_path = 'data/match_grid_expanded_sep_04_with_rights_holder_raw.csv'
output_csv_path = 'data/match_grid_expanded_sep_04_with_rights_holder_final.csv'

choose_rights_holder(input_csv_path, output_csv_path)