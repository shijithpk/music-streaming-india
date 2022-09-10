#!/usr/bin/python3

# for jiosaavn
from jiosaavn.Sync import searchAlbum
import html
from .helpers import *
from jiosaavn.Sync import album as jiosaavn_album

def find_matches_jiosaavn(albums_df, csv_name, min_matched, min_checked, min_combos):

	albums_df_copy = albums_df.copy(deep=True)
	for index,row in albums_df_copy.iterrows():
		title = row['title']
		artist = row['artist']
		genre = row['genre']
		csv_index = str(index).zfill(4)
		keywords = artist + ' ' + title
		time_now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
		print(time_now + '|' + 'jiosaavn|' + csv_index + '|' + keywords)
		string_combos = create_list_queries(title,artist)
		albums_checked = set()
		albums_matched = set()		
		for combo in string_combos[0:min_combos]:
			if ((len(albums_checked) >= min_checked) or 
				(len(albums_matched) >= min_matched)):
				break
			query = ' '.join(combo)
			time_sleep(16,20)
			album_list = searchAlbum(query) 
			# below is 'got reponse, but no results' condition
				# we get an empty list back. So if empty list, move on 
			if not album_list: continue
			for album in album_list:
				if ((len(albums_checked) >= min_checked) or 
					(len(albums_matched) >= min_matched)):
					break
				try:
					search_title_raw = album['albumName']
				except:
					print('redo search|jiosaavn|' + csv_index + '|' + keywords)
					time_sleep(120,180)
					continue
				search_title = html.unescape(search_title_raw)
				search_title_url = album['albumUrl']
				if search_title_url in albums_checked: continue
				albums_checked.add(search_title_url)
				search_artist_raw = album['music']
				search_artist = html.unescape(search_artist_raw)
				songIds_string = album['songIds']
				songIds_list = [x.strip() for x in songIds_string.split(',')]
				if ((genre not in ['Blues','Jazz','Western Classical',
					'World Music']) and (len(songIds_list) <= 1)):
					continue
				level_of_title_match = max(
					get_elkan_score_jarowink(title, search_title),
					get_elkan_score_jarowink(search_title, title))
				level_of_artist_match = max(
					get_elkan_score_jarowink(artist, search_artist),
					get_elkan_score_jarowink(search_artist, artist))
					
				# try:
				# 	title_threshold =\
				# 		100*((len(tokenize(title))-1)/len(tokenize(title)))
				# except:
				# 	title_threshold = 85
				# try:
				# 	artist_threshold =\
				# 		100*((len(tokenize(artist))-1)/len(tokenize(artist)))
				# except:
				# 	artist_threshold = 85
				title_threshold = 85
				artist_threshold = 85

				if 'various' in artist.lower():
					if (level_of_title_match < title_threshold):
						continue
				else:
					if ((level_of_title_match < title_threshold) or
						(level_of_artist_match < artist_threshold)):
						continue
				if search_title_url in albums_matched: continue
				albums_matched.add(search_title_url)
				suffix = '_' + str(len(albums_matched))
				albums_df_copy.loc[index,'match_artist_jiosaavn' + suffix] =\
																search_artist
				albums_df_copy.loc[index,'match_title_jiosaavn' + suffix] =\
																search_title
				albums_df_copy.loc[index,'match_url_jiosaavn' + suffix] =\
																search_title_url

	save_path = 'data/' + csv_name
	albums_df_copy.to_csv(save_path, 
						encoding='utf-8')


# def playable_on_jiosaavn_old(album_url):
# 	results_dict = jiosaavn_album(album_url)
# 	try:
# 		track_list = results_dict['songs']
# 	except:
# 		print('issue with album_url: ' + album_url)
# 		return None

# 	total_duration = 0
# 	playable_duration = 0
# 	for track in track_list:
# 		track_duration = int(track['duration'])
# 		total_duration += track_duration
# 		if track['audioUrls']:
# 			# if track not available, audioUrls will be None in json response
# 				# and won't add to playable duration. If sthing's there, it will
# 			playable_duration += track_duration

# 	# print(total_duration)
# 	# print(playable_duration)
# 	if playable_duration/total_duration >= 0.95:
# 		return True
# 	else:
# 		return False

# Had to come up with new playable function since some albums that were playable
	# did have audioUrls, so couldn't use that as a criteria to determine playability

def playable_on_jiosaavn(album_url):
	session = create_session()
	album_page = session.get(url=album_url)
	treex = lxml_html.fromstring(album_page.content)
	album_inactive_list = treex.xpath("//p[text()='This album is currently unavailable in your area. ']")
	if len(album_inactive_list) == 0:
		return True
	else:
		return False


def get_artist_title_jiosaavn(album_url, genre):
	
	results_dict = jiosaavn_album(album_url)
	
	title = results_dict['title']
	title = html.unescape(title)

	artist = results_dict['primaryArtists']
	artist = html.unescape(artist)

	return [artist, title]


def get_label_copyright_jiosaavn(album_url):

	results_dict = jiosaavn_album(album_url)
	# copyright info here could be phonographic or composition or both
		# dont rely on it 
	try:
		label = html.unescape(results_dict['songs'][0]['label'])
		label = label.strip()
	except:
		label = ''

	try:
		phono_copyright = html.unescape(results_dict['songs'][0]['copyright'])
		phono_copyright = phono_copyright.strip()
	except: 
		phono_copyright = ''

	listx = [label, phono_copyright]
	return listx

def get_activity_tracks_jiosaavn(album_url):
	session = create_session()
	album_page = session.get(url=album_url)
	treex = soup_fromstring(album_page.content)
	
	album_inactive_list = treex.xpath("//p[text()='This album is currently unavailable in your area. ']")
	if len(album_inactive_list) > 0:
		inactive_dict = {
				'activity_status': 'inactive without a doubt', 
				'tracks_count': 0,
				'tracks_count_playable': 0,
				}
		return inactive_dict

	try:
		info_script_string = treex.xpath("//script[contains(text(),'numTracks')]/text()")[0]
	except:
		issue_dict = {
				'activity_status': 'redo the check, had an issue', 
				'tracks_count': 0,
				'tracks_count_playable': 0,
				}
		return issue_dict

	# info_script_json = json.loads(info_script_string)
	# tracks_count_raw = info_script_json["numTracks"]
	tracks_count_raw = re.search(r"numTracks.*?\"(\d{1,4})\"\,", info_script_string).group(1)
	tracks_count = int(tracks_count_raw)

	item_list = treex.xpath("//section[@class='u-margin-bottom-large@sm']/ol[contains(@class,'o-list-bare')]//li")
	tracks_count_playable = 0
	for item in item_list:
		# unplayable_song_button = item.xpath(".//i[contains(@class,'o-icon-ban')]")
		# if unplayable_song_button > 0: continue
		playable_song_button = item.xpath(".//span[contains(@class,'o-icon-play-circle')]")
		if playable_song_button == 0: continue
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
