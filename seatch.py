#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 13:13:44 2022

@author: paula
"""
import requests,json

'''
Return movie information, details, and keywords
'''

API_key = '21b421ab2e0fb3417ba507e17c1d21df'

#write a function to compose the query using the parameters provided
def get_data(query):
    response =  requests.get(query)
    if response.status_code==200: 
    #status code ==200 indicates the API query was successful
        array = response.json()
        text = json.dumps(array)
        return text
    else:
        return "error"
    
#returns list of all possible movie names    
def select_movie(title):
    mov = []
    
    response =  requests.get('https://api.themoviedb.org/3/search/movie?api_key='+API_key+'&query='+title)
    if response.status_code==200: 
    #status code ==200 indicates the API query was successful
        array = response.json()
    for tit in array['results']:
        try:
            if tit['release_date']:
                string = tit['title']+' ('+str(tit['release_date'][:4])+')'
                mov.append(string)
        except KeyError:
            continue
    return mov
    
    
#returns movie id, language, overview, release date
def result(text,title,date):
    dataset = json.loads(text)
    if '(' in title:
        e = title.split('(')
        title = e[0]
        date = e[1]
    #unpack the result 
    for i in range(len(dataset['results'])):
        try:
            movie_name = dataset['results'][i]
        except:
            movie_name = None
        if movie_name is None or (movie_name['title'] == title.rstrip() and movie_name['release_date'][:4] == date):
            break
    
    try:
        result = movie_name['title']
    except:
        return "error"
        
    return (movie_name['id'], movie_name['original_language'], movie_name['overview'], movie_name['release_date'])

#return movie genre and tagline
def details(text):
    dataset = json.loads(text)
    genres = []
    for g in dataset['genres']:
        genres.append(g['name'])
    
    return genres, dataset['tagline']

#return movie keywords
def keywords(text):
    dataset = json.loads(text)
    keywords = []
    for k in dataset['keywords']:
        keywords.append(k['name'])
    return keywords

#return language, overview, release data if id provided    
def with_id_data(movie_id):
    response = requests.get("https://api.themoviedb.org/3/movie/"+str(movie_id)+"?api_key="+API_key)
    movie_name = response.json()
    return (movie_id, movie_name['original_language'], movie_name['overview'], movie_name['release_date'])




def main(title='Little Women', movie_id=None):
    if movie_id is None:
        #query for movie_id
        date = title[1].strip(')')
        title = title[0]
        title_query = 'https://api.themoviedb.org/3/search/movie?api_key='+API_key+'&query='+title
        
        #get movie_info; movie id, language, overview, release date
        text = get_data(title_query)
        if text == "error":
            movie_id= "error"
        info = result(text, title, date)
        movie_id = info[0]
    else:
        info = with_id_data(movie_id)

    #query for movie_details
    details_query = 'https://api.themoviedb.org/3/movie/'+str(movie_id)+'?api_key='+API_key
    
    #get movie details
    text = get_data(details_query)
    if text == "error":
        deets= "error"
    deets = details(text)
    
    #query for movie keywords
    key_query = 'https://api.themoviedb.org/3/movie/'+str(movie_id)+'/keywords?api_key='+API_key
    
    #getmovie_keywords
    text = get_data(key_query)
    if text == "error":
        keys= "error"
    keys = keywords(text)

    return info, deets, keys
  
if __name__ == '__main__':
    main()

    #movie_match(['high school', 'coming of age', 'friend', 'society', 'scary', 'nature', 'home', 'touching', 'school', 'family', 'disturbing', 'human', 'love', 'talk', 'emotional'])
