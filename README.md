# TG-bot 

Allow you to control and get you subscribe info
___
## Project info

### Components 

1) Tg-bot
2) Newsletter scheduler
3) DB (Postgres)
4) Migration service


## Quiq start
1) Create .env (copy .env.template and modify)
2) ``pip install -r requirements.txt``
3) ``run ./main.py``

### Explanations

**main.py** запускает:
- scheduler  # Запускается ассинхронная задача (пока пустая) 
- migrate    # Запускается миграция БД (создается схема базы данных)
- tg_bot     # Запускается телеграмм бот