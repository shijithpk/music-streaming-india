import numpy as np 
import pandas as pd 
import copy
from pathlib import Path

root = Path(__file__).parent.parent

def calculate_scores(input_csv_path):

	expanded_grid_df = pd.read_csv(input_csv_path,  dtype = str, index_col='index')

	service_list = ['amazon','apple','gaana','hungama',
					'jiosaavn','spotify','wynk','ytmusic']

	column_name_list = ['genre','category','total',] + service_list
	new_df = pd.DataFrame(columns = column_name_list)

	np_nan_dict = {}
	for service in service_list:
		np_nan_dict[service] = np.nan

	for genre in expanded_grid_df['genre'].unique():
		if genre != 'All':
			for category in expanded_grid_df['canon_contemp'].unique():
				genre_category_total = expanded_grid_df[(expanded_grid_df['genre']== genre) &\
					(expanded_grid_df['canon_contemp']== category)].shape[0]
				new_row = {'genre': genre, 'category': category, 'total': genre_category_total}
				new_row.update(np_nan_dict)
				new_df = new_df.append(new_row, ignore_index=True)
		else:
			for list_name in ['Rolling_Stone_500','NME_500']:
				new_row = {'genre': list_name, 'category': 'canon', 'total': 500}
				new_row.update(np_nan_dict)
				new_df = new_df.append(new_row, ignore_index=True)


	for genre in expanded_grid_df['genre'].unique():
		for category in expanded_grid_df['canon_contemp'].unique():
			for service in service_list:
				relevant_column_name = 'matched_url_' + service
				if genre != 'All':
					service_genre_category_count = expanded_grid_df[(expanded_grid_df['genre']== genre) &\
					(expanded_grid_df['canon_contemp']== category) & (expanded_grid_df[relevant_column_name].notnull())].shape[0]
					new_df.loc[((new_df['genre'] == genre) & (new_df['category'] == category)), service] = service_genre_category_count
				else:
					for list_name in ['Rolling_Stone_500','NME_500']:
						if category == 'contemporary': continue
						service_genre_category_count = expanded_grid_df[(expanded_grid_df['genre']== 'All') &\
						(expanded_grid_df['canon_contemp']== 'canon') & (expanded_grid_df['list_name'].str.contains(list_name)) &\
						(expanded_grid_df[relevant_column_name].notnull())].shape[0]
						new_df.loc[((new_df['genre'] == list_name) & (new_df['category'] == category)), service] = service_genre_category_count

	new_df.to_csv(root / 'data/analysis/intermediate_file_01.csv', encoding='utf-8', index=False)

	########################################################################

	new_df = pd.read_csv(root / 'data/analysis/intermediate_file_01.csv')

	service_list = ['amazon','apple','gaana','hungama',
					'jiosaavn','spotify','wynk','ytmusic']

	for service in service_list:
		new_column_name = service + '_percent'
		new_df[new_column_name] = round(100 * (new_df[service]/new_df['total']), 3)

	columns_to_drop = service_list + ['total']
	new_df.drop(columns=columns_to_drop, axis=1, inplace=True)

	new_df.to_csv(root / 'data/analysis/intermediate_file_02.csv', encoding='utf-8', index=False)

	#######################################################################

	old_df = pd.read_csv(root / 'data/analysis/intermediate_file_02.csv')

	service_list = ['amazon','apple','gaana','hungama',
					'jiosaavn','spotify','wynk','ytmusic']

	new_df_raw = old_df[['genre']]
	new_df = copy.deepcopy(new_df_raw)
	new_df.drop_duplicates(keep = 'first', inplace = True)

	for index, row in new_df.iterrows():
		genre = row['genre']
		for service in service_list:
			old_column_name = service + '_percent'
			new_column_name = service + '_combined_percent'
			if genre in ['Rolling_Stone_500','NME_500']:
				canon_percent = 2* old_df.loc[((old_df['genre'] == genre) & (old_df['category'] == 'canon')), old_column_name].values[0]
				contemp_percent = 0
			else:
				canon_percent = old_df.loc[((old_df['genre'] == genre) & (old_df['category'] == 'canon')), old_column_name].values[0]
				contemp_percent = old_df.loc[((old_df['genre'] == genre) & (old_df['category'] == 'contemporary')), old_column_name].values[0]

			combined_percent = canon_percent + contemp_percent
			new_df.loc[index, new_column_name] = combined_percent

	new_df.to_csv(root / 'data/analysis/intermediate_file_03.csv', encoding='utf-8', index=False)

	########################################################################


	old_df = pd.read_csv(root / 'data/analysis/intermediate_file_03.csv')

	service_list = ['amazon','apple','gaana','hungama',
					'jiosaavn','spotify','wynk','ytmusic']

	columns_to_drop = []
	for service in service_list:
		old_column_name = service + '_combined_percent'
		columns_to_drop.append(old_column_name)

		new_column_name = service
		old_df[new_column_name] = round(old_df[old_column_name]/20,1)

	old_df.drop(columns=columns_to_drop, axis=1, inplace=True)

	# old_df.set_index('genre', inplace=True)

	# new_df = old_df.transpose().rename_axis('service')

	new_df = old_df.set_index('genre').T.rename_axis('service').rename_axis(None, axis=1).reset_index()

	new_df.to_csv(root / 'data/analysis/genre_wise_out_of_10.csv', encoding='utf-8', index=False)

	#######################################################################

	old_df = pd.read_csv(root / 'data/analysis/intermediate_file_03.csv')

	index_list = old_df[(old_df['genre'] == 'Rolling_Stone_500') |\
						(old_df['genre'] == 'NME_500')].index
	old_df.drop(index_list, inplace = True)
	old_df.reset_index(inplace = True)

	service_list = ['amazon','apple','gaana','hungama',
					'jiosaavn','spotify','wynk','ytmusic']
	new_df = pd.DataFrame({'service': service_list})

	for index, row in new_df.iterrows():
		service = row['service']
		old_column_name = service + '_combined_percent'
		service_sum = old_df[old_column_name].sum()
		value_for_insertion = round(10*(service_sum/2000), 1)
		new_df.loc[index, 'overall_out_of_10'] = value_for_insertion

	new_df.to_csv('data/analysis/overall_out_of_10.csv', encoding='utf-8', index=False)

	############################################################


	old_df = pd.read_csv(root / 'data/analysis/intermediate_file_03.csv')

	old_df.set_index('genre')

	old_df['average'] = round(10*(old_df.mean(axis=1)/200),1)

	service_list = ['amazon','apple','gaana','hungama',
					'jiosaavn','spotify','wynk','ytmusic']

	columns_to_drop = []
	for service in service_list:
		old_column_name = service + '_combined_percent'
		columns_to_drop.append(old_column_name)

	old_df.drop(columns=columns_to_drop, axis=1, inplace=True)

	old_df.to_csv(root / 'data/analysis/genre_wise_average.csv', encoding='utf-8', index=False)

	############################################################

	service_list = ['amazon','apple','gaana','hungama',
					'jiosaavn','spotify','wynk','ytmusic']

	expanded_grid_df = pd.read_csv(input_csv_path, dtype = str, 
															index_col='index')

	for listx in ['Rolling_Stone_500','NME_500']:
		expanded_grid_df_culled =\
			expanded_grid_df[expanded_grid_df['list_name'].str.contains(listx)]
		
		new_df = pd.DataFrame({'service': service_list})

		for index, row in new_df.iterrows():
			service = row['service']
			service_col_name = 'matched_url_' + service 
			expanded_grid_df_service =\
				expanded_grid_df_culled[expanded_grid_df_culled[service_col_name].notnull()]
			insertion_value = len(expanded_grid_df_service)
			new_df.loc[index, 'out_of_500'] = insertion_value

		new_df_sorted = new_df.sort_values(by=['out_of_500'], ascending=False)
		save_path = root / ('data/analysis/' + listx + '_available.csv')
		new_df_sorted.to_csv(save_path, encoding='utf-8', index=False)


	############################################################

	genre_ratings_csv_path = root / 'data/analysis/genre_wise_out_of_10.csv'
	genre_ratings_df = pd.read_csv(genre_ratings_csv_path)

	proper_name_dict = {
						'spotify': 'Spotify',
						'apple': 'Apple',
						'ytmusic': 'YouTube Music',
						'amazon': 'Amazon',
						'jiosaavn': 'JioSaavn',
						'wynk': 'Wynk',
						'hungama': 'Hungama',
						'gaana': 'Gaana',
						}

	genre_ratings_df['service'] =\
		genre_ratings_df['service'].map(proper_name_dict)

	global_list= ['Amazon','Apple','Spotify','YouTube Music']
	homegrown_list = ['Gaana','Hungama','JioSaavn','Wynk']
						

	genre_ratings_df.rename(columns =\
			 {'Western Classical':"West'n Class'l"}, inplace = True)

	genre_list = ['Pop', 'EDM', 'Rock', 'Metal', 'Hip-Hop', 'R&B', 
					'Jazz', 'Blues', "West'n Class'l",'World Music']

	new_df = pd.DataFrame(genre_list, columns =['genre'])

	new_cols = ['Best global service',
				'Best global service rating',
				'Best homegrown service',
				'Best homegrown service rating'
				]

	for col in new_cols:
		new_df[col] = np.nan

	for genre in genre_list:
		culled_df_raw = genre_ratings_df[['service', genre]]
		culled_df = copy.deepcopy(culled_df_raw)

		culled_df_global = culled_df[culled_df['service'].isin(global_list)]
		sorted_df_global =\
			culled_df_global.sort_values(by=[genre], ascending=False)
		# print(sorted_df_global)
		top_global_service = sorted_df_global['service'].iloc[0]
		top_global_service_rating = sorted_df_global[genre].iloc[0]
		new_df.loc[new_df['genre'] == genre, 'Best global service'] =\
															 top_global_service
		new_df.loc[new_df['genre'] == genre, 'Best global service rating'] =\
													top_global_service_rating

		culled_df_homegrown = culled_df[culled_df['service'].isin(homegrown_list)]
		sorted_df_homegrown =\
			culled_df_homegrown.sort_values(by=[genre], ascending=False)
		# print(sorted_df_homegrown)
		top_homegrown_service = sorted_df_homegrown['service'].iloc[0]
		top_homegrown_service_rating = sorted_df_homegrown[genre].iloc[0]
		new_df.loc[new_df['genre'] == genre, 'Best homegrown service'] =\
															 top_homegrown_service
		new_df.loc[new_df['genre'] == genre, 'Best homegrown service rating'] =\
													top_homegrown_service_rating

	new_df.to_csv(root / 'data/analysis/top_homegrown_global.csv', 
						encoding='utf-8', index=False)

	

########## RUN THE FUNCTION #######################

input_csv_path =\
	root/'data/match_grid_expanded_sep_27_after_jiosaavn_rights_holder_final.csv'
calculate_scores(input_csv_path)

