## Bot description
ЧТО: Бот для матчинга людей по интересам (на основе резюме и соцсетей)
ДЛЯ КОГО: Для участников профессиональных сходок.
ЗАЧЕМ: Чтобы люди могли на конференции находить интересные знакомства автоматически.
ВЫДЕЛЯЕТ: сфера – именно в первую очередь проф. знакомства; используем ллм и nlp для матчинга.
```
/start - Show this message
/create_profile - create a profile
/join_party - join to party
/get_matches - when you created profile you can get matches
```


## How to run
0. Вам нужна ветка `olga/current-build`
1. Скопируйте .env.example, создайте .env файл и заполните его.
2.  `docker compose up -d bot --build`
