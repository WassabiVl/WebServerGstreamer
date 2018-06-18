# Installation
### pip install django
### python -m pip install django

# Creating a project
### django-admin startproject mysite

## creating an app
### python manage.py startapp polls

## database
### python manage.py migrate ( migrate the default db structure)
### python manage.py makemigrations app (creates the migrations for the newly created app db)
### python manage.py sqlmigrate app 0001

# running django
### python manage.py runserver (run the server)

## running the shell
### python manage.py shell

## creating an admin
### python manage.py createsuperuser
### Username: admin
### Email address: admin@example.com
### password