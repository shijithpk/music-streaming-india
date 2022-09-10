#!/usr/bin/python3

from .helpers import *
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from creds_headers import cred_spotify 
#above path is relative to main.py which is the script that's run, not this .py


session = create_session()

client_credentials_manager = SpotifyClientCredentials(
							client_id = cred_spotify.client_id,
							client_secret = cred_spotify.client_secret
							)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager,
					requests_session=session,
						)

def find_matches_spotify(albums_df, csv_name, min_matched, min_checked, min_combos):
	'''
	Takes in the dataframe of album titles & artists.
	Finds matches for them if any on spotify.
	Creates new columns in the dataframe with details, url, name of the matches
	Saves the modified dataframe as 'csv_name'
	min_matched is the min no. of albums that should be a match to your search
	min_checked is the min no. of albums your code should go through
	min_combos is the min no. of keyword combos your code should query for
	'''

	albums_df_copy = albums_df.copy(deep=True)
	for index,row in albums_df_copy.iterrows():
		title = row['title']
		artist = row['artist']
		genre = row['genre']
		csv_index = str(index).zfill(4)
		keywords = artist + ' ' + title
		time_now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
		print(time_now + '|' + 'spotify|' + csv_index + '|' + keywords)
		string_combos = create_list_queries(title,artist)
		albums_checked = set()
		albums_matched = set()		
		for combo in string_combos[0:min_combos]:
			if ((len(albums_checked) >= min_checked) or 
				(len(albums_matched) >= min_matched)):
				break
			query = ' '.join(combo)
			time_sleep(21,25)
			results = sp.search(query, limit=50, offset=0, 
								type="album", market='IN')
			if not results['albums']['items']: continue
			# above is 'got response, but no results' condition for spotify
			#if no results, we'll get an empty list, which is a Falsy value
				# So NOT a falsy value would be true, so we move to next combo
			album_list = results['albums']['items']
			for album in album_list:
				if ((len(albums_checked) >= min_checked) or 
					(len(albums_matched) >= min_matched)):
					break
				# if album['album_type'] != 'album': continue
				#sometimes album_type can be single, EP or compilation
					# if you want to restrict results to albums proper, 
						# uncomment line above
				search_artist_name_list = [artist['name'] for artist in
							 album['artists']]
				search_artist = ', '.join(search_artist_name_list)
				search_title = album['name']
				search_title_url = album['external_urls']['spotify']
				if search_title_url in albums_checked: continue
				albums_checked.add(search_title_url)
				search_title_number_tracks = album['total_tracks']
				if ((genre not in ['Blues','Jazz','Western Classical',
						'World Music']) and (search_title_number_tracks <= 1)):
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
				albums_df_copy.loc[index,('match_artist_spotify' + suffix)] =\
																 search_artist
				albums_df_copy.loc[index,('match_title_spotify' + suffix)] =\
																 search_title
				albums_df_copy.loc[index,('match_url_spotify' + suffix)] =\
															search_title_url

	
	save_path = 'data/' + csv_name #relative to main.py
	albums_df_copy.to_csv(save_path, 
						encoding='utf-8')


def playable_on_spotify(album_url):
	'''
	Takes an album url and checks its availability in India.\n
	If 95% of the album's duration is playable, it's available in India.\n
	I think spotify won't even show an album in its search results, unless all
	the tracks on it are playable.\n
	'''

	# album_id = re.search(r"album\/(.*)", album_url).group(1)
	album_id = re.search(r"album\/(.*?)(?=\?|$)", album_url).group(1)

	response = sp.album_tracks(album_id=album_id,limit=50,market='IN')

	tracks = response['items']
	while response['next']:
		time.sleep(5)
		response = sp.next(response)
		tracks.extend(response['items'])

	total_duration = 0
	playable_duration = 0
	for track in tracks:
		track_duration = track['duration_ms']
		total_duration += track_duration
		if track['is_playable']:
			playable_duration += track_duration

	if playable_duration/total_duration >= 0.95:
		return True
	else:
		return False


def get_artist_title_spotify(album_url, genre):
	album_id = re.search(r"album\/(.*?)(?=\?|$)", album_url).group(1)
	response = sp.album(album_id=album_id)

	title = response['name']
	artist_name_list = [artistx['name'] for artistx in
					response['artists']]
	artist = ', '.join(artist_name_list)
	return [artist, title]


def get_label_copyright_spotify(album_url):
	album_id = re.search(r"album\/(.*?)(?=\?|$)", album_url).group(1)
	response = sp.album(album_id=album_id)
	
	label = response['label']

	phono_copyright = ''
	
	if response['copyrights']:
		for index, value in enumerate(response['copyrights']):
			if response['copyrights'][index]['type'] == 'P':
				# phono short for phonographic
				phono_copyright = response['copyrights'][index]['text']

		if phono_copyright == '':
			phono_copyright = response['copyrights'][0]['text']
		
	listx = [label, phono_copyright]
	return listx


def get_activity_tracks_spotify(album_url):

	album_id = re.search(r"album\/(.*?)(?=\?|$)", album_url).group(1)
	response = sp.album_tracks(album_id=album_id,limit=50,market='IN')

	tracks_count = response["total"] #already an integer

	tracks = response['items']
	while response['next']:
		time.sleep(5)
		response = sp.next(response)
		tracks.extend(response['items'])

	tracks_count_playable = 0
	for track in tracks:
		if track['is_playable']:
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










