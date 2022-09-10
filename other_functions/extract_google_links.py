import pandas as pd
import copy
import numpy as np

from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

from search_functions import *

input_csv_path = 'data/match_grid_expanded_sep_04_after_integration.csv'
round_num = '09'

output_csv_path = 'data/round_' + round_num + '/google_links_extracted.csv'


def extract_google_links(input_csv_path, round_num, output_csv_path):

	match_grid_expanded_df =\
		pd.read_csv(input_csv_path, dtype = str, index_col='index')

	service_list = ['amazon','apple','gaana',
					'hungama',
					'jiosaavn','spotify','wynk','ytmusic']

	holding_dict = {
					'amazon':{'domain': 'amazon.com',
								'link': np.nan,
					},
					'apple':{'domain': 'apple.com',
								'link': np.nan,
					},
					'gaana':{'domain': 'gaana.com',
								'link': np.nan,
					},
					'hungama':{'domain': 'hungama.com',
								'link': np.nan,
					},
					'jiosaavn':{'domain': 'jiosaavn.com',
								'link': np.nan,
					},
					'spotify':{'domain': 'spotify.com',
								'link': np.nan,
					},
					'wynk':{'domain': 'wynk.com',
								'link': np.nan,
					},
					'ytmusic':{'domain': 'youtube.com',
								'link': np.nan,
					},
					}

	match_grid_expanded_df_column_names =\
		match_grid_expanded_df.columns.values.tolist()
	basic_column_name_list = []
	for column_name in match_grid_expanded_df_column_names:
		if not any(substring in column_name for substring in service_list):
			basic_column_name_list.append(column_name)

	df_for_saving_raw = match_grid_expanded_df[basic_column_name_list]
	df_for_saving = copy.deepcopy(df_for_saving_raw)

	for service in service_list:
		column_name = service + '_link'
		df_for_saving[column_name] = np.nan

	for index, row in df_for_saving.iterrows():
		row_dict = copy.deepcopy(holding_dict)

		genre = row['genre']
		if genre == 'Western Classical':
			file_namex = str(index).zfill(4) + '_classical.html'
		else:
			file_namex = str(index).zfill(4) + '.html'
		file_path = 'data/round_' + round_num + '/google_pages/' + file_namex

		treex = lxml_html.parse(file_path)
		# if treex.xpath("//div[text()='Something went wrong.']"):
		# 	print('Download page again -- ' + str(index).zfill(4))
		# 	continue
		
		# now to get the listen box 
		listen_box_list = treex.xpath("//div[@data-attrid='action:listen_album']")
		if not listen_box_list: # if empty
			continue
		service_links = listen_box_list[0].xpath(".//a[@href]")
		for cell in service_links:
			link = cell.xpath("./@href")[0]
			for service in row_dict:
				if row_dict[service]['domain'] in link:
					row_dict[service]['link'] = link
		for service in service_list:
			column_name = service + '_link'
			df_for_saving.loc[index, column_name] = row_dict[service]['link']

	
	df_for_saving.to_csv(output_csv_path, encoding='utf-8')


input_csv_path = 'data/match_grid_expanded_sep_04_after_integration.csv'
round_num = '09'
output_csv_path = 'data/round_' + round_num + '/google_links_extracted.csv'

extract_google_links(input_csv_path, round_num, output_csv_path)
