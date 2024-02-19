#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: paula
"""
import spacy
import heapq
import requests, re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from operator import itemgetter
from config import API_KEY as API_KEY
# Load the spaCy English model 
nlp = spacy.load("en_core_web_lg")


'''


~.~.~.~.~.~.~.~.~.~.~.~.~.~.~. GET MOVIE INFO ~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.



'''
headers = {
    "Authorization": "Bearer " + API_KEY
}

def get_movie_id(title): #return movie id
    response =  requests.get("https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&query="+title, headers=headers)
    if response.status_code==200: 
        array = response.json()
        print([(arr["original_title"], arr["release_date"]) for arr in array["results"]])
        selection = int(input("Make Selection: "))
        movie_id = array["results"][selection]["id"]
        
        return movie_id
        
    else: raise(Exception("Not valid"))

def get_synopsis(movie_id): #return movie synopsis
    response = requests.get("https://api.themoviedb.org/3/movie/"+str(movie_id), headers=headers)
    
    if response.status_code==200: 
        array = response.json()
        return array["overview"]
        
    else: raise(Exception("Not valid"))

def get_genres(movie_id): #return movie genres as a list of dics:[{id: genre}...]
    response = requests.get("https://api.themoviedb.org/3/movie/"+str(movie_id), headers=headers)
    
    if response.status_code==200: 
        array = response.json()
        return array["genres"]
        
    else: raise(Exception("Not valid"))

def get_keywords(movie_id): #return up to 8 of a movie's relevant keywords as a list of dics:[{id: keywords}...]
    response = requests.get("https://api.themoviedb.org/3/movie/"+str(movie_id)+"/keywords", headers=headers)
    if response.status_code==200: 
        array = response.json()
        
        return array["keywords"][:8]
        
    else: raise(Exception("Not valid"))

def get_actors(movie_id): #return up to 6 of a movie's cast members as a list of dics:[{id: actors}...]
    response = requests.get("https://api.themoviedb.org/3/movie/"+str(movie_id)+"/credits", headers=headers)
    if response.status_code==200: 
        array = response.json()
        mini = min(len(array["cast"]), 6)
        return [{"id":array["cast"][i]["id"], "actor":array["cast"][i]["name"]} for i in range(mini)]

        
    else: raise(Exception("Not valid"))

def get_lang(movie_id): #return original language of movie. needed for bollywood as a string
    response = requests.get("https://api.themoviedb.org/3/movie/"+str(movie_id), headers=headers)
    
    if response.status_code==200: 
        array = response.json()
        return array["original_language"]
        
    else: raise(Exception("Not valid"))
    
    
def get_keyword_ids(keywords): #when given a list of keywords, converts those keywords to a list of ids
    keyword_ids = []
    for keyword in keywords:
        response =  requests.get("https://api.themoviedb.org/3/search/keyword?query="+keyword, headers=headers)
        if response.status_code==200: 
            array = response.json()
            for result in array["results"]:
                if result["name"] == keyword.lower():
                    keyword_ids.append(str(result["id"]))
                    continue
            
    return keyword_ids

def get_id_list(detailed_list): #convert list of dics into just list of ids
    return [str(arr["id"]) for arr in detailed_list]




















'''


~.~.~.~.~.~.~.~.~.~.~.~.~.~.~. FILTER MOVIES ~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.



'''




def filter_relevant_movies(genre_id, main_keyword, key): #main function to "discover" movies. returns a list of up to 40 movies that fit in a given criteria
    movies = []
    
    urls = []
    genres = '%2C'.join(genre_id)
    if key == "actor":
        actors = '%7C'.join(main_keyword)
        url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page={1}&sort_by=popularity.desc&with_cast="+actors+"&with_genres="+genres
    elif key == "bollywood":
        url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page={1}&sort_by=popularity.desc&with_genres="+genres+"&with_original_language=te"
        urls.append(url)
        url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page={1}&sort_by=popularity.desc&with_genres="+genres+"&with_original_language=hi"
        
    elif key == "period" or key == "location":
        timeorloc = '%7C'.join(main_keyword)
        url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page={1}&sort_by=popularity.desc&with_genres="+genres+"&with_keywords="+timeorloc
    else:
        keywords = '%7C'.join(main_keyword)
        url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page={1}&sort_by=popularity.desc&with_genres="+genres+"&with_keywords="+keywords

    urls.append(url)

    for url in urls:
        for page in range(1, 11):
            response = requests.get(url.format(url, page), headers=headers)
            if response.status_code==200:
                array = response.json()
                if page > array["total_pages"]:break
                for result in array["results"]:
                    movies.append((result["id"], result["title"], result["overview"]))
                
            
            else: raise(Exception("Not valid"))
            
    if not movies:
        url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page={1}&sort_by=vote_count.desc&with_genres="+genres
        for page in range(1, 11):
            response = requests.get(url.format(url, page), headers=headers)
            if response.status_code==200:
                array = response.json()
                if page > array["total_pages"]:break
                for result in array["results"]:
                    movies.append((result["id"], result["title"], result["overview"]))
                
            
            else: raise(Exception("Not valid"))
        
    return movies
            
   
    
def get_movies(criteria, genre, actors, period, location, keyword): #determine what criteria to get movies based on (i.e. movies with  the same actors? in same lang? same time period?...) then get those movies
    if criteria == "actor":
        main_keyword = actors
    elif criteria == "bollywood":
        main_keyword = "hi"
    elif criteria == "period":
        main_keyword = period
    elif criteria == "location":
        main_keyword = location
    else:
        main_keyword = keyword
    
    movies = filter_relevant_movies(genre, main_keyword, criteria)
    
    return movies

def determine_match_type(movie1_details, movie2_details): #determine what similarities the two movies have in common
    movie1Lang, movie1Actors, movie1Period, movie1Location  = movie1_details
    movie2Lang, movie2Actors, movie2Period, movie2Location  = movie2_details
    
    m1time = generalize_time_period(movie1Period)
    m2time = generalize_time_period(movie2Period)
    
    m1loc = generalize_location(movie1Location)
    m2loc = generalize_location(movie2Location)
    
    if set(movie1Actors).intersection(set(movie2Actors)):
        return "actor", False, False
    elif movie1Lang == "te" or movie1Lang == "hi"or movie2Lang == "hi" or movie2Lang == "te":
        return "bollywood", False, False
    elif m1time == m2time:
        return "period", m1time, False
    elif m1loc == m2loc:
        return "location", False, m1loc
    else:
        return False, False, False
    
def  merge_movies(movie1_details, movie2_details): #return the common genre between two movies and if possible, their common actors, or time periods, or location
    movie1Genres, movie1Actors, movie1Period, movie1Location  = movie1_details
    movie2Genres, movie2Actors, movie2Period, movie2Location = movie2_details
    
    genres = set(movie1Genres).intersection(set(movie2Genres))
    actors = set(movie1Actors).intersection(set(movie2Actors))
    period = ""
    location = ""
    
    if not genres:
        genres = [movie1Genres[0], movie2Genres[0]]

        
    if movie1Period and movie2Period:
        period = movie1Period if movie1Period==movie2Period else ""
    
    if movie1Location and movie2Location:
        location = movie1Location if movie1Location==movie2Location else ""
    
    
    
    return genres, actors, period, location
    
    
def generalize_time_period(periods): #generalize a time period. ie, 90s=1990s, 2004=y2k...
    if "years" in periods or "weekend" in periods or "days" in periods or "weekends" in periods or "days" in periods:
        return []
    
    year_matches = re.findall(r'\b\d{4}s?\b', periods)
    decade_matches = re.findall(r'\b\d{2}s?\b', periods)
    
    
    for year in year_matches:
        if year[-1] == "s":year = year[:-1]
        if int(year) >= 1000 and int(year) <= 2100:
            if year[:2] == "19":
                return [year[2] +"0s", year, year[2] +"0's", year+"s"]
            if year[:3] == "200":
                return ["2000s", "Y2K", "y2k"]
            else: return [year]
            
    for decade in decade_matches:
        if int(decade[:-1]) >= 10 and int(decade[:-1]) <= 90 and (decade[-2]) == "0":
            return [decade, "19"+decade[:-1]]
    
    return [periods]
    

def generalize_location(location): #generalize location, ie. atlanta = southern...
    nyc = ["nyc", "new york city", "brooklyn", "manhattan", "queens", "staten island", "long island", "bronx", "the bronx", "ny city", "lower east side", "upper west side", "harlem", "new york"]
    southern = ["georgia", "texas", "tennessee", "alabama", "west virgina", "louisiana", "new orleans"]
    if location.lower() in nyc:
        return ["nyc", location, "new york", "new york city"]
    if location.lower() in southern:
        return ["south", "southern", location]
    
    return location 

def filter_context(movie1Keys, movie2Keys): #given a dic of plot tags and their frequencies, return common plot tags. bonus: main keyword for prior discover implentation
    ands = set(movie1Keys).intersection(set(movie2Keys))
    ors = []
    
    ors += [k for k,v in movie1Keys.items() if v > 1]
    ors += [k for k,v in movie2Keys.items() if v > 1]
    
    top_keyword = None
    keyword_weight = 0
    for k,v in movie1Keys.items():
        if k in movie2Keys and v + movie2Keys[k] > keyword_weight:
            top_keyword, keyword_weight = k, v + movie2Keys[k]
            
    if top_keyword is None:
        top_keyword = [max(movie1Keys, key=movie1Keys.get), max(movie2Keys, key=movie2Keys.get)]
    
    return top_keyword, set(ors).union(ands)


def get_movies_with_closest_plots(movies, keywords, movie1id, movie2id): #return discovered movies with similar plots to target movies
    moviesAndKeys = {}
    
    for movie in movies:
        movieId = movie[0]
        if movieId == movie1id or movieId == movie2id:
            continue
        
        movie_keys = get_keywords(movieId)
        key_lists = get_id_list(movie_keys)
        moviesAndKeys[movie[1]] = (len(set(key_lists).intersection(keywords)), movieId)
    
    movie_similarity = heapq.nlargest(15, moviesAndKeys.items(), key=itemgetter(1))

    return movie_similarity
    



    











'''


~.~.~.~.~.~.~.~.~.~.~.~.~.~.~. ANALYZE MOVIE ~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.



'''


def perform_contextual_analysis(sentence): #returns related plots after performing contextual analysis and locations and time periods if any found.
    # Tokenization and parsing
    doc = nlp(sentence)
    
    tokens = []
    for token in doc:
        if token.pos_ == "NOUN" or token.pos_ == "VERB":
            tokens.append(token.text)
            
    
    
    time_period = ""
    location = ""
    for ent in doc.ents:
        if ent.label_ == "DATE": time_period = ent.text 
        if ent.label_ == "GPE":  location = ent.text
    
    return ((nearest_plot(tokens)), time_period, location)

def nearest_plot(nouns): #the meat! using cosine sim, find the closest matching word in the given plot list
    plot_list = ["uncover", "undercover", "rivalry", "vampire", "revenge", "violence", "workplace", "terrorism", "school", "supernatural", "government", "conspiracy", "outerspace", "afresh", "resistance", "psyche", "oddball", "infidelity", "patrolman", "legal", "psychological", "obsession", "rescue", "killer", "erotic", "ambition", "friendship", "superhero", "americana", "animal", "music", "showbiz", "athlete", "pursuit", "deceit", "antihero", "creature", "cataclysm", "dysfunctional", "family", "feminism", "romance", "resilient", "adolescence", "zombie"]
    plot_freq = {} #track the most common associated plot based on each word
    
    for noun in nouns:
        similarity_scores = []
        noun = nlp(noun)
        
        #calculate similarity scores for each plot word and synopsis word
        for plot in plot_list:
            plot = nlp(plot)
            similarity = noun.similarity(plot)
            similarity_scores.append((similarity*-1, plot.text))
        heapq.heapify(similarity_scores)
        
        #get top 3 plot words for each synopsis word
        for _ in range(3):
            count = 1
            score, p = heapq.heappop(similarity_scores)
            if score*-1 >= 0.89:
                count = 100
            plot_freq[p] = plot_freq.get(p, 0)+count

    return ([plot for plot,freq in plot_freq.items() if freq > 1], plot_freq)


def analyze_sentiment_vader(text): #sentiment analysis

    analyzer = SentimentIntensityAnalyzer()
    
    sentiment_score = analyzer.polarity_scores(text)
    return sentiment_score["compound"]


def rank_movies(simMovies, combinedMoods): #this is where mood algo comes in. with all the movies in the list, rank them based on which has the closest mood to the given movies
    
    sentiment_scores = {}
    
    for name, info in simMovies:
        simscore, movieid = info[0], info[1]
        
        synopsis = get_synopsis(movieid)
        score = analyze_sentiment_vader(synopsis)
        sentiment_scores[(name, movieid)] = abs(max(combinedMoods, score) - min(combinedMoods, score))
    
    
    return sentiment_scores
        










'''


~.~.~.~.~.~.~.~.~.~.~.~.~.~.~. RUNN ~.~.~.~.~.~.~.~.~.~.~.~.~.~.~.



'''

'''
Example ids for testing:
    
331482 (Little Women)
391713 (lady Bird)

'''
def main(movie1_id, movie2_id, movie1Title=None, movie2Title=None):
    '''
    # maps each plot tag to relevant tmdb keyword ids
    plot_to_key_ids = {'uncover': ['207108'], 'undercover': ['1568', '163589', '269652', '4654', '11199'], 'rivalry': ['9823', '255190', '232700', '189964', '4516', '11157', '297542', '320822'], 'vampire': ['3133',  '317770'], 'revenge': ['9748', '295222', '15095',  '197088'], 'violence': ['312898'], 'workplace': ['6282', '261286'], 'terrorism': ['13015', '41501', '225136', '218122', '252593', '160914', '232675', '298592', '322590', '326962'], 'teacher': ['10508', '193547'], 'supernatural': ['6152', '250461', '68646', '251513', '196975'], 'government': ['6086', '181635'], 'social': ['229296','220993',], 'outer space': ['252634', '9882', '273493', '313071', '4270'], 'afresh': ['2062', '208476', '230574'], 'resistance': ['836', '171051'], 'psyche': ['244078', '297549', '243090', '298773'], 'oddball': ['2794', '280791'], 'infidelity': ['1326'], 'police': ['6149', '193264', '193309', '237369', '5430', '238359', '279544', '280146', '15321', '250091', '214799', '155446', '155531', '155546', '215882', '155715', '217474', '217476', '251963', '161249','163081'], 'legal': ['298545', '10909', '33519','300847', '33518', '155873'], 'psychological': ['272553', '224845', '260030', '2629', '235847', '12565', '236653', '237735', '199079', '9332', '258549', '288859', '295907', '301541', '304017', '304276', '304998', '309029', '311371', '316790'], 'obsession': ['1523', '10333'], 'rescue': ['10084', '206692', '196899', '193544', '299714'], 'killer': ['15127', '193021', '175388', '175593', '227428', '288238', '10714'], 'ambition': ['3734'], 'friendship': ['6054', '5248', '197194', '213873', '165583', '223612', '257090', '257890', '258197', '3230', '236626', '7508', '282941', '220669', '166623', '167982', '187214', '292334', '310034', '318505'], 'heroes': ['1701', '225679', '193545', '252030', '285081', '221871', '266233', '292834', '292835', '206701', '206702', '246087', '290907', '312742', '318140',], 'americana': ['165508', '305941', '155291'], 'animal': ['18165', '238405', '210620', '279453', '279501', '210937', '212810', '41538', '155235', '251351', '251362', '251363','251365'], 'music': ['6029', '283297', '3017', '193829', '7386', '196089', '238000', '279461', '14825', '248675', '249084', '18395', '215073', '250883', '282244', '215608', '155650', '251660', '282278', '282350', '217468'], 'showbiz': ['164282'], 'athlete': ['274126', '215754', '163097', '256609', '256610', '233438', '269736', '208820'], 'pursuit': ['15290', '3713', '195295', '217887', '275905', '12391', '14967', '11148', '166519', '229620', '185590', '301229',  '324109', '325402'], 'deceit': ['159608', '193665', '11454', '206718'], 'couples': ['33494', '14534', '164698', '162296'], 'antihero': ['285809', '252203', '2095', '206701'], 'creature': ['13031', '195269', '5457', '68646', '217461', '224052', '286709', '179986', '231345', '206835', '230857', '292657'], 'disaster': ['10617', '238352', '233934', '268809', '189411', '5096', '208849', '207841', '319113'], 'dysfunctional': ['208344', '223609', '226325', '10041', '10061', '318325'], 'family': ['18035'], 'feminism': ['2383', '293179', '309966', '320094'], 'romance': ['9840', '212760', '213429', '282984', '283057', '219877', '283172', '284235', '284274', '221882', '222963', '223521', '258262', '188237', '233305', '269719', '272698'], 'resilient': ['294852'], 'adolescence': ['704', '308454', '293194', '10683', '286189', '296608'], 'zombie': ['12377', '186565']}
    '''
    if not (movie1_id and movie2_id):
        # get movie ids
        movie1_id, movie2_id = get_movie_id(movie1Title), get_movie_id(movie2Title)
    
    #get movie genres
    movie1_genres, movie2_genres = get_genres(movie1_id), get_genres(movie2_id)
    
    #get movie actors
    movie1_actors, movie2_actors = get_actors(movie1_id), get_actors(movie2_id)
    
    #get movie languages
    movie1_language, movie2_language = get_lang(movie1_id), get_lang(movie2_id)
    
    #get list of genre ids
    movie1_genre_id_list, movie2_genre_id_list = get_id_list(movie1_genres), get_id_list(movie2_genres)
    
    #get list of actors
    movie1_actor_id_list, movie2_actor_id_list  = get_id_list(movie1_actors), get_id_list(movie2_actors)
    
    #get synopsis 
    movie1_synop, movie2_synop = get_synopsis(movie1_id), get_synopsis(movie2_id)
    
    #perform contextual analysis. This returns a tuple in the form ((list of plot tags, freq each plot tag occurs), a relevant time period, a relevant location)
    movie1_context_analysis = perform_contextual_analysis(movie1_synop)
    movie2_context_analysis = perform_contextual_analysis(movie2_synop)
    #unpack said tuple
    movie1_plot_tags, movie1_plot_freq, movie1_time_tags, movie1_location_tags = movie1_context_analysis[0][0], movie1_context_analysis[0][1], movie1_context_analysis[1], movie1_context_analysis[2]
    movie2_plot_tags, movie2_plot_freq, movie2_time_tags, movie2_location_tags = movie2_context_analysis[0][0], movie2_context_analysis[0][1], movie2_context_analysis[1], movie2_context_analysis[2]
    #place in list for easier access. includes actor id lists, time, and location tags
    movie1_details = [movie1_actor_id_list, movie1_time_tags, movie1_location_tags]
    movie2_details = [movie2_actor_id_list, movie2_time_tags, movie2_location_tags]
    
    #get movie keywords. Returns list in form [{id, keyword}...]
    movie1_keywords, movie2_keywords = get_keywords(movie1_id), get_keywords(movie2_id)
    #get list of key ids
    movie1_keys_id_list, movie2_keysid_list = get_id_list(movie1_keywords), get_id_list(movie2_keywords)

    #combine keys from movie 1 and 2
    all_keys = set(movie1_keys_id_list).union(movie2_keysid_list)
    
    '''
    main_keywords, combined_plots = filter_context(freq1, freq2)
    main_keywords = get_keyword_ids(main_keywords)
    main_keywords = map(str, main_keywords) if main_keywords else ""
    '''
    #perform sentiment analysis on the synopses and combine
    movie1_mood_score = analyze_sentiment_vader(movie1_synop)
    movie2_mood_score = analyze_sentiment_vader(movie2_synop)
    aggregate_mood_score = (movie1_mood_score + movie2_mood_score)/2
    
    
    #determine if movies have the same actors, location, time period, or is a bollywood movie
    matchType, isPeriod, isLocation = determine_match_type([movie1_language]+movie1_details, [movie2_language]+movie2_details)
    
    #get all common genres, actors, time periods, or locations
    aggregate_genre, aggregate_actors, aggregate_time, aggregate_location = merge_movies([movie1_genre_id_list]+movie1_details, [movie2_genre_id_list]+movie2_details)
    if isPeriod: aggregate_time = get_keyword_ids(isPeriod) 
    if isLocation: aggregate_location = get_keyword_ids(isLocation)
    '''
    potential_keys= []
    
    for plot in combined_plots:
        if plot in freq1 and plot in freq2:
            if freq1[plot] > 3 and freq2[plot] > 3:
                potential_keys += plot_to_key_ids[plot]
    '''

    '''
    keys = all_keys or main_keywords or [keys1[0], keys2[0]]
    '''
    #get ~40 movies in genre with either matching actors, time, location, or just keywords
    filtered_movies = get_movies(matchType, aggregate_genre, aggregate_actors, aggregate_time, aggregate_location, all_keys)
    #get ~12 movies that have the most common keywords 
    similar_movies = get_movies_with_closest_plots(filtered_movies, all_keys, movie1_id, movie2_id)
    #rank ^^^ movies
    ranked = rank_movies(similar_movies, aggregate_mood_score)
    
    #return ranked movies in sorted order
    sorted_ranked_movies = sorted(ranked.items(), key=lambda x: x[1], reverse=True)
    return sorted_ranked_movies

if __name__ == "__main__":
    main()
    

