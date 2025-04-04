from testapi import app_settings


class TestCommonRoutes:
    def test_get_info(self, client, info_data):
        """
        GIVEN client is up and running
        WHEN get_info endpoint is called
        THEN it returns the config info
        """
        expected_response = info_data.get("response_data", {})
        expected_status_code = info_data.get("response_code", 200)
        actual_response = client.get(
            f"{app_settings.base_url_prefix}/common/api/v1/info"
        )
        assert actual_response.status_code == expected_status_code
        assert actual_response.json() == expected_response

    def test_get_healthcheck(self, client):
        """
        GIVEN client is up and running
        WHEN get_healthcheck endpoint is called
        THEN it returns the response data
        """
        expected_response = {"msg": "Happy"}
        expected_status_code = 200
        actual_response = client.get(
            f"{app_settings.base_url_prefix}/common/api/v1/healthcheck"
        )
        assert actual_response.status_code == expected_status_code
        assert actual_response.json() == expected_response
