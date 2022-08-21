#!/usr/bin/python

from datetime import date, datetime
from thefuzz import fuzz
#not using older fuzzywuzzy
from itertools import combinations
from lxml import html as lxml_html
import json
import pandas as pd
import re 
import requests
import time
import unidecode
import urllib.parse
import math
from py_stringmatching import utils
from py_stringmatching import Levenshtein, GeneralizedJaccard,Jaro,JaroWinkler
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import logging
import logging.handlers
import configparser
from random import randint
import os
import numpy as np
import copy
import psutil
from lxml.html.soupparser import fromstring as soup_fromstring

service_list = ['amazon','apple','gaana','hungama','jiosaavn','spotify','wynk','ytmusic']

def time_sleep(n1,n2):
	'''
	makes program sleep for n seconds.
	n being any number from n1 to n2
	'''
	delay = randint(n1,n2)
	time.sleep(delay)

def tokenize(keywords):
	'''
	Takes a string of keywords, lower-cases every word,
	removes punctuation, ascii-fies all the letters,
	so no diacritics etc. 
	Returns a python list of all these words/tokens.
	Also removes 'various' and 'artists' from this list of tokens
	'''
	if (keywords == '') or (isinstance(keywords, float) and  math.isnan(keywords)):
		return []
	keywords = keywords.lower()
	keywords = keywords.replace("‘","'").replace("’","'")
	# line below is for removing punctuation, keeps single apostrophes and periods in 
	keywords = re.sub(r"[^\w\s.']", ' ', keywords)
	keywords = unidecode.unidecode(keywords)
	# dont have to worry about trimming leading and trailing space or
		# multiple spaces in a string. When you split, all that is taken care of
	keywords_list = keywords.split()
	# keeping in any keyword with 2 characters or more
		# NOPE. decided to keep in single character keywords too
	# keywords_list = [keywordx for keywordx in keywords_list 
	# 								if len(keywordx) >= 2]
	# sort list by keyword length, longest keyword comes first
	for tokenx in ['various','artists']:
		while tokenx in keywords_list:
			keywords_list.remove(tokenx)

	return keywords_list

def create_list_queries(title,artist):
	'''
	Takes title of album and name of artists, creates a list of	queries. 
	The title & artist name are transformed, they're ascii-fied, lowercased etc.
	This then becomes a list of keywords.
	The function returns a list of combinations of these keywords. 
	The first combination will have all the keywords.
	The combinations after that will have all the keywords but one, and so on
	This is fed into a service one after the other to find a specific album.
	'''
	keywords = artist + ' ' + title
	keywords_list = tokenize(keywords)
	string_combos = [keywords_list]
	keywords_list_sorted = sorted(keywords_list, key=len,reverse=True)
	
	len_keywords_list_sorted = len(keywords_list_sorted)
	#if no result at first, use combinations of keywords
		#these combinations come after query containing all keywords
		#a combination will have at least 3 keywords
		
	if len_keywords_list_sorted >= 4:
		string_combos_additional = list(combinations(keywords_list_sorted,
		(len_keywords_list_sorted - 1)))
		string_combos.extend(string_combos_additional)

	if len_keywords_list_sorted >= 5:
		string_combos_additional_2 = \
		list(combinations(keywords_list_sorted, 
						(len_keywords_list_sorted - 2)))
		string_combos.extend(string_combos_additional_2)

	# DO I NEED THE SET OF COMBOS BELOW? CREATES TOO MANY QUERIES TO GO THROUGH
	# 	i think once we reach this point, we know a particular album isnt there.
	if len_keywords_list_sorted >= 6:
		string_combos_additional_3 =\
		list(combinations(keywords_list_sorted, 
						(len_keywords_list_sorted - 3)))
		string_combos.extend(string_combos_additional_3)

	return string_combos

def get_elkan_score(source_string, target_string):
	'''
	Takes a source string and target string, creates two bags (python lists) of 
	tokens from them, and returns a value from 0-100 for how similar they are.
	The higher the value, the more similar.

	Here I'm just modifying the code from the py_stringmatching package.
	Specifically the code from their implementation of the monge-elkan measure.
	https://github.com/anhaidgroup/py_stringmatching/blob/master/py_stringmatching/similarity_measure/monge_elkan.py
	'''

	lev = Levenshtein()
	bag1 = tokenize(source_string)
	bag2 = tokenize(target_string)

	# input validations
	utils.sim_check_for_none(bag1, bag2)
	utils.sim_check_for_list_or_set_inputs(bag1, bag2)

	# if exact match return 100
	if utils.sim_check_for_exact_match(bag1, bag2):
		return 100

	# if one of the strings is empty return 0
	if utils.sim_check_for_empty(bag1, bag2):
		return 0

	# aggregated sum of all the max sim score of all the elements in bag1
	# with elements in bag2
	sum_of_maxes = 0
	for el1 in bag1:
		max_sim = float('-inf')
		for el2 in bag2:
			max_sim = max(max_sim, lev.get_sim_score(el1, el2))
		sum_of_maxes += max_sim
	elkan_score = (float(sum_of_maxes) / float(len(bag1)))*100
	return elkan_score

def get_elkan_score_jaro(source_string, target_string):

	jaro = Jaro()
	bag1 = tokenize(source_string)
	bag2 = tokenize(target_string)

	# input validations
	utils.sim_check_for_none(bag1, bag2)
	utils.sim_check_for_list_or_set_inputs(bag1, bag2)

	# if exact match return 100
	if utils.sim_check_for_exact_match(bag1, bag2):
		return 100

	# if one of the strings is empty return 0
	if utils.sim_check_for_empty(bag1, bag2):
		return 0

	# aggregated sum of all the max sim score of all the elements in bag1
	# with elements in bag2
	sum_of_maxes = 0
	for el1 in bag1:
		max_sim = float('-inf')
		for el2 in bag2:
			max_sim = max(max_sim, jaro.get_sim_score(el1, el2))
		sum_of_maxes += max_sim
	elkan_score = (float(sum_of_maxes) / float(len(bag1)))*100
	return elkan_score

def get_elkan_score_jarowink(source_string, target_string):
	'''
	Takes a source string and target string, creates two bags (python lists) of 
	tokens from them, and returns a value from 0-100 for how similar they are.
	The higher the value, the more similar.

	Here I'm just modifying the code from the py_stringmatching package.
	Specifically the code from their implementation of the monge-elkan measure.
	https://github.com/anhaidgroup/py_stringmatching/blob/master/py_stringmatching/similarity_measure/monge_elkan.py

	Here the sim_func is jarowink instead of levenshtein as in get_elkan_score
	'''	

	jarowink = JaroWinkler()
	bag1 = tokenize(source_string)
	bag2 = tokenize(target_string)

	# input validations
	utils.sim_check_for_none(bag1, bag2)
	utils.sim_check_for_list_or_set_inputs(bag1, bag2)

	# if exact match return 100
	if utils.sim_check_for_exact_match(bag1, bag2):
		return 100

	# if one of the strings is empty return 0
	if utils.sim_check_for_empty(bag1, bag2):
		return 0

	# aggregated sum of all the max sim score of all the elements in bag1
	# with elements in bag2
	sum_of_maxes = 0
	for el1 in bag1:
		max_sim = float('-inf')
		for el2 in bag2:
			max_sim = max(max_sim, jarowink.get_sim_score(el1, el2))
		sum_of_maxes += max_sim
	elkan_score = (float(sum_of_maxes) / float(len(bag1)))*100
	return elkan_score


def create_session():
	# code below from https://stackoverflow.com/questions/47675138/how-to-override-backoff-max-while-working-with-requests-retry/

	class RetryRequest(Retry):
		def __init__(self, backoff_max=Retry.BACKOFF_MAX, **kwargs):
			super().__init__(**kwargs)
			self.BACKOFF_MAX = backoff_max

		def new(self, **kwargs):
			return super().new(backoff_max=self.BACKOFF_MAX, **kwargs)

	# code below from https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/

	retry_strategy = RetryRequest(
		total = 3,
		read = 3,
		connect = 3,
		status = 3,
		redirect = 3,
		backoff_factor = 2,
		backoff_max = 7200,
		status_forcelist=[101, 104, 301, 404, 408, 413, 429, 500, 502, 503, 504],
	)

	DEFAULT_TIMEOUT = (5, 5) # tuple for connect and read timeout in seconds

	class TimeoutHTTPAdapter(HTTPAdapter):
		def __init__(self, *args, **kwargs):
			self.timeout = DEFAULT_TIMEOUT
			if "timeout" in kwargs:
				self.timeout = kwargs["timeout"]
				del kwargs["timeout"]
			super().__init__(*args, **kwargs)

		def send(self, request, **kwargs):
			timeout = kwargs.get("timeout")
			if timeout is None:
				kwargs["timeout"] = self.timeout
			return super().send(request, **kwargs)

	adapter = TimeoutHTTPAdapter(max_retries=retry_strategy, timeout=(10, 20))
	session = requests.Session()
	session.mount("https://", adapter)
	session.mount("http://", adapter)

	return session


def create_logger():
	'''
	creates a logger that extracts any error message and sends it in an email
	'''
	logger = logging.getLogger()
	# below is just code to send me an email if the script run fails for any reason
	config_email = configparser.ConfigParser()
	config_email.read('creds_headers/config_email.ini')
	receiver_email = config_email['info']['email'] 
	sender_email = config_email['info']['sender_email']
	sender_password = config_email['info']['sender_password'] 
	time_now = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
	subjectx = time_now + " Error: music service search"
	smtp_handler = logging.handlers.SMTPHandler(
							mailhost=("smtp.gmail.com", 587),
							fromaddr=sender_email, 
							toaddrs=receiver_email,
							subject=subjectx,
							credentials=(sender_email, sender_password),
							secure=()
							)
	logger.addHandler(smtp_handler)
	return logger


def check_subset(string1,string2):
	'''
	Takes two strings string1 and string2\n
	Checks if the words from string1 are in string2 or vice versa\n
	That is, if either is a subset of the other.\n
	It does this by tokenizing the two strings into python lists\n
	Uses set operations to see if all elements from one list are in the other\n
	The words will exclude 'various' and 'artists'\n
	Returns a boolean value True or False\n
	'''
	string1_list = tokenize(string1)
	string2_list = tokenize(string2)
	if((set(string1_list).issubset(set(string2_list))) or
		(set(string2_list).issubset(set(string1_list)))):
		return True
	else:
		return False

def get_genjacc_score(source_string, target_string):
	'''
	Takes a source string and target string, creates two bags (python lists) of 
	tokens from them, and returns a value from 0-100 for how similar they are.
	The higher the value, the more similar.

	Here i'm using something called generalized jaccard algorithm. The more words
	or tokens that the two strings DON'T have in common, the lower the score.

	So this is different from elkan_score which was just looking at 'subset-iness'
	'''

	bag1 = tokenize(source_string)
	bag2_raw = tokenize(target_string)

	redundant_words_list = ["edition","deluxe","version","anniversary",
		"remastered","remaster","expanded","bonus","track","international",
		"reissue","explicit","collector's","extended","ultimate","special",
		"legacy","studio","essential","original","supreme","complete","super",
		"tracks","re-issue",]

	bag2 = [x for x in bag2_raw if x not in redundant_words_list]

	gj = GeneralizedJaccard(sim_func=Levenshtein().get_sim_score, threshold=0.0)
	genjacc_score = gj.get_sim_score(bag1, bag2) * 100

	return genjacc_score

def get_genjacc_score_jarowink(source_string, target_string):
	'''
	Takes a source string and target string, creates two bags (python lists) of 
	tokens from them, and returns a value from 0-100 for how similar they are.
	The higher the value, the more similar.

	Here i'm using something called generalized jaccard algorithm. The more words
	or tokens that the two strings DON'T have in common, the lower the score.

	So this is different from elkan_score which was just looking at 'subset-iness'

	Here the sim_func is jarowink instead of levenshtein
	'''

	bag1 = tokenize(source_string)
	bag2_raw = tokenize(target_string)

	redundant_words_list = ["edition","deluxe","version","anniversary",
		"remastered","remaster","expanded","bonus","track","international",
		"reissue","explicit","collector's","extended","ultimate","special",
		"legacy","studio","essential","original","supreme","complete","super",
		"tracks","re-issue",]

	bag2 = [x for x in bag2_raw if x not in redundant_words_list]

	gj = GeneralizedJaccard(sim_func=JaroWinkler().get_sim_score, threshold=0.0)
	genjacc_score = gj.get_sim_score(bag1, bag2) * 100

	return genjacc_score


def merge_round_csvs(service_list):
	'''
	Merges csvs from round 1 with those from round 2.
	In round 1, we tried to get matches for all albums
	In round 2, we focused on the albums without any matches in round 1
	The merged CSVs are saved as matches_<service>_round_02_merged.csv
	'''
	for service in service_list:
		round_01_csv_path = 'data/round_01/matches_' + service + '_round_01.csv'
		round_01_df = pd.read_csv(round_01_csv_path, dtype = str, 
							index_col='index')
		title_col_name = 'match_title_' + service + '_1'
		round_01_df_matched = round_01_df[round_01_df[title_col_name].notnull()]

		round_02_culled_csv_path = 'data/round_02/matches_' + service +\
									 '_round_02_culled.csv'
		round_02_culled_df = pd.read_csv(round_02_culled_csv_path, dtype = str, 
							index_col='index')
		round_02_merged_df = pd.concat([round_01_df_matched,
										round_02_culled_df],
										axis=0)
		round_02_merged_csv_path = 'data/round_02/matches_' + service +\
									 '_round_02_merged.csv'
		round_02_merged_df.to_csv(round_02_merged_csv_path, encoding='utf-8')


def merge_service_csvs():
	'''
	Takes CSVs with the suffix round_nn from folder round_nn and merges them.
	Each CSV is the result of a search for matches on a particular music service
	All these CSVs are merged with the all_data file
	Then saves everthing as merged_csv_name
	'''
	
	all_data_csv_path = 'data/all_data_v09.csv'
	albums_df = pd.read_csv(all_data_csv_path, dtype = str, index_col='index')

	for service in service_list:
		service_csv_path = 'data/round_02/matches_' + service + '_' +\
							'round_02_merged.csv'
		service_df = pd.read_csv(service_csv_path, dtype = str, 
								index_col='index')
		service_df.drop(labels=['year','title','artist','source','canon_contemp',
						'genre','list_name'], axis=1, inplace=True)
		albums_df = albums_df.join(service_df)

	merged_csv_path = 'data/round_02_all.csv'
	albums_df.to_csv(merged_csv_path, encoding='utf-8')


def insert_genjacc_score_columns():
	'''
	Makes a dataframe out of merged_csv_name\n
	Goes through each service, and each match\n
	Finds out what the generalized jaccard score is for the match's artist and 
	title combined\n
	Inserts a column with that score into the dataframe\n
	Then saves everything as csv_with_scores_name
	'''
	# NEED TO EXCLUDE WORDS LIkE DELUXE, REMASTER, REISSUE ETC. 
	merged_csv_path = 'data/round_02_all.csv'
	merged_df = pd.read_csv(merged_csv_path, dtype = str, 
								index_col='index')

	for index,row in merged_df.iterrows():
		source_title = row['title']
		source_artist = row['artist']
		source_artist_title_combined = source_artist + source_title
		for service in service_list:
			for match_num in ['1','2','3']:
				target_artist_col_name = 'match_artist_' + service + '_' +\
										match_num
				target_title_col_name = 'match_title_' + service + '_' +\
										match_num
				target_artist = row[target_artist_col_name]
				target_title = row[target_title_col_name]
				#if a NaN value, break loop
				if ((isinstance(target_title, float) and  math.isnan(target_title)) or\
				(isinstance(target_artist, float) and  math.isnan(target_artist))):
					break
				target_artist_title_combined = target_artist + target_title
				#below we get the similiarity score acc to an algo called 
					# generalized jaccard
				score_raw = get_genjacc_score_jarowink(source_artist_title_combined,
										target_artist_title_combined)
				score = round(score_raw,1)
				score_col_name = 'genjacc_score_' + service + '_match_' + str(match_num)
				merged_df.loc[index, score_col_name] = score

	csv_with_scores_path = 'data/round_02_all_with_genjacc_scores.csv'
	merged_df.to_csv(csv_with_scores_path, encoding='utf-8')	


def insert_tokenset_score_columns():
	'''
	Makes a dataframe out of merged_csv_name\n
	Goes through each service, and each match\n
	Finds out what the fuzzywuzzy token set score is for the match's artist and 
	title combined\n
	Inserts a column with that score into the dataframe\n
	Then saves everything as csv_with_scores_name
	'''
	merged_csv_path = 'data/round_02_all_with_genjacc_scores.csv'
	merged_df = pd.read_csv(merged_csv_path, dtype = str, 
								index_col='index')

	for index,row in merged_df.iterrows():
		source_title = row['title']
		source_artist = row['artist']
		source_artist_title_combined = source_artist + source_title
		for service in service_list:
			for match_num in ['1','2','3']:
				target_artist_col_name = 'match_artist_' + service + '_' +\
										match_num
				target_title_col_name = 'match_title_' + service + '_' +\
										match_num
				target_artist = row[target_artist_col_name]
				target_title = row[target_title_col_name]
				if ((isinstance(target_title, float) and  math.isnan(target_title)) or\
				(isinstance(target_artist, float) and  math.isnan(target_artist))):
					break
				target_artist_title_combined = target_artist + target_title
				#below we get the similiarity score acc to a 
					# method in fuzzywuzzy -- token_set_ratio 
				score_raw = fuzz.token_set_ratio(source_artist_title_combined,
										target_artist_title_combined)
				score = round(score_raw,1)
				score_col_name = 'tokenset_score_' + service + '_match_' + str(match_num)
				merged_df.loc[index, score_col_name] = score

	csv_with_scores_path = 'data/round_02_all_with_tokenset_scores.csv'
	merged_df.to_csv(csv_with_scores_path, encoding='utf-8')	


def create_txt_false_positive_check(print_filename):
	print_filepath = 'data/' + print_filename
	if os.path.exists(print_filepath):
		os.remove(print_filepath)
	f = open(print_filepath,'a')

	service_list = ['amazon','apple','gaana',
					'hungama',
					'jiosaavn','spotify','wynk','ytmusic']

	scores_csv_path = 'data/round_02_all_with_tokenset_scores.csv'
	scores_df = pd.read_csv(scores_csv_path, dtype = str, index_col='index')
	for index,row in scores_df.iterrows():
		source_artist = row['artist']
		source_title = row['title']
		statement_A = '\n' +\
			'INDEX_NUMBER: ' + str(index) + '\n' +\
			'SOURCE_TITLE: ' + source_title + ' * SOURCE_ARTIST: ' + source_artist
		print(statement_A, file=f)
		for service in service_list:
			statement_B =  '\n' +\
					'	SERVICE: ' + service
			print(statement_B, file=f)
			for match_num in ['1','2','3']:
				target_title_col_name = 'match_title_' + service + '_' +\
										match_num
				target_artist_col_name = 'match_artist_' + service + '_' +\
										match_num
				target_title = row[target_title_col_name]
				target_artist = row[target_artist_col_name]
				
				if ((isinstance(target_title, float) and  math.isnan(target_title)) or\
					(isinstance(target_artist, float) and  math.isnan(target_artist))):
					break
					# target_title = 'nan'
					# target_artist = 'nan'
				genjacc_score_col_name = 'genjacc_score_' + service + '_match_' + match_num
				tokenset_score_col_name = 'tokenset_score_' + service + '_match_' + match_num
				genjacc_score = row[genjacc_score_col_name]
				tokenset_score = row[tokenset_score_col_name]
				statement_C = '\n' +\
					'		MATCH_NUM: ' + match_num + '\n' +\
					'		TARGET_TITLE: ' + target_title + ' * TARGET_ARTIST: ' + target_artist + '\n' +\
					'		GENJACC_SCORE: ' + str(genjacc_score) + ' * TOKENSET_SCORE: ' + str(tokenset_score)
				print(statement_C, file=f)


def create_csvs_manual_correction():

	scores_csv_path = 'data/round_02_all_with_tokenset_scores.csv'
	scores_df = pd.read_csv(scores_csv_path, dtype = str, index_col='index')

	df_for_saving_all_columns = copy.deepcopy(scores_df)
	df_for_saving = df_for_saving_all_columns[['title', 'artist']]

	for index,row in scores_df.iterrows():
		source_artist = row['artist']
		source_title = row['title']
		for service in service_list:
			highest_genjacc_score = 0
			df_for_saving.loc[index, service] = np.nan
			for match_num in ['1','2','3']:
				target_title_col_name = 'match_title_' + service + '_' +\
										match_num
				target_artist_col_name = 'match_artist_' + service + '_' +\
										match_num
				target_title = row[target_title_col_name]
				target_artist = row[target_artist_col_name]

				if ((isinstance(target_title, float) and math.isnan(target_title)) or\
					(isinstance(target_artist, float) and math.isnan(target_artist))):
					break
				genjacc_score_col_name = 'genjacc_score_' + service + '_match_' + match_num
				# tokenset_score_col_name = 'tokenset_score_' + service + '_match_' + match_num
				genjacc_score_raw = row[genjacc_score_col_name]
				genjacc_score = float(genjacc_score_raw)
				# tokenset_score_raw = row[tokenset_score_col_name]
				# tokenset_score = float(tokenset_score_raw)
				if genjacc_score > highest_genjacc_score:
					highest_genjacc_score = genjacc_score
					df_for_saving.loc[index, service] = match_num

	filepath_original = 'data/matches_original.csv'
	df_for_saving.to_csv(filepath_original, encoding='utf-8')

	filepath_corrected = 'data/matches_corrected.csv'	
	df_for_saving.to_csv(filepath_corrected, encoding='utf-8')

def create_session_hungama():
	# code below from https://stackoverflow.com/questions/47675138/how-to-override-backoff-max-while-working-with-requests-retry/

	class RetryRequest(Retry):
		def __init__(self, backoff_max=Retry.BACKOFF_MAX, **kwargs):
			super().__init__(**kwargs)
			self.BACKOFF_MAX = backoff_max

		def new(self, **kwargs):
			return super().new(backoff_max=self.BACKOFF_MAX, **kwargs)

	# code below from https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/

	retry_strategy = RetryRequest(
		total = 3,
		read = 3,
		connect = 3,
		status = 3,
		redirect = 3,
		backoff_factor = 2,
		backoff_max = 7200,
		status_forcelist=[101, 104, 301, 404, 408, 413, 429, 500, 502, 503, 504],
	)

	DEFAULT_TIMEOUT = 10

	class TimeoutHTTPAdapter(HTTPAdapter):
		def __init__(self, *args, **kwargs):
			self.timeout = DEFAULT_TIMEOUT
			if "timeout" in kwargs:
				self.timeout = kwargs["timeout"]
				del kwargs["timeout"]
			super().__init__(*args, **kwargs)

		def send(self, request, **kwargs):
			timeout = kwargs.get("timeout")
			if timeout is None:
				kwargs["timeout"] = self.timeout
			return super().send(request, **kwargs)

	adapter = TimeoutHTTPAdapter(max_retries=retry_strategy, timeout=10)
	session = requests.Session()
	session.mount("https://", adapter)
	session.mount("http://", adapter)

	return session

# code from https://stackoverflow.com/a/63738197/6403539
def get_pids_by_script_name(script_name):

	pids = []
	for proc in psutil.process_iter():

		try:
			cmdline = proc.cmdline()
			pid = proc.pid
		except psutil.NoSuchProcess:
			continue

		if ((len(cmdline) >= 2)
			and ('python3' in cmdline[0])
			and (script_name in cmdline[1])):

			pids.append(pid)

	return pids