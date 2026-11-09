

import argparse
import os
import platform


def build_report(name, version=None, working_directory=None):
    """Baut die drei geforderten Angaben für die Ausgabe zusammen."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Der Name darf nicht leer sein.")
    version = version or platform.python_version()
    working_directory = working_directory or os.getcwd()
    return (
        "Name: {}\nPython-Version: {}\nArbeitsverzeichnis: {}".format(
            name, version, working_directory
        )
    )


def main():
    parser = argparse.ArgumentParser(
        description="Gibt Name, Python-Version und Arbeitsverzeichnis aus."
    )
    parser.add_argument("--name", default="Raphael Bleier", help="Name für die Ausgabe")
    args = parser.parse_args()
    print(build_report(args.name))


if __name__ == "__main__":
    main()
