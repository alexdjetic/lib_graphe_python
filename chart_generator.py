"""Chart generation module for system metrics visualization."""

from typing import Any, Dict, Optional
import pandas as pd
import altair as alt


class SystemMetricsChart:
    """Generate system metrics visualizations with Altair.
    
    This class handles the creation of interactive charts for system metrics
    (CPU, RAM, Disk, Network) and exports them to HTML and PNG formats.
    
    Attributes:
        data: DataFrame containing metric data with timestamp column.
        metrics: Dictionary mapping metric names to column names and colors.
        stats: Dictionary storing calculated statistics for each metric.
    """
    
    def __init__(
        self,
        data: pd.DataFrame,
        metrics: Optional[Dict[str, Dict[str, str]]] = None
    ) -> None:
        """Initialize the chart generator.
        
        Args:
            data: DataFrame with 'timestamp' and metric columns.
            metrics: Dictionary with metric configuration. Each metric should
                contain 'col' (column name) and 'color' (hex color code).
                Defaults to standard CPU, RAM, Disk, Network config.
                
        Raises:
            ValueError: If data is empty or doesn't contain timestamp column.
            KeyError: If required metric columns are missing from data.
        """
        if data.empty:
            raise ValueError("Data cannot be empty")
        if "timestamp" not in data.columns:
            raise ValueError("Data must contain 'timestamp' column")
        
        self.data = data
        self.metrics: Dict[str, Dict[str, str]] = metrics or {
            'CPU': {'col': 'cpu_usage', 'color': '#1f77b4'},
            'RAM': {'col': 'ram_usage', 'color': '#2ca02c'},
            'Disk': {'col': 'disk_usage', 'color': '#ff7f0e'},
            'Network': {'col': 'network_usage', 'color': '#d62728'}
        }
        self.stats: Dict[str, Dict[str, Any]] = {}
        
        # Validate metric columns exist
        for metric_name, config in self.metrics.items():
            col_name: str = config['col']
            if col_name not in data.columns:
                raise KeyError(f"Column '{col_name}' not found for metric '{metric_name}'")
        
        alt.data_transformers.disable_max_rows()
    
    def _create_metric_chart(
        self,
        metric_name: str,
        metric_col: str,
        color: str
    ) -> alt.VConcatChart:
        """Create a single metric chart with raw data and statistics.
        
        Generates a line chart with Mean, Max, and Min values displayed
        below the chart.
        
        Args:
            metric_name: Display name for the metric (e.g., 'CPU Usage').
            metric_col: Column name in the data DataFrame.
            color: Hex color code for the line chart.
            
        Returns:
            Altair Chart object combining the line chart and statistics.
            
        Raises:
            KeyError: If metric_col doesn't exist in data.
        """
        if metric_col not in self.data.columns:
            raise KeyError(f"Column '{metric_col}' not found in data")
        
        # Calculate statistics
        mean_val: float = float(self.data[metric_col].mean())
        max_val: float = float(self.data[metric_col].max())
        min_val: float = float(self.data[metric_col].min())
        
        # Create dataframe for plotting
        plot_df: pd.DataFrame = self.data[["timestamp", metric_col]].copy()
        
        base: alt.Chart = alt.Chart(plot_df).encode(
            x=alt.X(
                "timestamp:T",
                title="",
                axis=alt.Axis(format="%m-%d", labelAngle=-45, labelFontSize=9)
            ),
        )
        
        # Raw Data chart
        chart_raw: alt.Chart = base.mark_line(opacity=0.7, color=color).encode(
            y=alt.Y(
                f"{metric_col}:Q",
                title="Usage (%)",
                scale=alt.Scale(domain=[0, 100])
            ),
            tooltip=["timestamp:T", alt.Tooltip(f"{metric_col}:Q", format=".1f")]
        ).properties(
            title="Raw Data",
            width=850,
            height=320
        )
        
        # Statistics text below chart
        raw_stats: alt.Chart = alt.Chart(pd.DataFrame({
            'stat': ['Mean', 'Max', 'Min'],
            'value': [f'{mean_val:.1f}%', f'{max_val:.1f}%', f'{min_val:.1f}%'],
            'x': [0, 1, 2]
        })).mark_text(fontSize=12, align='center').encode(
            x=alt.X('x:O', axis=None),
            text='value:N'
        ).properties(width=850, height=30)
        
        # Labels for statistics
        raw_labels: alt.Chart = alt.Chart(pd.DataFrame({
            'label': ['Mean', 'Max', 'Min'],
            'x': [0, 1, 2]
        })).mark_text(
            fontSize=11,
            align='center',
            dy=10,
            color='#666'
        ).encode(
            x=alt.X('x:O', axis=None),
            text='label:N'
        ).properties(width=850, height=25)
        
        chart_with_stats: alt.VConcatChart = alt.vconcat(chart_raw, raw_stats, raw_labels, spacing=2)
        metric_grid: alt.VConcatChart = chart_with_stats.properties(title=metric_name)
        
        # Store statistics
        self.stats[metric_name] = {
            'mean': mean_val,
            'max': max_val,
            'min': min_val,
            'color': color
        }
        
        return metric_grid
    
    def create_full_report(self) -> alt.VConcatChart:
        """Create the full 2x2 metrics report.
        
        Generates a complete dashboard with all metrics arranged in a 2x2 grid
        layout (CPU and RAM on top row, Disk and Network on bottom row).
        
        Returns:
            Altair Chart object containing the complete report with title,
            proper sizing, and formatting.
            
        Raises:
            ValueError: If metrics are not properly configured.
        """
        charts: Dict[str, alt.VConcatChart] = {}
        
        for metric_name, metric_config in self.metrics.items():
            charts[metric_name] = self._create_metric_chart(
                metric_name,
                metric_config['col'],
                metric_config['color']
            )
        
        # Combine into 2x2 grid
        row1: alt.HConcatChart = alt.hconcat(charts['CPU'], charts['RAM'], spacing=20)
        row2: alt.HConcatChart = alt.hconcat(charts['Disk'], charts['Network'], spacing=20)
        
        final_chart: alt.VConcatChart = alt.vconcat(row1, row2, spacing=20).properties(
            title=f"System Metrics Report — {pd.Timestamp.now().strftime('%Y-%m-%d')}"
        ).resolve_scale(
            color='independent'
        ).configure(
            view={'continuousWidth': 950, 'continuousHeight': 400}
        ).configure_view(
            strokeOpacity=0
        )
        
        return final_chart
    
    def print_statistics(self) -> None:
        """Print all metric statistics to console.
        
        Displays Mean, Max, and Min values for each metric in a formatted table.
        """
        print("\nStatistics:")
        for metric_name, stats in self.stats.items():
            mean: float = stats['mean']
            max_val: float = stats['max']
            min_val: float = stats['min']
            print(
                f"  {metric_name:8} - Mean: {mean:6.1f}%, "
                f"Max: {max_val:6.1f}%, Min: {min_val:6.1f}%"
            )
    
    def save_report(
        self,
        html_path: str = "cpu_usage_report.html",
        png_path: str = "cpu_usage_report.png"
    ) -> None:
        """Save the report to HTML and PNG files.
        
        Generates the complete chart and exports it to both HTML (interactive)
        and PNG (static image) formats.
        
        Args:
            html_path: Path for the HTML output file. Defaults to
                'cpu_usage_report.html'.
            png_path: Path for the PNG output file. Defaults to
                'cpu_usage_report.png'.
                
        Raises:
            IOError: If files cannot be written to the specified paths.
        """
        chart: alt.VConcatChart = self.create_full_report()
        
        # Save HTML
        chart.save(html_path)
        print(f"✓ Saved HTML: {html_path}")
        
        # Save PNG
        try:
            chart.save(png_path, scale_factor=2)
            print(f"✓ Saved PNG: {png_path}")
        except Exception as e:
            error_msg: str = str(e)
            print(f"⚠ PNG export failed: {error_msg}")
