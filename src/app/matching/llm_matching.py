import json
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain_core.output_parsers import JsonOutputParser

from consts import OPENAI_API_KEY, PROXY_URL


template = """
Ты получишь список пользователей в формате JSON, включая целевого пользователя и десять других пользователей. 
Твоя задача — проанализировать каждого пользователя и оценить их схожесть с целевым пользователем. 
Используй следующие параметры для сравнения: 
- возраст
- интересы (профессиональные и личные)
- технологии и инструменты, с которыми работали пользователи (например, языки программирования, фреймворки, библиотеки)
- профессиональный опыт (включая позиции, компании и проекты)
  
Верни мне список десяти пользователей, отсортированный по убыванию схожести с целевым пользователем, где первый в списке — наиболее похожий.

Целевой пользователь:
{target_user}

Пользователи для сравнения:
{other_users}

Сортируй пользователей и возвращай результат в виде списка JSON, где каждый элемент содержит:
- имя пользователя
- оценку схожести
- краткое объяснение основных факторов схожести.
"""

prompt = PromptTemplate(
    input_variables=["target_user", "other_users"],
    template=template
)


llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY,
                 base_url=PROXY_URL, max_tokens=None)
chain = prompt | llm


def get_matching_llm(user1: dict, users_top: list[dict]) -> str:
    variables = {
        "target_user": str(user1),
        "other_users": json.dumps(users_top, ensure_ascii=False, indent=4)
    }
    result = chain.invoke(variables)
    return result.content
