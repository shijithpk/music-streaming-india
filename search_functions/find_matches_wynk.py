from .helpers import *
from creds_headers import headers_wynk

session = create_session()

headersx = headers_wynk.headers
paramsx = headers_wynk.params

def find_matches_wynk(albums_df, csv_name, min_matched, min_checked, min_combos):

	albums_df_copy = albums_df.copy(deep=True)
	for index,row in albums_df_copy.iterrows():
		title = row['title']
		artist = row['artist']
		genre = row['genre']
		csv_index = str(index).zfill(4)
		keywords = artist + ' ' + title
		time_now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
		print(time_now + '|' + 'wynk|' + csv_index + '|' + keywords)
		# for wynk only using album title for query, not artist name
		string_combos = create_list_queries(title,'')
		albums_checked = set()
		albums_matched = set()		
		for combo in string_combos[0:min_combos]:
			if ((len(albums_checked) >= min_checked) or 
				(len(albums_matched) >= min_matched)):
				break
			query = ' '.join(combo)
			paramsx['q'] = query
			urlx = 'https://search.wynk.in/music/v4/search'
			time_sleep(21,25)
			try:
				response = session.get(url=urlx, headers=headersx, 
										params=paramsx)
				results_dict = response.json()
				# below is 'got response, but no results' condition for wynk
				results_dict_total = results_dict['total']
			except:
				print('redo search|' + 'wynk|' + csv_index + '|' + keywords)
				time_sleep(150,180)
				continue
			if results_dict_total == 0: continue
			albums_list = results_dict['items']
			for album in albums_list:
				if ((len(albums_checked) >= min_checked) or 
					(len(albums_matched) >= min_matched)):
					break
				try:
					search_title = album['title']
				except:
					continue
				level_of_title_match = max(
					get_elkan_score_jarowink(title, search_title),
					get_elkan_score_jarowink(search_title, title))
				# try:
				# 	title_threshold =\
				# 			100*((len(tokenize(title))-1)/len(tokenize(title)))
				# except:
				# 	title_threshold = 85
				title_threshold = 85
				if level_of_title_match < title_threshold: continue
				url_fragment = album['id']
				search_title_url = "https://wynk.in/music/album/" + url_fragment
				if search_title_url in albums_checked: continue
				albums_checked.add(search_title_url)
				track_list_count = album['count']
				if ((genre not in ['Blues','Jazz','Western Classical',
								'World Music']) and (track_list_count <= 1)):
					continue
				try:
					search_artist = album['artist']
				except:
					continue
				level_of_artist_match = max(
					get_elkan_score_jarowink(artist, search_artist),
					get_elkan_score_jarowink(search_artist, artist))
				# try:
				# 	artist_threshold =\
				# 			100*((len(tokenize(artist))-1)/len(tokenize(artist)))
				# except:
				# 	artist_threshold = 85
				artist_threshold = 85
				if 'various' not in artist.lower():
					if level_of_artist_match < artist_threshold:
						continue				
				if search_title_url in albums_matched: continue
				albums_matched.add(search_title_url)
				suffix = '_' + str(len(albums_matched))
				albums_df_copy.loc[index,'match_artist_wynk' + suffix] =\
															search_artist
				albums_df_copy.loc[index,'match_title_wynk' + suffix] =\
															search_title
				albums_df_copy.loc[index,'match_url_wynk' + suffix] =\
															search_title_url

	save_path = 'data/' + csv_name
	albums_df_copy.to_csv(save_path, encoding='utf-8')


def playable_on_wynk(album_url):

	album_page = session.get(url=album_url, headers=headersx)
	treex = lxml_html.fromstring(album_page.content)

	script_text = treex.xpath("//script[@id='__NEXT_DATA__']/text()")[0]
	results_dict = json.loads(script_text)

	total_duration =\
		results_dict['props']['initialState']['album']['info']['duration']
	# print(total_duration)

	playable_duration = 0
	item_list = results_dict['props']['initialState']['album']['info']['items']
	song_rows =\
		treex.xpath("//div[@class='block']//div[contains(@class,'items-center')]")
	i = -1
	for row in song_rows:
		i+=1
		play_button_list =\
			row.xpath(".//i[contains(@class,'icon-ic_global_play_dark')]")
		if len(play_button_list) == 0: continue
		item_duration = item_list[i]['duration']
		playable_duration += item_duration
	# print(playable_duration)
	
	if playable_duration/total_duration >= 0.95:
		return True
	else:
		return False


def get_artist_title_wynk(album_url, genre):

	album_page = session.get(url=album_url, headers=headersx)
	treex = lxml_html.fromstring(album_page.content)

	title = treex.xpath("//h1[@class='heading1']/text()")[0]
	artist_list = treex.xpath("//h3[text()='Featured Artists']/following-sibling::ul[1]//li/a/@title")
	if genre == 'Western Classical':
		artist = ', '.join(artist_list)
	else:
		artist = artist_list[0]
	return [artist, title]


def get_label_copyright_wynk(album_url):	

	label = ''

	if 'srch_' in album_url:
		phono_copyright = re.search(r"\/srch_(.*?)_", album_url).group(1)
	elif 'QVV' in album_url:
		album_page = session.get(url=album_url, headers=headersx)
		treex = lxml_html.fromstring(album_page.content)
		phono_copyright_raw = treex.xpath("//link[@rel='image_src']/@href")[0]
		phono_copyright = re.search(r"music.*\/srch_(.*?)_", phono_copyright_raw).group(1)
	else:
		phono_copyright = re.search(r".*\/([a-z]{2})_", album_url).group(1)

	listx = [label, phono_copyright]
	return listx


def get_activity_tracks_wynk(album_url):

	headersx = headers_wynk.headers_alt

	# album_page = session.get(url=album_url, headers=headersx)
	album_page = requests.get(url=album_url, headers=headersx)
	treex = soup_fromstring(album_page.content)

	album_inactive_list = treex.xpath("//p[text()='Looks like few of our notes got missed somewhere. Try again later. Keep Wynk-ing!']")
	if len(album_inactive_list) > 0:
		inactive_dict = {
				'activity_status': 'inactive without a doubt', 
				'tracks_count': 0,
				'tracks_count_playable': 0,
				}
		return inactive_dict

	script_text = treex.xpath("//script[@id='__NEXT_DATA__']/text()")[0]
	results_dict = json.loads(script_text)

	tracks_count =\
		results_dict['props']['initialState']['album']['info']['total']

	# tracks_count_playable = 0
	# song_rows =\
	# 	treex.xpath("//div[@class='block']//div[contains(@class,'items-center')]")
	# for row in song_rows:
	# 	play_button_list =\
	# 		row.xpath(".//i[contains(@class,'icon-ic_global_play_dark')]")
	# 	if len(play_button_list) == 0: continue
	# 	tracks_count_playable += 1

	tracks_count_playable =\
		results_dict['props']['initialState']['album']['info']['actualTotal']

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
