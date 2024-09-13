# Generate Build Provenance Buildkite Plugin

This [Buildkite plugin](https://buildkite.com/docs/agent/v3/plugins) generates a build provenance attestation for artifacts that were produced in a Buildkite build step.

It runs as a [post-artifact hook](https://buildkite.com/docs/agent/v3/hooks#job-lifecycle-hooks) that generates a build provenance attestation for all the relevant artifacts that were built and uploaded by the step that it is attached to.

The plugin then uploads the attestation to artifact storage for downstream usage.

### Attestation format

The core of the attestation is an intermediate [in-toto Statement](https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md) that attests to the build provenance of artifacts that were produced in a Buildkite build step. See [examples/statement.json](./examples/statement.json).

This statement is serialised and signed in an [in-toto Envelope](https://github.com/in-toto/attestation/blob/main/spec/v1/envelope.md) using the [DSSE v1.0](https://github.com/secure-systems-lab/dsse/blob/v1.0.0/envelope.md) format. See [examples/envelope.json](examples/envelope.json).

The [envelope](examples/envelope.json) is the resultant attestation that is uploaded to the build's artifact storage.

### SLSA Build Levels

The in-toto Statement satisfies the [Provenance Exists requirement](https://slsa.dev/spec/v1.0/requirements#provenance-exists) needed for [SLSA Build Level 1](https://slsa.dev/spec/v1.0/requirements#build-levels).

The in-toto Envelope is currently signed using a hard-coded private key for demonstration purposes. This lays the groundwork for the Statement to be signed with a user-specified private key in the future, which will satisfy the [Provenance is Authentic requirement](https://slsa.dev/spec/v1.0/requirements#provenance-authentic) needed for [SLSA Build Level 2](https://slsa.dev/spec/v1.0/requirements#build-levels).

## Options

#### `artifacts` (string, required)

A glob pattern to select for artifacts that will be included in the build provenance document.

#### `provenance_filename` (string, required)

Filename to use when uploading the build provenance document to artifact storage.

## Usage

In the example below, the pipeline step builds a gem **awesome-logger-<version>.gem** and uploads it to artifact storage.

The Generate Build Provenance plugin generates a build provenance document that incorporates the gem file (included by the `artifacts` glob), and uploads the build provenance document to artifact storage as `gem-provenance.json` (as specified by `provenance_filename`).

`gem-provenance.json` can then be persisted in later steps or published to a package registry alongside the newly built gem.

```yaml
steps:
  - label: "Build Gem"
    key: "build-gem"
    command: "gem build awesome-logger.gemspec"
    artifact_paths: "awesome-logger-*.gem"
    plugins:
      - generate-build-provenance#v2.0.0:
        artifacts: "awesome-logger-*.gem"
        provenance_filename: "gem-provenance.json"
```

## Development

The core of the plugin is a [Python](https://www.python.org) program [main.py](./main.py).

It accepts the following arguments:

| Argument             | Description                                           |
| -------------------- | ----------------------------------------------------- |
| -g, --artifacts-glob | Only include artifacts that match this glob.          |
| -o, --output         | Write provenance document to a file instead of STDOUT |

#### Example

```shell
python3 ./main.py \
  --artifacts-glob "*.gem" \
  --output "./gem-provenance.json"
```

### Other common tasks

#### Running with fake environment variables

If `FAKE_ENV` environment variable is set to `1`, the program will use a set of fake `BUILDKITE_*` environment variables and fake artifact files defined in [provenance_generator/helpers.py](./provenance_generator/helpers.py).

```shell
FAKE_ENV=1 python3 ./main.py
```

#### Check type annotations with mypy

```shell
brew install mypy # once-off setup

mypy --strict **/*.py
```

#### Run unit tests

```shell
python3 -m unittest tests/*.py
```
