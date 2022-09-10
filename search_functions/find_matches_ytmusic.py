#for youtube music
from ytmusicapi import YTMusic
from .helpers import *

ytmusic = YTMusic()

def find_matches_ytmusic(albums_df, csv_name, min_matched, min_checked, min_combos):

	albums_df_copy = albums_df.copy(deep=True)
	for index,row in albums_df_copy.iterrows():
		title = row['title']
		artist = row['artist']
		csv_index = str(index).zfill(4)
		keywords = artist + ' ' + title
		time_now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
		print(time_now + '|' + 'ytmusic|' + csv_index + '|' + keywords)
		string_combos = create_list_queries(title,artist)
		albums_checked = set()
		albums_matched = set()
		for combo in string_combos[0:min_combos]:
			if ((len(albums_checked) >= min_checked) or 
				(len(albums_matched) >= min_matched)):
				break
			query = ' '.join(combo)
			time_sleep(16,20)
			album_list = ytmusic.search(query, filter='albums')
			# below is 'got response, but no results' condition for yt music
				# we get an empty list back 
			if not album_list: continue
			for album in album_list:
				if ((len(albums_checked) >= min_checked) or 
					(len(albums_matched) >= min_matched)):
					break
				if album['category'] != 'Albums': continue
				if album['resultType'] != 'album': continue
				if album['type'] != 'Album': continue
				#sometime the album-type is 'single', so checking for that
				search_artist_name_list =\
						 [artist['name'] for artist in album['artists']]
				search_artist = ', '.join(search_artist_name_list)
				search_title = album['title']
				search_title_url = 'https://music.youtube.com/browse/' +\
															album['browseId']
				if search_title_url in albums_checked: continue
				albums_checked.add(search_title_url)							
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
				albums_df_copy.loc[index,'match_artist_ytmusic' + suffix] =\
															search_artist
				albums_df_copy.loc[index,'match_title_ytmusic' + suffix] =\
															search_title
				albums_df_copy.loc[index,'match_url_ytmusic' + suffix] =\
															search_title_url

	save_path = 'data/' + csv_name
	albums_df_copy.to_csv(save_path, 
						# index=False, 
						encoding='utf-8')

def playable_on_ytmusic(album_url):

	if 'browse' in album_url:
		browse_id = re.search(r".*browse\/(.*)", album_url).group(1)
	elif 'playlist' in album_url:
		url_fragment = re.search(r"list\=(.*?)(?=&|$)", album_url).group(1)
		browse_id = ytmusic.get_album_browse_id(url_fragment)

	results_dict = ytmusic.get_album(browse_id)

	total_duration = results_dict['duration_seconds']
	# print(total_duration)

	track_list = results_dict['tracks']
	playable_duration = 0
	for track in track_list:
		if track['isAvailable']:
			track_duration = track['duration_seconds']
			playable_duration += track_duration
	# print(playable_duration)

	if playable_duration/total_duration >= 0.95:
		return True
	else:
		return False


def get_artist_title_ytmusic(album_url, genre):

	if 'browse' in album_url:
		browse_id = re.search(r".*browse\/(.*)", album_url).group(1)
	elif 'playlist' in album_url:
		url_fragment = re.search(r"list\=(.*?)(?=&|$)", album_url).group(1)
		browse_id = ytmusic.get_album_browse_id(url_fragment)

	results_dict = ytmusic.get_album(browse_id)

	title = results_dict['title']
	artist_name_list = [artistx['name'] for artistx in results_dict['artists']]
	artist = ', '.join(artist_name_list)
	return [artist, title]



# function below of no use, youtube music doesnt display copyright info anywhere 

# def get_label_copyright_ytmusic(album_url):

# 	if 'browse' in album_url:
# 		browse_id = re.search(r".*browse\/(.*)", album_url).group(1)
# 	elif 'playlist' in album_url:
# 		url_fragment = re.search(r"list\=(.*?)(?=&|$)", album_url).group(1)
# 		browse_id = ytmusic.get_album_browse_id(url_fragment)

# 	results_dict = ytmusic.get_album(browse_id)

# 	label = ''

# 	phono_copyright = ''

# 	listx = [label, phono_copyright]
# 	return listx

def get_activity_tracks_ytmusic(album_url):

	if 'browse' in album_url:
		browse_id = re.search(r".*browse\/(.*)", album_url).group(1)
	elif 'playlist' in album_url:
		url_fragment = re.search(r"list\=(.*?)(?=&|$)", album_url).group(1)
		browse_id = ytmusic.get_album_browse_id(url_fragment)

	results_dict = ytmusic.get_album(browse_id)

	tracks_count = results_dict['trackCount']

	track_list = results_dict['tracks']
	tracks_count_playable = 0
	for track in track_list:
		if track['isAvailable']:
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
