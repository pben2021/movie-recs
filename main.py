#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 12:33:28 2022

@author: paula
"""
import seatch as tmdb
import bestpick as retrieve
import string

import nltk
import ssl
import warnings

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
warnings.filterwarnings("ignore", message=r"\[W008\]", category=UserWarning)
#nltk.download()

from nltk.stem import WordNetLemmatizer
lemmatizer=WordNetLemmatizer()   


import spacy
nlp = spacy.load("en_core_web_lg")


class MovieInfo:
    def __init__(self, title, movie_id=None):
        self.title = title
        self.movie_id = movie_id
        self.movie_info = self.get_info()
        self.keywords = self.movie_info[2]
        self.tagline = self.movie_info[1][1]
        self.genre = self.movie_info[1][0]
        self.date = self.movie_info[0][3]
        self.plot = self.movie_info[0][2]
        self.lang = self.movie_info[0][1]
        self.id = self.movie_info[0][0]
        self.stop = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
    
    #return lists of possible movies
    @staticmethod
    def get_list(search):
        l = tmdb.select_movie(search)
        return l
    
    #get correct movie based on input string. returns all movie information
    def get_info(self):
        info = tmdb.main(title = self.title, movie_id=self.movie_id)
        return info
    def get_title(self):
        return self.title[0]
    def get_keys(self):
        return self.keywords
    def get_tagline(self):
        return self.tagline
    def get_genre(self):
        return self.genre
    def get_date(self):
        return self.date
    def get_plot(self):
        return self.plot
    def get_lang(self):
        return self.lang
    def get_id(self):
        return self.id
    
    #return tagline in form of list of keywords
    def get_tagline_list(self):
        tagline = self.tagline
        try:
            tagline = tagline.translate(str.maketrans('', '', string.punctuation))
        except:
            return tagline
        
        #get parts of speech that are nouns and certain verbs only (weeds out names, leftover words like willing etc..)
        doc = nlp(tagline)
        tagline = []
        for sent in doc.sents: #noun_chunks:
            [tagline.append(token.text) for token in sent if (token.pos_ == 'NOUN' or token.pos_ =='VERB' or token.tag_ =='VB' or token.tag_ =='VBN' or token.tag_ =='CD' or token.tag_ =='FW')]
        
        tags = [word for word in tagline if word not in self.stop and word[0].islower()]
        tags = [lemmatizer.lemmatize(wrd) for wrd in tags]
        return tags
    
    #return plot in form of list of keywords  
    def get_plot_list(self):
        plot = self.plot
        try:
            plot = plot.translate(str.maketrans('', '', string.punctuation))
        except:
            return plot
        
        #get parts of speech that are nouns and certain verbs only (weeds out names, leftover words like 'willing' etc..)
        doc = nlp(plot)
        plot = []
        for sent in doc.sents: #noun_chunks:
            [(plot.append(token.text)) for token in sent if (token.pos_ == 'NOUN' or token.tag_ =='VB' or token.tag_ =='VBN' or token.tag_ =='CD' or token.tag_ =='FW')]
            
        plots = [word for word in plot if word not in self.stop and word[0].islower()]
        plots = [lemmatizer.lemmatize(wrd) for wrd in plots]
        return plots
    
    #return list of all keywords, taglines, and plot
    def all_tags(self):
        return self.get_tagline_list() + self.get_plot_list() + self.keywords
        

class Match:
    def __init__(self, movie1, movie2, movie3=None):
        self.movie1 = movie1
        self.movie2 = movie2
        self.movie3 = movie3
    
    #return list of exact similarities between movies
    def matched(self):
        movie1 = self.movie1
        movie2 = self.movie2
        movie3 = self.movie3
        
        if movie3 is None:
            incts = list(set(movie1).intersection(movie2))
        else:
            incts = list(set.intersection(*map(set, [movie1, movie2, movie3])))
    
        return incts
    #return list of near matches
    def near_match(self):
        movie1 = self.mood(self.movie1) + self.genre(self.movie1) + self.place(self.movie1) + self.plot(self.movie1)
        movie2 = self.mood(self.movie2) + self.genre(self.movie2) + self.place(self.movie2) + self.plot(self.movie2)

        incts = set(movie1).intersection(movie2)
    
        return incts
    
    #return top 5 moods of movie based on movie tags
    def mood(self, words):
        buckets = {}
        moodtext = "atmospheric biting bittersweet bleak captivating clever contemplative comical cynical terrifying affecting exciting gloomy humorous perplexing offbeat crude uneasy sentimental sensual sexy sincere stylized suspenseful tense engaging heartbreaking uplifting witty"
        
        #compute similarity    
        doc = nlp(moodtext)
        similarities = {}   
        for word in words:
            tok = nlp(word)
            similarities[tok.text] ={}
            for tok_ in doc:
                similarities[tok.text].update({tok_.text:tok.similarity(tok_)})
            
            #prioritize all similarities greater than 85% similarity
            l =[k for k, v in similarities[tok.text].items() if v >= 0.85]
            for i in l:
                buckets[i] = 100
                
        top5 = lambda x: {k: v for k, v in sorted(similarities[x].items(), key=lambda item: item[1], reverse=True)[:5]}
        
        #count instances of mood
        for w in words:
            l1 = list(top5(w))[:5]
            for i in l1:
                buckets[i] = buckets.get(i,1) +1
                
        #sort most frequent moods
        top5= {k: v for k, v in sorted(buckets.items(), key=lambda item: item[1], reverse = True)}
         
        return list(top5)[:5]
    
    #return top 3 places of movie based on movie tags
    def place(self, words):
        buckets= {}
        placetext = "africa airplane airport asia australia pub battle casino chicago china college countryside courtroom desert galaxy england estate europe farm france germany haunted school seminary hollywood hotel woods india indoors island italy japan jungle vegas latin london angeles mars arabia mideast moon mountains nyc york ocean office palaces castle temple paris prison resort restaurant roman rome royal court russia francisco ship town spacecraft spain suburbs usa underwater university urban ghetto slum village washington dc presidential wilderness global"
        
        # # compute similarity    
        doc = nlp(placetext)
        similarities = {}   
        for word in words:
            tok = nlp(word)
            similarities[tok.text] ={}
            for tok_ in doc:
                similarities[tok.text].update({tok_.text:tok.similarity(tok_)})
                
            #prioritize all similarities greater than 85% similarity
            l =[k for k, v in similarities[tok.text].items() if v >= 0.85]
            for i in l:
                buckets[i] = 100
                
        top3 = lambda x: {k: v for k, v in sorted(similarities[x].items(), key=lambda item: item[1], reverse=True)[:3]}
        
        #count instances of place
        for w in words:
            l1 = list(top3(w))[:3]
            for i in l1:
                buckets[i] = buckets.get(i,1) +1
                
        #sort most frequent places
        top3= {k: v for k, v in sorted(buckets.items(), key=lambda item: item[1], reverse = True)}
         
        return list(top3)[:3]
    
    #return top 3 genres of movie based on movie tags
    def genre(self, words):
        buckets = {}
        # genretext = "action adventure animation anime culture biography bollywood business finance comedy crime culinary documentary drama educational childsafe teens friendship fantasy health historical horror independent martial medical motor concert musical mystery news period romance sci-fi science technology sport thriller travel war western"
        genretext = "action adventure animation comedy crime documentary drama family fantasy historical horror music mystery romance science thriller war western"
        
        # # compute similarity    
        doc = nlp(genretext)
        similarities = {}   
        for word in words:
            tok = nlp(word)
            similarities[tok.text] ={}
            for tok_ in doc:
                similarities[tok.text].update({tok_.text:tok.similarity(tok_)})
                
            #prioritize all similarities greater than 85% similarity
            l =[k for k, v in similarities[tok.text].items() if v >= 0.85]
            for i in l:
                buckets[i] = 100
        
        top4 = lambda x: {k: v for k, v in sorted(similarities[x].items(), key=lambda item: item[1], reverse=True)[:4]}
        
        #count instances of genre
        for w in words:
            l1 = list(top4(w))[:4]
            for i in l1:
                buckets[i] = buckets.get(i,1) +1
                
        #sort most frequent genre
        top4= {k: v for k, v in sorted(buckets.items(), key=lambda item: item[1], reverse = True)}
        #print(top4)
        return list(top4)[:4]
    
    
    #return top 6 plots of movie based on movie tags
    def plot(self, words):
        buckets = {}
        plottext = "underdog ambition americana animal artists showbiz athlete chaos hunt pursiuit races scams couples criminal heroes deadly creature disaster dysfunctional household folk kin adoration romantic compassion lust fondness relations feminism businesslike outcast friendship gender heroes human spirited imaginary infidelity introspection enforcement legal tribulation media psychological murder obsession psychological rescue heroic killer acquaintances humankind cosmos aliens reset politics supernatural teachers students terrorism uncover undercover rivalry vampire vengeance violence workplace youth zombie"
        
        #compute similarity    
        doc = nlp(plottext)
        similarities = {}   
        for word in words:
            tok = nlp(word)
            similarities[tok.text] ={}
            for tok_ in doc:
                similarities[tok.text].update({tok_.text:tok.similarity(tok_)})
                
            #prioritize all similarities greater than 85% similarity
            l =[k for k, v in similarities[tok.text].items() if v >= 0.85]
            for i in l:
                buckets[i] = 100
        
        top6 = lambda x: {k: v for k, v in sorted(similarities[x].items(), key=lambda item: item[1], reverse=True)[:6]}
        
        #count instances of plot
        for w in words:
            l1 = list(top6(w))[:6]
            for i in l1:
                buckets[i] = buckets.get(i,1) +1
                
        #sort most frequent plot
        top6= {k: v for k, v in sorted(buckets.items(), key=lambda item: item[1], reverse = True)}
         
        return list(top6)[:6]
    
    # COMING SOOON!!!
#     def period(self, words):
#         periodtext = "15th 1400s 16th 1500s 17th 1600s 18th 1700s 1900s 1910s 19th 1800s  20th 21st 30s 40s 50s 60s 70s 80s 90s Civil War Ancient Greece Contemporary Normandy Future Gulf Ages West Prehistory Victorian Vietnam WWI WW2 World War 1 World War 2" #needs to be restructured
#         pass
#     def actors(self):
#         pass
#     def style(self):
#         pass
#     def audience(self, words):
#         audiencetext = "boys date family girls kids teens adult"
#         pass
    
class Retrieval:
    def __init__(self, simlist):
        self.simlist = list(simlist)
    
    def matched(self):
        sim = self.simlist
        return retrieve.genreids(sim)
        
def main(id1=None, id2=None):
    #get movies from user
    title1 = input("Enter Title 1: ")
    movie1 = MovieInfo.get_list(title1)
    if not movie1:
        print("We can't find that movie. Try again")
        title1 = input("Enter Title 1: ")
        movie1 = MovieInfo.get_list(title1)
    print(movie1)
    selection1 = int(input("Select choice (first position=1): "))
    if selection1 > len(movie1):
        print('Incorrect selection. Try again. ')
        selection1 = int(input("Select choice (first position=1): "))
        
    title2 = input("Enter Title 2: ")  
    movie2 = MovieInfo.get_list(title2)
    if not movie2:
        print("We can't find that movie. Try again")
        title2 = input("Enter Title 2: ")
        movie2 = MovieInfo.get_list(title2)
    print(movie2)
    selection2 = int(input("Select choice (first position=1): "))
    if selection2 > len(movie2):
        print('Incorrect selection. Try again. ')
        selection2 = int(input("Select choice (first position=1): "))
    
    print('▒▒loading...')
    movie1 = movie1[selection1-1].split('(')
    movie2 = movie2[selection2-1].split('(')
    movie1 = MovieInfo(movie1)
    movie2 = MovieInfo(movie2)
    print('▒▒▒▒loading...')
    genre1 = movie1.get_genre()
    genre2 = movie2.get_genre()
    intersect = Match(genre1,genre2).matched()
    print('▒▒▒▒▒▒▒▒loading...')
    if len(intersect) == 0:
        matchObj = Match(genre1,genre2)
        matchedKeys = Match(matchObj.genre(matchObj.movie1), matchObj.genre(matchObj.movie2)).matched()
    else: matchedKeys = intersect
    print('▒▒▒▒▒▒▒▒▒▒▒▒▒▒loading...')
    genreids = retrieve.genreids(matchedKeys)
    print('▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒loading...')
    resp = retrieve.simlist(genreids)
    allTags1 = movie1.all_tags()
    allTags2 = movie2.all_tags()
    searchKeys = list(Match(allTags1, allTags2).matched()) + list(Match(allTags1,allTags2).near_match())
    print('▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒loading...')
    recs=retrieve.sift(resp, retrieve.keyids(searchKeys))
    print('▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒loading...')
    top6= list({k: v for k, v in sorted(recs.items(), key=lambda item: item[1], reverse = True)})[:7]

    print(top6)
    
if __name__ == '__main__':
    main()

