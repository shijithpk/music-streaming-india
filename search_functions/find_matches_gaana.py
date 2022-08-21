#!/usr/bin/python

from .helpers import *

session = create_session()

headers_gaana_path = 'creds_headers/headers_gaana.json'
with open(headers_gaana_path) as json_file:
	headers_gaana = json.load(json_file)

def find_matches_gaana(albums_df, csv_name, min_matched, min_checked, min_combos, threshold):

	albums_df_copy = albums_df.copy(deep=True)
	for index,row in albums_df_copy.iterrows():
		title = row['title']
		artist = row['artist']
		genre = row['genre']
		csv_index = str(index).zfill(4)
		keywords = artist + ' ' + title
		time_now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
		print(time_now + '|' + 'gaana|' + csv_index + '|' + keywords)
		string_combos = create_list_queries(title,artist)
		albums_checked = set()
		albums_matched = set()
		for combo in string_combos[0:min_combos]:
			if ((len(albums_checked) >= min_checked) or 
				(len(albums_matched) >= min_matched)):
				break
			query = ' '.join(combo)
			query_encoded = urllib.parse.quote(query)
			referer = 'https://gaana.com/search/albums/' + query_encoded
			headers_gaana.update({"Referer": referer})
			urlx = 'https://gaana.com/apiv2?country=IN&keyword=' +\
				 query_encoded + '&page=0&secType=album&type=search'
			time_sleep(16,20)
			try:
				response = session.post(url=urlx,headers=headers_gaana)
				results_dict = response.json()
				# below is 'got response, but no results' condition
				albums_list = results_dict['gr'][0]['gd']
			except:
				print('redo search|' + 'gaana|' + csv_index + '|' + keywords)
				time_sleep(150,180)
				continue
			for album in albums_list:
				if ((len(albums_checked) >= min_checked) or 
					(len(albums_matched) >= min_matched)):
					break
				search_title = album['ti']
				search_title_url = 'https://gaana.com/album/' + album['seo']
				if search_title_url in albums_checked: continue
				albums_checked.add(search_title_url)
				level_of_title_match = max(
					get_elkan_score_jarowink(title, search_title),
					get_elkan_score_jarowink(search_title, title))
				if level_of_title_match < threshold: continue
				time_sleep(12,18)
				# visiting webpage of album to get artist name
				album_page = session.get(search_title_url, 
									headers = headers_gaana)
				treex = lxml_html.fromstring(album_page.content)

				album_active_list = treex.xpath("//li[contains(text(),'Album is inactive')]")
				album_active_list_2 = treex.xpath("//li[contains(text(),'Sorry, this content is not available')]")
				if (len(album_active_list) > 0) or (len(album_active_list_2) > 0):
					continue

				search_artist_list = [artist.xpath('@title')[0] for 
						artist in treex.xpath("//ul[@class='singers']/li/a")]
				try:
					search_artist = ', '.join(search_artist_list)
					# use condition below if you just want first artist listed
					# if genre == 'Western Classical':
					# 	search_artist = ', '.join(search_artist_list)
					# else:
					# 	search_artist = search_artist_list[0]
				except:
					print('redo search|' + 'gaana|' + csv_index + '|' + keywords)
					continue 
				track_list = treex.xpath("//ul[contains(@class,'list_data')]")
				if ((genre not in ['Blues','Jazz','Western Classical',
					'World Music']) and (len(track_list) <= 1)):
					continue
				level_of_artist_match = max(
					get_elkan_score_jarowink(artist, search_artist),
					get_elkan_score_jarowink(search_artist, artist))
				if 'various' not in artist.lower():
					if level_of_artist_match < threshold:
						continue				
				if search_title_url in albums_matched: continue
				albums_matched.add(search_title_url)
				suffix = '_' + str(len(albums_matched))
				albums_df_copy.loc[index,'match_artist_gaana' + suffix] = search_artist
				albums_df_copy.loc[index,'match_title_gaana' + suffix] = search_title
				albums_df_copy.loc[index,'match_url_gaana' + suffix] = search_title_url

	save_path = 'data/' + csv_name
	albums_df_copy.to_csv(save_path, 
						encoding='utf-8')



def playable_on_gaana(album_url):
	album_page = session.get(url=album_url, headers=headers_gaana)
	treex = lxml_html.fromstring(album_page.content)
	album_active_list = treex.xpath("//li[contains(text(),'Album is inactive')]")
	album_active_list_2 = treex.xpath("//li[contains(text(),'Sorry, this content is not available')]")
	if (len(album_active_list) > 0) or (len(album_active_list_2) > 0):
		return False
	
	total_duration_string =\
		treex.xpath("//span[contains(@class,'_duration')]/text()")[0]

	total_duration = 0
	if 'hr' in total_duration_string:
		num_hours_string = re.search(r"(\d+)\shr", 
									total_duration_string).group(1)
		num_seconds = int(num_hours_string) * 60 * 60
		total_duration += num_seconds
	if 'min' in total_duration_string:
		num_minutes_string = re.search(r"(\d+)\smin", 
									total_duration_string).group(1)
		num_seconds_2 = int(num_minutes_string) * 60
		total_duration += num_seconds_2
	if 'sec' in total_duration_string:
		num_seconds_string = re.search(r"(\d+)\ssec", 
									total_duration_string).group(1)
		num_seconds_3 = int(num_seconds_string)
		total_duration += num_seconds_3
	# print(total_duration)

	item_list = treex.\
	xpath("//section[contains(@class,'song-list')]//ul[@class='_row list_data']")
	# print('number of songs in list:' + str(len(item_list)))
	# total_duration = 0
	playable_duration = 0
	for item in item_list:
		item_duration_string =\
		  item.xpath("./descendant::li[contains(@class,'_dur')][1]/span/text()")[0]
		# print(item_duration_string)
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

		# total_duration += item_duration

		play_button_list = item.xpath("./descendant::li[@title='Play'][1]")
		if not play_button_list: continue
		#above line says if there's no play button svg element for song, move on
		  #if it's an empty list, empty list is falsy value, so NOT False == True

		playable_duration += item_duration
	# print(total_duration)
	# print(playable_duration)

	if playable_duration/total_duration >= 0.95:
		return True
	else:
		return False


def playable_on_gaana_details(album_url):
	album_page = session.get(url=album_url, headers=headers_gaana)
	treex = lxml_html.fromstring(album_page.content)
	album_active_list = treex.xpath("//li[contains(text(),'Album is inactive')]")
	if len(album_active_list) != 0:
		return 'album inactive'
	
	total_duration_string =\
		treex.xpath("//span[contains(@class,'_duration')]/text()")[0]

	total_duration = 0
	if 'hr' in total_duration_string:
		num_hours_string = re.search(r"(\d+)\shr", 
									total_duration_string).group(1)
		num_seconds = int(num_hours_string) * 60 * 60
		total_duration += num_seconds
	if 'min' in total_duration_string:
		num_minutes_string = re.search(r"(\d+)\smin", 
									total_duration_string).group(1)
		num_seconds_2 = int(num_minutes_string) * 60
		total_duration += num_seconds_2
	if 'sec' in total_duration_string:
		num_seconds_string = re.search(r"(\d+)\ssec", 
									total_duration_string).group(1)
		num_seconds_3 = int(num_seconds_string)
		total_duration += num_seconds_3
	# print(total_duration)

	item_list = treex.\
	xpath("//section[contains(@class,'song-list')]//ul[@class='_row list_data']")
	# print('number of songs in list:' + str(len(item_list)))
	# total_duration = 0
	playable_duration = 0
	for item in item_list:
		item_duration_string =\
		  item.xpath("./descendant::li[contains(@class,'_dur')][1]/span/text()")[0]
		# print(item_duration_string)
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

		# total_duration += item_duration

		play_button_list = item.xpath("./descendant::li[@title='Play'][1]")
		if not play_button_list: continue
		#above line says if there's no play button svg element for song, move on
		  #if it's an empty list, empty list is falsy value, so NOT False == True

		playable_duration += item_duration
	# print(total_duration)
	# print(playable_duration)

	if playable_duration/total_duration >= 0.95:
		return 'duration ok'
	else:
		return 'duration not ok'


def get_artist_title_gaana(album_url, genre):
	album_page = session.get(url=album_url, headers=headers_gaana)
	treex = lxml_html.fromstring(album_page.content)
	artist_list = [artist.xpath('@title')[0] for 
		artist in treex.xpath("//ul[@class='singers']/li/a")]
	if genre == 'Western Classical':
		artist = ', '.join(artist_list)
	else:
		artist = artist_list[0]
	title = treex.xpath("//h2[@class='title']/text()")[0]
	return [artist, title]


def get_label_copyright_gaana(album_url):
	album_page = session.get(url=album_url, headers=headers_gaana)
	treex = lxml_html.fromstring(album_page.content)

	label = ''

	phono_copyright_raw = treex.xpath("//div[@class='copyright']/text()")
	phono_copyright_raw = ' '.join(phono_copyright_raw)
	phono_copyright = phono_copyright_raw.replace('©','').strip()

	listx = [label, phono_copyright]
	return listx


def get_activity_tracks_gaana(album_url):

	album_page = session.get(url=album_url, headers=headers_gaana)
	treex = soup_fromstring(album_page.content)
	album_active_list_1 = treex.xpath("//li[contains(text(),'Album is inactive')]")
	album_active_list_2 = treex.xpath("//li[contains(text(),'No tracks found in this album')]")
	album_active_list_3 = treex.xpath("//li[contains(text(),'Sorry, this content is not available')]")
	if ((len(album_active_list_1) > 0) or (len(album_active_list_2) > 0) or (len(album_active_list_3) > 0)):
		inactive_dict = {
				'activity_status': 'inactive without a doubt', 
				'tracks_count': 0,
				'tracks_count_playable': 0,
				}
		return inactive_dict
	
	tracks_count_string =\
		treex.xpath("//span[@class='_date' and contains(text(),'Track')]/text()")[0]
	tracks_count_raw = re.search(r"(\d+)\sTrack", 
									tracks_count_string).group(1)
	tracks_count = int(tracks_count_raw)

	tracks_count_playable = 0
	item_list = treex.\
	xpath("//section[contains(@class,'song-list')]//ul[@class='_row list_data']")
	for item in item_list:
		play_button_list = item.xpath("./descendant::li[@title='Play'][1]")
		if not play_button_list: continue
		#above line says if there's no play button svg element for song, move on
		  #if it's an empty list, empty list is falsy value, so NOT False == True
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
							'tracks_count_playable': tracks_count_playable
							}

	return activity_tracks_dict
