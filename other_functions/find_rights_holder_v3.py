import pandas as pd
import numpy as np
from data import label_groups
import re

label_dict = label_groups.label_dict

def get_most_associated_group(label_dictx, string):
	
	count_dict = {}
	for group in label_dictx:
		count_dict[group] = 0 #initialising count at 0 

	for group in label_dictx:
		for label in label_dictx[group]:
			if ((label in string) or (label.upper() in string)):
				label_occurrence_count_normal = string.count(label)
				if label.isupper():
					label_occurrence_count_upper = 0
				else:
					label_occurrence_count_upper = string.count(label.upper())
				label_occurrence_count = (label_occurrence_count_normal +\
											label_occurrence_count_upper)
				count_dict[group] += label_occurrence_count

	count_dict_sorted = dict(sorted(count_dict.items(), 
									key=lambda item: item[1],
									reverse=True))

	first_key = list(count_dict_sorted)[0]
	first_value = count_dict_sorted[first_key]
	if first_value == 0:
		return np.nan

	list_groups_tied_first =\
		[k for k,v in count_dict_sorted.items() if v == first_value]
	
	def get_biggest_group(sorted_dict, combined_label):
		label_name = re.search(r"(.*)_combined", combined_label).group(1)
		parent_count = sorted_dict[label_name + '_parent']
		main_count = sorted_dict[label_name + '_main']
		indie_count = sorted_dict[label_name + '_indie']
		total_count = parent_count + main_count + indie_count
		max_count = max(main_count,indie_count)

		if ((total_count == parent_count) or (max_count == 0)):
			return (label_name + '_parent')
		elif max_count == main_count:
			return (label_name + '_main')
		elif max_count == indie_count:
			return (label_name + '_indie')
	
	if len(list_groups_tied_first) == 1:
		if 'combined' not in first_key:
			return first_key
		else:
			biggest_constituent = get_biggest_group(count_dict_sorted, 
													first_key)
			return biggest_constituent
	
	list_groups_tied_first_not_combined =\
		[x for x in list_groups_tied_first if 'combined' not in x]

	if len(list_groups_tied_first_not_combined) > 0:
		return list_groups_tied_first_not_combined[0]
		# not caring if there's a tie, just returning first in list
	elif len(list_groups_tied_first_not_combined) == 0:
		# meaning there are multiple groups tied first with 'combined' in name
		first_combined_group = list_groups_tied_first[0]
		biggest_constituent = get_biggest_group(count_dict_sorted, 
												first_combined_group)
		return biggest_constituent


label_info_csv_path = 'data/match_grid_expanded_aug_06_apple_corrected.csv'
label_info_df = pd.read_csv(label_info_csv_path, dtype = str, index_col='index')

service_list = [
				'spotify',
				'apple',
				'amazon',
				'jiosaavn',
				'wynk',
				'gaana',
				]

url_column_name_list = []
for service in service_list:
	url_column_name = 'matched_url_' + service
	url_column_name_list.append(url_column_name)

# get all rows where any of the url columns are filled 
notnull_any_one_service_df = label_info_df[label_info_df[url_column_name_list].notnull().any(axis=1)]

def correct_label_dict_EMI(genre, label_dict):
	universal_main_list = label_dict['universal_main']
	warner_main_list = label_dict['warner_main']

	if genre == 'Western Classical':
		if 'EMI Records' not in warner_main_list:
			warner_main_list.append('EMI Records')

		if 'EMI Records' in universal_main_list:
			universal_main_list.remove('EMI Records')

	else:
		if 'EMI Records' not in universal_main_list:
			universal_main_list.append('EMI Records')

		if 'EMI Records' in warner_main_list:
			warner_main_list.remove('EMI Records')

	label_dict['universal_main'] = universal_main_list
	label_dict['warner_main'] = warner_main_list

	return label_dict


for index, row in notnull_any_one_service_df.iterrows():
	
	genre = row['genre']
	label_dict = correct_label_dict_EMI(genre, label_dict)

	# 1
	# this code finds first match against any group and assigns that group
	for service in service_list:

		copyright_column_name = 'matched_copyright_' + service
		service_copyright = notnull_any_one_service_df.at[index, copyright_column_name]
		if ((isinstance(service_copyright, float) and np.isnan(service_copyright))):
			service_copyright = ''

		label_column_name = 'matched_label_' + service
		service_label = notnull_any_one_service_df.at[index, label_column_name]
		if ((isinstance(service_label, float) and np.isnan(service_label))):
			service_label = ''

		# in combined string have copyright first, label name 2nd 
		service_combined_copyright_label = service_copyright + ' ' + service_label

		# if copyright and label are np.nan, move on to next service and get from there 
		if service_combined_copyright_label == ' ':
			continue
		else:
			break
	
	# matched_term = np.nan
	matched_group_1st = np.nan
	group_found = False #flag variable
	
	for group in label_dict:
		if group_found == True: break 
		term_list = label_dict[group]
		for term in term_list:
			if group_found == True: break
			if term in service_combined_copyright_label:
				# matched_term = term
				matched_group_1st = group
				group_found = True

	# label_info_df.at[index, 'matched_term'] = matched_term
	label_info_df.at[index, 'matched_group_1st'] = matched_group_1st


	# 2 
	#combine copyright info for spotify - apple into string 
	# find group that matches most against that string
	sp_ap_string = ''
	for fragment in ['label','copyright']:
		for service in ['apple','spotify']:
			relevant_column_name = 'matched_' + fragment + '_' + service
			relevant_value = notnull_any_one_service_df.at[index, 
														relevant_column_name]
			if ((isinstance(relevant_value, float) and np.isnan(relevant_value))):
				relevant_value = ''
			sp_ap_string = sp_ap_string + ' ' + relevant_value 

	matched_group_sp_ap = get_most_associated_group(label_dict, 
														sp_ap_string)
	label_info_df.at[index, 'matched_group_sp_ap'] = matched_group_sp_ap


	# 3 
	# combine copyright info for everything into a string 
	# find group that matches most against that string
	all_string = ''
	for fragment in ['label','copyright']:
		for service in service_list:
			relevant_column_name = 'matched_' + fragment + '_' + service
			relevant_value = notnull_any_one_service_df.at[index, 
														relevant_column_name]
			if ((isinstance(relevant_value, float) and np.isnan(relevant_value))):
				relevant_value = ''
			all_string = all_string + ' ' + relevant_value 


	matched_group_all = get_most_associated_group(label_dict, all_string)
	label_info_df.at[index, 'matched_group_all'] = matched_group_all


new_expanded_grid_csv_path =\
					'data/match_grid_expanded_aug_06_with_rights_holder_raw.csv'
label_info_df.to_csv(new_expanded_grid_csv_path, encoding='utf-8')

print('done and done')


# line for cron jobs
# cd /home/ubuntu/work/2022_03_17_music_app_remote && stdbuf -o0 -e0 /usr/bin/python3 ./find_rights_holder_v3.py >> /home/ubuntu/work/2022_03_17_music_app_remote/responses_logs/cron_logs/`date +\%Y-\%m-\%d-\%H:\%M`-rights_holder-cron.log 2>&1

