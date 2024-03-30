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


Perform the migration: `alembic upgrade head`


Seed the database with `python data_to_db.py`

###

Generate new migration revision: `alembic revision --autogenerate -m "initial setup"`


```mermaid
flowchart LR
    A(Provide Guidance) --> B(Consolidate Information)
    B --> B1(Concise description of\n MSCI option and benefits)
    B --> B2(Quickly accessible)
    B2 --> B21(Visible to public)
    B --> B3(Incorporate data\n from multiple sources\nin scraped data)
    B3 --> B31(Get data)
    B31 --> B311(Scrape website\n e.g. UG Course Calendar,\n UG Schedule of Classes)
    B31 --> B312(EngAdvisor Integration)
    A --> C(Planning/Scheduling)
    C --> C1(Get past data)
    C --> C2(Analyze data)
    C1 --> C11(Data exploration)
    C2 --> C21(Data exploration)
    C2 --> C22(By Home Department)
    C2 --> C23(Most common course paths)
    C2 --> C24(Trends over time)
```


