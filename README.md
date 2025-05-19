# SupplyChainDash application

## Setup

The first thing to do is to clone the repository:

# TODO update add commands to clone
```sh
$ git clone ********
$ cd SupplyChainDasu
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ python -m venv .venv
$ source .venv/bin/activate
```

Then install the dependencies:

```sh
(.venv)$ pip install -r requirements.txt
```
Note the `(.venv)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment.

Once `pip` has finished downloading the dependencies:
```sh
(.venv)$ cd SupplyChainPlanning
(.venv)$ python manage.py runserver
```
And navigate to `http://127.0.0.1:8000/mainDash/`.

## Admin 
### Access
URL: http://127.0.0.1:8000/admin/
Username: admin
Password: admin

## To Migrate

```sh
(.venv)$ python manage.py makemigrations mainDash
```

```sh
(.venv)$ python manage.py sqlmigrate mainDash 0004
```

```sh
(.venv)$ python manage.py migrate
```