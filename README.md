# SupplyChainDash application

## Setup

The first thing to do is to clone the repository:

# Clone from GitHub
```sh
$ git clone https://github.com/k3smith/supply-chain-dash.git
$ cd SupplyChainDash
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

## Generate data files
```sh
python utility\data_gen_suppliers.py
python utility\data_mappers_parts.py
```

## Run Django
**If this is the first time running the Django app, follow the steps in the "To Migrate" section below first.**

Once `pip` has finished downloading the dependencies:
```sh
(.venv)$ cd SupplyChainPlanning
(.venv)$ python manage.py runserver
```
And navigate to `http://127.0.0.1:8000/mainDash/`.

### Loading Data files
You will need to load the data files you generated `mock_bom_data.csv` and `mock_supplier_data.csv` the first time you run the dashboard application. There are green buttons in the lower left corner to "Link Data Sets". 

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
(.venv)$ python manage.py sqlmigrate mainDash ****
```

```sh
(.venv)$ python manage.py migrate
```
