#!/usr/bin/python3

from pathlib import Path
import sys

root = Path(__file__).parent.parent
sys.path.append(str(root))

from search_functions import *
from playwright.sync_api import sync_playwright
import random
import pandas as pd
import copy
import numpy as np

def create_txt_false_positive_check_google(round_num, service_list):
	for service in service_list:
		service_csv_path = 'data/round_' + round_num + '/artists_titles_for_' +\
													service + '_playable.csv'
		service_df = pd.read_csv(service_csv_path, dtype = str, index_col='index')

		print_filepath='data/round_' + round_num +\
			'/for_manually_checking_false_positives_after_round_' + round_num +\
				'_' + service + '.txt'
		if os.path.exists(print_filepath):
			os.remove(print_filepath)
		f = open(print_filepath,'a')

		for index,row in service_df.iterrows():
			source_artist = row['artist']
			source_title = row['title']
			statement_A = '\n' +\
				'INDEX_NUMBER: ' + str(index) + '\n' +\
				'SOURCE_TITLE: ' + source_title + ' * SOURCE_ARTIST: ' + source_artist
			print(statement_A, file=f)

			artist_column_name = service + '_artist'
			target_artist_raw = row[artist_column_name]
			if (isinstance(target_artist_raw, float) and np.isnan(target_artist_raw)):
				target_artist = 'EMPTY CELL'
			else:
				target_artist = target_artist_raw.strip()

			title_column_name = service + '_title'
			target_title_raw = row[title_column_name]
			if (isinstance(target_title_raw, float) and np.isnan(target_title_raw)):
				target_title = 'EMPTY CELL'
			else:
				target_title = target_title_raw.strip()
				
			statement_B = '\n' +\
				'TARGET_TITLE: ' + target_title + ' * TARGET_ARTIST: ' + target_artist + '\n'
			print(statement_B, file=f)

			playable = row['playable']
			if (type(playable) == float) and (np.isnan(playable)):
				playable = 'no'
			statement_C = '\n' +\
				'PLAYABLE: ' + playable
			print(statement_C, file=f)


round_num = '09'
service_list = ['apple','gaana','jiosaavn','spotify','ytmusic','hungama']
create_txt_false_positive_check_google(round_num, service_list)
