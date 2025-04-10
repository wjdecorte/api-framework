from api_framework.common.exceptions import (
    WorkflowDoesNotExistError,
    WorkflowAlreadyExistError,
)
from api_framework.user.services import UserService
import pytest


class TestWorkflowService:
    def test_create_workflow(self, database_session, workflow_data):
        """
        GIVEN database is up and running
        WHEN create workflow method is called
        THEN it adds the workflow in database or throws exception if same workflow already exists in the system
        """
        w = UserService(session=database_session)
        for workflow in workflow_data:
            w.create_workflow(workflow)
            # Fetch the new workflow and verify changes
            new_workflow = w.get_workflow(workflow_name=workflow["name"])
            assert new_workflow.description == workflow["description"]
            assert new_workflow.status == workflow["status"]

            # Verify steps
            new_steps = new_workflow.steps
            expected_steps = workflow["steps"]
            assert len(new_steps) == len(expected_steps)
            for step, expected_step in zip(new_steps, expected_steps):
                assert step.name == expected_step["name"]
                assert step.type == expected_step["type"]
                assert step.index == expected_step["index"]
                assert step.inputs == expected_step["inputs"]
                assert step.display_name == expected_step["display_name"]

            # Verify inputs
            new_inputs = new_workflow.inputs
            expected_inputs = workflow["inputs"]
            assert len(new_inputs) == len(expected_inputs)
            for input_, expected_input in zip(new_inputs, expected_inputs):
                assert input_.name == expected_input["name"]
                assert input_.type == expected_input["type"]

            # Attempt to create a duplicate workflow and verify it raises an exception
            with pytest.raises(WorkflowAlreadyExistError):
                w.create_workflow(workflow)

    def test_update_workflow(self, database_session, workflow_data):
        """
            GIVEN database is up and running
            WHEN update workflow method is called
            THEN it updates the workflow in the database if it exists, raises an exception otherwise,
        and ensures updated attributes are reflected.
        """

        w = UserService(session=database_session)

        non_existent_workflow_name = "non_existent_workflow"
        update_data = {
            "description": "Updated description",
            "name": non_existent_workflow_name,
        }
        with pytest.raises(
            WorkflowDoesNotExistError
        ):  # Assuming you have a custom exception for this case
            with database_session.no_autoflush:
                w.update_workflow(update_data)

        # Scenario 2: Attributes updated indeed got updated
        for workflow in workflow_data:
            # Update the workflow
            updated_data = {
                "description": "New Description",
                "status": "draft",
                "name": workflow.get("name"),
                "steps": [
                    {
                        "name": "step2",
                        "type": "renamer2",
                        "index": 1,
                        "inputs": {"mapping": "b"},
                        "display_name": "Step2",
                    }
                ],
                "inputs": [
                    {"name": "test", "type": "Dataset"},
                    {"name": "test", "type": "test"},
                ],
            }
            with database_session.no_autoflush:
                w.update_workflow(updated_data)

            # Fetch the updated workflow and verify changes
            updated_workflow = w.get_workflow(workflow_name=workflow["name"])
            assert updated_workflow.description == "New Description"
            assert updated_workflow.status == updated_data.get("status")

            # Verify steps
            updated_steps = updated_workflow.steps
            expected_steps = updated_data["steps"]
            assert len(updated_steps) == len(expected_steps)
            for step, expected_step in zip(updated_steps, expected_steps):
                assert step.name == expected_step["name"]
                assert step.type == expected_step["type"]
                assert step.index == expected_step["index"]
                assert step.inputs == expected_step["inputs"]
                assert step.display_name == expected_step["display_name"]

            # Verify inputs
            updated_inputs = updated_workflow.inputs
            expected_inputs = updated_data["inputs"]
            assert len(updated_inputs) == len(expected_inputs)
            for input_, expected_input in zip(updated_inputs, expected_inputs):
                assert input_.name == expected_input["name"]
                assert input_.type == expected_input["type"]

    def test_get_all_workflows(self, database_session, workflow_data):
        """
        GIVEN database is up and running
        WHEN get all workflows method is called
        THEN it gets the workflows from database
        """
        w = UserService(session=database_session)
        searched_workflows = w.get_user(search="new")
        assert len(searched_workflows) == 1

        for actual_workflow, expected_workflow in zip(w.get_user(), workflow_data):
            assert actual_workflow.model_dump()["name"] == expected_workflow["name"]

    def test_get_workflow(self, database_session, workflow_data):
        """
        GIVEN database is up and running
        WHEN get workflow method is called
        THEN it gets the workflow from database
        """
        w = UserService(session=database_session)

        assert w.get_workflow(workflow_name="non_existing_workflow") is None

        for workflow in workflow_data:
            assert (
                w.get_workflow(workflow_name=workflow["name"]).name == workflow["name"]
            )

    def test_delete_workflow_by_workflow_name(self, database_session, workflow_data):
        """
        GIVEN database is up and running
        WHEN delete workflow method is called with workflow_name
        THEN it delete the workflow associated with that name from database
        """
        w = UserService(session=database_session)
        with pytest.raises(WorkflowDoesNotExistError):
            w.delete_workflow(workflow_name="non_existing_workflow")

        w.delete_workflow(workflow_name=workflow_data[0]["name"])
        assert w.get_workflow(workflow_name=workflow_data[0]["name"]) is None

    def test_save_workflow(self, database_session, create_workflow_data):
        """
        GIVEN database is up and running
        WHEN save workflow method is called with workflow data
        THEN it save the workflow in the database
        """
        w = UserService(session=database_session)
        workflow = create_workflow_data.get("workflow")
        w.save_workflow(workflow=workflow)
        assert w.get_workflow(workflow_name=workflow.name) is workflow
