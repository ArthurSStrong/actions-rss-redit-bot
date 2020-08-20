"""
Takes the top 2 Google News and posts them to Reddit.
"""

import xml.etree.ElementTree as ET

import os
import requests
import praw


CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]

LOG_FILE = "./processed_urls.txt"
NEWS_URL = "https://news.google.com/rss/topics/CAAqKggKIiRDQkFTRlFvTEwyY3ZNVEl3Y0RsNWFHc1NCbVZ6TFRReE9TZ0FQAQ?hl=es-419&gl=MX&ceid=MX%3Aes-419"


def load_log():
    """Loads the log file and creates it if it doesn't exist.

    Returns
    -------
    list
        A list of urls.

    """

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as temp_file:
            return temp_file.read().splitlines()

    except Exception:
        with open(LOG_FILE, "w", encoding="utf-8") as temp_file:
            return []


def update_log(url):
    """Updates the log file.

    Parameters
    ----------
    url : str
        The url to log.

    """

    with open(LOG_FILE, "a", encoding="utf-8") as temp_file:
        temp_file.write(url + "\n")


def init_bot():
    """Reads the RSS feed."""

    # We create the Reddit instance.
    reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, username=USERNAME, password=PASSWORD,user_agent="testscript by /u/larry3000bot")

    with requests.get(NEWS_URL) as response:

        root = ET.fromstring(response.text)

        # Only read the first 3 links.
        for item in root.findall(".//item")[:2]:          
            log = load_log()

            title = item.find("title").text.split(" - ")[0].split(" | ")[0].strip()
            url = item.find("link").text

            if url not in log and title not in log:

                reddit.subreddit('lazonacero').submit(
                    title=title, url=url)

                update_log(url)
                update_log(title)
                print("Posted:", url)


if __name__ == "__main__":

    init_bot()
