"""
Problems to solve
1. Ensure all Movies sit inside a directory which has the same name as the Movie Name.avi movie
2. Ensure all directories are called Movie Name (YYYY) 
3. Ensure each directory has 4 files
    1. Movie Name.avi
    2. Movie Name-fanart.jpg
    3. 
Author: Lex Toumbourou
"""
import os
import glob
import re
import urllib
import httplib2
import json
import secret
from shutil import move
from sys import exit

def has_space_word_separator(file_name):
    pass
    #if re.search(u"")

def has_year_in_brackets(movie_name):
    # Ensure file name includes year in format (YYYY).avi
    if re.search(u"(\w+ )+\(\d{4}\)", movie_name):
        return True

    return False

def clean_movie_name(movie_name):
    bad_words = ["xvid", "divx", "dvdrip",
                 "ws", "eng", "dmd", "-",
                 "trij", "klaxxon"]

    # Convert movie name to lowercase
    movie_name = movie_name.lower()

    # Replace all dots with spaces
    movie_name = movie_name.replace(".", " ")

    # Remove all known bad words
    for word in bad_words:
        movie_name = movie_name.replace(word, "")

    return movie_name.strip().title()

def get_year(movie_name, try_count=2):
    # Encode movie name
    query_url = urllib.quote_plus(movie_name)
    url = ("http://api.rottentomatoes.com/"
           "api/public/v1.0/movies.json?"
           "apikey={0}&q={1}&page_limit=1").format(secret.API_KEY,
                                                   query_url)
    h = httplib2.Http(".cache")
    resp, content = h.request(url, "GET")

    result = json.loads(content)

    # If we can't find a suitable year for the movie
    # we try again with just the first 3 words,
    # if nothing then the first two until we've exhausted them
    # all. Then we give up and get the user to manually enter
    # the movie
    if try_count < 1:
        return ("", "") 
    try:
        return (result['movies'][0]['title'], result['movies'][0]['year'])
    except IndexError:
        movie_name = movie_name.split(" ")[:try_count]
        return get_year(" ".join(movie_name), try_count-1)

def move_related_files(path, movie_file, new_dir):
    print path
    print movie_file
    print new_dir
    for file in glob.glob(path+"/"+movie_file+"*"):
        print "First file, ", file
        base_file = os.path.basename(file)
        print path+"/"+base_file, new_dir+"/"+base_file
        move(path+"/"+base_file, new_dir+"/"+base_file)

def update_all_files(path):
    if not os.path.isdir(path):
        print "Movie path not valid"
        return False

    # Find all the videos not in a sub directory
    for file in glob.glob(path+"/*.avi"):
        # See if a directory already exists for it
        # if so, just move all the files into it
        if os.path.isdir(file):
            move_related_files(file)
            continue

        file_name = os.path.basename(file)
        movie_file, extension = os.path.splitext(file_name)

        if not has_year_in_brackets(movie_file):
            movie_name = clean_movie_name(movie_file)
            name, year = get_year(movie_name)

            if year:
                new_dir = "{0} ({1})".format(movie_name, year)
            else:
                new_dir = False
        else:
            new_dir = "{0}".format(movie_name)

        print "Attempting to create ", new_dir
        try:
            os.makedirs(path+new_dir)
        except OSError:
            pass
        move_related_files(path, movie_file, new_dir)

if __name__ == "__main__":
    movie_path = "/media/tbmedia/Media/Movies"
    update_all_files(movie_path)
