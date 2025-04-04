# Test API

A common framework based off FastAPI, Pydantic, Pydantic Settings, SqlModel, Alembic and 
other established Python libraries and best practices with dictionary logging config.  The
project is managed by `uv` and formatted/linted using `ruff`.

### Create database revision

    DATABASE_URL="postgresql+psycopg2://testapi:testapi@0.0.0.0:5440/testapi" alembic --config testapi/alembic.ini revision --autogenerate -m "<enter message here>"
