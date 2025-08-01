#!/usr/bin/env python3

import argparse
import os


def parse_external_deps(external_deps_file, lib_dir):
    if not lib_dir.endswith("/"):
        lib_dir = lib_dir + "/"
    with open(external_deps_file, "r") as f:
        lines = f.readlines()
    deps = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        group, artifact, _ = line.split(":", 2)  # Remove the version
        group_path = group.replace(".", "/")
        deps.append(f"//{lib_dir}{group_path}/{artifact}:{artifact}")
    return deps


def append_android_library(buck_file, deps_list):
    android_library_rule = f"""
android_library(
    name = "lib",
    srcs = glob(["src/main/java/**/*.java", "src/main/java/**/*.kt"]),
    deps = [
        ":res",
        {',\n        '.join(f'"{dep}"' for dep in deps_list)},
    ],
)
"""
    with open(buck_file, "a") as f:
        f.write("\n" + android_library_rule)


if __name__ == "__main__":
    if not os.path.exists(".buckconfig"):
        current_dir = os.getcwd()
        raise RuntimeError(
            f"No .buckconfig found in {current_dir}. Run this script from the root of your Buck project."
        )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--external_deps",
        required=True,
        help="Path to external_deps.txt file to parse",
    )
    parser.add_argument(
        "--lib_dir",
        required=True,
        help="Path to directory where external dependencies are located relative to current directory. Hint: most likely same directory as external_deps.txt",
    )
    parser.add_argument(
        "--buck_file", required=True, help="Path to BUCK file to append to"
    )

    args = parser.parse_args()
    external_deps = args.external_deps
    lib_dir = args.lib_dir
    buck_file = args.buck_file

    if not os.path.exists(external_deps):
        raise FileNotFoundError(f"Error: File '{external_deps}' not found")
    if not os.path.isdir(lib_dir):
        raise FileNotFoundError(f"Error: Directory '{lib_dir}' not found")
    if lib_dir.startswith("/") or not os.path.isdir(os.path.join(os.getcwd(), lib_dir)):
        raise FileNotFoundError(
            f"Error: '{lib_dir}' is not a subdirectory of '{os.getcwd()}'"
        )
    if not os.path.exists(buck_file):
        raise FileNotFoundError(f"Error: File '{buck_file}' not found")

    deps = parse_external_deps(external_deps, lib_dir)
    append_android_library(buck_file, deps)
