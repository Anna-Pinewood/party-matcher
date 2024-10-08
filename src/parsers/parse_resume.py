"""Extract text from pdfs and parse resume with llm"""
import json
import logging
import os

import requests
from openai import DefaultHttpxClient, OpenAI
from pypdf import PdfReader

from consts import OPENAI_API_KEY, PROXY_URL, YANDEX_API_KEY, YANDEX_FOLDER_ID
from parsers.prompts import RESUME_PROMPT_BASE

logging.basicConfig(level=logging.INFO)


def extract_text_from_pdf_file(input_filepath: str) -> str:
    reader = PdfReader(input_filepath)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        full_text += text
    return full_text


def parse_resume_yandexgpt(input_filepath: str) -> dict:
    if not os.path.exists(input_filepath):
        logging.error(f": {input_filepath}")
        return {}
    resume_text = extract_text_from_pdf_file(input_filepath)

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YANDEX_API_KEY}"
    }
    query_json = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": RESUME_PROMPT_BASE + resume_text
            }
        ]
    }
    response = requests.post(url, headers=headers, json=query_json)
    if response.status_code != 200:
        logging.error("Error during request %s: %s",
                      response.status_code, response.text)
        return {}
    result = response.json()
    json_str_repr = result['result']['alternatives'][0]['message']['text'].replace(
        '\n', '').replace('`', '')
    try:
        return json.loads(json_str_repr)
    except json.JSONDecodeError:
        logging.error(f"Can't convert str to json: {json_str_repr}")
    return {}


def parse_resume_openaigpt(input_filepath: str) -> dict:
    if not os.path.exists(input_filepath):
        logging.error("No such file: %s", input_filepath)
        return {}
    resume_text = extract_text_from_pdf_file(input_filepath)
    logging.info("Text extracted: %s...", resume_text[:100])

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
                "content": RESUME_PROMPT_BASE + resume_text,
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
