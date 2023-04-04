# Training project: foodgram - а service where everyone can share recipes.

## Working project can be found here:
http://158.160.49.18

Admin panel: 
http://158.160.49.18/admin/
login:
superuser
password:
superuser

## GitHub Action status:
![foodgaram workflow](https://github.com/damarkevich/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## Technologies used:
Python3, Django Framework, Django Rest Framework, Postgresql, Djoser, JWT, docker, docker-compose, Nginx, GitHub Actions

## Important note:
The react frontend was provided by the Yandex Practicum training platform. I developed only the backend part, set up containerization, deployed the project.

## Project description:

On this service, users will be able to publish recipes, subscribe to publications of other users, add their favorite recipes to the "Favorites" list, and before going to the store, download a summary list of products needed to prepare one or more selected dishes.

The project is pack into a docker container.

Separate frontend and backend containers are connected to each other via API.
The API documentation is available at: http://158.160.49.18/api/docs/redoc.html

When uploading to GitHub, GitHub Actions starting: The project image is automatically collected and sent to the DockerHub. Next, this image is deploing and starting on the server.

To use this feature you need to fill secrets section in GitHub actions: DB_ENGINE, DB_NAME, POSTGRES_USER, POSTGRES_PASSWORD, DB_HOST, DB_PORT, HOST, DOCKER_USERNAME, DOCKER_PASSWORD, USER, SSH_KEY, PASSPHRASE


## How to launch a project:

Clone the repository and switch to it on the command line:

```
git clone git@github.com:Damarkevich/foodgram-project-react.git
```

```
cd foodgram-project-react/infra
```

Create and fill .env file according to sample ".env.example":

```
cp .env.example .env
```
```
nano .env 
```

Create and run docker-compose container:

```
docker-compose up
```

Run migrations:

```
docker-compose exec backend python manage.py migrate
```

Create superuser:

```
docker-compose exec backend python manage.py createsuperuser
```

Collect static:

```
docker-compose exec backend python manage.py collectstatic --no-input 
```

Project localy reacheble at:

```
http://localhost/
```

## .ENV example:

```
SECRET_KEY=
DB_ENGINE=
DB_NAME=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=
DB_PORT=
```

## Project author

```
Dmitrii Markevich
github: https://github.com/Damarkevich/
```