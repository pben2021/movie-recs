#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  8 10:53:36 2022

@author: paula
"""
import requests, json
API_key = '21b421ab2e0fb3417ba507e17c1d21df'

#single linked list class for storing recommendations shoutout cs102
class SLL:
    class _Node:
        """Lightweight, nonpublic class for storing a singly linked node."""
        __slots__ = '_element', '_title', '_keys', '_date', '_next'         # streamline memory usage

        def __init__(self, movieid, title, keys, date, next):      # initialize node's fields
            self._element = movieid              
            self._title = title
            self._keys = keys
            self._date = date
            self._next = next                     

    def __init__(self):
        """Create an empty linkedlist."""
        self._head = None
        self._size = 0

    def __len__(self):
        """Return the number of elements in the linkedlist."""
        return self._size

    def is_empty(self):
        """Return True if the linkedlist is empty."""
        return self._size == 0

    def top(self):
        """Return (but do not remove) the element at the top of the linkedlist.

        Raise Empty exception if the linkedlist is empty.
        """
        if self.is_empty():
            return []
        return self._head             # head of list

    def insert_from_head(self, movieid, title, keys, date):
        """Add element e to the head of the linkedlist."""
        # Create a new link node and link it
        new_node = self._Node(movieid, title, keys, date, self._head)
        self._head = new_node
        self._size += 1

    def delete_from_head(self):
        """Remove and return the element from the head of the linkedlist.
        """
        if self.is_empty():
            return []
        to_return = self._head._element
        self._head = self._head._next
        self._size -= 1
        return to_return

    def __str__(self):
        result = []
        curNode = self._head
        while (curNode is not None):
            result.append(str(curNode._element) + "-->")
            curNode = curNode._next
        result.append("None")
        return "".join(result)

    def __getitem__(self, k):
        """
        return the element (not the node) stored at kth indexed node.
        index range: [0, len(self) - 1]
        """
        if self.is_empty():
            return []
        if k > self._size:
            raise Exception()

        temp = self._head
        for i in range(k):
            temp = temp._next
        
        return temp._element



''' GETTING IDS AND STUFF '''


#return list of keyword ids
def keyids(keys):
    l=[]
    for k in keys:
        response = requests.get('https://api.themoviedb.org/3/search/keyword?api_key='+API_key+'&query='+k)
        array = response.json()
        for r in array['results']:
            if r['name'] == k:
                l.append(r['id'])
                break                   
    return l

#return genreids
def genreids(keys):#%2c is and %7c is or
    genre={'action': '28', 'adventure': '12', 'animation': '16', 'comedy': '35', 'crime': '80', 'documentary': '99', 'drama': '18', 'family': '10751', 'fantasy': '14', 'history': '36', 'horror': '27', 'music': '10402', 'mystery': '9648', 'romance': '10749', 'science': '878', 'thriller': '53', 'war': '10752', 'western': '37'}
    #other possible genre categorizations --> genre={'friendship':'12','teens':'12','religious':'18','sport':'28','parody':'35','travel':'12', 'sci-fi':'878','technology':'878','action': '28','motor':'28','martial':'28', 'concert':'10402','news':'99','period':'36','culinary':'12','adventure': '12', 'bollywood':'10402','culture':'12','animation': '16', 'anime': '16','comedy': '35', 'crime': '80', 'documentary': '99','educational':'99','biography':'18', 'business':'18', 'finance':'18','drama': '18', 'independent':'18','health':'18', 'family': '10751', 'fantasy': '14', 'history': '36', 'horror': '27', 'music': '10402', 'mystery': '9648', 'romance': '10749', 'science': '878', 'thriller': '53', 'war': '10752', 'western': '37'}
    l=[]
    for k in keys:
        l.append(genre[k.lower()])                   
    return l

#using list of combined genre ids, get all movies with same genre ids
def simlist(ids, lang='en-US'):
    allresp = []
    idquery=''
    for i in ids[:2]:
        idquery += str(i)+'%2C'
    idquery=idquery[:-3]
    
    #get all relevant movies from page1 and add to list of all responses
    response = requests.get('https://api.themoviedb.org/3/discover/movie?api_key='+API_key+'&language='+lang+'&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&with_genres='+idquery+'&with_watch_monetization_types=flatrate')
    allresp.append(response)
    
    #add up to 17 pages of responses to allresp list.
    for page in range(2, 20):#pages['total_pages']):
        resp = requests.get('https://api.themoviedb.org/3/discover/movie?api_key='+API_key+'&language='+lang+'&sort_by=popularity.desc&include_adult=false&include_video=false&page='+str(page)+'&with_genres='+idquery+'&with_watch_monetization_types=flatrate')
        allresp.append(resp)
        
    #create SLL and add every page and every movie within a page to SLL
    movie = SLL()
    for resp in allresp:
        addtoSLL(resp, movie)
        
    return movie

#create Node with movie information in single linked list
def addtoSLL(resp, movie):
    resp = resp.json()
    #for each movie in a page, create node and insert at head
    for r in resp['results']:
        movieid = str(r['id'])
        title = r['title']
        date = r.get('release_date','----')
        keys = requests.get('https://api.themoviedb.org/3/movie/'+movieid+'/keywords?api_key='+API_key)
        keys = keys.json()
        temp = []
        for k in keys['keywords']:
            temp.append(k['id'])
        movie.insert_from_head(movieid, title, temp, date[:4])
        
#rank movies based on similarity    
def sift(nodelist, keys):
    curr = nodelist.top()
    
    d = {}
    #for each node, find how many common keys between the node and the ideal movie and store in dictionary
    for i in range(nodelist._size):
        incts = set(keys).intersection(curr._keys)
        d[str(curr._title+ '('+curr._date+')')] = len(incts)
        curr= curr._next
    return d
            
