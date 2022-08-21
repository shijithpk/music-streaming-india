import pandas as pd
import numpy as np

def is_nan(valuex):
	if ((isinstance(valuex, float) and np.isnan(valuex))):
		return True
	else:
		return False

raw_csv_path = 'data/match_grid_expanded_aug_06_with_rights_holder_raw.csv'
raw_df = pd.read_csv(raw_csv_path, dtype = str, index_col='index')

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

columns_to_drop = ['matched_group_1st', 'matched_group_sp_ap', 'matched_group_all']
raw_df.drop(columns=columns_to_drop, axis=1, inplace = True)

new_csv_path = 'data/match_grid_expanded_aug_06_with_rights_holder_final.csv'
raw_df.to_csv(new_csv_path, encoding='utf-8')

print('done and done')