"""
Movie Collection Organiser

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
    for file in glob.glob(path+"/"+movie_file+"*"):
        if os.path.isdir(file):
            continue
        base_file = os.path.basename(file)
        move(path+"/"+base_file, path+"/"+new_dir+"/"+base_file)

def update_all_files(path):
    if not os.path.isdir(path):
        print "Movie path not valid"
        return False

    # Find all the videos not in a sub directory
    for file in glob.glob(path+"/*.avi"):
        file_name = os.path.basename(file)
        movie_file, extension = os.path.splitext(file_name)

        # See if a directory already exists for it
        # if so, just move all the files into it
        if os.path.isdir(file):
            continue

        movie_name = clean_movie_name(movie_file)

        if not has_year_in_brackets(movie_file):
            name, year = get_year(movie_name)

            if year:
                new_dir = "{0} ({1})".format(movie_name, year)
            else:
                new_dir = False
        else:
            new_dir = "{0}".format(movie_name)

        if new_dir:
            print "Attempting to create ", new_dir
            try:
                os.makedirs(path+new_dir)
            except OSError:
                pass
            move_related_files(path, movie_file, new_dir)
        else:
            print "You'll have to fix {0} yourself.".format(file_name)

if __name__ == "__main__":
    movie_path = "/media/tbmedia/Media/Movies/"
    update_all_files(movie_path)
