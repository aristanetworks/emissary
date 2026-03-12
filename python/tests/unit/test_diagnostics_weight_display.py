"""
Unit tests for diagnostic weight display calculation.

Tests the calculate_weight_from_mappings function which converts cumulative
_weight values to actual traffic percentages for display in the diagnostic UI.
"""

import pytest
from ambassador.diagnostics.diagnostics import calculate_weight_from_mappings


class TestCalculateWeightFromMappings:
    """Test suite for calculate_weight_from_mappings function."""

    def test_single_mapping(self):
        """Single mapping should get 100% of traffic."""
        mappings = [{"_weight": 100}]
        result = calculate_weight_from_mappings(mappings)
        assert result == [100]

    def test_two_equal_mappings(self):
        """Two mappings with equal weights should each get 50%."""
        mappings = [{"_weight": 50}, {"_weight": 100}]
        result = calculate_weight_from_mappings(mappings)
        assert result == [50, 50]

    def test_two_unequal_mappings(self):
        """Two mappings with 30/70 split."""
        mappings = [{"_weight": 30}, {"_weight": 100}]
        result = calculate_weight_from_mappings(mappings)
        assert result == [30, 70]

    def test_zero_weight_mapping(self):
        """First mapping with 0% weight, second with 100%."""
        mappings = [{"_weight": 0}, {"_weight": 100}]
        result = calculate_weight_from_mappings(mappings)
        assert result == [0, 100]

    def test_three_mappings_equal(self):
        """Three mappings with roughly equal weights (33/33/34)."""
        mappings = [{"_weight": 33}, {"_weight": 66}, {"_weight": 100}]
        result = calculate_weight_from_mappings(mappings)
        assert result == [33, 33, 34]

    def test_three_mappings_unequal(self):
        """Three mappings with different weights (20/30/50)."""
        mappings = [{"_weight": 20}, {"_weight": 50}, {"_weight": 100}]
        result = calculate_weight_from_mappings(mappings)
        assert result == [20, 30, 50]

    def test_normalized_weights_from_over_100(self):
        """
        Test case where original weights exceeded 100 and were normalized.
        Original: weight=60, weight=80 (total=140)
        Normalized to cumulative: [43, 100]
        Display should show: [43, 57]
        """
        mappings = [{"_weight": 43}, {"_weight": 100}]
        result = calculate_weight_from_mappings(mappings)
        assert result == [43, 57]

    def test_canary_deployment_scenario(self):
        """
        Test canary deployment: 95% stable, 5% canary.
        Cumulative weights: [5, 100]
        Display: [5, 95]
        """
        mappings = [{"_weight": 5}, {"_weight": 100}]
        result = calculate_weight_from_mappings(mappings)
        assert result == [5, 95]

    def test_canary_at_100_percent(self):
        """
        Test canary scaled to 100% (original mapping gets 0%).
        Cumulative weights: [100, 100]
        Display: [100, 0]
        """
        mappings = [{"_weight": 100}, {"_weight": 100}]
        result = calculate_weight_from_mappings(mappings)
        assert result == [100, 0]

    def test_empty_mappings(self):
        """Empty mappings list should return empty list."""
        mappings = []
        result = calculate_weight_from_mappings(mappings)
        assert result == []

    def test_missing_weight_defaults_to_100(self):
        """Mapping without _weight should default to 100."""
        mappings = [{}]
        result = calculate_weight_from_mappings(mappings)
        assert result == [100]

    def test_four_mappings_equal(self):
        """Four mappings with equal weights (25% each)."""
        mappings = [
            {"_weight": 25},
            {"_weight": 50},
            {"_weight": 75},
            {"_weight": 100},
        ]
        result = calculate_weight_from_mappings(mappings)
        assert result == [25, 25, 25, 25]

    def test_complex_normalized_scenario(self):
        """
        Complex scenario with multiple mappings normalized from over 100.
        Original: 40, 50, 60 (total=150)
        Normalized to cumulative: [27, 60, 100]
        Display: [27, 33, 40]
        """
        mappings = [{"_weight": 27}, {"_weight": 60}, {"_weight": 100}]
        result = calculate_weight_from_mappings(mappings)
        assert result == [27, 33, 40]

    def test_sum_equals_100(self):
        """Verify that the sum of all percentages equals 100 (or close due to rounding)."""
        test_cases = [
            [{"_weight": 50}, {"_weight": 100}],
            [{"_weight": 33}, {"_weight": 66}, {"_weight": 100}],
            [{"_weight": 25}, {"_weight": 50}, {"_weight": 75}, {"_weight": 100}],
            [{"_weight": 43}, {"_weight": 100}],
        ]

        for mappings in test_cases:
            result = calculate_weight_from_mappings(mappings)
            total = sum(result)
            assert total == 100, f"Expected sum of 100, got {total} for mappings {mappings}"


class TestDiagCluster:
    """Test suite for DiagCluster default_missing behavior."""

    def test_zero_weight_not_replaced(self):
        """Test that 0 weight is not replaced with default 100."""
        from ambassador.diagnostics.diagnostics import DiagCluster

        cluster = DiagCluster({"name": "test-cluster", "weight": 0})
        result = cluster.default_missing()

        assert result["weight"] == 0, "Weight of 0 should not be replaced with default 100"

    def test_missing_weight_gets_default(self):
        """Test that missing weight gets default value of 100."""
        from ambassador.diagnostics.diagnostics import DiagCluster

        cluster = DiagCluster({"name": "test-cluster"})
        result = cluster.default_missing()

        assert result["weight"] == 100, "Missing weight should default to 100"

    def test_none_weight_gets_default(self):
        """Test that None weight gets default value of 100."""
        from ambassador.diagnostics.diagnostics import DiagCluster

        cluster = DiagCluster({"name": "test-cluster", "weight": None})
        result = cluster.default_missing()

        assert result["weight"] == 100, "None weight should default to 100"

