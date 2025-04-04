from unittest.mock import patch

from testapi import app_settings


class TestRouters:
    @patch("testapi.workflows.service.WorkflowService.create_workflow")
    def test_create_workflow(
        self, mock_create_workflow, client, headers, create_workflow_data
    ):
        """
        GIVEN client is up and running
        WHEN create workflow endpoint is called
        THEN it create the workflow and returns the response
        """
        payload = create_workflow_data.get("payload")
        expected_response = create_workflow_data.get("expected_response")
        expected_status_code = create_workflow_data.get("expected_status_code")
        mock_create_workflow.return_value = create_workflow_data.get("workflow")
        actual_response = client.post(
            f"{app_settings.base_url_prefix}/workflows/api/v1/create-workflow",
            headers=headers,
            json=payload,
        )
        assert actual_response.status_code == expected_status_code
        assert actual_response.json() == expected_response

    @patch("testapi.interfaces.airflow.AirflowInterface.create_dag")
    @patch("testapi.workflows.service.WorkflowService.save_workflow")
    @patch("testapi.workflows.service.WorkflowService.update_workflow")
    def test_update_workflow_when_dag_success(
        self,
        mock_update_workflow,
        mock_save_workflow,
        mock_create_dag,
        client,
        headers,
        update_workflow_data,
    ):
        """
        GIVEN client is up and running
        WHEN update workflow endpoint is called
        THEN it updates the workflow and creates the dag so status will be published
        """
        payload = update_workflow_data.get("payload")
        expected_response = update_workflow_data.get("expected_response")
        expected_status_code = update_workflow_data.get("expected_status_code")
        mock_update_workflow.return_value = update_workflow_data.get("workflow")
        mock_save_workflow.return_value = None
        mock_create_dag.return_value = update_workflow_data.get("create_dag_success")
        actual_response = client.put(
            f"{app_settings.base_url_prefix}/workflows/api/v1/update-workflow",
            headers=headers,
            json=payload,
        )
        assert actual_response.status_code == expected_status_code
        assert actual_response.json() == expected_response

    @patch("testapi.interfaces.airflow.AirflowInterface.create_dag")
    @patch("testapi.workflows.service.WorkflowService.save_workflow")
    @patch("testapi.workflows.service.WorkflowService.update_workflow")
    def test_update_workflow_when_dag_failed(
        self,
        mock_update_workflow,
        mock_save_workflow,
        mock_create_dag,
        client,
        headers,
        update_workflow_data,
    ):
        """
        GIVEN client is up and running
        WHEN update workflow endpoint is called
        THEN it updates the workflow but dag fails to create so status will be error
        """
        payload = update_workflow_data.get("payload")
        expected_response = update_workflow_data.get("failed_response")
        expected_status_code = update_workflow_data.get("expected_status_code")
        mock_update_workflow.return_value = update_workflow_data.get("workflow")
        mock_save_workflow.return_value = None
        mock_create_dag.return_value = update_workflow_data.get("create_dag_failure")
        actual_response = client.put(
            f"{app_settings.base_url_prefix}/workflows/api/v1/update-workflow",
            headers=headers,
            json=payload,
        )
        assert actual_response.status_code == expected_status_code
        assert actual_response.json() == expected_response

    @patch("testapi.workflows.service.WorkflowService.delete_workflow")
    def test_delete_workflow(
        self, mock_delete_workflow, client, headers, delete_workflow_data
    ):
        """
        GIVEN client is up and running
        WHEN delete workflow endpoint is called
        THEN it delete the workflow and returns the response
        """
        expected_response = delete_workflow_data.get("expected_response")
        expected_status_code = delete_workflow_data.get("expected_status_code")
        mock_delete_workflow.return_value = None
        actual_response = client.delete(
            f"{app_settings.base_url_prefix}/workflows/api/v1/delete-workflow/{delete_workflow_data.get('name')}",
            headers=headers,
        )
        assert actual_response.status_code == expected_status_code
        assert actual_response.json() == expected_response

    @patch("testapi.workflows.service.WorkflowService.get_all_workflows")
    def test_get_workflows(
        self, mock_get_all_workflows, client, headers, get_workflows_data
    ):
        """
        GIVEN client is up and running
        WHEN get workflows endpoint is called
        THEN it get all workflow and returns the response
        """
        expected_response = get_workflows_data.get("expected_response")
        expected_status_code = get_workflows_data.get("expected_status_code")
        mock_get_all_workflows.return_value = get_workflows_data.get("get_all_workflow")
        actual_response = client.get(
            f"{app_settings.base_url_prefix}/workflows/api/v1/get-workflows",
            headers=headers,
        )
        assert actual_response.status_code == expected_status_code
        assert actual_response.json() == expected_response

    @patch("testapi.workflows.service.WorkflowService.get_workflow")
    def test_get_workflow(self, mock_get_workflow, client, headers, get_workflow_data):
        """
        GIVEN client is up and running
        WHEN get workflow endpoint is called
        THEN it gets the workflow and returns the response or throws 404 not found
        """
        expected_response = get_workflow_data.get("expected_response")
        expected_status_code = get_workflow_data.get("expected_status_code")
        mock_get_workflow.return_value = get_workflow_data.get("workflow")
        actual_response = client.get(
            f"{app_settings.base_url_prefix}/workflows/api/v1/get-workflow/test_workflow_v2",
            headers=headers,
        )

        assert actual_response.status_code == expected_status_code
        assert actual_response.json() == expected_response

        mock_get_workflow.return_value = None
        actual_response = client.get(
            f"{app_settings.base_url_prefix}/workflows/api/v1/get-workflow/non_existent_workflow_get",
            headers=headers,
        )
        assert actual_response.status_code == 404

    @patch("testapi.workflows.service.WorkflowService.save_workflow")
    @patch("testapi.workflows.routers.AirflowInterface.create_dag")
    @patch("testapi.workflows.routers.get_old_pipeline_data")
    @patch("testapi.workflows.service.WorkflowService.create_workflow")
    def test_migrate_workflow_all_dag_success(
        self,
        mock_create_workflow,
        mock_get_old_pipeline_data,
        mock_create_dag,
        mock_save_workflow,
        client,
        headers,
        migrate_workflow_data,
    ):
        """
        GIVEN client is up and running
        WHEN migrate workflow endpoint is called without pipeline id and DAG creates
        THEN it migrate all the workflow from old to new db and returns the response
        """
        expected_response = migrate_workflow_data.get("expected_response_for_all")
        expected_status_code = migrate_workflow_data.get("expected_status_code")
        mock_get_old_pipeline_data.return_value = migrate_workflow_data.get(
            "old_pipeline_data"
        )
        mock_create_workflow.return_value = migrate_workflow_data.get("workflow")
        mock_create_dag.return_value = migrate_workflow_data.get("dag_success_response")
        mock_save_workflow.return_value = None
        actual_response = client.patch(
            f"{app_settings.base_url_prefix}/workflows/api/v1/migrate-workflow",
            json=migrate_workflow_data.get("payload_null"),
            headers=headers,
        )
        assert actual_response.status_code == expected_status_code
        assert actual_response.json() == expected_response

    @patch("testapi.workflows.service.WorkflowService.save_workflow")
    @patch("testapi.workflows.routers.AirflowInterface.create_dag")
    @patch("testapi.workflows.routers.get_old_pipeline_data")
    @patch("testapi.workflows.service.WorkflowService.create_workflow")
    def test_migrate_workflow_all_dag_failed(
        self,
        mock_create_workflow,
        mock_get_old_pipeline_data,
        mock_create_dag,
        mock_save_workflow,
        client,
        headers,
        migrate_workflow_data,
    ):
        """
        GIVEN client is up and running
        WHEN migrate workflow endpoint is called without pipeline id and DAG creation failed
        THEN it migrate all the workflow from old to new db with DAG error and returns the response
        """
        expected_response = migrate_workflow_data.get("expected_response_for_all")
        expected_status_code = migrate_workflow_data.get("expected_status_code")
        mock_get_old_pipeline_data.return_value = migrate_workflow_data.get(
            "old_pipeline_data"
        )
        mock_create_workflow.return_value = migrate_workflow_data.get("workflow")
        mock_create_dag.return_value = migrate_workflow_data.get("dag_failure_response")
        mock_save_workflow.return_value = None
        actual_response = client.patch(
            f"{app_settings.base_url_prefix}/workflows/api/v1/migrate-workflow",
            json=migrate_workflow_data.get("payload_null"),
            headers=headers,
        )
        assert actual_response.status_code == expected_status_code
        assert actual_response.json() == expected_response

    @patch("testapi.workflows.service.WorkflowService.save_workflow")
    @patch("testapi.workflows.routers.get_old_pipeline_data")
    @patch("testapi.workflows.service.WorkflowService.create_workflow")
    def test_migrate_workflow_pipeline_id_list(
        self,
        mock_create_workflow,
        mock_get_old_pipeline_data,
        mock_save_workflow,
        client,
        headers,
        migrate_workflow_data,
    ):
        """
        GIVEN client is up and running
        WHEN migrate workflow endpoint is called with pipeline id
        THEN it migrate the workflow from old to new db and returns the response
        """
        expected_response = migrate_workflow_data.get("expected_response_for_pipeline")
        expected_status_code = migrate_workflow_data.get("expected_status_code")
        mock_get_old_pipeline_data.return_value = migrate_workflow_data.get(
            "old_pipeline_data"
        )[:1]
        mock_create_workflow.return_value = migrate_workflow_data.get("workflow")
        mock_save_workflow.return_value = None
        actual_response = client.patch(
            f"{app_settings.base_url_prefix}/workflows/api/v1/migrate-workflow",
            json=migrate_workflow_data.get("payload"),
            headers=headers,
        )
        assert actual_response.status_code == expected_status_code
        assert actual_response.json() == expected_response

    @patch("testapi.workflows.routers.get_old_pipeline_data")
    def test_migrate_workflow_error(
        self,
        mock_get_old_pipeline_data,
        client,
        headers,
        migrate_workflow_data,
    ):
        """
        GIVEN client is up and running
        WHEN migrate workflow endpoint is called with pipeline id but it does not exists in old db
        THEN it returns the error response
        """
        expected_response = migrate_workflow_data.get("error_response")
        expected_status_code = migrate_workflow_data.get("expected_status_code")
        mock_get_old_pipeline_data.return_value = None
        actual_response = client.patch(
            f"{app_settings.base_url_prefix}/workflows/api/v1/migrate-workflow",
            json=migrate_workflow_data.get("payload"),
            headers=headers,
        )

        assert actual_response.status_code == expected_status_code
        assert actual_response.json() == expected_response
