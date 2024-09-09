import argparse
import typing


class CliArguments:
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            prog="python3 main.py",
            description="Generates build provenance",
            epilog="Have a nice day!",
        )
        parser.add_argument("-g", "--artifacts-glob", default="*")
        parser.add_argument("-o", "--output", default=None)
        parser.add_argument("-p", "--plugin-version", default="development")
        self.arguments = parser.parse_args()

    def get_artifacts_glob(self) -> str:
        return str(self.arguments.artifacts_glob)

    def get_output_file(self) -> typing.Union[str, None]:
        if self.arguments.output:
            return str(self.arguments.output)
        else:
            return None

    def get_plugin_version(self) -> str:
        return str(self.arguments.plugin_version)
