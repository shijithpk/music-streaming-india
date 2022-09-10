### About the repo

This repo contains code for my analysis of how well streaming services in India cover western music. The report is available on [my blog](http://shijith.com/blog/2022-07-26-music-streaming-india/). 

The code here may not allow you to fully reproduce my results, because there were many manual steps in addition to all the work done programatically, but it should give anyone interested a glimpse of how I went about doing this project.

### The goal

The aim of the analysis was to find which streaming services cover western msuic best. To do this, we came up with a list of albums across several genres Pop, Rock etc. and tried to see which of these services have it in India. These lists cover alums that are seen as the best of all time in a particular genre according to critics. Acclaimed albums from the past 10 years were also taken. Then according to how many albums were available, each service was given a rating out of 10.

### The datasets 

The raw dataset XXGIVE INTERNAL LINKXX contains all the albums we were searching for, their genres as well as the time period (canon|contemporary) they represent.
The final dataset XXGIVE INTERNAL LINKXX gives all the album urls captured programatically and manually on different services that match our albums. 
Source_list XXGIVE INTERNAL LINKXX gives the website urls of all the album lists used from reputable music publications and websites.

### The code 

The script main.py XXGIVE INTERNAL LINKXX is the one that's run to search for albums. It corrals functions in the search_functions folder and runs them in parallel to do the job. For example, if you look at find_matches_spotify.py, there's the main function that searches for albums and stores them in a csv, there's one function that checks if an album is playable in India or not, 

 There are several other functions that are listed in the other_functions XXGIVE LINKXX folder. The search_functions folder XXGIVE LINKXX has the functions that query different music services and find matches for the albums in our dataset.

## How it all works 

Essentially, I run main.py . What this does first is go to the dataset XXLINK all_data_v14.csv XX , then for each album in the dataset tries o find matches across the services. It does this by running search functions like find_matches_amazon, find_matches_apple in parallel. 

It collects upto 5 matches for each album. (Collects multiple matches because our selection criteria are set loosely at first, to allow for the possibility of false positives. The title, artist and url of the album is stored.

Just to go deep into the details for a moment, an album is seen as a possible match if the words in our source album title and source artist name are a subset of the target album title and target artist name. So if we're searching for matches, for say, 'Ok Computer' by Radiohead and we come across an album "OK Computer OKNOTOK 1997 2017" by Radiohead on YouTube Music, that's seen as a possible match and stored.

Scores are then given to each of the 5 matches collected based on an algorithm called Generalised Jaccard XXGIVE LINK TO SLIDESHOW PDF EXACT PAGEXX. Basically, this looks not just at subset-iness, how many terms from our source string are there in target string, but also reduces the score for how many terms extra there are in the target string. The script GIVE_NAME XXX GIVE_LINK XX helps assign the generalised jaccard scores.

You could go by whichever album got the highest score according to the generalised jaccard algorithm and move on to the next step, but I chose to manually check them as well, by printing out the various matches with the help of the script XX GIVE NAME GIVE LINK XX and we then note the correct matches if any.

Also, for albums that haven't got any matches, you could do another round of searching on the various services. I also did one round where I looked at album matches given by Google with the help of XX GIVE SCRIPT NAME GIVE LINK SCRIPT. What happens is whey you search the name of an album and its artist in google, they have an info box on the side with links to the album on the various services. Some of these work, some of them don't, and many times in the case of apple link to the albums on the US website when they may not be available in India. Here again, links were stored and gone through manually to see if they were actual matches or not. 

Then based on how many albums in the dataset a service has got, we calculate ratings for each genre and overall ratings using the script calculate_scores.py XXGIVE LINKXX

I care about reproducibility of results, but unfortunately here, the final scores can't be reproduced by others because of how many rounds of searching i've done (upto 7) and the numerous manual interventions I've had to do/make/ALT. But hopefully making publicly available all the code I've used and being transparent about the various steps I've taken will allay/SIMPLER_CONVERSATIONAL_WORD concerns about the validity of the results.

One script online_check.py XXGIVE LINKXX was used to check which albums had at least 80% of their tracks playable. The problem with some of the albums is that because of some rights or legal issue, not all of the tracks would be playable, some would be grayed out. This script checks if at least 80% of the tracks on an album are playable, and if they aren't, it was marked as not available on a service and removed from the matches. Ideally, all tracks should be available, but 80% is an acceptable minimum threshold.

Other scripts like find_label_info, choose_rights_holder, guess_label_tieup are about trying to figure out which corporate music group holds the rights for an album.

Made use of copyright info that's displayed on each page and lists of subsidiaries available on the Universal, Sony Music websites etc. to come up with label_groupings.py XXGIVE LINKXX. This is then used by the find_rights_holder_v3.py XXGIVE LINK XX script to make a best effort guess. 

This then helps determine which of the majors -- Universal, Sony, Warner etc. -- a music service will have to make deals with, or expand existing deals, to improve their genre-wise and overall ratings, ie. their coverage of critically-acclaimed music.

### Suggestions, feedback
I'm not a professional developer, so am sure there are things here I should be doing differently. If you have any suggestions, please contact me on mail@shijith.com or my twitter handle [@shijith](https://twitter.com/shijith).  
