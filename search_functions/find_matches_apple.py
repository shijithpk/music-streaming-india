from .helpers import *
from creds_headers import headers_apple

session = create_session()
headers_applex = headers_apple.headers_apple

def find_matches_apple(albums_df, csv_name, min_matched, min_checked, min_combos):

	albums_df_copy = albums_df.copy(deep=True)
	for index,row in albums_df_copy.iterrows():
		title = row['title']
		artist = row['artist']
		genre = row['genre']
		csv_index = str(index).zfill(4)
		keywords = artist + ' ' + title
		time_now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
		print(time_now + '|' + 'apple|' + csv_index + '|' + keywords)
		string_combos = create_list_queries(title,artist)
		albums_checked = set()
		albums_matched = set()		
		for combo in string_combos[0:min_combos]:
			if ((len(albums_checked) >= min_checked) or 
				(len(albums_matched) >= min_matched)):
				break
			query = ' '.join(combo)
			query_encoded = urllib.parse.quote(query)
			urlx = 'https://amp-api.music.apple.com/v1/catalog/in/search?term=' +\
				 query_encoded +'&l=en-gb&platform=web&types=albums&limit=25'
			time_sleep(28,32)
			response = session.get(urlx, headers=headers_applex)

			try:
				albums_check = response.json()['results']['albums']
			except:
				print('redo search|' + 'apple|' + csv_index + '|' + keywords)
				time_sleep(120,180)
				continue
			def matches_present(response):
				results_dict = response.json()
				albums_list = results_dict['results']['albums']['data']
				# below is 'got response, but no results' condition for apple
					# albums_list will be an empty list
					# so if no results, function doesnt modify dataframe
				if not albums_list: return None
				for album in albums_list:
					if ((len(albums_checked) >= min_checked) or 
						(len(albums_matched) >= min_matched)):
						break
					search_artist = album['attributes']['artistName']
					search_title = album['attributes']['name']
					search_title_url = album['attributes']['url']
					if search_title_url in albums_checked: continue
					albums_checked.add(search_title_url)
					search_title_number_tracks = album['attributes']['trackCount']
					if ((genre not in ['Blues','Jazz','Western Classical',
						'World Music']) and (search_title_number_tracks <= 1)):
						continue
					level_of_title_match = max(
						get_elkan_score_jarowink(title, search_title),
						get_elkan_score_jarowink(search_title, title))
					level_of_artist_match = max(
						get_elkan_score_jarowink(artist, search_artist),
						get_elkan_score_jarowink(search_artist, artist))
					if 'various' in artist.lower():
						if (level_of_title_match < 85):
							continue
					else:
						if ((level_of_title_match < 85) or
							(level_of_artist_match < 85)):
							continue
					if search_title_url in albums_matched: continue
					albums_matched.add(search_title_url)
					suffix = '_' + str(len(albums_matched))
					albums_df_copy.loc[index,'match_artist_apple' + suffix] =\
														search_artist
					albums_df_copy.loc[index,'match_title_apple' + suffix] =\
														search_title
					albums_df_copy.loc[index,'match_url_apple' + suffix] =\
														search_title_url

			matches_present(response)

	save_path = 'data/' + csv_name
	albums_df_copy.to_csv(save_path, 
						encoding='utf-8')

# FUNCTION BELOW NEEDS TO BE REWORKED, THE PLAYABLE SONG XPATH IS WRONG
# It's not "//button[contains(text(),'PREVIEW')]". Correct xpath is 
# "//div[contains(@class,'songs-list-row--web-preview') and not(contains(@class,'songs-list-row--disabled'))]"

# def playable_on_apple(album_url):

# 	# if we get us market url, change to indian market one 
# 	if '.com/us/album/' in album_url:
# 		album_url = album_url.replace('.com/us/album/','.com/in/album/')

# 	album_page = session.get(album_url, headers = headers_applex)
# 	treex = lxml_html.fromstring(album_page.content)

# 	try:
# 		song_stats =\
# 		treex.xpath("//p[@class='song-stats-container']/div/text()")[0]
# 	except:
# 		# if element missing, means blank page returned, means album not playable in India
# 		return False

# 	# getting total duration of album on page
# 	total_duration = 0
# 	for element in song_stats.split(','):
# 		element = element.strip()
# 		if 'Hours' in element:
# 			num_hours_string = re.search(r"(\d{1,4})\sHours", element).group(1)
# 			num_seconds = int(num_hours_string) * 60 * 60 #converted to seconds
# 			total_duration += num_seconds
# 		if 'Minutes' in element:
# 			num_minutes_string = re.search(r"(\d{1,4})\sMinutes", element).group(1)
# 			num_seconds_2 = int(num_minutes_string) * 60 # converted to seconds
# 			total_duration += num_seconds_2
	
# 	playable_rows = treex.xpath("//button[contains(text(),'PREVIEW')]")
# 	playable_duration = 0
# 	for row in playable_rows:
# 		playable_time_string = row.xpath("./preceding::time[1]/@datetime")[0]
# 		if 'H' in playable_time_string:
# 			num_hours_string = re.search(r"PT(\d+)H.*", 
# 										playable_time_string).group(1)
# 			num_seconds = int(num_hours_string) * 60 * 60
# 			playable_duration += num_seconds
# 		if 'M' in playable_time_string:
# 			num_minutes_string = re.search(r".*[TH]{1}(\d+)M.*", 
# 										playable_time_string).group(1)
# 			num_seconds_2 = int(num_minutes_string) * 60
# 			playable_duration += num_seconds_2
# 		if 'S' in playable_time_string:
# 			num_seconds_string = re.search(r".*[THM]{1}(\d+)S", 
# 										playable_time_string).group(1)
# 			num_seconds_3 = int(num_seconds_string)
# 			playable_duration += num_seconds_3
		
# 	if playable_duration/total_duration >= 0.95:
# 		return True
# 	else:
# 		return False

def get_artist_title_apple(album_url, genre):
	album_page = session.get(album_url, headers = headers_applex)
	treex = lxml_html.fromstring(album_page.content)
	artist_list = treex.xpath("//div[contains(@class,'product-creator')]//a/text()")
	artist = ', '.join(artist_list)
	title_raw = treex.xpath("//h1[@id='page-container__first-linked-element']/text()")[0]
	title = title_raw.strip()
	return [artist, title]


def get_label_copyright_apple(album_url):
	album_page = session.get(album_url, headers = headers_applex)
	treex = lxml_html.fromstring(album_page.content)
	label = re.search(r'recordLabel[\\]{1,2}":[\\]{1,2}"(.*?)[\\]{1,2}",', album_page.text).group(1)	

	phono_copyright_raw = treex.xpath("//p[@class='song-copyright']/text()")[0]
	phono_copyright = phono_copyright_raw.strip()

	listx = [label, phono_copyright]
	return listx

def get_activity_tracks_apple(album_url):
	'''
	A function where a dict of two key-value pairs is returned , first tells us
	whether album is active or not, 2nd element is number of tracks 
	# {'activity_status': 'active', 'tracks_count':9}
	'''

	# if we get us market url, change to indian market one 
	if '.com/us/album/' in album_url:
		album_url = album_url.replace('.com/us/album/','.com/in/album/')

	album_page = session.get(album_url, headers = headers_applex)
	# treex = lxml_html.fromstring(album_page.content)
	treex = soup_fromstring(album_page.content)

	try:
		song_stats = treex.xpath("//p[@class='song-stats-container']/div/text()")[0]
	except:
		# if element missing, means blank page returned, means album not playable in India
		inactive_dict = {
				'activity_status': 'inactive without a doubt', 
				'tracks_count': 0,
				'tracks_count_playable': 0,
				}
		return inactive_dict

	for element in song_stats.split(','):
		element = element.strip()
		if 'Song' in element:
			tracks_count_raw = re.search(r"(\d{1,4})\sSong", element).group(1)
			tracks_count_stated = int(tracks_count_raw)

	row_number_list = treex.xpath("//span[contains(@class,'songs-list-row__column-data')]/text()")
	last_row_number_raw = row_number_list[-1]
	tracks_count_from_rows = int(last_row_number_raw)

	tracks_count = max(tracks_count_stated, tracks_count_from_rows)

	playable_rows = treex.xpath("//div[contains(@class,'songs-list-row--web-preview') and not(contains(@class,'songs-list-row--disabled'))]")
	tracks_count_playable = len(playable_rows)

	threshold = 0.8*tracks_count

	if tracks_count_playable >= tracks_count:
		activity_status = 'possibly active'
	elif tracks_count_playable >= threshold:
		activity_status = 'possibly inactive: but over internal threshold'
	elif tracks_count_playable < threshold:
		activity_status = 'possibly inactive: below internal threshold'

	active_dict = {
					'activity_status': activity_status, 
					'tracks_count': tracks_count,
					'tracks_count_playable': tracks_count_playable,
					}

	return active_dict