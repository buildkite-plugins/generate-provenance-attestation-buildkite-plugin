import hashlib
import pathlib
import uuid
from typing import Dict


def compute_hash(file_path: pathlib.Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read the file in 4096-byte chunks
        while True:
            data = f.read(4096)
            if not data:
                break
            # Update the hash object with the data
            sha256.update(data)
    return sha256.hexdigest()


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


def generate_uuid() -> str:
    return str(uuid.uuid4())
