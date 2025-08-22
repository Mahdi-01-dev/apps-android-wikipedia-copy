#!/usr/bin/env python3

import argparse
import os
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import sys

# Register the default namespace to avoid ns0: prefixes
ET.register_namespace('', 'http://maven.apache.org/POM/4.0.0')
ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')

# Version overrides - mapping from groupId:artifactId to desired version
VERSION_OVERRIDES = {
    "org.jetbrains.kotlin:kotlin-stdlib": "2.1.0",
    "org.jetbrains.kotlin:kotlin-stdlib-common": "2.1.0",
    "org.jetbrains.kotlin:kotlin-stdlib-jdk7": "2.1.0",
    "org.jetbrains.kotlin:kotlin-stdlib-jdk8": "2.1.0",
    "androidx.lifecycle:lifecycle-common": "2.9.2",
    "androidx.lifecycle:lifecycle-runtime": "2.9.2",
    "androidx.lifecycle:lifecycle-viewmodel": "2.9.2",
    "androidx.emoji2:emoji2": "1.4.0",
    "androidx.collection:collection": "1.5.0",
    "androidx.collection:collection-jvm": "1.5.0",
    "androidx.compose.runtime:runtime": "1.8.3",
    "androidx.compose.ui:ui-geometry": "1.8.3",
    "androidx.compose.ui:ui-graphics": "1.8.3",
    "androidx.compose.ui:ui-text": "1.8.3",
    "androidx.compose.ui:ui-unit": "1.8.3",
    "androidx.compose.ui:ui-util": "1.8.3",
    "androidx.savedstate:savedstate": "1.3.1",
    "androidx.compose.animation:animation-core": "1.8.3",
}


def find_pom_files(cache_dir):
    """Recursively find all POM files in the Coursier cache."""
    pom_files = []
    cache_path = Path(cache_dir)

    if not cache_path.exists():
        print(f"Cache directory not found: {cache_dir}")
        return pom_files

    # Find all .pom files recursively
    for pom_file in cache_path.rglob("*.pom"):
        pom_files.append(pom_file)

    return pom_files


def modify_pom_file(pom_path, dry_run=False):
    """Modify a POM file to update dependency versions."""
    try:
        # Parse the XML file
        tree = ET.parse(pom_path)
        root = tree.getroot()

        # Handle XML namespaces
        namespaces = {"maven": "http://maven.apache.org/POM/4.0.0"}
        if root.tag.startswith("{"):
            # Extract namespace from root tag
            namespace = root.tag[1 : root.tag.index("}")]
            namespaces["maven"] = namespace

        modified = False
        changes = []

        # Find all dependency elements in <dependencies> sections
        for dependencies in root.findall(".//maven:dependencies", namespaces):
            for dependency in dependencies.findall("maven:dependency", namespaces):
                group_id_elem = dependency.find("maven:groupId", namespaces)
                artifact_id_elem = dependency.find("maven:artifactId", namespaces)
                version_elem = dependency.find("maven:version", namespaces)

                if (
                    group_id_elem is not None
                    and artifact_id_elem is not None
                    and version_elem is not None
                ):
                    group_id = group_id_elem.text
                    artifact_id = artifact_id_elem.text
                    current_version = version_elem.text

                    # Check if this dependency should be overridden
                    dep_key = f"{group_id}:{artifact_id}"
                    if dep_key in VERSION_OVERRIDES:
                        new_version = VERSION_OVERRIDES[dep_key]

                        # Skip if version is in brackets (version ranges)
                        if (
                            current_version
                            and current_version.startswith("[")
                            and current_version.endswith("]")
                        ):
                            continue

                        if current_version != new_version:
                            changes.append(
                                f"  {dep_key}: {current_version} -> {new_version}"
                            )
                            if not dry_run:
                                version_elem.text = new_version
                            modified = True

        # Also check dependencyManagement section
        for dep_mgmt in root.findall(".//maven:dependencyManagement", namespaces):
            for dependencies in dep_mgmt.findall(".//maven:dependencies", namespaces):
                for dependency in dependencies.findall("maven:dependency", namespaces):
                    group_id_elem = dependency.find("maven:groupId", namespaces)
                    artifact_id_elem = dependency.find("maven:artifactId", namespaces)
                    version_elem = dependency.find("maven:version", namespaces)

                    if (
                        group_id_elem is not None
                        and artifact_id_elem is not None
                        and version_elem is not None
                    ):
                        group_id = group_id_elem.text
                        artifact_id = artifact_id_elem.text
                        current_version = version_elem.text

                        # Check if this dependency should be overridden
                        dep_key = f"{group_id}:{artifact_id}"
                        if dep_key in VERSION_OVERRIDES:
                            new_version = VERSION_OVERRIDES[dep_key]

                            # Skip if version is in brackets (version ranges)
                            if (
                                current_version
                                and current_version.startswith("[")
                                and current_version.endswith("]")
                            ):
                                continue

                            if current_version != new_version:
                                changes.append(
                                    f"  {dep_key}: {current_version} -> {new_version}"
                                )
                                if not dry_run:
                                    version_elem.text = new_version
                                modified = True

        # Save the modified file
        if modified and not dry_run:
            tree.write(pom_path, encoding="utf-8", xml_declaration=True)

        return modified, changes

    except ET.ParseError as e:
        print(f"Error parsing {pom_path}: {e}")
        return False, []
    except Exception as e:
        print(f"Error processing {pom_path}: {e}")
        return False, []


def main():
    """Main function to process POM files."""
    parser = argparse.ArgumentParser(
        description="Modify POM files to force specific dependency versions"
    )
    parser.add_argument(
        "cache_dir",
        default="/Users/b41z33d/Library/Caches/Coursier/v1/https/maven.google.com/androidx/appcompat/appcompat/1.7.1",
        nargs="?",
        help="Path to Coursier cache directory (default: /Users/b41z33d/Library/Caches/Coursier/v1)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show verbose output"
    )

    args = parser.parse_args()

    print(f"Scanning for POM files in: {args.cache_dir}")
    pom_files = find_pom_files(args.cache_dir)

    if not pom_files:
        print("No POM files found!")
        return 1

    print(f"Found {len(pom_files)} POM files")

    total_modified = 0
    total_changes = 0

    for pom_file in pom_files:
        if args.verbose:
            print(f"Processing: {pom_file}")

        modified, changes = modify_pom_file(pom_file, dry_run=args.dry_run)

        if modified:
            total_modified += 1
            total_changes += len(changes)

            if args.dry_run:
                print(f"[DRY-RUN] Would modify {pom_file}:")
            else:
                print(f"Modified {pom_file}:")

            for change in changes:
                print(change)
            print()

    if args.dry_run:
        print(
            f"[DRY-RUN] Would modify {total_modified} POM files with {total_changes} version changes"
        )
    else:
        print(
            f"Modified {total_modified} POM files with {total_changes} version changes"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
