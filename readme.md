# Python Flask Stores REST API

## Context

The API can handle stores, items, tags and users. The user can register, login, recieve confirmation email and manage stores, where items are allocated. Tags can be assinged to stores and items both. To manage items, JWT is required.

## Stack

- Python 3.10
- Docker
- Redis
- Postgres 13
- Mailgun (Requires credentials in the .env file to send emails.)
- Flask (with SQLAlchemy, Smorest, JWT Extended, Migrate)

## Basic usage

Documentation: `/swagger-ui`
Postman collection is in `./postman_collection` folder.

1. Prepare the empty DB as shown below in Database section
2. Run flask: `docker-compose up`
3. Port 5005 is listening on localhost.
4. Register and login.
5. Create update delete stores and items, use tags as well.
6. Logout and try to work with items (they require a valid token).

## Database

To prepare the empty DB: `docker-compose run --rm app sh -c "flask db upgrade"`

If no DB path is given by env variables, then it defaults back to SQLite.
The SQLite DB will be located in `./instance` folder as `data.db`.

## Redis

When user registers, the event is collected in a redis queue, that will be processed and forwarded to Mailgun.
The rq worker needs to run separately. Use the same app service to ensure they are sharing the same code.

Run the rq worker in the app service. The name of the worker is given in app.py -> app.queue. </br>
`docker-compose run --rm app sh -c "rq worker -u redis://redis_db:6379 emails"`

## Flask-Migrate commands

Documentation:
* https://flask-migrate.readthedocs.io/en/latest/
* https://rest-apis-flask.teclado.com/docs/flask_migrate/initialize_database_flask_db_init/


This will add a migrations folder to your application.
The contents of this folder need to be added to version control along with your other source files.
```
flask db inin
```

Generate the first or next migration to set up the database
```
flask db migrate
```

Apply migration
```
flask db upgrade
```