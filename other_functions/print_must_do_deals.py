import pandas as pd
import numpy as np
import copy
import re

from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

def is_nan(valuex):
	if ((isinstance(valuex, float) and np.isnan(valuex))):
		return True
	else:
		return False

def print_must_do_deals(input_csv_path):
	expanded_grid_df = pd.read_csv(input_csv_path, dtype = str, 
						index_col='index')

	genre_list = list(expanded_grid_df['genre'].unique())
	genre_list.remove('All')

	canon_contemp_dict = {	
						'canon':0,
						'contemporary':0,
							}

	genre_count_dict = {}
	for genre in genre_list:
		genre_count_dict[genre] = copy.deepcopy(canon_contemp_dict)

	for index, row in expanded_grid_df.iterrows():
		genre = row['genre']
		if (genre == 'All'): continue
		period = row['canon_contemp']
		genre_count_dict[genre][period] += 1


	percent_conversion_dict = copy.deepcopy(genre_count_dict)

	for genre in percent_conversion_dict:
		for period in percent_conversion_dict[genre]:
			percent_conversion_dict[genre][period] =\
									0.5/(percent_conversion_dict[genre][period])

	label_group_list =\
				list(expanded_grid_df['matched_group_final'].dropna().unique())

	for major in ['universal','sony','warner']:
		for category in ['main','parent']:
			combined = major + '_' + category
			label_group_list.remove(combined)
		label_group_list.append(major)

	label_group_list.append('unclassified')

	label_group_count_dict = {}
	for label_group in label_group_list:
		label_group_count_dict[label_group] = 0

	service_list = ['amazon','apple','gaana',
					'hungama',
					'jiosaavn','spotify','wynk','ytmusic']

	service_dict = {}
	service_dict['overall'] = copy.deepcopy(label_group_count_dict)
	for service in service_list:
		service_dict[service] = copy.deepcopy(label_group_count_dict)


	for index, row in expanded_grid_df.iterrows():
		genre = row['genre']
		if (genre == 'All'): continue
		period = row['canon_contemp']
		percent_value = percent_conversion_dict[genre][period]

		label_group = row['matched_group_final']
		if is_nan(label_group): #unclassified
			service_dict['overall']['unclassified'] += percent_value
			for service in service_list:
				service_url_col_name = 'matched_url_' + service
				service_url = row[service_url_col_name]
				if not is_nan(service_url):
					service_dict[service]['unclassified'] += percent_value
		else:
			if (('_parent' in label_group) or ('_main' in label_group)):
				major = re.search(r"(.*)_.*", label_group).group(1)
				service_dict['overall'][major] += percent_value
				for service in service_list:
					service_url_col_name = 'matched_url_' + service
					service_url = row[service_url_col_name]
					if not is_nan(service_url):
						service_dict[service][major] += percent_value
			else:
				service_dict['overall'][label_group] += percent_value
				for service in service_list:
					service_url_col_name = 'matched_url_' + service
					service_url = row[service_url_col_name]
					if not is_nan(service_url):
						service_dict[service][label_group] += percent_value


	new_df = pd.DataFrame(service_dict)
	new_df.index.name = 'label_group'

	new_df = new_df.round(2)

	for service in service_list:
		new_col_name = service + '_diff'
		new_df[new_col_name] = new_df['overall'] - new_df[service]
		new_df.drop([service], axis=1, inplace=True)

	new_df.drop(['overall'], axis=1, inplace=True)
	new_df.drop('unclassified', inplace=True)

	for service in service_list:
		new_col_name = service + '_diff'
		col_max_value = round(new_df[new_col_name].max(),1)
		col_max_label = new_df[new_col_name].idxmax()
		print('for ' + service + ', single biggest improvement (' +\
			str(col_max_value) + ') to overall rating ' +\
			'will come from doing a deal for ' + col_max_label)

input_csv_path ='data/match_grid_expanded_sep_04_with_rights_holder_final.csv'

print_must_do_deals(input_csv_path)