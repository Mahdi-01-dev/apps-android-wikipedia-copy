#!/usr/bin/env python3

import argparse
import os
import tomllib


def __formatted_deps(items, versions, key):
    result = []
    for _, attrs in items:
        if "version" in attrs:
            version = versions[attrs["version"]["ref"]]
            result.append(f"{attrs[key]}:{version}")
    return result


def __generate_external_deps(toml_file):
    with open(toml_file, "rb") as f:
        toml_data = tomllib.load(f)
    versions = toml_data["versions"]
    libraries = toml_data["libraries"]

    result = __formatted_deps(libraries.items(), versions, "module")
    return "\n".join(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--libs_versions", required=True, help="Path to libs.versions.toml"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output file where external dependencies will be listed. Hint: app/libs/external_deps.txt",
    )
    args = parser.parse_args()

    libs_versions = args.libs_versions
    output = args.output

    if not os.path.exists(libs_versions):
        raise FileNotFoundError(f"File {libs_versions} does not exist")
    os.makedirs(os.path.dirname(output), exist_ok=True)

    with open(output, "a") as f:
        f.write(__generate_external_deps(libs_versions))
        f.write("\n")
