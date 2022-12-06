# Setup DB connection

Edit file `alembic.ini`. You need look at `sqlalchemy.url` field for bind with DB. And edit `file_template` field for
creating pretty migration module names
For example:

```ini
sqlalchemy.url = postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}
file_template = %%(year)d-%%(month).2d-%%(day).2d_%%(rev)s_%%(slug)s
```

# Migration create

```commandline
alembic revision --autogenerate -m "Some message"
```

How it's work?
You need add your app package to settings.main.APP_MODULES list. Next step is initialization project's alembic with
alembic/env.py and custom function `get_project_models_metadata()`.
Function `get_project_models_metadata()` append all metadata objects to list for field `target_metadata`. Target
metadata objects is observed Models to check changes and add new Models.

# Migrate

```commandline
alembic upgrade head
```

# Rollback last migrate

```commandline
alembic downgrade -1
```

Package for migration chains is `alembic/versions`. Package contains .py scripts with upgrade and downgrade scenarios.