from datetime import datetime
from uuid import uuid4

from sqlalchemy import create_engine, text
import pytest
import toml

from starlette.testclient import TestClient
from sqlmodel import SQLModel, Session

from api_framework.app import app as fastapi_app
from api_framework.exceptions import InvalidActionError
from api_framework.user import models
from testcontainers.postgres import PostgresContainer


WORKFLOW_NOT_EXIST_CODE = "workflows.error.017"

WORKFLOW_DOES_NOT_EXIST = "Workflow does not exist"

WORKFLOW_DESCRIPTION = "this is another test"


@pytest.fixture(scope="session")
def app():
    app = fastapi_app
    # app.config.update({"TESTING": True})

    @app.get("/test-non-existing-error")
    def trigger_non_existing_error():
        raise ValueError("This end point results in an error")

    @app.get("/test-existing-error")
    def trigger_existing_error():
        raise InvalidActionError

    yield app


@pytest.fixture(scope="module")
def client(app):
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="function")
def info_data():
    with open("pyproject.toml", "r") as f:
        pyproject_data = toml.load(f)
        version = pyproject_data.get("project", {}).get("version")

    return {
        "response_data": {
            "version": version,
            "aws_default_region": "us-east-1",
            "aws_endpoint_url": None,
            "base_url_prefix": "/framework/api/v1",
            "debug_mode": False,
            "database_url": "postgresql+psycopg2://api:{pswd}@api_postgres_1:5432/api",
            "api_log_type": "json",
            "json_log_format": """{
        "Name":            "name",
        "Levelno":         "levelno",
        "Levelname":       "levelname",
        "Pathname":        "pathname",
        "Filename":        "filename",
        "Module":          "module",
        "Lineno":          "lineno",
        "FuncName":        "funcName",
        "Created":         "created",
        "Asctime":         "asctime",
        "Process":         "process",
        "Message":         "message"
    }""",
            "logger_name": "testapi",
            "log_level": "INFO",
            "standard_log_format": "[%(asctime)s] [%(process)s] [%(name)s:%(module)s:%(funcName)s] [%(levelname)s]  %(message)s",
        },
        "response_code": 200,
    }


@pytest.fixture(scope="module")
def database_session():
    # Start a PostgreSQL container
    with PostgresContainer("postgres") as postgres:
        # Get the connection URL from the container
        connection_url = postgres.get_connection_url()

        # Create a SQLAlchemy engine
        engine = create_engine(connection_url)

        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS user_example;"))
            conn.execute(text("commit;"))

        # Create tables in the database
        SQLModel.metadata.create_all(bind=engine)

        with Session(engine) as session:
            yield session

            session.close()


@pytest.fixture(scope="function")
def headers():
    return {
        "x_auth_key": f"spr:clt::{uuid4()}",
        "x_tenant_id": f"spr:user::{uuid4()}",
    }


@pytest.fixture(scope="function")
def workflow_data():
    return [
        dict(
            name="test_workflow",
            description="this is a test",
            steps=[
                dict(
                    name="step1",
                    display_name="step1",
                    type="renamer",
                    index=1,
                    inputs={"mapping": "a"},
                )
            ],
            inputs=[{"name": "dataset", "type": "Dataset"}],
            status="draft",
        ),
        dict(
            name="test_workflow_new",
            description="this is a new test",
            steps=[
                dict(
                    name="step1",
                    display_name="step1",
                    type="renamer",
                    index=1,
                    inputs={"mapping": "a"},
                ),
                dict(
                    name="step2",
                    display_name="step2",
                    type="mapper",
                    index=2,
                    inputs={"mapping": "d"},
                ),
            ],
            inputs=[{"name": "dataset", "type": "Dataset"}],
            status="published",
        ),
    ]


@pytest.fixture(scope="function")
def update_workflow_data(create_workflow_data):
    error_message = "Error while creating DAG"
    return {
        **create_workflow_data,
        "payload": create_workflow_data.get("payload") | {"status": "published"},
        "create_dag_success": {"status": "success", "error_message": None},
        "create_dag_failure": {"status": "failed", "error_message": error_message},
        "failed_response": create_workflow_data.get("expected_response")
        | {"status": "error", "errorMessage": error_message},
        "expected_status_code": 200,
    }


@pytest.fixture(scope="function")
def create_workflow_data():
    return {
        "payload": {
            "name": "test_workflow_v2",
            "description": WORKFLOW_DESCRIPTION,
            "steps": [
                {
                    "name": "step1",
                    "type": "renamer",
                    "index": 1,
                    "inputs": {"mapping": "a"},
                }
            ],
            "inputs": [{"name": "dataset", "type": "Dataset"}],
            "status": "draft",
        },
        "workflow": models.Workflow(
            name="test_workflow_v2",
            modify_date=datetime(2025, 1, 30, 8, 8, 37, 733738),
            create_date=datetime(2025, 1, 30, 8, 8, 37, 731132),
            description=WORKFLOW_DESCRIPTION,
            status="draft",
            error_message=None,
            steps=[
                models.WorkflowStep(
                    name="step1",
                    type="renamer",
                    index=1,
                    display_name="Step1",
                    inputs={"mapping": "a"},
                ),
            ],
            inputs=[models.WorkflowInput(name="dataset", type="Dataset")],
        ),
        "expected_response": {
            "name": "test_workflow_v2",
            "description": WORKFLOW_DESCRIPTION,
            "inputs": [{"name": "dataset", "type": "Dataset"}],
            "steps": [
                {
                    "name": "step1",
                    "type": "renamer",
                    "index": 1,
                    "inputs": {"mapping": "a"},
                    "displayName": "Step1",
                }
            ],
            "status": "draft",
            "errorMessage": None,
        },
        "expected_status_code": 201,
    }


@pytest.fixture(scope="function")
def delete_workflow_data():
    return {
        "name": "test_workflow_v2",
        "expected_response": {"message": "Workflow deleted: test_workflow_v2"},
        "expected_status_code": 200,
    }


@pytest.fixture(scope="function")
def get_workflows_data():
    return {
        "expected_response": [
            {
                "name": "test_workflow_v2",
                "description": WORKFLOW_DESCRIPTION,
                "inputs": [{"name": "dataset", "type": "Dataset"}],
                "steps": [
                    {
                        "name": "step1",
                        "type": "renamer",
                        "index": 1,
                        "inputs": {"mapping": "a"},
                        "displayName": "Step1",
                    }
                ],
                "status": "draft",
                "errorMessage": None,
            }
        ],
        "get_all_workflow": [
            {
                "name": "test_workflow_v2",
                "description": WORKFLOW_DESCRIPTION,
                "inputs": [
                    models.WorkflowInput(
                        name="dataset",
                        type="Dataset",
                        create_date=datetime(2025, 1, 17, 12, 26, 16, 108465),
                        modify_date=datetime(2025, 1, 17, 12, 26, 16, 108466),
                        id=1,
                        workflow_id=1,
                    )
                ],
                "steps": [
                    models.WorkflowStep(
                        create_date=datetime(2025, 1, 17, 12, 26, 16, 108341),
                        modify_date=datetime(2025, 1, 17, 12, 26, 16, 108342),
                        id=1,
                        inputs={"mapping": "a"},
                        type="renamer",
                        display_name="Step1",
                        name="step1",
                        index=1,
                        workflow_id=1,
                    )
                ],
                "status": "draft",
            }
        ],
        "expected_status_code": 200,
    }


@pytest.fixture(scope="function")
def get_workflow_data():
    return {
        "workflow": models.Workflow(
            name="test_workflow_v2",
            description=WORKFLOW_DESCRIPTION,
            inputs=[
                models.WorkflowInput(
                    name="dataset",
                    type="Dataset",
                    create_date=datetime(2025, 1, 17, 12, 26, 16, 108465),
                    modify_date=datetime(2025, 1, 17, 12, 26, 16, 108466),
                    id=1,
                    workflow_id=1,
                )
            ],
            steps=[
                models.WorkflowStep(
                    create_date=datetime(2025, 1, 17, 12, 26, 16, 108341),
                    modify_date=datetime(2025, 1, 17, 12, 26, 16, 108342),
                    id=1,
                    inputs={"mapping": "a"},
                    type="renamer",
                    display_name="Step1",
                    name="step1",
                    index=1,
                    workflow_id=1,
                )
            ],
            status="draft",
        ),
        "expected_response": {
            "name": "test_workflow_v2",
            "description": WORKFLOW_DESCRIPTION,
            "inputs": [{"name": "dataset", "type": "Dataset"}],
            "steps": [
                {
                    "name": "step1",
                    "type": "renamer",
                    "index": 1,
                    "inputs": {"mapping": "a"},
                    "displayName": "Step1",
                }
            ],
            "status": "draft",
            "errorMessage": None,
        },
        "expected_status_code": 200,
    }


@pytest.fixture(scope="function")
def migrate_workflow_data(create_workflow_data, create_dag_data):
    return {
        "name": "test_workflow_v1",
        "workflow": create_workflow_data.get("workflow"),
        "payload": {
            "workflows": [
                "spr:bz:pipeline::test_workflow_v1:1",
            ]
        },
        "payload_null": {"workflows": None},
        "old_pipeline_data": [
            {
                "pipeline_state_id": 1,
                "pipeline_id": "spr:bz:pipeline::test_workflow_v1:1",
                "pipeline_code": "test_workflow_v1",
                "version_number": 1,
                "created": 1737366950150,
                "last_updated": 1737366950150,
                "data": {
                    "info": {
                        "code": "test_workflow_v1",
                        "description": "This is a test workflow for v1 routes",
                        "displayName": "test_workflow_v1",
                        "pipelineType": "",
                        "versionNumber": 1,
                    },
                    "tags": {"tags": {}},
                    "inputs": {
                        "dataset": {
                            "description": "The person's first name.",
                            "type": "Dataset",
                        }
                    },
                    "allSteps": [
                        {
                            "displayName": "step1",
                            "inputs": {"mapping": "a"},
                            "name": "step1",
                            "stepIndex": 1,
                            "stepType": "renamer",
                            "stepVersionNumber": None,
                        }
                    ],
                    "schedule": None,
                    "copiedFrom": None,
                    "pipelineId": "spr:bz:pipeline::test_workflow_v1:1",
                    "isPublished": False,
                    "lastUpdated": 1737366950150,
                    "maxVersionNumber": 1,
                },
            },
            {
                "pipeline_state_id": 2,
                "pipeline_id": "spr:bz:pipeline::test_workflow_v1:2",
                "pipeline_code": "test_workflow_v1",
                "version_number": 2,
                "created": 1737366950150,
                "last_updated": 1737366950150,
                "data": {
                    "info": {
                        "code": "test_workflow_v1",
                        "description": "This is a test workflow for v1 routes",
                        "displayName": "test_workflow_v1",
                        "pipelineType": "",
                        "versionNumber": 2,
                    },
                    "tags": {"tags": {}},
                    "inputs": {
                        "dataset": {
                            "description": "The person's last name.",
                            "type": "Dataset",
                        }
                    },
                    "allSteps": [
                        {
                            "displayName": "step1",
                            "inputs": {"mapping": "a"},
                            "name": "step1",
                            "stepIndex": 1,
                            "stepType": "renamer",
                            "stepVersionNumber": None,
                        }
                    ],
                    "schedule": None,
                    "copiedFrom": None,
                    "pipelineId": "spr:bz:pipeline::test_workflow_v1:2",
                    "isPublished": True,
                    "lastUpdated": 1737366950150,
                    "maxVersionNumber": 1,
                },
            },
        ],
        "dag_success_response": create_dag_data.get("success_response"),
        "dag_failure_response": create_dag_data.get("failure_response"),
        "expected_response_for_all": {
            "message": "Success=2 and Failure=0",
            "success": [
                "spr:bz:pipeline::test_workflow_v1:1",
                "spr:bz:pipeline::test_workflow_v1:2",
            ],
            "failure": [],
        },
        "expected_response_for_pipeline": {
            "message": "Success=1 and Failure=0",
            "success": ["spr:bz:pipeline::test_workflow_v1:1"],
            "failure": [],
        },
        "error_response": {
            "message": "No workflows found",
            "success": None,
            "failure": None,
        },
        "error_status_code": 404,
        "expected_status_code": 200,
    }


@pytest.fixture(scope="function")
def create_dag_data():
    return {
        "workflow_data": {
            "name": "test_workflow",
            "steps": [
                {
                    "name": "step2",
                    "type": "renamer",
                    "index": 1,
                    "inputs": {"mapping1": "a", "mapping2": "b"},
                    "display_name": "Step2",
                }
            ],
        },
        "success_response": {"status": "created", "error_message": None},
        "failure_response": {
            "status": "failed",
            "error_message": "Failed to create DAG",
        },
        "internal_error_response": {
            "status": "failed",
            "error_message": "Failed to create DAG. See Airflow2 Webserver Logs for more details",
        },
        "load_balancer_host": "http://localhost",
    }


@pytest.fixture(scope="function")
def delete_dag_data(create_dag_data):
    return {
        **create_dag_data,
        "success_response": {"status": "deleted", "error_message": None},
        "internal_error_response": {
            "status": "failed",
            "error_message": "Failed to delete DAG. See Airflow2 Webserver Logs for more details",
        },
    }
