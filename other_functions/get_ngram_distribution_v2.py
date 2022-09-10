import pandas as pd
import nltk
import os
import numpy as np
from collections import Counter
from thefuzz import fuzz

expanded_grid_csv_path =\
					'data/match_grid_expanded_aug_06_with_rights_holder_raw.csv'
expanded_grid_df = pd.read_csv(expanded_grid_csv_path, dtype = str, 
					index_col='index')

service_list = [
				'spotify',
				'apple',
				'amazon',
				'jiosaavn',
				'wynk',
				'gaana',
				]

relevant_column_name_list = []
for service in service_list:
	for fragment in ['label','copyright']:
		relevant_column_name = 'matched_' + fragment + '_' + service
		relevant_column_name_list.append(relevant_column_name)

notnull_any_label_copyright_df = expanded_grid_df[expanded_grid_df[relevant_column_name_list].notnull().any(axis=1)]

major_assigned_cols = ['matched_group_1st', 'matched_group_sp_ap', 'matched_group_all']

notnull_any_label_copyright_df_null_major_assigned_all =\
	notnull_any_label_copyright_df[notnull_any_label_copyright_df[major_assigned_cols].isnull().all(axis=1)]

print_filepath='data/for_manually_checking_ngram_distribution.txt'
if os.path.exists(print_filepath):
	os.remove(print_filepath)
f = open(print_filepath,'a')

all_string_list = []

for index, row in notnull_any_label_copyright_df_null_major_assigned_all.iterrows():
	sentence = ''
	for col in relevant_column_name_list:
		relevant_string = row[col]
		if ((isinstance(relevant_string, float) and np.isnan(relevant_string))):
			relevant_string = ''
		sentence = sentence + ' ' + relevant_string

	tokenizer = nltk.RegexpTokenizer("[\w\'’‘]+")
	tokens = tokenizer.tokenize(sentence)

	str_list = []
	for n_value in range(5,0,-1):
		ngrams = nltk.ngrams(tokens, n_value)
		for element in ngrams:
			ngram_string = " ".join(element)
			if ngram_string not in str_list:
				str_list.append(ngram_string)
	all_string_list.extend(str_list) #extend not append

counter = Counter(all_string_list)
ngram_sorted = counter.most_common()



def fuzz_score(string1, string2):
	fuzz_score = fuzz.token_set_ratio(string1, string2)
	return fuzz_score

unique_str_list = []
for item in ngram_sorted:
	ngram_str = item[0]
	value = item[1]
	if value == 1: continue
	# if (any(ngram_str in unique_str for unique_str in unique_str_list)\
	# 	# or any(unique_str in ngram_str for unique_str in unique_str_list)
	# 	):
	# 	continue
	if (any((fuzz_score(ngram_str,unique_str) >= 85) for unique_str in unique_str_list)\
		):
		continue
	unique_str_list.append(ngram_str)
	statement = "'" + ngram_str + "'. Freq: " + str(value)
	print(statement, file=f)

print('done and done')

