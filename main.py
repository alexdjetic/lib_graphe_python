"""Main entry point for the system metrics report generator.

This module orchestrates the generation of system metrics visualizations
by coordinating data generation and chart creation.
"""

import pandas as pd
from data_generator import generate_fake_data
from chart_generator import SystemMetricsChart


def main() -> None:
    """Generate and save system metrics report.
    
    This function performs the following steps:
    1. Generates synthetic system metrics data
    2. Creates metric visualizations
    3. Exports report to HTML and PNG formats
    4. Prints statistics to console
    """
    # Generate synthetic data
    data: pd.DataFrame = generate_fake_data(200)
    
    # Create chart generator and report
    chart_gen: SystemMetricsChart = SystemMetricsChart(data)
    
    # Save report in both formats
    chart_gen.save_report()
    
    # Display statistics
    chart_gen.print_statistics()


if __name__ == "__main__":
    main()
