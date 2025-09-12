import argparse
import statistics
from datetime import datetime
from pathlib import Path
from string import Template

import plotly.graph_objects as go
import plotly.offline as pyo

from build_visualiser import read_csv_data


def create_summary_stats(build_data):
    stats = {}
    for build_system, times in build_data.items():
        stats[build_system] = {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
            "count": len(times),
        }
    return stats


def create_bar_chart(
    build_data,
    colors,
    xlabel="Build System",
    ylabel="Time (seconds)",
    title="Average Build Times",
    formatter=lambda x: f"{x:.2f}s",
):
    """
    Args:
        build_data: Dictionary where keys are labels and values are lists of measurements
        colors: Dictionary mapping labels to hex color codes
        xlabel: Label for the x-axis
        ylabel: Label for the y-axis
        title: Title for the chart
        formatter: Function that takes a value and returns a formatted string for bar labels and hover text
    """
    build_systems = list(build_data.keys())
    avg_times = [statistics.mean(times) for times in build_data.values()]
    chart_colors = [colors[system] for system in build_systems]

    fig = go.Figure(
        data=[
            go.Bar(
                x=build_systems,
                y=avg_times,
                marker_color=chart_colors,
                text=[formatter(time) for time in avg_times],
                textposition="outside",
                hovertemplate=f"<b>%{{x}}</b><br>{ylabel}: %{{y:.2f}}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title={"text": title, "x": 0.5, "xanchor": "center", "font": {"size": 20}},
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        yaxis={"range": [0, max(avg_times) * 1.2]},
        template="plotly_white",
        height=500,
        font={"size": 14},
    )

    return fig


def create_pie_chart(
    build_data, colors, title="Build Time Distribution", formatter=lambda x: f"{x:.2f}s"
):
    """
    Args:
        build_data: Dictionary where keys are labels and values are lists of measurements
        colors: Dictionary mapping labels to hex color codes
        title: Title for the chart
        formatter: Function that takes a value and returns a formatted string for hover text
    """
    build_systems = list(build_data.keys())
    avg_times = [statistics.mean(times) for times in build_data.values()]
    chart_colors = [colors[system] for system in build_systems]

    formatted_times = [formatter(avg_time) for avg_time in avg_times]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=build_systems,
                values=avg_times,
                marker_colors=chart_colors,
                customdata=formatted_times,
                hovertemplate="<b>%{label}</b><br>Time: %{customdata}<br>Percentage: %{percent}<extra></extra>",
                textinfo="label+percent",
                textposition="outside",
            )
        ]
    )

    fig.update_layout(
        title={"text": title, "x": 0.5, "xanchor": "center", "font": {"size": 20}},
        template="plotly_white",
        height=500,
        font={"size": 14},
    )

    return fig


def create_integer_step_line_graph(
    build_data,
    colors,
    title="Sequential Build Times",
    xlabel="Build Number",
    ylabel="Time (seconds)",
    formatter=lambda x: f"{x:.2f}",
):
    """
    Args:
        build_data: Dictionary where keys are labels and values are lists of measurements
        colors: Dictionary mapping labels to hex color codes
        title: Title for the chart
        xlabel: Label for the x-axis
        ylabel: Label for the y-axis
        formatter: Function that takes a value and returns a formatted string for hover text
    """
    fig = go.Figure()

    num_builds = len(list(build_data.values())[0])
    x_values = list(range(1, num_builds + 1))

    for build_system, times in build_data.items():
        formatted_times = [formatter(time) for time in times]

        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=times,
                mode="lines+markers",
                name=build_system,
                line={"color": colors[build_system], "width": 3},
                marker={"size": 8},
                customdata=formatted_times,
                hovertemplate=f"<b>{build_system}</b><br>{xlabel}: %{{x}}<br>{ylabel}: %{{customdata}}<extra></extra>",
            )
        )

    fig.update_layout(
        title={"text": title, "x": 0.5, "xanchor": "center", "font": {"size": 20}},
        xaxis_title=xlabel,
        yaxis_title=ylabel,
        xaxis={"dtick": 1},
        yaxis={"range": [0, None]},
        template="plotly_white",
        height=500,
        font={"size": 14},
        legend={"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 1.01},
    )

    return fig


def create_box_plot(
    build_data,
    colors,
    title="Build Time Distribution Analysis",
    formatter=lambda x: f"{x:.2f}s",
):
    """
    Args:
        build_data: Dictionary where keys are labels and values are lists of measurements
        colors: Dictionary mapping labels to hex color codes
        title: Title for the chart
        formatter: Function that takes a value and returns a formatted string for hover text
    """
    fig = go.Figure()

    for build_system, times in build_data.items():
        formatted_times = [formatter(time) for time in times]

        fig.add_trace(
            go.Box(
                y=times,
                name=build_system,
                marker_color=colors[build_system],
                boxpoints="all",
                jitter=0.3,
                pointpos=-1.8,
                customdata=formatted_times,
                hovertemplate=f"<b>{build_system}</b><br>Time: %{{customdata}}<extra></extra>",
            )
        )

    fig.update_layout(
        title={"text": title, "x": 0.5, "xanchor": "center", "font": {"size": 20}},
        xaxis_title="Build System",
        yaxis_title="Time (seconds)",
        template="plotly_white",
        height=500,
        font={"size": 14},
    )

    return fig


def create_comparison_table(stats):
    """Create an HTML table with build statistics using template."""
    table_rows = ""
    for build_system, stat in stats.items():
        table_rows += f"""
                <tr>
                    <td><strong>{build_system}</strong></td>
                    <td>{stat['mean']:.2f}</td>
                    <td>{stat['std_dev']:.2f}</td>
                    <td>{stat['median']:.2f}</td>
                    <td>{stat['min']:.2f}</td>
                    <td>{stat['max']:.2f}</td>
                    <td>{stat['count']}</td>
                </tr>"""

    template_path = Path(__file__).parent / "build_stats_table_template.html"
    try:
        with open(template_path, "r") as f:
            table_template = Template(f.read())
    except FileNotFoundError:
        raise FileNotFoundError(f"Table template not found at {template_path}")

    return table_template.substitute(TABLE_ROWS=table_rows)


def create_insights_section(stats):
    """Generate insights and recommendations based on the data using template."""
    fastest_system = min(stats.items(), key=lambda x: x[1]["mean"])
    slowest_system = max(stats.items(), key=lambda x: x[1]["mean"])
    most_consistent = min(stats.items(), key=lambda x: x[1]["std_dev"])

    template_path = Path(__file__).parent / "build_insights_template.html"
    try:
        with open(template_path, "r") as f:
            insights_template = Template(f.read())
    except FileNotFoundError:
        raise FileNotFoundError(f"Insights template not found at {template_path}")

    return insights_template.substitute(
        FASTEST_SYSTEM=fastest_system[0],
        FASTEST_TIME=f"{fastest_system[1]['mean']:.2f}",
        SLOWEST_SYSTEM=slowest_system[0],
        SLOWEST_TIME=f"{slowest_system[1]['mean']:.2f}",
        CONSISTENT_SYSTEM=most_consistent[0],
        CONSISTENT_STDDEV=f"{most_consistent[1]['std_dev']:.2f}",
    )


def create_html_report(build_data, colors, output_path="build_performance_report.html"):
    stats = create_summary_stats(build_data)

    bar_chart = create_bar_chart(build_data, colors)
    pie_chart = create_pie_chart(build_data, colors)
    line_graph = create_integer_step_line_graph(build_data, colors)
    box_plot = create_box_plot(build_data, colors)

    # Configure minimal Plotly toolbar for all charts
    config = {
        "modeBarButtonsToRemove": [
            "pan2d",
            "lasso2d",
            "select2d",
            "autoScale2d",
            "hoverClosestCartesian",
            "hoverCompareCartesian",
            "toggleSpikelines",
        ],
        "displaylogo": False,
        "modeBarButtonsToAdd": [],
    }

    bar_html = pyo.plot(
        bar_chart, output_type="div", include_plotlyjs=False, config=config
    )
    pie_html = pyo.plot(
        pie_chart, output_type="div", include_plotlyjs=False, config=config
    )
    line_html = pyo.plot(
        line_graph, output_type="div", include_plotlyjs=False, config=config
    )
    box_html = pyo.plot(
        box_plot, output_type="div", include_plotlyjs=False, config=config
    )

    table_html = create_comparison_table(stats)
    insights_html = create_insights_section(stats)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    template_path = Path(__file__).parent / "build_report_template.html"
    try:
        with open(template_path, "r") as f:
            html_template = Template(f.read())
    except FileNotFoundError:
        raise FileNotFoundError(f"HTML template not found at {template_path}")

    html_content = html_template.substitute(
        TIMESTAMP=timestamp,
        INSIGHTS_HTML=insights_html,
        TABLE_HTML=table_html,
        BAR_HTML=bar_html,
        PIE_HTML=pie_html,
        LINE_HTML=line_html,
        BOX_HTML=box_html,
    )

    with open(output_path, "w") as f:
        f.write(html_content)

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate interactive HTML build performance visualisations from CSV data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
    python build_html_visualiser.py data.csv
    python build_html_visualiser.py data.csv --output my_report.html

Example CSV file (no headers required):
    Bazel,#4CAF50,"[4.2, 3.9, 4.1]"
    Buck2,#FF9800,"[8.7, 8.5, 8.6]"
    Gradle,#9C27B0,"[7.6, 7.4, 7.5]"
        """,
    )

    parser.add_argument(
        "csv_file",
        help="CSV file containing build time data (no headers required - 3 columns: build_system, color, measurements)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="build_performance_report.html",
        help="Output file path for the generated HTML report (default: build_performance_report.html)",
    )
    args = parser.parse_args()

    build_data, custom_colors = read_csv_data(args.csv_file)

    output_file = create_html_report(build_data, custom_colors, output_path=args.output)

    print(f"Interactive build performance report generated: {output_file}")
    print(f"Open {output_file} in your web browser to view")
