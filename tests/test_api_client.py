import json
import unittest
from unittest.mock import Mock, patch

from attestation_generator.api_client import ApiClient


class ApiClientTests(unittest.TestCase):

    @patch("attestation_generator.api_client.HTTPSConnection")
    def test_get_artifacts_list(self, mock_HTTPSConnection: Mock) -> None:
        expectation = [
            dict(path="file_1.ext", sha256sum="fake_sha_1"),
            dict(path="file_2.ext", sha256sum="fake_sha_2"),
        ]

        json_body = bytearray(json.dumps(expectation), encoding="utf-8")

        mock_HTTPSConnection.return_value.getresponse.return_value.status = 200
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

    @patch("builtins.print")  # mock_print
    @patch("builtins.exit")  # mock_exit
    @patch("attestation_generator.api_client.HTTPSConnection")  # mock_HTTPSConnection
    def test_get_artifacts_list_error_exits_on_unsuccessful_status_code(
        self,
        mock_HTTPSConnection: Mock,
        mock_exit: Mock,
        mock_print: Mock,
    ) -> None:

        class ExitException(Exception):
            pass

        def mock_exit_fn(_: int) -> None:
            raise ExitException

        mock_exit.side_effect = mock_exit_fn

        mock_HTTPSConnection.return_value.getresponse.return_value.status = 400
        mock_HTTPSConnection.return_value.getresponse.return_value.read.return_value = (
            b'{"fake": "json"}'
        )

        api_client = ApiClient("fake_token")

        with self.assertRaises(ExitException):
            api_client.get_artifacts_list(
                query="*.gem", build_id="build_1", job_id="job_1"
            )

        mock_exit.assert_called_with(1)
        self.assertEqual(len(mock_print.call_args_list), 4)
