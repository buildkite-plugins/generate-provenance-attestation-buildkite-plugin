import unittest
from typing import Any, Dict, List
from unittest.mock import call, Mock, patch

from provenance_generator.helpers import get_files_and_shas


class HelpersTests(unittest.TestCase):

    @patch("provenance_generator.helpers.ApiClient")
    def test_get_files_and_shas_0(self, mock_api_client: Mock) -> None:
        expectation = [
            dict(path="file_1.ext", sha256sum="fake_sha_1"),
            dict(path="file_2.ext", sha256sum="fake_sha_2"),
        ]

        mock_api_client.return_value = Mock(name="ApiClient")
        mock_api_client.return_value.get_artifacts_list.return_value = expectation

        result = get_files_and_shas(
            query="*.ext",
            build_id="build_1",
            job_id="job_1",
            access_token="access_token",
        )
        mock_api_client.assert_called_with("access_token")

        mock_api_client.return_value.get_artifacts_list.assert_called_with(
            "*.ext", "build_1", "job_1"
        )

        self.assertEqual(result, expectation)

    @patch("provenance_generator.helpers.ApiClient")
    def test_get_files_and_shas_collapses_paths_0(self, mock_api_client: Mock) -> None:
        artifacts_list = [
            dict(path="some/dir/file_1.ext", sha256sum="fake_sha_1"),
            dict(path="some/other/dir/file_2.ext", sha256sum="fake_sha_2"),
        ]

        mock_api_client.return_value = Mock(name="ApiClient")
        mock_api_client.return_value.get_artifacts_list.return_value = artifacts_list

        result = get_files_and_shas(
            query="*.ext",
            build_id="build_1",
            job_id="job_1",
            access_token="access_token",
        )

        self.assertEqual(
            result,
            [
                dict(path="file_1.ext", sha256sum="fake_sha_1"),
                dict(path="file_2.ext", sha256sum="fake_sha_2"),
            ],
        )

    @patch("provenance_generator.helpers.ApiClient")
    def test_get_files_and_shas_handles_subqueries_0(
        self, mock_api_client: Mock
    ) -> None:
        tgz_artifacts_list = [
            dict(path="some/dir/file_1.tgz", sha256sum="fake_sha_1"),
            dict(path="some/other/dir/file_2.tgz", sha256sum="fake_sha_2"),
        ]

        zip_artifacts_list = [
            dict(path="some/dir/file_1.zip", sha256sum="fake_sha_1"),
            dict(path="some/other/dir/file_2.zip", sha256sum="fake_sha_2"),
        ]

        mock_api_client.return_value = Mock(name="ApiClient")

        def mock_get_artifacts_list(query: str, *_: List[Any]) -> List[Dict[str, str]]:
            responses = {"*.tgz": tgz_artifacts_list, "*.zip": zip_artifacts_list}

            return responses[query]

        mock_api_client.return_value.get_artifacts_list.side_effect = (
            mock_get_artifacts_list
        )

        result = get_files_and_shas(
            query="*.tgz; *.zip",
            build_id="build_1",
            job_id="job_1",
            access_token="access_token",
        )

        mock_api_client.return_value.get_artifacts_list.assert_has_calls(
            [call("*.tgz", "build_1", "job_1"), call("*.zip", "build_1", "job_1")]
        )

        self.assertEqual(
            result,
            [
                dict(path="file_1.tgz", sha256sum="fake_sha_1"),
                dict(path="file_2.tgz", sha256sum="fake_sha_2"),
                dict(path="file_1.zip", sha256sum="fake_sha_1"),
                dict(path="file_2.zip", sha256sum="fake_sha_2"),
            ],
        )
