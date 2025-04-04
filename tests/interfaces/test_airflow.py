from httpx import RequestError, codes

from unittest.mock import patch

from testapi.interfaces.airflow import AirflowInterface


class TestAirflow:
    @patch("testapi.interfaces.airflow.httpx.post")
    async def test_create_dag_success(self, mock_post, create_dag_data):
        """
        GIVEN load balancer host is up and running
        WHEN create_dag method is called, it creates a DAG
        THEN it returns success response
        """
        mock_post.return_value.status_code = codes.CREATED
        airflow = AirflowInterface(
            load_balancer_host=create_dag_data.get("load_balancer_host")
        )
        assert await airflow.create_dag(
            workflow_data=create_dag_data.get("workflow_data")
        ) == create_dag_data.get("success_response")

    @patch("testapi.interfaces.airflow.httpx.post")
    async def test_create_dag_failed(self, mock_post, create_dag_data):
        """
        GIVEN load balancer host is up and running
        WHEN create_dag method is called, it fails to create a DAG
        THEN it returns failure response
        """
        mock_post.side_effect = RequestError("Failed to create DAG")
        airflow = AirflowInterface(
            load_balancer_host=create_dag_data.get("load_balancer_host")
        )
        assert await airflow.create_dag(
            workflow_data=create_dag_data.get("workflow_data")
        ) == create_dag_data.get("failure_response")

    @patch("testapi.interfaces.airflow.httpx.post")
    async def test_create_dag_server_error(self, mock_post, create_dag_data):
        """
        GIVEN load balancer host is up and running
        WHEN create_dag method is called and server error happens
        THEN it returns failure response
        """
        mock_post.return_value.status_code = codes.INTERNAL_SERVER_ERROR
        airflow = AirflowInterface(
            load_balancer_host=create_dag_data.get("load_balancer_host")
        )
        assert await airflow.create_dag(
            workflow_data=create_dag_data.get("workflow_data")
        ) == create_dag_data.get("internal_error_response")

    @patch("testapi.interfaces.airflow.httpx.delete")
    async def test_delete_dag_success(self, mock_delete, delete_dag_data):
        """
        GIVEN load balancer host is up and running
        WHEN delete_dag method is called, it deletes a DAG
        THEN it returns success response
        """
        mock_delete.return_value.status_code = codes.OK
        airflow = AirflowInterface(
            load_balancer_host=delete_dag_data.get("load_balancer_host")
        )
        assert await airflow.delete_dag(
            workflow_name=delete_dag_data.get("workflow_data", {}).get("name")
        ) == delete_dag_data.get("success_response")

    @patch("testapi.interfaces.airflow.httpx.delete")
    async def test_delete_dag_failed(self, mock_delete, delete_dag_data):
        """
        GIVEN load balancer host is up and running
        WHEN delete_dag method is called, it fails to delete a DAG
        THEN it returns failure response
        """
        mock_delete.return_value.status_code = codes.INTERNAL_SERVER_ERROR
        airflow = AirflowInterface(
            load_balancer_host=delete_dag_data.get("load_balancer_host")
        )
        assert await airflow.delete_dag(
            workflow_name=delete_dag_data.get("workflow_data", {}).get("name")
        ) == delete_dag_data.get("internal_error_response")
