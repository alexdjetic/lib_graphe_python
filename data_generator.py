"""Data generation module for system metrics."""

from typing import Any
import pandas as pd
import numpy as np
import polars as pl


def generate_fake_data(n: int = 200) -> pd.DataFrame:
    """Generate fake system metrics data.
    
    Creates synthetic time-series data for CPU, RAM, Disk, and Network
    usage metrics with realistic distributions.
    
    Args:
        n: Number of hourly data points to generate. Defaults to 200.
        
    Returns:
        DataFrame with timestamp and metric columns (cpu_usage, ram_usage,
        disk_usage, network_usage) with values between 0-100%.
        
    Raises:
        ValueError: If n is less than 1.
        
    Example:
        >>> data = generate_fake_data(200)
        >>> data.shape
        (200, 5)
        >>> list(data.columns)
        ['timestamp', 'cpu_usage', 'ram_usage', 'disk_usage', 'network_usage']
    """
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}")
    
    timestamps: pd.DatetimeIndex = pd.date_range("2025-01-01", periods=n, freq="h")
    
    cpu_usage: Any = np.abs(np.random.normal(loc=50, scale=15, size=n)).clip(0, 100)
    ram_usage: Any = np.abs(np.random.normal(loc=65, scale=12, size=n)).clip(0, 100)
    disk_usage: Any = np.abs(np.random.normal(loc=45, scale=10, size=n)).clip(0, 100)
    network_usage: Any = np.abs(np.random.normal(loc=55, scale=20, size=n)).clip(0, 100)
    
    df: pl.DataFrame = pl.DataFrame({
        "timestamp": timestamps,
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage,
        "disk_usage": disk_usage,
        "network_usage": network_usage
    })
    
    result: pd.DataFrame = df.to_pandas()
    return result
