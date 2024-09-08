import json
import unittest
from unittest.mock import Mock, patch

from provenance_generator.api_client import ApiClient


class ApiClientTests(unittest.TestCase):

    @patch("provenance_generator.api_client.HTTPSConnection")
    def test_get_artifacts_list_0(self, mock_HTTPSConnection: Mock) -> None:
        expectation = [
            dict(path="file_1.ext", sha256sum="fake_sha_1"),
            dict(path="file_2.ext", sha256sum="fake_sha_2"),
        ]

        json_body = json.dumps(expectation)

        mock_HTTPSConnection.return_value = Mock(name="HTTPSConnection")
        mock_HTTPSConnection.return_value.getresponse.return_value.read.return_value = (
            json_body
        )

        api_client = ApiClient("fake_token")

        result = api_client.get_artifacts_list(
            query="*.gem", build_id="build_1", job_id="job_1"
        )

        mock_HTTPSConnection.return_value.request.assert_called_with(
            "GET",
            "/v3/builds/build_1/artifacts/search?query=%2A.gem&scope=job_1",
            headers={
                "Host": "agent.buildkite.com",
                "Authorization": "Token fake_token",
            },
        )
        self.assertEqual(result, expectation)
