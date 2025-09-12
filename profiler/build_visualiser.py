import argparse
import ast
import csv
import re
import statistics
import sys

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def format_label_block(expected_keys, index):
    inner = ", ".join(f'"{key}": {key}{index}' for key in expected_keys)
    return f'"Label{index}": {{{inner}}}'


def expected_data_format(expected_keys):
    return f"""
Expected data format:
{{
    {format_label_block(expected_keys, 1)},
    {format_label_block(expected_keys, 2)},
    ...
}}
"""


def validate_data(data, expected_keys):
    if not isinstance(data, dict):
        raise TypeError(
            f"Expected a dictionary for data parameter, got {type(data).__name__}"
        )

    for key, value in data.items():
        if not isinstance(value, dict):
            raise ValueError(f"Value for key '{key}' must be a dictionary")

        for expected_key in expected_keys:
            if expected_key not in value:
                raise ValueError(
                    f"Missing required key '{expected_key}' in data for '{key}'\n{expected_data_format(expected_keys)}"
                )


def create_bar_chart(ax, data, xlabel, ylabel, title, formatter=lambda x: f"{x:.2f}s"):
    """
    Create a bar chart on the given axis.

    Args:
        ax: Matplotlib axis to draw on
        data: Dictionary with the following structure:
            {
                "Label1": {"value": value1, "color": color1},
                "Label2": {"value": value2, "color": color2},
                ...
            }
            Where each key is a label for the x-axis, and each value is a dictionary
            containing a "value" key (the height of the bar) and a "color" key
            (the color of the bar).
        xlabel: Label for the x-axis
        ylabel: Label for the y-axis
        title: Title for the chart
        formatter: Function that takes a value and returns a formatted string for the bar labels
    """
    validate_data(data, ["value", "color"])

    y_values = [value["value"] for value in data.values()]
    bars = ax.bar(
        data.keys(),
        y_values,
        color=[value["color"] for value in data.values()],
        width=0.6,
        edgecolor="black",
        linewidth=1,
    )
    ax.set_facecolor("#f8f8f8")

    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.1,
            formatter(height),
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    # Set title and labels
    ax.set_title(title, fontweight="bold", pad=20)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Adjust y-axis to start from 0 and have some headroom
    max_time = max(y_values) * 1.2
    ax.set_ylim(0, max_time)


def create_pie_chart(ax, data, title, formatter=lambda x: f"{x:.2f}s"):
    """
    Create a pie chart on the given axis.

    Args:
        ax: Matplotlib axis to draw on
        data: Dictionary with the following structure:
            {
                "Label1": {"value": value1, "color": color1},
                "Label2": {"value": value2, "color": color2},
                ...
            }
            Where each key is a label for a slice, and each value is a dictionary
            containing a "value" key (the size of the slice) and a "color" key
            (the color of the slice).
        title: Title for the chart
        formatter: Function that takes a value and returns a formatted string for the legend labels
    """
    validate_data(data, ["value", "color"])

    values = [value["value"] for value in data.values()]
    wedges, _ = ax.pie(
        values,
        labels=None,  # Will add custom labels
        startangle=90,
        colors=[value["color"] for value in data.values()],
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    ax.axis("equal")
    ax.set_title(title, fontweight="bold", pad=20)

    # Add custom labels with actual times
    ax.legend(
        wedges,
        [f"{key}: {formatter(value['value'])}" for key, value in data.items()],
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        frameon=True,
        fancybox=True,
        shadow=True,
    )


def create_integer_step_line_graph(ax, data, steps, title, xlabel, ylabel):
    """
    Create a line graph with integer steps on the x-axis.

    This function creates a line graph where each line represents a series of data points
    plotted against integer steps (e.g. iteration counts).

    Args:
        ax: Matplotlib axis to draw on
        data: Dictionary with the following structure:
            {
                "Label1": {"y_values": [y1, y2, ...], "color": color1},
                "Label2": {"y_values": [y1, y2, ...], "color": color2},
                ...
            }
            Where each key is a label for the line, and each value is a dictionary
            containing a "y_values" key (list of y-coordinates) and a "color" key
            (the color of the line).
        steps: List or range of x-coordinates (typically integers like [1, 2, 3, ...])
        title: Title for the chart
        xlabel: Label for the x-axis
        ylabel: Label for the y-axis
    """
    validate_data(data, ["y_values", "color"])

    for label, value in data.items():
        ax.plot(
            steps,
            value["y_values"],
            marker="o",
            linestyle="-",
            linewidth=2,
            color=value["color"],
            label=label,
            markersize=8,
        )

    ax.set_title(title, fontweight="bold", pad=20)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.02, 1),
        frameon=True,
        fancybox=True,
        framealpha=0.9,
        shadow=True,
        borderpad=1,
    )
    ax.set_ylim(bottom=0)


def read_csv_data(csv_file):
    """
    Returns:
        tuple: (data, colors) where:
            - data: Dictionary where keys are build system names and values are lists of floats
                   e.g., {"Bazel": [4.2, 3.9, 4.1], "Buck2": [8.7, 8.5, 8.6], ...}
            - colors: Dictionary where keys are build system names and values are hex color codes
                     e.g., {"Bazel": "#4CAF50", "Buck2": "#FF9800", ...}
    """

    def _parse_row(row, row_num):
        build_system = row["build_system"].strip()
        color = row["color"].strip()
        measurements_str = row["measurements"].strip()

        if not build_system:
            print(f"Error: Empty build_system name at row {row_num}")
            sys.exit(1)

        # Validate hex color format
        hex_color_pattern = r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$"
        if not re.match(hex_color_pattern, color):
            print(
                f"Error: Invalid hex color '{color}' for {build_system} at row {row_num}"
            )
            print(
                "Colors must be valid hex codes: #RGB or #RRGGBB (e.g., #FF0000, #4CAF50, #ABC)"
            )
            sys.exit(1)

        try:
            measurements = ast.literal_eval(measurements_str)
            if not isinstance(measurements, list):
                raise ValueError("measurements must be a list")
            measurements = [float(x) for x in measurements]
            return build_system, color, measurements
        except (ValueError, SyntaxError) as e:
            print(
                f"Error parsing measurements for {build_system} at row {row_num}: {e}"
            )
            print('Measurements should be in format: "[4.2, 3.9, 4.1]"')
            sys.exit(1)

    data = {}
    colors = {}

    try:
        with open(csv_file, "r") as file:
            fieldnames = ["build_system", "color", "measurements"]
            reader = csv.DictReader(file, fieldnames=fieldnames)

            for row_num, row in enumerate(reader, start=1):
                # Check if row has the expected number of columns
                row_values = list(row.values())
                if (
                    len([v for v in row_values if v is not None]) != 3
                ):  # DictReader automatically fills missing columns with None
                    print(
                        f"Error: Row {row_num} must have exactly 3 columns (build_system, color, measurements)"
                    )
                    print(f"Found: {row_values}")
                    sys.exit(1)

                build_system, color, measurements = _parse_row(row, row_num)
                data[build_system] = measurements
                colors[build_system] = color

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

    if not data:
        print("Error: No build system data found in CSV file")
        sys.exit(1)

    # Validate that all build systems have the same number of measurements
    measurement_counts = [len(times) for times in data.values()]
    if not all(count == measurement_counts[0] for count in measurement_counts):
        print("Error: All build systems must have the same number of measurements")
        sys.exit(1)

    if measurement_counts[0] == 0:
        print("Error: No build time data provided")
        sys.exit(1)

    return data, colors


def generate_build_visualisations(
    build_data,
    custom_colors,
    use_bar_chart=True,
    output_path="build_performance_analysis.png",
):
    """
    Generate build performance visualisations.

    Args:
        build_data: Dictionary where keys are build system names and values are lists of build time measurements
                   e.g., {"Bazel": [4.2, 3.9, 4.1], "Buck2": [8.7, 8.5, 8.6]}
        custom_colors: Dictionary mapping build system names to hex color codes
                      e.g., {"Bazel": "#4CAF50", "Buck2": "#FF9800"}
        use_bar_chart: Whether to use bar charts (True) or pie charts (False)
        output_path: Path to save the generated visualisation
    """
    colors = custom_colors

    plt.style.use("ggplot")
    plt.rcParams.update(
        {
            "font.size": 12,
            "axes.titlesize": 16,
            "axes.labelsize": 14,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "legend.fontsize": 12,
            "figure.dpi": 100,
        }
    )

    # Get number of measurements (assume all build systems have same number)
    num_rounds = len(list(build_data.values())[0])

    # 2 plots for average times and sequential measurements, plus 1 for each round
    num_plots = 2 + num_rounds
    fig, axes = plt.subplots(num_plots, 1, figsize=(12, 7 * num_plots))

    # Handle case where there's only one plot
    if num_plots == 1:
        axes = [axes]

    # 1. Average build times chart (bar or pie)
    title = "Average Build Times"
    data = {}
    for build_system, times in build_data.items():
        avg_time = statistics.mean(times)
        data[build_system] = {"value": avg_time, "color": colors[build_system]}

    if use_bar_chart:
        create_bar_chart(
            axes[0],
            data,
            "Build System",
            "Time (seconds)",
            title,
        )
    else:
        create_pie_chart(
            axes[0],
            data,
            title,
        )

    # 2. Sequential build times line graph
    data = {}
    for build_system, times in build_data.items():
        data[build_system] = {"y_values": times, "color": colors[build_system]}

    create_integer_step_line_graph(
        axes[1],
        data,
        range(1, num_rounds + 1),
        "Sequential Build Times",
        "Build Number",
        "Time (seconds)",
    )

    # 3. Individual round comparisons
    for i in range(num_rounds):
        title = f"Build Round {i+1} Comparison"
        data = {}
        for build_system, times in build_data.items():
            data[build_system] = {"value": times[i], "color": colors[build_system]}

        if use_bar_chart:
            create_bar_chart(
                axes[i + 2],  # +2 because we have 2 plots before the round comparisons
                data,
                "Build System",
                "Time (seconds)",
                title,
            )
        else:
            create_pie_chart(axes[i + 2], data, title)

    plt.tight_layout(pad=4.0, h_pad=5.0)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate build performance visualisations from CSV data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example CSV file (no headers required):
  Bazel,#4CAF50,"[4.2, 3.9, 4.1]"
  Buck2,#FF9800,"[8.7, 8.5, 8.6]"
  Gradle,#9C27B0,"[7.6, 7.4, 7.5]"

Column format (in order):
  1. Build system name
  2. Color (hex code starting with #)
  3. Measurements (quoted list: "[1.2, 3.4, 5.6]")

Notes:
  - NO header row needed - just data rows
  - Each row represents one build system
  - All build systems must have the same number of measurements

Usage examples:
  python build_visualiser.py data.csv
  python build_visualiser.py data.csv --output my_analysis.png --pie
        """,
    )

    parser.add_argument(
        "csv_file",
        help="CSV file containing build time data (no headers required - 3 columns: build_system, color, measurements)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="build_performance_analysis.png",
        help="Output file path for the generated visualisation (default: build_performance_analysis.png)",
    )

    parser.add_argument(
        "--pie",
        action="store_true",
        help="Use pie charts instead of bar charts for comparisons",
    )

    args = parser.parse_args()
    build_data, custom_colors = read_csv_data(args.csv_file)

    generate_build_visualisations(
        build_data,
        custom_colors=custom_colors,
        use_bar_chart=not args.pie,
        output_path=args.output,
    )

    print(f"Build performance analysis saved to: {args.output}")
