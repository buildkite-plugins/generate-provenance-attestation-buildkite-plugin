import re
import urllib.parse
from typing import Any, Callable, Dict, List, Mapping

from provenance_generator.path_sha import PathSha


class ProvenanceGenerator:
    def __init__(
        self,
        environment: Mapping[str, str] = {},
        files: List[PathSha] = [],
    ):
        self.environment = dict(environment.items())
        self.files = files

    def _env(self, key: str) -> str:
        return self.environment[key]

    def provenance(self) -> Dict[str, Any]:
        return {
            "_type": "https://in-toto.io/Statement/v1",
            "subject": self.subject(),
            "predicateType": "https://slsa.dev/provenance/v1",
            "predicate": {
                "buildDefinition": self.build_definition(),
                "runDetails": self.run_details(),
            },
        }

    def subject(self) -> List[Dict[str, Any]]:
        fn: Callable[[PathSha], Dict[str, Any]] = lambda path_sha: {
            "name": path_sha["path"],
            "digest": {"sha256": path_sha["sha256sum"]},
        }

        return list(map(fn, self.files))

    def build_definition(self) -> Dict[str, Any]:
        return {
            "buildType": "https://buildkite.github.io/slsa-buildtypes/job/v1",
            "externalParameters": {
                "pipeline": self.pipeline(),
                "repository": self._env("BUILDKITE_REPO"),
                "build": {
                    "branch": self._env("BUILDKITE_BRANCH"),
                    "commit": self._env("BUILDKITE_COMMIT"),
                    "tag": self._env("BUILDKITE_TAG"),
                },
                "step": {
                    "id": self._env("BUILDKITE_STEP_ID"),
                    "command": self._env("BUILDKITE_COMMAND"),
                    "key": self._env("BUILDKITE_STEP_KEY"),
                },
                "job": {"id": self._env("BUILDKITE_JOB_ID")},
            },
            "internalParameters": {
                "buildkite": {
                    "organization_id": self._env("BUILDKITE_ORGANIZATION_ID"),
                    "pipeline_id": self._env("BUILDKITE_PIPELINE_ID"),
                    "build_id": self._env("BUILDKITE_BUILD_ID"),
                    "build_number": self._env("BUILDKITE_BUILD_NUMBER"),
                }
            },
            "resolvedDependencies": [
                {
                    "uri": self.repo_uri(),
                    "digest": {"gitCommit": self._env("BUILDKITE_COMMIT")},
                }
            ],
        }

    def pipeline(self) -> str:
        return "https://buildkite.com/{}/{}".format(
            self._env("BUILDKITE_ORGANIZATION_SLUG"),
            self._env("BUILDKITE_PIPELINE_SLUG"),
        )

    def repo_uri(self) -> str:
        result = urllib.parse.urlparse(self._env("BUILDKITE_REPO"))
        path = re.sub(r"\.git$", "", result.path)
        return "git+https://{}{}@refs/heads/{}".format(
            result.netloc, path, self._env("BUILDKITE_BRANCH")
        )

    def run_details(self) -> Dict[str, Any]:
        return {
            "builder": {
                "id": "https://github.com/buildkite-plugins/generate-build-provenance-buildkite-plugin@refs/heads/main"
            },
            "metadata": {
                "invocationId": self.invocation_id(),
            },
        }

    def invocation_id(self) -> str:
        return "https://buildkite.com/{}/{}/builds/{}#{}".format(
            self._env("BUILDKITE_ORGANIZATION_SLUG"),
            self._env("BUILDKITE_PIPELINE_SLUG"),
            self._env("BUILDKITE_BUILD_NUMBER"),
            self._env("BUILDKITE_JOB_ID"),
        )
