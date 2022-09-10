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


logger = create_logger()


input_csv_path = 'data/match_grid_expanded_sep_04_after_integration.csv'
round_num = '09'


def download_google_results(input_csv_path, round_num):

	match_grid_expanded_df = pd.read_csv(input_csv_path, 
										dtype = str, index_col='index')

	google_files_path = 'data/round_' + round_num + '/google_pages/'
	path = Path(google_files_path)
	path.mkdir(parents=True, exist_ok=True)

	google_files_list = os.listdir(google_files_path)
	index_number_done_list = []
	for filename in google_files_list:
		index_filename_raw = filename.split('.')[0]
		index_filename = int(index_filename_raw)
		index_number_done_list.append(index_filename)

	match_grid_expanded_df_remaining =\
		match_grid_expanded_df[~match_grid_expanded_df.index.isin(index_number_done_list)]
	print('albums remaining: ' + str(len(match_grid_expanded_df_remaining)))

	def create_url(artist,title):
		artist_title = artist + ' ' + title
		query_fragment = 'listen to the album '
		query = query_fragment + artist_title
		query_encoded = urllib.parse.quote_plus(query)
		urlx = 'https://www.google.com/search?q=' + query_encoded
		return urlx

	initial_artist = 'the buggles'
	initial_title = 'the age of plastic'
	initial_url = create_url(initial_artist, initial_title)

	preference_order = ['spotify','apple','ytmusic','amazon','jiosaavn','gaana',
						'wynk','hungama']

	with sync_playwright() as p:
		browser = p.chromium.launch()
		page = browser.new_page()
		page.goto(initial_url)
		timeout = random.choice(range(25000,36000,1000)) #milliseconds
		page.wait_for_timeout(timeout)
		# for index, row in match_grid_expanded_df.loc[16:18].iterrows(): #for testing
		for index, row in match_grid_expanded_df_remaining.iterrows():
			genre = row['genre']

			csv_index = str(index).zfill(4)
			time_now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
			source_artist = row['artist']
			source_title = row['title']
			source_artist_title = source_artist + ' ' + source_title
			print(time_now + '|' + csv_index + '|' + source_artist_title)
			artist_title_combos = []
			for service in preference_order:
				service_artist_column = 'matched_artist_' + service
				service_artist = row[service_artist_column]
				service_title_column = 'matched_title_' + service
				service_title  = row[service_title_column]
				try:
					service_artist_title = service_artist + ' ' + service_title
					artist_title_combos.append(service_artist_title)
				except:
					# either title or artist here is np.nan
					continue
			artist_title_combos.append(source_artist_title)
			combo_for_search_field = 'listen to the album ' + artist_title_combos[0]
			search_field_selector = "//input[@aria-label='Search']"
			# if not page.locator(search_field_selector).is_visible():
			# 	print('redo download for index number ' + str(index))
			# 	time_sleep(600,900) #10-15 minutes
			# 	page.goto(initial_url)
			# 	timeout = random.choice(range(25000,36000,1000))
			# 	page.wait_for_timeout(timeout)
			# 	continue
			page.fill(selector=search_field_selector, value='')
			# page.type(selector=search_field_selector, text=combo_for_search_field, delay=250)
			page.fill(selector=search_field_selector, value=combo_for_search_field)
			page.press(selector=search_field_selector, key='Enter', delay=100)
			timeout = random.choice(range(25000,36000,1000))
			page.wait_for_timeout(timeout)

			pageload_selector = "//span[text()='Next']"
			if not page.locator(pageload_selector).is_visible():
				# next arrow link not in page, encountered a google captcha page
				print('redo download for index number ' + str(index))
				time_sleep(600,900) #10-15 minutes
				page.goto(initial_url)
				timeout = random.choice(range(25000,36000,1000))
				page.wait_for_timeout(timeout)
				continue

			listen_selector = "//a[@data-ti='default_tab:action:listen_album']"
			if page.locator(listen_selector).is_visible():
				page.locator(listen_selector).click(delay=100)
				timeout = 3000 #this is pretty much instantaneous, so only 3 seconds 
				page.wait_for_timeout(timeout)

			if genre == 'Western Classical':
				file_namex = str(index).zfill(4) + '_classical.html'
			else:
				file_namex = str(index).zfill(4) + '.html'
			page_save_path = 'data/round_' + round_num + '/google_pages/' + file_namex
			with open(page_save_path, 'w') as f:
				f.write(page.content())

		browser.close()

try:
	download_google_results()
except Exception as e:
  logger.exception(e, stack_info=True)



