# Foodgram - сайт с вкусными рецептами для програмистов

[![foodgram project](https://github.com/odolisk/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/odolisk/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

[![Python](https://img.shields.io/badge/-Python-464646??style=flat-square&amp;logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646??style=flat-square&amp;logo=Django)](https://www.djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646??style=flat-square&amp;logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646??style=flat-square&amp;logo=NGINX)](https://nginx.org/)
[![Docker](https://img.shields.io/badge/-docker-464646??style=flat-square&amp;logo=docker)](https://www.docker.com/)

## Описание

Foodgram project (Яндекс.Практикум) собирает кулинарные рецепты. Публикуйте свои рецепты, читайте рецепты других пользователей, добавляйте рецепты в избранное, подписывайтесь на других пользователей, создавайте свой список покупок и выгружайте его в формате PDF.
Backend сделан на базе Django Rest Framework. Frontend был предоставлен в виде готового одностраничного приложения SPA <https://en.wikipedia.org/wiki/Single-page_application>.

### Требования

- docker (_установка_ <https://docs.docker.com/engine/install/#server> )
- docker-compose (_установка_ <https://docs.docker.com/compose/install/> )

### Переменные

Переменные хранятся в файле .env в корне проекта.
Необходимо определить следующие переменные (в скобках значения по умолчанию):

- DB_ENGINE (django.db.backends.postgresql)
- DB_NAME (postgres)
- POSTGRES_USER (postgres)
- POSTGRES_PASSWORD
- DB_HOST (db)
- DB_PORT (5432)
- SECRET_KEY
- DEBUG (False)
- ALLOWED_HOST (localhost)

### Запуск проекта*

```bash
sudo docker-compose pull
sudo docker-compose up -d --build
```

### Создание суперпользователя и заполнение данными

```bash
sudo docker exec -it foodgram-project-react bash
```

и далее в терминале

```bash
cd backend/

python manage.py createsuperuser

python manage.py loaddata ../data/fixtures.json 
```

\* Для GitBash под Windows команды вводятся без sudo

### Инфо

- Документация доступна по адресу **/api/docs/**
- Админка **/admin/**
- API **/api/** (более подробно о эндпоинтах в redoc)
  - Пользователи **users/**
  - Подписки **users/subscriptions/**
  - Рецепты **recipes/**
  - Скачать список покупок **recipes/download_shopping_cart/**
  - Избранное **recipes/{id}/favorite/**
  - Ингредиенты **ingredients/**
  - Теги **tags/**

### Страница проекта

Готовый деплой можно увидеть по ссылке <http://odolisk.ru/>

#### Тестовый пользователь

**login:** test@odolisk.ru
**password:** Test0112

### Автор проекта

Дмитров Артем, студент Яндекс.Практикум (backend), 16 когорта
