from .helpers import *
from creds_headers import headers_amazon

session = create_session()

headers_amazonx = headers_amazon.headers_amazon

def find_matches_amazon(albums_df, csv_name, min_matched, min_checked, min_combos, threshold):
	'''
	Takes in the dataframe of album titles & artists.
	Finds matches for them if any on spotify.
	Creates new columns in the dataframe with details, url, name of the matches
	Saves the modified dataframe as 'csv_name'
	min_matched is the min no. of albums that should be a match to your search
	min_checked is the min no. of albums your code should go through
	min_combos is the min no. of keyword combos your code should query for
	'''
	set_results = headers_amazon.set_results

	albums_df_copy = albums_df.copy(deep=True)
	for index,row in albums_df_copy.iterrows():
		title = row['title']
		artist = row['artist']
		genre = row['genre']
		csv_index = str(index).zfill(4)
		keywords = artist + ' ' + title
		time_now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
		print(time_now + '|' + 'amazon|' + csv_index + '|' + keywords)
		string_combos = create_list_queries(title,artist)
		albums_checked = set()
		albums_matched = set()		
		for combo in string_combos[0:min_combos]:
			if ((len(albums_checked) >= min_checked) or 
				(len(albums_matched) >= min_matched)):
				break
			query = ' '.join(combo)
			#note below it's quote_plus as spaces are converted to plus signs
			query_encoded = urllib.parse.quote_plus(query)
			page_url = 'https://music.amazon.in/search/' +\
				query_encoded + '/albums?filter=IsLibrary%257Cfalse&sc=none'
			timestamp = str(int(time.time() * 1000))
			headers_amazonx.update({
									'x-amzn-page-url': page_url,
									'x-amzn-timestamp': timestamp 
									})
			for setx in set_results:
				if ((len(albums_checked) >= min_checked) or 
					(len(albums_matched) >= min_matched)):
					break
				datax = '{"keyword":"' + query + '",' + set_results[setx] +\
						'"userHash":"{\\"level\\":\\"LIBRARY_MEMBER\\"}"}'
				urlx = 'https://eu.mesk.skill.music.a2z.com/api/searchCatalogAlbums'
				time_sleep(21,25)
				try:
					response = session.post(urlx, headers=headers_amazonx, 
											data=datax)
					results_dict = response.json()
				except:
					print('redo search|' + 'amazon|' + csv_index + '|' + keywords)
					time_sleep(150,180)
					break
				# nested try-except below covers different json response structures 
				try:
					albums_list = \
					results_dict['methods'][0]['template']['widgets'][0]['items']
				except:
					try:
						albums_list = results_dict['methods'][0]['items']
					except:
						print('redo search|' + 'amazon|' + csv_index + '|' + keywords)
						time_sleep(150,180)
						break
				# below is the 'got response, but no results condition' for amazon
					# albums_list will be an empty list. So if empty, move on 
				if not albums_list: break
				for album in albums_list:
					if ((len(albums_checked) >= min_checked) or 
						(len(albums_matched) >= min_matched)):
						break
					search_title = album['imageAltText']
					search_artist = album['secondaryText']
					search_title_url = 'https://music.amazon.in' +\
										 album['primaryLink']['deeplink']
					if search_title_url in albums_checked: continue				 
					albums_checked.add(search_title_url)
					level_of_title_match =\
						max(get_elkan_score_jarowink(title, search_title),
							get_elkan_score_jarowink(search_title, title))
					level_of_artist_match =\
						max(get_elkan_score_jarowink(artist, search_artist),
							get_elkan_score_jarowink(search_artist, artist))
					if 'various' in artist.lower():
						if (level_of_title_match < threshold):
							continue
					else:
						if ((level_of_title_match < threshold) or
							(level_of_artist_match < threshold)):
							continue
					if search_title_url in albums_matched: continue
					albums_matched.add(search_title_url)
					suffix = '_' + str(len(albums_matched))
					albums_df_copy.loc[index,('match_artist_amazon' + suffix)] =\
														search_artist
					albums_df_copy.loc[index,('match_title_amazon' + suffix)] =\
														search_title
					albums_df_copy.loc[index,('match_url_amazon' + suffix)] =\
														search_title_url
				
				# condition for going to next set of results
					# a field in every response contains the url for the next set 
					# if that field is empty, then break loop, dont go to next set
				try:
					next_set_list =\
					results_dict['methods'][0]['template']['widgets'][0]['onEndOfWidget']
				except:
					next_set_list = results_dict['methods'][0]['onEndOfWidget']
				if not next_set_list: break

	save_path = 'data/' + csv_name
	albums_df_copy.to_csv(save_path, 
						# index=False, 
						encoding='utf-8')


def playable_on_amazon(album_url):
	'''
	If at least 95% of an album's tracks are playable on amazon in India, it's
	considered playable.
	'''

	data_startx = headers_amazon.data_start
	data_endx = headers_amazon.data_end
	timestamp = str(int(time.time() * 1000))
	headers_amazonx.update({
							'x-amzn-page-url': album_url,
							'x-amzn-timestamp': timestamp 
							})
	api_url = 'https://eu.mesk.skill.music.a2z.com/api/showHome'
	album_id = re.search(r".*albums\/(.*)", album_url).group(1)
	datax = data_startx + album_id + data_endx
	response = session.post(api_url, headers=headers_amazonx, data=datax)
	results_dict = response.json()
	
	total_duration_string =\
		results_dict['methods'][2]['template']["headerTertiaryText"]
	total_duration_string_part = total_duration_string.split('•')[1]
	total_duration_string_part = total_duration_string_part.strip()
	total_duration = 0
	if 'HOURS' in total_duration_string_part:
		num_hours_string = re.search(r"(\d+)\sHOURS.*", 
									total_duration_string_part).group(1)
		num_seconds = int(num_hours_string) * 60 * 60
		total_duration += num_seconds
	if 'MINUTES' in total_duration_string_part:
		num_minutes_string = re.search(r"(\d+)\sMINUTES", 
									total_duration_string_part).group(1)
		num_seconds_2 = int(num_minutes_string) * 60
		total_duration += num_seconds_2
	# print(total_duration)

	item_list = results_dict['methods'][2]['template']['widgets'][0]['items']

	playable_duration = 0 
	for item in item_list:
		if item['isDisabled']: continue
		# if item["iconButton"]["disabled"]: continue
		item_duration = 0
		item_duration_string = item['secondaryText3']
		item_duration_parts = item_duration_string.split(':')

		item_duration_seconds = int(item_duration_parts[-1])

		try:
			item_duration_minutes = int(item_duration_parts[-2])
			item_duration_seconds_2 = item_duration_minutes * 60
		except:
			item_duration_seconds_2 = 0

		try:
			item_duration_hours = int(item_duration_parts[-3])
			item_duration_seconds_3 = item_duration_hours * 60 * 60
		except:
			item_duration_seconds_3 = 0
		
		item_duration = item_duration_seconds +\
						item_duration_seconds_2 +\
						item_duration_seconds_3

		playable_duration += item_duration
	# print(playable_duration)

	if playable_duration/total_duration >= 0.95:
		return True
	else:
		return False



def get_artist_title_amazon(album_url, genre):
	data_startx = headers_amazon.data_start
	data_endx = headers_amazon.data_end
	timestamp = str(int(time.time() * 1000))
	headers_amazonx.update({
							'x-amzn-page-url': album_url,
							'x-amzn-timestamp': timestamp 
							})
	api_url = 'https://eu.mesk.skill.music.a2z.com/api/showHome'
	album_id = re.search(r".*albums\/(.*)", album_url).group(1)
	datax = data_startx + album_id + data_endx
	response = session.post(api_url, headers=headers_amazonx, data=datax)
	results_dict = response.json()
	artist = results_dict['methods'][2]['template']['headerPrimaryText']
	title = results_dict['methods'][2]['template']['headerImageAltText']	
	return [artist, title]


def get_label_copyright_amazon(album_url):

	data_startx = headers_amazon.data_start
	data_endx = headers_amazon.data_end
	timestamp = str(int(time.time() * 1000))
	headers_amazonx.update({
							'x-amzn-page-url': album_url,
							'x-amzn-timestamp': timestamp 
							})
	api_url = 'https://eu.mesk.skill.music.a2z.com/api/showHome'
	album_id = re.search(r".*albums\/(.*)", album_url).group(1)
	datax = data_startx + album_id + data_endx
	response = session.post(api_url, headers=headers_amazonx, data=datax)
	results_dict = response.json()
	
	label = ''

	footer_all = results_dict['methods'][2]['template']['footer']
	if '℗© ' in footer_all:
		phono_copyright = re.search(r"℗© (.*)", footer_all).group(1) 
	elif '℗ ' in footer_all:
		phono_copyright = re.search(r"℗ (.*?) © .*", footer_all).group(1)
	else:
		phono_copyright = ''
		
	listx = [label, phono_copyright]
	return listx



def get_activity_tracks_amazon(album_url):
	'''
	A function where a dict of two key-value pairs is returned , first tells us
	whether album is active or not, 2nd element is number of tracks 
	# {'activity_status': 'active', 'tracks_count':9}
	'''

	data_startx = headers_amazon.data_start
	data_endx = headers_amazon.data_end
	timestamp = str(int(time.time() * 1000))
	headers_amazonx.update({
							'x-amzn-page-url': album_url,
							'x-amzn-timestamp': timestamp 
							})
	api_url = 'https://eu.mesk.skill.music.a2z.com/api/showHome'
	album_id = re.search(r".*albums\/(.*)", album_url).group(1)
	datax = data_startx + album_id + data_endx
	response = session.post(api_url, headers=headers_amazonx, data=datax)
	results_dict = response.json()
	
	tracks_count_string =\
		results_dict['methods'][2]['template']["headerTertiaryText"]
	tracks_count_string_part = tracks_count_string.split('•')[0]
	tracks_count_string_part = tracks_count_string_part.strip()
	tracks_count_raw = re.search(r"(\d+)\sSONG.*",
									tracks_count_string_part).group(1)
	tracks_count = int(tracks_count_raw)

	item_list = results_dict['methods'][2]['template']['widgets'][0]['items']
	tracks_count_playable = 0
	for item in item_list:
		if item['isDisabled']: continue
		# if item["iconButton"]["disabled"]: continue
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