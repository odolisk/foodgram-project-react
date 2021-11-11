# Foodgram - сайт с вкусными рецептами для програмистов

[![foodgram project](https://github.com/odolisk/foodgram-project-react/actions/workflows/foodgram_project.yml/badge.svg)](https://github.com/odolisk/foodgram-project-react/actions/workflows/main.yml)

<p>
    <a href="https://www.python.org/" rel="nofollow"><img src="https://camo.githubusercontent.com/938bc97e6c0351babffcd724243f78c6654833e451efc6ce3f5d66a635727a9c/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d507974686f6e2d3436343634363f3f7374796c653d666c61742d737175617265266c6f676f3d507974686f6e" alt="Python" data-canonical-src="https://img.shields.io/badge/-Python-464646??style=flat-square&amp;logo=Python" style="max-width:100%;">
    </a>
    <a href="https://www.djangoproject.com/" rel="nofollow"><img src="https://camo.githubusercontent.com/99e48bebd1b4c03828d16f8625f34439aa7d298ea573dd4e209ea593a769bd06/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d446a616e676f2d3436343634363f3f7374796c653d666c61742d737175617265266c6f676f3d446a616e676f" alt="Django" data-canonical-src="https://img.shields.io/badge/-Django-464646??style=flat-square&amp;logo=Django" style="max-width:100%;">
    </a>
    <a href="https://www.postgresql.org/" rel="nofollow"><img src="https://camo.githubusercontent.com/18b5ef277b89701f948c212d45d3460070037bda9712fe5f1e64315811356ea2/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d506f737467726553514c2d3436343634363f3f7374796c653d666c61742d737175617265266c6f676f3d506f737467726553514c" alt="PostgreSQL" data-canonical-src="https://img.shields.io/badge/-PostgreSQL-464646??style=flat-square&amp;logo=PostgreSQL" style="max-width:100%;">
    </a>
    <a href="https://nginx.org/ru/" rel="nofollow"><img src="https://camo.githubusercontent.com/b9f9edede39c7f898e25e81ce431f7c4b8d0b375c05768fd6916e599fcba219f/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d4e47494e582d3436343634363f3f7374796c653d666c61742d737175617265266c6f676f3d4e47494e58" alt="NGINX" data-canonical-src="https://img.shields.io/badge/-NGINX-464646??style=flat-square&amp;logo=NGINX" style="max-width:100%;">
    </a>
    <a href="https://www.docker.com/" rel="nofollow"><img src="https://camo.githubusercontent.com/038c45c7c5f0059723bba28b5b77bd9ac7994c8da774814c8fcb620f4bc61b35/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d646f636b65722d3436343634363f3f7374796c653d666c61742d737175617265266c6f676f3d646f636b6572" alt="docker" data-canonical-src="https://img.shields.io/badge/-docker-464646??style=flat-square&amp;logo=docker" style="max-width:100%;">
    </a>
</p>

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
- ALLOWED_HOST (['*'])

### Запуск проекта*

```bash
sudo docker-compose pull
sudo docker-compose up -d --build
```

### Создание суперпользователя и заполнение данными

```bash
sudo docker exec -it foodgram-project-react_web_1 bash
```

и далее в терминале

```bash
cd backend/

python manage.py createsuperuser

python manage.py loaddata ../data/fixtures.json 
```

\* Для GitBash под Windows команды вводятся без sudo

### Инфо

- Документация доступна по адресу **/docs/**
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

**login:** test@test.odolisk.ru
**password:** Test0112

### Автор проекта

Дмитров Артем, студент Яндекс.Практикум (backend), 16 когорта
