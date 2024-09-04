import json
import os
from pathlib import Path

from provenance_generator.cli_arguments import CliArguments
from provenance_generator.core import ProvenanceGenerator
from provenance_generator.helpers import compute_hash, fake_env

arguments = CliArguments()
files = [
    file
    for file in Path(arguments.get_artifact_directory()).glob(
        arguments.get_artifact_glob()
    )
    if file.is_file()
]

environment = os.environ if os.environ.get("FAKE_ENV") != "1" else fake_env()

generator = ProvenanceGenerator(
    environment=environment,
    compute_hash_fn=compute_hash,
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
