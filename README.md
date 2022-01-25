# Restaurant voting app

Application purpose is to find best place to get lunch. Everyone can retrieve restaurant list, registered user can also
*add/remove/update* restaurants as well as vote for them. Every user gets 5 points (configurable) which can be spended
on voting.

## Install

In order to spin up application in local environment we can use docker-compose:

```bash
# Spin-up containers
$ docker-compose up -d
# To stop containers
$ docker-compose down
# Get bash of app container
$ docker exec -it backend_app_1 bash
# In bash we can add new superusers
$ python ./manage.py createsuperuser
```

> Git repo comes with pre-filled database db.sqlite, remove it if you want to have fresh installation

We are done, app is running!

## Usage

Django REST API comes with "Browsable REST API" UI, that allows more easily to figure out how to use REST API. Local
url: http://localhost:8000/ - please log in before voting.

> Pre-created user: admin/peter/tommy, password: superapp

Endpoints:

- */restaurant/* - List of restaurants, supported methods: GET, POST, OPTIONS
- */restaurant/{pk}/* - Detail restaurant view, GET, PUT, DELETE, OPTIONS
- */restaurant/{pk}/vote/* - voting endpoint, implemented as action. In order to vote for restaurant, make POST request
  to this endpoint.
- */admin/* - Admin site. Only "admin" user has access.

> Voting over Browsable REST API, choose "Extra Action" > Vote when you are in restaurant detail view

Vote count: Every user gets 5 (configurable) votes per day. First user vote on the same restaurant counts as 1, second
as 0.5, 3rd and all subsequent votes, as 0.25.

## Heroku

Running example can be found on: https://lunch-vote01.herokuapp.com/
> Pre-created user: admin/peter/tommy, password: superapp
