import pytest
import pandas as pd
import numpy as np

def calculate_z_score(value, mean, std):
    if std == 0: return 0
    return (value - mean) / std

def test_z_score_logic():
    # Test typical outlier
    assert calculate_z_score(100, 50, 10) == 5.0
    # Test normal value
    assert calculate_z_score(60, 50, 10) == 1.0
    # Test zero variance
    assert calculate_z_score(100, 50, 0) == 0

def test_concentration_math():
    total_spend = 1000
    code_spend = 960
    concentration = code_spend / total_spend
    assert concentration == 0.96
    assert concentration > 0.95 # Threshold

def test_sudden_utilization_threshold():
    first_month_spend = 1_500_000
    threshold = 1_000_000
    assert first_month_spend > threshold
