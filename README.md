# backend
🤮🤮🤮

Install with: `pip install -r requirements.txt`

Start with: `uvicorn src.main:app --reload`

## Development

Start the DB with `docker compose up`

You can access the admin interface at [http://localhost:15433](http://localhost:15433)

The DB is available at `postgresql://postgres:password@localhost:15432/postgres`, with the login with:
- username: `postgres`
- password: `password`
- database: `postgres`
- host: `localhost`
- port: `15432`

Seed the database with `python data_to_db.py`

###

Generate new migration revision: `alembic revision --autogenerate -m "initial setup"`


Perform the migration: `alembic upgrade head`
