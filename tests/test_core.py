# Run tests with: python3 -m unittest tests/*.py

import unittest
from pathlib import Path
from typing import Dict
from unittest.mock import Mock

from provenance_generator.core import ProvenanceGenerator
from provenance_generator.helpers import fake_env


class ProvenanceGeneratorTests(unittest.TestCase):
    def test_provenance_0(self) -> None:
        pg = ProvenanceGenerator(
            environment=self.generate_base_env(),
            compute_hash_fn=self.fake_compute_hash,
            files=[
                self.generate_mock_file("file_1.ext"),
                self.generate_mock_file("file_2.ext"),
            ],
        )

        result = pg.provenance()
        expectation = {
            "_type": "https://in-toto.io/Statement/v1",
            "subject": pg.subject(),
            "predicateType": "https://slsa.dev/provenance/v1",
            "predicate": {
                "buildDefinition": pg.build_definition(),
                "runDetails": pg.run_details(),
            },
        }
        self.assertEqual(result, expectation)

    def test_subject_0(self) -> None:
        pg = ProvenanceGenerator(
            compute_hash_fn=self.fake_compute_hash,
            files=[
                self.generate_mock_file("file_1.ext"),
                self.generate_mock_file("file_2.ext"),
            ],
        )
        expectation = [
            {
                "name": "file_1.ext",
                "digest": {"sha256": "fake_hash:/absolute/file_1.ext"},
            },
            {
                "name": "file_2.ext",
                "digest": {"sha256": "fake_hash:/absolute/file_2.ext"},
            },
        ]
        self.assertEqual(pg.subject(), expectation)

    def test_subject_entry_0(self) -> None:
        pg = ProvenanceGenerator(compute_hash_fn=self.fake_compute_hash)

        result = pg.subject_entry(self.generate_mock_file("name.ext"))
        expectation = {
            "name": "name.ext",
            "digest": {"sha256": "fake_hash:/absolute/name.ext"},
        }
        self.assertEqual(result, expectation)

    def test_build_definition_0(self) -> None:
        env = self.generate_base_env()
        pg = ProvenanceGenerator(environment=env)

        result = pg.build_definition()
        self.assertEqual(
            result["buildType"], "https://buildkite.github.io/slsa-buildtypes/job/v1"
        )
        self.assertEqual(result["externalParameters"]["pipeline"], pg.pipeline())
        self.assertEqual(
            result["externalParameters"]["build"],
            {
                "id": env["BUILDKITE_BUILD_ID"],
                "branch": env["BUILDKITE_BRANCH"],
                "commit": env["BUILDKITE_COMMIT"],
                "number": env["BUILDKITE_BUILD_NUMBER"],
                "repository": env["BUILDKITE_REPO"],
                "tag": env["BUILDKITE_TAG"],
            },
        )
        self.assertEqual(
            result["externalParameters"]["step"],
            {
                "id": env["BUILDKITE_STEP_ID"],
                "command": env["BUILDKITE_COMMAND"],
                "key": env["BUILDKITE_STEP_KEY"],
            },
        )
        self.assertEqual(
            result["externalParameters"]["job"], {"id": env["BUILDKITE_JOB_ID"]}
        )
        self.assertEqual(
            result["internalParameters"]["buildkite"],
            {
                "organization_id": env["BUILDKITE_ORGANIZATION_ID"],
                "pipeline_id": env["BUILDKITE_PIPELINE_ID"],
            },
        )
        self.assertEqual(
            result["resolvedDependencies"][0],
            {
                "uri": pg.repo_uri(),
                "digest": {"gitCommit": env["BUILDKITE_COMMIT"]},
            },
        )

    def test_pipeline_0(self) -> None:
        pg = ProvenanceGenerator(
            environment={
                "BUILDKITE_ORGANIZATION_SLUG": "org_slug",
                "BUILDKITE_PIPELINE_SLUG": "pipe_slug",
            }
        )

        self.assertEqual(pg.pipeline(), "https://buildkite.com/org_slug/pipe_slug")

    def test_repo_uri_0(self) -> None:
        pg = ProvenanceGenerator(
            environment={
                "BUILDKITE_REPO": "https://github.com/buildkite/demokite.git",
                "BUILDKITE_BRANCH": "a_branch",
            }
        )

        self.assertEqual(
            pg.repo_uri(),
            "git+https://github.com/buildkite/demokite@refs/heads/a_branch",
        )

    def test_run_details_0(self) -> None:
        pg = ProvenanceGenerator(environment=self.generate_base_env())

        expectation = {
            "builder": {"id": "https://agent.buildkite.com"},
            "metadata": {"invocationId": pg.invocation_id()},
        }
        self.assertEqual(pg.run_details(), expectation)

    def test_invocation_id_0(self) -> None:
        pg = ProvenanceGenerator(
            environment={
                "BUILDKITE_ORGANIZATION_SLUG": "org_slug",
                "BUILDKITE_PIPELINE_SLUG": "pipe_slug",
                "BUILDKITE_BUILD_NUMBER": "5",
                "BUILDKITE_JOB_ID": "00000000-0000-0000-0000-75f7571c8fbc",
            }
        )

        self.assertEqual(
            pg.invocation_id(),
            "https://buildkite.com/org_slug/pipe_slug/builds/5#00000000-0000-0000-0000-75f7571c8fbc",
        )

    def generate_mock_file(self, name: str) -> Path:
        file = Mock()
        file.name = name
        file.absolute = lambda: "/absolute/{}".format(name)
        return file

    def fake_compute_hash(self, file_path: Path) -> str:
        return "fake_hash:{}".format(file_path)

    def generate_base_env(self) -> Dict[str, str]:
        return fake_env()
