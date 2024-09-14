"""Extract info from reddit and parse it with llm"""
import json
import logging
import os

import praw
from collections import defaultdict
from openai import DefaultHttpxClient, OpenAI

from consts import OPENAI_API_KEY, PROXY_URL, REDDIT_CLIENT_SECRET, REDDIT_CLIENT_ID, YANDEX_FOLDER_ID
from parsers.prompts import REDDIT_PROMPT_BASE

logging.basicConfig(level=logging.INFO)


def extract_profile_info(username: str) -> dict:
    """
    Function parses redditor's info to explore their hobbies more.
    Args:
        username: str, redditor's username
    Output:
        info: dict, info about subreddits they joined based on posts and comments
    """

    reddit = praw.Reddit(client_secret=REDDIT_CLIENT_SECRET,
                         client_id=REDDIT_CLIENT_ID,
                         user_agent="matching"
                         )
    info = defaultdict(list)                     
    try:
        user = reddit.redditor(username)

        logging.info("Got data from %s...", username)

        for submission in user.submissions.new(limit=10):
            info[submission.subreddit.display_name].append(submission.title)

        for comment in user.comments.new(limit=10):
            info[comment.subreddit.display_name].append(comment.body)
        
        return info

    except Exception as e:
        logging.error(f"Auth failed: {e}")
    
    return {}


def parse_reddit_openaigpt(username: str) -> dict:

    """
    Function parses redditor's info to explore their hobbies more.
    Args:
        input_info: dict, info about subreddits they joined based on posts and comments
    Output:
        info: dict, info about subreddits they joined based on posts and comments
    """
    
    reddit_info = extract_profile_info(username)

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        http_client=DefaultHttpxClient(
            proxy=PROXY_URL,
        )
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": REDDIT_PROMPT_BASE + str(reddit_info),
            }
        ],
        model="gpt-4o-mini",
    )

    json_str_repr = chat_completion.choices[0].message.content.replace(
        '\n', '').replace('`', '')
    logging.info("Got json: %s...", json_str_repr[:100])
    try:
        return json.loads(json_str_repr)
    except json.JSONDecodeError:
        logging.error(f"Can't convert str to json: {json_str_repr}")
    return {}
