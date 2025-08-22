#!/usr/bin/env python3

import argparse
import os
import re
import sys
from pathlib import Path

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


def modify_pom_file_string(pom_path, dry_run=False):
    """Modify a POM file using string replacement to preserve formatting."""
    try:
        # Read the original file
        with open(pom_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        changes = []

        # For each version override, look for dependency blocks and update versions
        for dep_key, target_version in VERSION_OVERRIDES.items():
            group_id, artifact_id = dep_key.split(":")

            # Pattern to match a dependency block with this groupId and artifactId
            # This matches both regular dependencies and dependencyManagement entries
            pattern = (
                r"(<dependency[^>]*>\s*"
                r"<groupId[^>]*>" + re.escape(group_id) + r"</groupId>\s*"
                r"<artifactId[^>]*>" + re.escape(artifact_id) + r"</artifactId>\s*"
                r"<version[^>]*>)([^<]+)(</version[^>]*>)"
            )

            def replace_version(match):
                prefix = match.group(1)
                current_version = match.group(2)
                suffix = match.group(3)

                # Skip version ranges in brackets
                if current_version.startswith("[") and current_version.endswith("]"):
                    return match.group(0)  # Return unchanged

                if current_version != target_version:
                    changes.append(
                        f"  {dep_key}: {current_version} -> {target_version}"
                    )
                    return prefix + target_version + suffix
                else:
                    return match.group(0)  # Return unchanged

            content = re.sub(pattern, replace_version, content, flags=re.DOTALL)

        # Check if content was modified
        modified = content != original_content

        # Save the modified file
        if modified and not dry_run:
            with open(pom_path, "w", encoding="utf-8") as f:
                f.write(content)

        return modified, changes

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

        modified, changes = modify_pom_file_string(pom_file, dry_run=args.dry_run)

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
