import os

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg2://testapi:{pswd}@barrelapi_postgres_1:5432/testapi"
)
os.environ["WORKFLOWS_CREATE_DAG"] = "True"
