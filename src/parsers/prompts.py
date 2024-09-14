
RESUME_PROMPT_BASE = """
You have a resume text, that was extracted from pdf. I want you to read this semistuctured text and 
understand person main interests. After that, fill in the json template, which represents main info of the person. 
Return only filled in JSON object without any additional text and do not format it.
Note: professional_interests is technical fields that person admires, e.g. "Computer Vision", "NLP", "Backend Development", etc.
field "summary" is where you summarize main topics from job experience.
Today is 12 September 2024. If you can't fill info, fill in null (e.g. age or sex is undetermined).

Here is the template, do not use any additional fields:
{
"name": "",
"gender": "",
"age": 0,
"country": "",
"city": "",
"professional_field": "",
"professional_interests: "",
"languages": ["", ],
"study_universities": ["", ]
"professional_experience": [
    {
    "position": "",
    "company": "",
    "duration_in_months": 0,
    "main_info": ["", ],
    "summary": ""
    },
],
"skills": ["",],
"projects": [
    {
    "title": "",
    "description": ""
    }
],
"publications": [
    {
    "title": "",
    "journal": ""
    }
],
"achievements": ["",]
}

Here is the resume text:
"""


REDDIT_PROMPT_BASE = """
You have a redditor subreddits activity, that is stored in json and sorted by subreddit. I want you to read this semistuctured text and 
understand person main interests. After that, fill in the json template, which represents main info of the person. 
Return only filled in JSON object without any additional text and do not format it.
Traits are representing person's behaviour, mention them in 2-3 words. The field summary is for an overall expression of the person.

Here is the template, do not use any additional fields:
{
"name": "",
"gender": "",
"languages": ["", ],
"interests": ["". ],
"traits": ["", ],
"summary": ""
}

Here is the redditor's info:
"""
