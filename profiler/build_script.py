import argparse
import csv
import json
import re
import shutil
import statistics
import subprocess
import time
from pathlib import Path

from function_kicker import FunctionKicker


def abs_path(root, path):
    """Returns the absolute path of @path relative to @root."""

    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if parent.name == root:
            return parent / path
    raise RuntimeError(f"Could not find {root} in the path hierarchy: {current_path}")


def replace_target_prefix(target_file, dir):
    dir_str = str(dir)
    parts = target_file.split("//")
    if len(parts) != 2:
        raise ValueError("target_file must contain '//' once")

    if not dir_str.endswith("/"):
        dir_str += "/"

    return dir_str + parts[1]


def get_source_files_buck(path_to_cell, root_target_prefix, target):
    result = subprocess.run(
        [
            "/Users/b41z33d/.cargo/bin/buck2",
            "uquery",
            f"filter('{root_target_prefix}', deps({target}))",
            "--output-attribute",
            "srcs",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Buck2 query failed: {result.stderr}")

    data = json.loads(result.stdout)
    source_files = []
    for _, attrs in data.items():
        srcs = attrs.get("srcs", [])
        source_files.extend(srcs)

    # Filter out XML files
    filtered_source_files = [
        source_file
        for source_file in source_files
        if not source_file.lower().endswith(".xml")
    ]

    return [
        replace_target_prefix(source_file, path_to_cell)
        for source_file in filtered_source_files
    ]


def get_source_files_bazel(file_extensions, working_dir, target):
    source_files = []
    result = subprocess.run(
        ["bazel", "query", f'kind("source file", deps({target}))'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_dir,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Bazel query failed: {result.stderr}")

    regexes = [
        re.compile(f"^//.*{file_extension}$") for file_extension in file_extensions
    ]

    for line in result.stdout.splitlines():
        if any(regex.match(line) for regex in regexes):
            line = line.replace(":", "/")
            abs_path = replace_target_prefix(f"{line}", working_dir)
            source_files.append(abs_path)
    return source_files


class BuildSys:
    def __init__(self, build_sys, invocation, working_dir=None):
        self.build_sys = build_sys  # The build system's name
        self.invocation = invocation  # The command used to invoke the build system
        self.working_dir = working_dir  # The working directory for the build system

    def execute(self, cmd, target=None, args=None, verbose=True):
        command = [self.invocation]

        if args:
            for arg, value in args.items():
                command.append(f"{arg}")
                command.append(f"{value}")

        command.append(cmd)

        if target:
            command.append(target)

        start = time.perf_counter()
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE if verbose else subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            cwd=self.working_dir,
            text=True,
        )
        end = time.perf_counter()
        return result, end - start

    def build(self, build_cmd, target=None, args=None):
        print(f"Building with {self.build_sys}...")
        result, time = self.execute(build_cmd, target, args)
        print(result.stdout)
        if result.returncode != 0:
            raise RuntimeError(f"{self.build_sys} build failed: {result.stdout}")
        print(f"{self.build_sys} build time: {time} seconds\n")
        return time

    def build_n_times(self, build_cmd, n, target=None, args=None):
        for i in range(n):
            print(f"{self.build_sys} build {i+1} of {n}:")
            self.build(build_cmd, target, args)


if __name__ == "__main__":

    def bazel_target_type(value: str):
        """
        Validates that the bazel target argument is in the expected format: path/to/root//target
        """
        parts = value.split("//")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise argparse.ArgumentTypeError(
                f"Invalid bazel target format: '{value}'. Expected format: 'path/to/root//target'"
            )
        return value

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_count", type=int, required=True, help="Number of incremental builds"
    )
    parser.add_argument(
        "--bazel_target",
        type=bazel_target_type,
        required=True,
        help="Bazel target to build (format: path/to/root//target)",
    )
    parser.add_argument(
        "--buck_target", type=str, required=True, help="Buck target to build"
    )
    parser.add_argument(
        "--gradle_dir",
        type=str,
        required=True,
        help="Gradle working directory (project root)",
    )
    parser.add_argument(
        "--visualise",
        action="store_true",
        help="Generate visualisations of build performance",
    )
    parser.add_argument(
        "--pie",
        action="store_true",
        help="Use pie charts instead of bar charts for visualisations",
    )
    parser.add_argument(
        "--output-vis",
        type=str,
        default="build_performance_analysis.png",
        help="Output file path for visualisation graphs (default: build_performance_analysis.png)",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="incremental_build_times.csv",
        help="Output file path for CSV data (default: incremental_build_times.csv)",
    )

    args = parser.parse_args()
    build_count = args.build_count

    bazel_parts = args.bazel_target.split("//")
    bazel_working_dir = bazel_parts[0]
    bazel_target = f"//{bazel_parts[1]}"  # Reinstate the "//"

    buck_target = args.buck_target
    buck_args = {"--isolation-dir": "buck2_isolation"}

    bazel_build = BuildSys(
        "Bazel",
        "bazel",
        bazel_working_dir,
    )
    buck_build = BuildSys("Buck2", "/Users/b41z33d/.cargo/bin/buck2")
    gradle_build = BuildSys(
        "Gradle",
        "./gradlew",
        args.gradle_dir,
    )

    # Warm up the build systems
    print("Warming up the build systems...")
    initial_bazel_time = bazel_build.build("build", bazel_target)
    res = "/path/apps-android-wikipedia-copy/app/src/main/res/"
    raw = "/path/apps-android-wikipedia-copy/app/src/main/res/raw/"
    shutil.move(raw + "resources.properties", res)
    initial_gradle_time = gradle_build.build("assembleDevRelease")
    initial_buck_time = buck_build.build("build", buck_target)

    file_extensions = ["kt", "java"]

    source_files = get_source_files_buck(
        "/path/apps-android-wikipedia-copy",
        "root//app",
        "root//app:app",
    )

    # Run the builds
    bazel_times = []
    buck_times = []
    gradle_times = []

    kicker = FunctionKicker()

    try:
        for _ in range(build_count):
            for file in source_files:
                if "/_generated_databinding/" in file:
                    continue
                kicker.append(file)
            shutil.move(res + "resources.properties", raw)
            bazel_times.append(bazel_build.build("build", bazel_target))
            shutil.move(raw + "resources.properties", res)
            gradle_times.append(gradle_build.build("assembleDevRelease"))
            buck_times.append(buck_build.build("build", buck_target))
    finally:
        kicker.cleanup_all_dirty()

    print("Warm up times:")
    print(f"Bazel: {initial_bazel_time} seconds")
    print(f"Buck2: {initial_buck_time} seconds")
    print(f"Gradle: {initial_gradle_time} seconds\n")
    print("Average Bazel incremental build time:", statistics.mean(bazel_times))
    print("Average Buck2 incremental build time:", statistics.mean(buck_times))
    print("Average Gradle incremental build time:", statistics.mean(gradle_times))

    custom_colors = {
        "Bazel": "#4CAF50",  # Green
        "Buck2": "#FF9800",  # Orange
        "Gradle": "#9C27B0",  # Purple
    }

    # Generate visualisations if requested
    # if args.visualise:
    #     print("\nGenerating build performance visualisations...")
    #     build_data = {
    #         "Buck2": buck_times,
    #         "Gradle": gradle_times,
    #     }

    #     generate_build_visualisations(
    #         build_data,
    #         custom_colors,
    #         use_bar_chart=not args.pie,
    #         output_path=args.output_vis,
    #     )
    #     print(f"Build performance visualisations saved to: {args.output_vis}")

    # Generate CSV file with incremental build times (excluding warm-up times)
    print("\nGenerating CSV file with incremental build times...")
    try:
        with open(args.output_csv, "w", newline="") as csvfile:
            fieldnames = ["build_system", "color", "measurements"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            for (build_system, color), times in zip(
                custom_colors.items(), [bazel_times, buck_times, gradle_times]
            ):
                writer.writerow(
                    {
                        "build_system": build_system,
                        "color": color,
                        "measurements": str(times),
                    }
                )

        print(f"Incremental build times CSV saved to: {args.output_csv}")
        print(
            f"This CSV can be used with: python build_visualiser.py {args.output_csv}"
        )
    except Exception as e:
        print(f"Error generating CSV file: {e}")
