[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru)

# FOODGRAM
«Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 
Зарегистрированным пользователям также будет доступен сервис «Список покупок». 
Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.


## Стек технологий:
* Python
* React
* Django
* Django REST Framework
* Docker
* Docker-compose
* Postgres
* Nginx
* Workflow

## Для просмотра документации API и frontend необходимо:

Находясь в папке infra, выполнить команду docker-compose up. 

По адресу http://localhost можно просмотреть frontend веб-приложения, а по 
адресу http://localhost/api/docs/ — спецификацию API.

## Запуск проекта локально:

1. Клонируйте репозиторий проекта с GitHub:
```
git clone <ссылка на проект>
```

2. В терминале, перейдите в каталог и создайте там файл .evn для хранения 
   ключей в соответствии с .env.example. 
```
cd .../foodgram/gateway
```

3. Запустите docker-compose:
```
docker-compose up
```

4. Выполните миграции:
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

5. Соберите статику:
```
docker compose exec backend python manage.py collectstatic
```

6. Заполнить базу данных ингредиентов и тегов из csv файлов:
```
docker compose exec backend python manage.py load_data
```
7. Создайте суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```