import argparse


class CliArguments:
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            prog="python3 main.py",
            description="Generates build provenance",
            epilog="Have a nice day!",
        )
        parser.add_argument("-d", "--artifact-directory", default="")
        parser.add_argument("-g", "--artifact-glob", default="*")
        parser.add_argument("-o", "--output", default="provenance.json")
        self.arguments = parser.parse_args()

    def get_artifact_directory(self) -> str:
        return str(self.arguments.artifact_directory)

    def get_artifact_glob(self) -> str:
        return str(self.arguments.artifact_glob)

    def get_output_file(self) -> str:
        return str(self.arguments.output)
