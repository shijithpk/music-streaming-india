#!/usr/bin/python3

from .helpers import *
import csv
import os
from creds_headers import headers_hungama_brute

headers_search = headers_hungama_brute.headers_search
params_search = headers_hungama_brute.params_search
headers_specific_album = headers_hungama_brute.headers_specific_album
params_specific_album = headers_hungama_brute.params_specific_album

def collect_album_results(albums_df, save_csv_name, albums_processed_csv_name, 
													min_checked, min_combos, 
													threshold, folder_path):

	if not os.path.exists(folder_path):
		os.makedirs(folder_path)

	session = create_session_hungama()
	
	for_hungama_files_list = os.listdir(folder_path)
	save_csv_path = folder_path + save_csv_name
	albums_processed_csv_path = folder_path + albums_processed_csv_name

	if ((save_csv_name not in for_hungama_files_list) and \
		(albums_processed_csv_name not in for_hungama_files_list)):
			
		headings = ['index','artist','title','genre','search_title',
					'search_title_url']
		with open(save_csv_path, "w") as filem:   
			wr = csv.writer(filem, delimiter = ',' , quotechar = '"' )
			wr.writerow(headings)

		headingsx = ['index_processed']
		with open(albums_processed_csv_path, "w") as filem:   
			wr = csv.writer(filem, delimiter = ',' , quotechar = '"' )
			wr.writerow(headingsx)

		albums_df_culled = albums_df.copy(deep=True)

	else:
		albums_processed_df = pd.read_csv(albums_processed_csv_path, dtype = int)
		albums_processed_list = albums_processed_df['index_processed'].tolist()

		albums_df_copy = albums_df.copy(deep=True)
		albums_df_culled = albums_df_copy[~albums_df_copy.index\
			.isin(albums_processed_list)]

		# 	wiping out rows for last index, in case it was interrupted 
		so_far_df = pd.read_csv(save_csv_path, dtype = str, index_col='index')
		so_far_df_culled = so_far_df[so_far_df.index.isin(albums_processed_list)]
		so_far_df_culled.to_csv(save_csv_path, encoding='utf-8')

	for index,row in albums_df_culled.iterrows():
		title = row['title']
		artist = row['artist']
		genre = row['genre']
		csv_index = str(index).zfill(4)
		keywords = artist + ' ' + title
		string_combos = create_list_queries(title, artist)
		albums_checked = set()
		for combo in string_combos[0:min_combos]:
			if (len(albums_checked) == min_checked):
				break
			query = ' '.join(combo)
			query_encoded = urllib.parse.quote(query)
			headers_search["cookie"] = headers_search["cookie"] +\
				'mysearchstring=' + query_encoded + "%7Cnull"
			for i in [1,2]:
				urlx = "https://www.hungama.com/search-albums/" +\
											query_encoded + '/' + str(i) + '/'
				time_sleep(25,35)
				time_now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
				print(time_now + '|' + 'hungama|' + csv_index + '|' + query, flush=True)
				response = session.get(url=urlx, headers=headers_search, 
									params = params_search, timeout=20)
				results_dict = response.json()
				number_results = results_dict['total']
				## use snippet below if you want code to run without erroring out 
				# try:
				# 	response = session.get(url=urlx, headers=headers_search, 
				# 						params = params_search, timeout=20)
				# 	results_dict = response.json()
				# 	number_results = results_dict['total']
				# except:
				# 	time_now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
				# 	print('problem|' + time_now + '|' + 'hungama|' + csv_index +\
				# 		 '|' + keywords, flush=True)
				# 	time.sleep(900) #sleep 15 minutes
				# 	return None
				if number_results == "": continue 
				albums_list = results_dict['album']
				for album in albums_list:
					if (len(albums_checked) >= min_checked):
						break
					search_title_url = album['url']
					if search_title_url in albums_checked: continue
					albums_checked.add(search_title_url)
					search_title = album['name']
					level_of_title_match = max(
						get_elkan_score_jarowink(title, search_title),
						get_elkan_score_jarowink(search_title, title))
					if level_of_title_match < threshold: continue
					row_list = [index, artist, title, genre, search_title, 
								search_title_url]
					with open(save_csv_path, "a") as filen:
						wrz = csv.writer(filen, delimiter = ',' , quotechar = '"' )
						wrz.writerow(row_list)
						filen.flush()
		with open(albums_processed_csv_path, "a") as filex:
			wrz = csv.writer(filex, delimiter = ',' , quotechar = '"' )
			wrz.writerow([index])
			filex.flush()

def collect_artist_names(load_csv_name, save_csv_name, folder_path):

	session = create_session_hungama()

	for_hungama_files_list = os.listdir(folder_path)

	load_csv_filepath = folder_path + load_csv_name
	save_csv_filepath = folder_path + save_csv_name

	collected_albums_df = pd.read_csv(load_csv_filepath, dtype = str, 
									index_col='index')
	# note there will be multiple rows with the same index in this dataframe

	if (save_csv_name not in for_hungama_files_list):

		headings = ['index','artist','title','genre','search_title',
					'search_title_url','number_tracks','search_artist']
		with open(save_csv_filepath, "w") as filem:   
			wr = csv.writer(filem, delimiter = ',' , quotechar = '"' )
			wr.writerow(headings)
			filem.flush()

		collected_albums_df_now = collected_albums_df.copy(deep=True)
	else:
		collected_artist_names_df = pd.read_csv(save_csv_filepath, dtype = str, 
															index_col='index')

		collected_albums_df_copy = collected_albums_df.copy(deep=True)

		collected_albums_df_copy['hash'] = collected_albums_df_copy.index\
			.astype(str) + '-' + collected_albums_df_copy['search_title_url']

		collected_artist_names_df['hash'] = collected_artist_names_df.index\
			.astype(str) + '-' + collected_artist_names_df['search_title_url']

		hash_done_list = collected_artist_names_df['hash'].to_list()
		collected_albums_df_now = collected_albums_df_copy\
						[~collected_albums_df_copy['hash'].isin(hash_done_list)]

		collected_albums_df_now.drop(['hash'], axis=1, inplace=True)

	for index, row in collected_albums_df_now.iterrows():
		artist = row['artist']
		title = row['title']
		genre = row['genre']
		search_title = row['search_title']
		search_title_url = row['search_title_url']
		csv_index = str(index).zfill(4)
		keywords = artist + ' ' + title
		combo = tokenize(keywords)
		query = ' '.join(combo)
		query_encoded = urllib.parse.quote(query)
		headers_specific_album["cookie"] = headers_specific_album["cookie"] +\
			'mysearchstring=' + query_encoded + "%7Cnull"
		time_sleep(15,20)
		time_now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
		print (time_now + '|' + 'hungama|' + csv_index + '|' + keywords +\
			 '|' + search_title + '|' + search_title_url, flush=True)
		album_page = session.get(search_title_url, headers=headers_specific_album, 
						params=params_specific_album, timeout=20)
		treex = lxml_html.fromstring(album_page.content)
		# # use try-except below if you want code to run without erroring out
		# try:
		# 	album_page = session.get(search_title_url, headers=headers_specific_album, 
		# 					params=params_specific_album, timeout=20)
		# 	treex = lxml_html.fromstring(album_page.content)
		# except:
		# 	time_now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
		# 	print('problem|' + time_now + '|' + 'hungama|' + csv_index + '|' +\
		# 	keywords +	'|' + search_title + '|' + search_title_url, flush=True)
		# 	time_sleep(61,90)
		# 	continue
		
		# playability condition, no block of songs on webpage 
		songs_blocks = treex.xpath("//div[contains(@class,'block-songs')]")
		if len(songs_blocks) == 0:
			continue

		# another playability condition, songs with play icons on them
		item_list = treex\
			.xpath(("//div[contains(@class,'block-songs')]//td[(@role='cell')" +\
				" and not(@colspan='2')]"))
		total_number_songs = len(item_list)
		playable_number_songs = 0
		for item in item_list:
			play_button_list = item.xpath(".//span[@class='icon-ic_play']")
			if len(play_button_list)==0: continue
			playable_number_songs += 1

		if playable_number_songs == 0: 
			continue

		track_list = treex.xpath("//div[@class='song']")
		number_tracks = len(track_list)
		search_artist_main_list =\
				treex.xpath("//span[@class='singn']//a/text()")
		if search_artist_main_list:
			search_artist_main = ', '.join(search_artist_main_list)
			# if you just want first artist listed, use line below
			# search_artist = search_artist_list[0]
		else:
			search_artist_main = ''
		
		search_artist_main_score = max(
					get_elkan_score_jarowink(artist, search_artist_main),
					get_elkan_score_jarowink(search_artist_main, artist))

		search_artist_first_track_list = track_list[0].xpath('.//h5//a/text()')
		if search_artist_first_track_list:
			search_artist_first_track = ', '.join(search_artist_first_track_list)
		else:
			search_artist_first_track = ''

		search_artist_first_track_score = max(
					get_elkan_score_jarowink(artist, search_artist_first_track),
					get_elkan_score_jarowink(search_artist_first_track, artist))

		if search_artist_main_score >= search_artist_first_track_score:
			search_artist = search_artist_main
		else:
			search_artist = search_artist_first_track
		
		row_list = [index, artist, title, genre, search_title, search_title_url,
					number_tracks,search_artist]
		with open(save_csv_filepath, "a") as filen:
			wrz = csv.writer(filen, delimiter = ',' , quotechar = '"' )
			wrz.writerow(row_list)
			filen.flush()


def collect_matches(albums_df, load_csv_name, save_csv_name, min_matched, threshold, folder_path):
	albums_df_copy = albums_df.copy(deep=True)
	load_csv_filepath = folder_path + load_csv_name
	collected_albums_artists_df = pd.read_csv(load_csv_filepath, dtype = str, 
									index_col='index')
	for index_main in collected_albums_artists_df.index.unique().tolist():
		#double square bracket around index_main below is intentional
			#sthing about getting back a dataframe instead of a series?
		index_df = collected_albums_artists_df.copy(deep=True).loc[[index_main]] 
		index_df.reset_index(inplace = True)
		artistx = index_df['artist'].iloc[0]
		for index, row in index_df.iterrows():

			artist = row['artist']
			title = row['title']
			genre = row['genre']
			search_title = row['search_title']
			search_title_url = row['search_title_url']
			number_tracks = int(row['number_tracks'])
			search_artist = row['search_artist']
			if ((genre not in ['Blues','Jazz','Western Classical','World Music']) 
				and (number_tracks <= 1)):
				level_of_title_match = 0
				level_of_artist_match = 0		
			else:
				level_of_title_match = max(
					get_elkan_score_jarowink(title, search_title),
					get_elkan_score_jarowink(search_title, title))
				level_of_artist_match = max(
					get_elkan_score_jarowink(artist, search_artist),
					get_elkan_score_jarowink(search_artist, artist))
			index_df.loc[index,'level_of_title_match'] = level_of_title_match
			index_df.loc[index,'level_of_artist_match'] = level_of_artist_match
		
		if ('various' in artistx.lower()) or ('artists' in artistx.lower()):
			#actually dont need line below, all title match scores are >threshold anyway
				#keeping it in so logic is clear, do need line about sorting though
			index_df_title_over_threshold =\
				index_df[(index_df['level_of_title_match'] >= threshold)]
			index_df_title_over_threshold.sort_values(by=['level_of_title_match'], 
				ascending=False, inplace=True)
			index_df_top = index_df_title_over_threshold[0:min_matched]
		else:
			index_df_over_threshold =\
				index_df[(index_df['level_of_title_match'] >= threshold) & 
						(index_df['level_of_artist_match'] >= threshold)]
			index_df_over_threshold.sort_values(by=['level_of_artist_match',
				 'level_of_title_match'], ascending=False, inplace=True)
			index_df_top = index_df_over_threshold[0:min_matched]
		for i in range(0,len(index_df_top)):
			suffix = '_' + str(i+1)
			search_artist = index_df_top.iloc[i]['search_artist']
			search_title = index_df_top.iloc[i]['search_title']
			search_title_url = index_df_top.iloc[i]['search_title_url']
			albums_df_copy.loc[index_main,'match_artist_hungama' + suffix] =\
																search_artist
			albums_df_copy.loc[index_main,'match_title_hungama' + suffix] =\
																search_title
			albums_df_copy.loc[index_main,'match_url_hungama' + suffix] =\
																search_title_url
	save_path = 'data/' + save_csv_name
	albums_df_copy.to_csv(save_path, encoding='utf-8')


def find_matches_hungama(albums_df, save_csv_name, albums_processed_csv_name, 
		min_matched, min_checked, min_combos, threshold, folder_path):

	# # UNCOMMENT AFTER ROUND 8 
	# for_hungama_files_list = os.listdir(folder_path)
	# if albums_processed_csv_name in for_hungama_files_list:
	# 	albums_processed_csv_path = folder_path + albums_processed_csv_name
	# 	albums_processed_df = pd.read_csv(albums_processed_csv_path, dtype = int)
	# 	last_index_processed_value = albums_processed_df.iloc[-1]['index_processed']
	# 	last_albumdf_index_value = albums_df.index[-1]
	# 	if last_index_processed_value != last_albumdf_index_value:
	# 		collect_album_results(albums_df, 'collected_albums.csv', 
	# 			albums_processed_csv_name, min_checked, min_combos, threshold, folder_path)
	# else:
	# 	collect_album_results(albums_df, 'collected_albums.csv', 
	# 				albums_processed_csv_name, min_checked, min_combos, threshold, folder_path)

	for_hungama_files_list = os.listdir(folder_path)
	collected_artist_names_csv_filename = 'collected_artist_names.csv'
	if collected_artist_names_csv_filename in for_hungama_files_list:
		collected_artist_names_csv_filepath = folder_path +\
									 collected_artist_names_csv_filename
		collected_artist_names_df = pd.read_csv(collected_artist_names_csv_filepath, 
																	dtype = str)
		collected_albums_csv_path = folder_path + 'collected_albums.csv'
		collected_albums_df = pd.read_csv(collected_albums_csv_path, 
										dtype = str, index_col='index')
		
		last_url_collected_albums_df = collected_albums_df['search_title_url'].iat[-1]
		last_url_collected_artist_names_df = collected_artist_names_df['search_title_url'].iat[-1]

		# to make this generalisable, use some hash to ensure uniqueness instead of using last url of column
			# this works here becaue I know the last url isnt present elsewhere in column. Wouldnt work otherwise.
		if last_url_collected_artist_names_df != last_url_collected_albums_df:
		# if len(collected_albums_df) != len(collected_artist_names_df):	
			collect_artist_names('collected_albums.csv', 'collected_artist_names.csv', folder_path)
	else:
		collect_artist_names('collected_albums.csv', 'collected_artist_names.csv', folder_path)

	collect_matches(albums_df, 'collected_artist_names.csv', 
					save_csv_name, min_matched, threshold, folder_path)


def playable_on_hungama(album_url):
	'''
	Not using duration here, but number of tracks on album
	'''
	session = create_session_hungama()

	album_page = session.get(url=album_url, headers=headers_specific_album, 
												params=params_specific_album)
	treex = lxml_html.fromstring(album_page.content)
	songs_block_list = treex.xpath("//div[contains(@class,'block-songs')]")
	if len(songs_block_list) == 0:
		return False

	item_list = treex\
		.xpath(("//div[contains(@class,'block-songs')]//td[(@role='cell')" +\
			" and not(@colspan='2')]"))
	total_number_songs = len(item_list)
	# print(total_number_songs)
	playable_number_songs = 0
	for item in item_list:
		play_button_list = item.xpath(".//span[@class='icon-ic_play']")
		if len(play_button_list)==0: continue
		playable_number_songs += 1
	# print(playable_number_songs)

	if playable_number_songs/total_number_songs >= 0.95:
		return True
	else:
		return False


def get_activity_tracks_hungama(album_url):

	session = create_session_hungama()

	album_page = session.get(url=album_url, headers=headers_specific_album, 
												params=params_specific_album)
	treex = soup_fromstring(album_page.content)

	songs_block_list = treex.xpath("//div[contains(@class,'block-songs')]")
	if len(songs_block_list) == 0:
		inactive_dict = {
						'activity_status': 'inactive without a doubt', 
						'tracks_count': 0,
						'tracks_count_playable': 0,
						}
		return inactive_dict

	tracks_count_string = treex.xpath("//a[@class='songcount']/text()")[0]
	tracks_count_raw =  re.search(r"(\d+)\sSong", 
									tracks_count_string).group(1) 
	tracks_count = int(tracks_count_raw)

	item_list = treex\
		.xpath(("//div[contains(@class,'block-songs')]//td[(@role='cell')" +\
			" and not(@colspan='2')]"))
	tracks_count_playable = 0
	for item in item_list:
		play_button_list = item.xpath(".//span[@class='icon-ic_play']")
		if len(play_button_list)==0: continue
		tracks_count_playable += 1

	threshold = 0.8*tracks_count

	if tracks_count_playable >= tracks_count:
		activity_status = 'possibly active'
	elif tracks_count_playable >= threshold:
		activity_status = 'possibly inactive: but over internal threshold'
	elif tracks_count_playable < threshold:
		activity_status = 'possibly inactive: below internal threshold'

	activity_tracks_dict = {
							'activity_status': activity_status, 
							'tracks_count': tracks_count,
							'tracks_count_playable': tracks_count_playable,
							}

	return activity_tracks_dict



def get_artist_title_hungama(album_url, genre):
	session = create_session_hungama()
	album_page = session.get(album_url, headers=headers_specific_album, 
				params=params_specific_album, timeout=20)
	treex = lxml_html.fromstring(album_page.content)
	artist_list = treex.xpath("//span[@class='singn']//a/text()")
	if genre == 'Western Classical':
		artist = ', '.join(artist_list)
	else:
		artist = artist_list[0]
	title = treex.xpath("//h1[@class='artist-name']/text()")[0] #oh hungama, a class named 'artist-name' for album title?
	return [artist, title]


def get_label_copyright_hungama(album_url):
	session = create_session_hungama()
	album_page = session.get(album_url, headers=headers_specific_album, 
				params=params_specific_album, timeout=20)
	treex = lxml_html.fromstring(album_page.content)

	label_raw = treex.xpath("//div[@class='artist-details1']/text()")[0]
	label = label_raw.strip()

	phono_copyright = ''

	listx = [label, phono_copyright]
	return listx
