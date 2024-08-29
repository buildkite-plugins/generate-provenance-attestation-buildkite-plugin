import hashlib
import pathlib
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
        "BUILDKITE_BUILD_ID": "01919c03-1f85-4b3f-9594-2986d23b14c4",
        "BUILDKITE_BUILD_NUMBER": "49387",
        "BUILDKITE_COMMAND": "gem build wget https://rubygems.org/downloads/logger-1.6.0.gem",
        "BUILDKITE_COMMIT": "2b4ba8fe79386d40ce27dc5f6cc4161a0f598cc2",
        "BUILDKITE_JOB_ID": "01919c03-1f99-4e5e-a0f8-75f7571c8fbc",
        "BUILDKITE_ORGANIZATION_ID": "019033f0-0b83-41d7-a327-def5f678906c",
        "BUILDKITE_ORGANIZATION_SLUG": "provkite",
        "BUILDKITE_PIPELINE_ID": "01919c01-132f-46f1-803f-2efc0c444af7",
        "BUILDKITE_PIPELINE_SLUG": "prov-generator",
        "BUILDKITE_REPO": "https://github.com/provekite/prov-generator.git",
        "BUILDKITE_STEP_ID": "01919c03-1f78-4951-bf28-6b0e293ab2bd",
        "BUILDKITE_STEP_KEY": "wget-gem",
        "BUILDKITE_TAG": "fan-tag-stic",
    }
