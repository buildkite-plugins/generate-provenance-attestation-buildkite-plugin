import json
import os

from provenance_generator.cli_arguments import CliArguments
from provenance_generator.core import ProvenanceGenerator
from provenance_generator.enveloper import Enveloper
from provenance_generator.helpers import (
    example_rsa_private_key,
    fake_env,
    fake_files,
    get_files_and_shas,
)

arguments = CliArguments()


environment = fake_env() if os.environ.get("FAKE_ENV") == "1" else os.environ
files = (
    fake_files()
    if os.environ.get("FAKE_ENV") == "1"
    else get_files_and_shas(
        query=arguments.get_artifacts_glob(),
        build_id=str(environment.get("BUILDKITE_BUILD_ID")),
        job_id=str(environment.get("BUILDKITE_JOB_ID")),
        access_token=str(environment.get("BUILDKITE_AGENT_ACCESS_TOKEN")),
    )
)

generator = ProvenanceGenerator(
    environment=environment, files=files, plugin_version=arguments.get_plugin_version()
)


# Eventually we'll take a base64-encoded private key here.
# But for now, we'll use the hard-coded example_rsa_private_key()
# which SHOULD NOT BE TRUSTED because anyone can make up a fake
# statement payload and sign it with this key.
enveloper = Enveloper(
    key_id="generate_build_provenance_plugin_example_key",
    private_key_b64=example_rsa_private_key(),
)

statement: str = json.dumps(generator.provenance())
envelope: str = enveloper.wrap(statement)

output_file = arguments.get_output_file()

if isinstance(output_file, str):
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(envelope)
    print("Build Provenance written to: {}".format(arguments.get_output_file()))
else:
    print(envelope)
