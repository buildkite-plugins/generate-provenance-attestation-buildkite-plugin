import json
import os

from provenance_generator.cli_arguments import CliArguments
from provenance_generator.core import ProvenanceGenerator
from provenance_generator.helpers import fake_env, fake_files, get_files_and_shas

arguments = CliArguments()

environment = fake_env() if os.environ.get("FAKE_ENV") == "1" else os.environ
files = (
    fake_files()
    if os.environ.get("FAKE_ENV") == "1"
    else get_files_and_shas(
        query=arguments.get_artifact_glob(),
        build_id=str(environment.get("BUILDKITE_BUILD_ID")),
        job_id=str(environment.get("BUILDKITE_JOB_ID")),
        access_token=str(environment.get("BUILDKITE_AGENT_ACCESS_TOKEN")),
    )
)

generator = ProvenanceGenerator(
    environment=environment,
    files=files,
)

provenance = generator.provenance()

output_file = arguments.get_output_file()

if isinstance(output_file, str):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(provenance, f, indent=2)
    print("Build Provenance written to: {}".format(arguments.get_output_file()))
else:
    print(json.dumps(provenance, indent=2))
