import uuid
from pathlib import Path
from typing import Dict, List, Mapping

from provenance_generator.api_client import ApiClient
from provenance_generator.path_sha import PathSha


def fake_env() -> Dict[str, str]:
    return {
        "BUILDKITE_BRANCH": "main",
        "BUILDKITE_BUILD_ID": generate_uuid(),
        "BUILDKITE_BUILD_NUMBER": "49387",
        "BUILDKITE_COMMAND": "gem build awesome-logger.gemspec",
        "BUILDKITE_COMMIT": "2b4ba8fe79386d40ce27dc5f6cc4161a0f598cc2",
        "BUILDKITE_JOB_ID": generate_uuid(),
        "BUILDKITE_ORGANIZATION_ID": generate_uuid(),
        "BUILDKITE_ORGANIZATION_SLUG": "acme-corp",
        "BUILDKITE_PIPELINE_ID": generate_uuid(),
        "BUILDKITE_PIPELINE_SLUG": "awesome-logger",
        "BUILDKITE_REPO": "https://github.com/acme-corp/awesome-logger.git",
        "BUILDKITE_STEP_ID": generate_uuid(),
        "BUILDKITE_STEP_KEY": "build-gem",
        "BUILDKITE_TAG": "v1.6.0",
    }


def fake_files() -> List[PathSha]:
    return [
        dict(path="file_1.ext", sha256sum="fake_sha_1"),
        dict(path="file_2.ext", sha256sum="fake_sha_2"),
    ]


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_files_and_shas(
    query: str, build_id: str, job_id: str, access_token: str
) -> List[PathSha]:
    client = ApiClient(access_token)
    artifacts = client.get_artifacts_list(query, build_id, job_id)
    return list(
        map(
            artifact_to_path_sha,
            artifacts,
        )
    )


def strip_dirs(path: str) -> str:
    p = Path(path)
    return p.name


def artifact_to_path_sha(artifact: Mapping[str, str]) -> PathSha:
    return dict(
        path=strip_dirs(str(artifact["path"])),
        sha256sum=str(artifact["sha256sum"]),
    )
