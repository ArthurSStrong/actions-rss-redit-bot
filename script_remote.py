#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Takes the top 2 Google News and posts them to Reddit.
"""

import xml.etree.ElementTree as ET

import os
import requests
import praw

CLIENT_ID = (os.environ['CLIENT_ID'] if 'CLIENT_ID'
             in os.environ else '')
CLIENT_SECRET = (os.environ['CLIENT_SECRET'] if 'CLIENT_SECRET'
                 in os.environ else '')
USERNAME = (os.environ['USERNAME'] if 'USERNAME' in os.environ else '')
PASSWORD = (os.environ['PASSWORD'] if 'PASSWORD' in os.environ else '')

LOG_FILE = './processed_urls.txt'
NEWS_URL_FILE = './source_urls.txt'


def load_file(file):
    """Loads the log file and creates it if it doesn't exist.
     Parameters
    ----------
    file : str
        The file to write down
    Returns
    -------
    list
        A list of urls.

    """

    try:
        with open(file, 'r', encoding='utf-8') as temp_file:
            return temp_file.read().splitlines()
    except Exception:

        with open(LOG_FILE, 'w', encoding='utf-8') as temp_file:
            return []


def update_file(file, data):
    """Updates the log file.

    Parameters
    ----------
    file : str
        The file to write down.
    data : str
        The data to log.

    """

    with open(file, 'a', encoding='utf-8') as temp_file:
        temp_file.write(data + '\n')

        
def resolve_shortener(url):
    """Gets the real url from the url-shortener service.
    Parameters
    ----------    
    url : str
        A shortened url.
    Returns
    -------
    str
        The real url.
    """

    with requests.head(url) as response:
        return response.headers["location"]


def init_bot():
    """Reads the RSS feed."""

    # We create the Reddit instance.

    reddit = praw.Reddit(client_id=CLIENT_ID,
                         client_secret=CLIENT_SECRET,
                         username=USERNAME, password=PASSWORD,
                         user_agent='testscript by /u/larry3000bot')

    rss_urls = load_file(NEWS_URL_FILE)

    for rss_url in rss_urls:
        try:
            with requests.get(rss_url) as response:
                root = ET.fromstring(response.text)

                # Only read the first 3 links.

                for item in reversed(root.findall('.//item')[:3]):
                    log = load_file(LOG_FILE)

                    title = item.find('title').text.split(' - '
                            )[0].split(' | ')[0].strip()
                    url = item.find('link').text
                    
                    if 'anime' in title.lower():
                        continue

                    if 'feedity' in url:
                        url = item.find('guid').text
                        
                    if 'google' in url:
                        url = resolve_shortener(url)

                    if url not in log and title not in log:
                        reddit.subreddit('lazonacero'
                                ).submit(title=title, url=url)
                        update_file(LOG_FILE, url)
                        update_file(LOG_FILE, title)
                        print ('Posted:', url)
        except requests.ConnectionError:
            continue
    print('end of script')


if __name__ == '__main__':

    init_bot()
