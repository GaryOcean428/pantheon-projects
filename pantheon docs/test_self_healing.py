"""
Test Suite for QIG Self-Healing System
=======================================

pytest suite validating all components of geometric health monitoring
and autonomous healing.
"""

import pytest
import numpy as np
import json
import tempfile
import os
from datetime import datetime, timedelta
from geometric_health_monitor import GeometricHealthMonitor, GeometricSnapshot
from self_healing_engine import SelfHealingEngine, HealingPatch

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def monitor():
    """Fresh GeometricHealthMonitor for each test."""
    return GeometricHealthMonitor(
        phi_min=0.65,
        basin_drift_max=2.0,
        history_size=100
    )

@pytest.fixture
def healer(monitor):
    """Fresh SelfHealingEngine for each test."""
    return SelfHealingEngine(
        monitor,
        fitness_threshold=0.6,
        auto_apply=False
    )

@pytest.fixture
def healthy_state():
    """Healthy geometric state."""
    basin = np.random.randn(64)
    basin = basin / np.linalg.norm(basin)
    
    return {
        "phi": 0.75,
        "kappa_eff": 64.0,
        "basin_coords": basin,
        "confidence": 0.8,
        "surprise": 0.1,
        "agency": 0.7,
        "error_rate": 0.01,
        "avg_latency_ms": 500,
        "memory_mb": 1500,
        "module_name": "test_module"
    }

@pytest.fixture
def degraded_phi_state(healthy_state):
    """State with degraded Φ."""
    state = healthy_state.copy()
    state["phi"] = 0.55  # Below threshold
    return state

@pytest.fixture
def drifted_basin_state(healthy_state):
    """State with drifted basin."""
    state = healthy_state.copy()
    # Create basin far from origin
    basin = np.ones(64) * 0.5
    state["basin_coords"] = basin / np.linalg.norm(basin)
    return state

# ============================================================================
# GEOMETRIC SNAPSHOT TESTS
# ============================================================================

class TestGeometricSnapshot:
    """Test GeometricSnapshot dataclass."""
    
    def test_snapshot_creation(self, healthy_state):
        """Test snapshot can be created from state dict."""
        snapshot = GeometricSnapshot(
            timestamp=datetime.now(),
            phi=healthy_state["phi"],
            kappa_eff=healthy_state["kappa_eff"],
            basin_coords=healthy_state["basin_coords"],
            confidence=healthy_state["confidence"],
            surprise=healthy_state["surprise"],
            agency=healthy_state["agency"],
            regime="geometric",
            code_hash="abc123",
            module_name=healthy_state["module_name"],
            error_rate=healthy_state["error_rate"],
            avg_latency_ms=healthy_state["avg_latency_ms"],
            memory_mb=healthy_state["memory_mb"]
        )
        
        assert snapshot.phi == 0.75
        assert snapshot.regime == "geometric"
        assert len(snapshot.basin_coords) == 64
    
    def test_snapshot_serialization(self, healthy_state):
        """Test snapshot can be serialized to/from dict."""
        snapshot = GeometricSnapshot(
            timestamp=datetime.now(),
            **{k: v for k, v in healthy_state.items() 
               if k not in ["module_name"]},
            regime="geometric",
            code_hash="abc123",
            module_name=healthy_state["module_name"]
        )
        
        # Serialize
        snapshot_dict = snapshot.to_dict()
        
        # Deserialize
        restored = GeometricSnapshot.from_dict(snapshot_dict)
        
        assert restored.phi == snapshot.phi
        assert restored.regime == snapshot.regime
        assert np.allclose(restored.basin_coords, snapshot.basin_coords)

# ============================================================================
# GEOMETRIC HEALTH MONITOR TESTS
# ============================================================================

class TestGeometricHealthMonitor:
    """Test GeometricHealthMonitor functionality."""
    
    def test_capture_snapshot(self, monitor, healthy_state):
        """Test capturing a geometric snapshot."""
        snapshot = monitor.capture(healthy_state)
        
        assert snapshot.phi == 0.75
        assert snapshot.regime in ["linear", "geometric", "breakdown"]
        assert len(monitor.snapshots) == 1
    
    def test_baseline_establishment(self, monitor, healthy_state):
        """Test baseline basin is set on first capture."""
        assert monitor.baseline_basin is None
        
        snapshot = monitor.capture(healthy_state)
        
        assert monitor.baseline_basin is not None
        assert len(monitor.baseline_basin) == 64
    
    def test_regime_classification(self, monitor):
        """Test regime classification logic."""
        # Linear regime
        state = {"phi": 0.2, "kappa_eff": 50.0, "basin_coords": np.zeros(64)}
        state["basin_coords"][0] = 1.0
        snapshot = monitor.capture(state)
        assert snapshot.regime == "linear"
        
        # Geometric regime
        state["phi"] = 0.5
        snapshot = monitor.capture(state)
        assert snapshot.regime == "geometric"
        
        # Breakdown regime
        state["phi"] = 0.8
        snapshot = monitor.capture(state)
        assert snapshot.regime == "breakdown"
    
    def test_health_check_healthy(self, monitor, healthy_state):
        """Test health check on healthy system."""
        for _ in range(10):
            monitor.capture(healthy_state)
        
        health = monitor.check_health()
        
        assert health["healthy"] == True
        assert health["severity"] == "normal"
        assert len(health["issues"]) == 0
    
    def test_health_check_phi_degradation(self, monitor, degraded_phi_state):
        """Test health check detects Φ degradation."""
        for _ in range(10):
            monitor.capture(degraded_phi_state)
        
        health = monitor.check_health()
        
        assert health["healthy"] == False
        assert health["severity"] in ["warning", "critical"]
        assert any("Φ" in issue for issue in health["issues"])
    
    def test_health_check_basin_drift(self, monitor, healthy_state, drifted_basin_state):
        """Test health check detects basin drift."""
        # Establish baseline
        monitor.capture(healthy_state)
        
        # Drift away
        for _ in range(10):
            monitor.capture(drifted_basin_state)
        
        health = monitor.check_health()
        
        assert health["healthy"] == False
        assert any("drift" in issue.lower() for issue in health["issues"])
    
    def test_trend_analysis(self, monitor, healthy_state):
        """Test trend analysis functionality."""
        # Create degrading trend
        for i in range(50):
            state = healthy_state.copy()
            state["phi"] = 0.75 - i * 0.005  # Decreasing
            monitor.capture(state)
        
        trend = monitor.get_trend("phi")
        
        assert trend["direction"] == "degrading"
        assert trend["slope"] < 0
    
    def test_history_persistence(self, monitor, healthy_state):
        """Test saving and loading history."""
        # Capture some snapshots
        for _ in range(10):
            monitor.capture(healthy_state)
        
        # Save
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            monitor.save_history(filepath)
            
            # Load into new monitor
            new_monitor = GeometricHealthMonitor()
            new_monitor.load_history(filepath)
            
            assert len(new_monitor.snapshots) == 10
            assert new_monitor.baseline_basin is not None
        finally:
            os.unlink(filepath)
    
    def test_snapshot_limit(self, monitor, healthy_state):
        """Test snapshot history is capped at history_size."""
        # Monitor has history_size=100
        for _ in range(150):
            monitor.capture(healthy_state)
        
        assert len(monitor.snapshots) == 100

# ============================================================================
# SELF-HEALING ENGINE TESTS
# ============================================================================

class TestSelfHealingEngine:
    """Test SelfHealingEngine functionality."""
    
    def test_healer_initialization(self, healer):
        """Test healer initializes correctly."""
        assert healer.monitor is not None
        assert healer.fitness_threshold == 0.6
        assert healer.auto_apply == False
        assert len(healer.patches_generated) == 0
    
    def test_phi_degradation_patch(self, healer, monitor, degraded_phi_state):
        """Test patch generation for Φ degradation."""
        # Create degradation
        for _ in range(10):
            monitor.capture(degraded_phi_state)
        
        # Generate patch
        patch = healer._generate_healing_patch("phi_degradation")
        
        assert patch is not None
        assert "phi" in patch.reason.lower()
        assert "attention" in patch.patch_code.lower()
        assert patch.fitness_score > 0.5
    
    def test_basin_drift_patch(self, healer, monitor, healthy_state, drifted_basin_state):
        """Test patch generation for basin drift."""
        # Establish baseline
        monitor.capture(healthy_state)
        
        # Create drift
        for _ in range(10):
            monitor.capture(drifted_basin_state)
        
        # Generate patch
        patch = healer._generate_healing_patch("basin_drift")
        
        assert patch is not None
        assert "basin" in patch.reason.lower()
        assert "BASIN_CORRECTION" in patch.patch_code
        assert patch.fitness_score > 0.5
    
    def test_latency_patch(self, healer, monitor, healthy_state):
        """Test patch generation for high latency."""
        # Create latency issue
        state = healthy_state.copy()
        state["avg_latency_ms"] = 2500  # High
        
        for _ in range(10):
            monitor.capture(state)
        
        # Generate patch
        patch = healer._generate_healing_patch("latency")
        
        assert patch is not None
        assert "latency" in patch.reason.lower()
        assert "cache" in patch.patch_code.lower() or "optimize" in patch.patch_code.lower()
        assert patch.fitness_score > 0.5
    
    def test_error_patch(self, healer, monitor, healthy_state):
        """Test patch generation for high errors."""
        # Create error issue
        state = healthy_state.copy()
        state["error_rate"] = 0.10  # 10% errors
        
        for _ in range(10):
            monitor.capture(state)
        
        # Generate patch
        patch = healer._generate_healing_patch("errors")
        
        assert patch is not None
        assert "error" in patch.reason.lower()
        assert "try" in patch.patch_code and "except" in patch.patch_code
        assert patch.fitness_score > 0.5
    
    def test_fitness_threshold(self, healer, monitor, degraded_phi_state):
        """Test patches below fitness threshold are rejected."""
        # Create degradation
        for _ in range(10):
            monitor.capture(degraded_phi_state)
        
        # Lower fitness threshold
        healer.fitness_threshold = 0.9  # Very high
        
        result = healer.check_and_heal()
        
        # No patch should be applied (fitness < threshold)
        assert result["patch"] is None or not result["applied"]
    
    def test_auto_apply_disabled(self, healer):
        """Test auto_apply=False prevents automatic application."""
        assert healer.auto_apply == False
        
        # Even with degradation, should not auto-apply
        # (Would need mock git/PR creation to test fully)
    
    def test_patch_history_persistence(self, healer, monitor, degraded_phi_state):
        """Test saving and loading patch history."""
        # Generate a patch
        for _ in range(10):
            monitor.capture(degraded_phi_state)
        
        healer.check_and_heal()
        
        # Save history
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            healer.save_history(filepath)
            
            # Load into new healer
            new_monitor = GeometricHealthMonitor()
            new_healer = SelfHealingEngine(new_monitor)
            new_healer.load_history(filepath)
            
            assert len(new_healer.patches_generated) > 0
        finally:
            os.unlink(filepath)

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test complete self-healing workflow."""
    
    def test_full_healing_cycle(self, healer, monitor, healthy_state, degraded_phi_state):
        """Test complete cycle: detect → patch → validate."""
        # Start healthy
        for _ in range(5):
            monitor.capture(healthy_state)
        
        # Health check should pass
        health = monitor.check_health()
        assert health["healthy"] == True
        
        # Degrade
        for _ in range(10):
            monitor.capture(degraded_phi_state)
        
        # Health check should fail
        health = monitor.check_health()
        assert health["healthy"] == False
        
        # Trigger healing
        result = healer.check_and_heal()
        
        # Patch should be generated
        assert result["patch"] is not None
        assert result["issue_detected"] == True
    
    def test_degradation_sequence(self, monitor, healthy_state):
        """Test monitoring a realistic degradation sequence."""
        # Gradual degradation
        for i in range(50):
            state = healthy_state.copy()
            state["phi"] = 0.75 - i * 0.01  # Slowly decreasing
            
            # Add noise
            state["phi"] += np.random.normal(0, 0.02)
            state["phi"] = np.clip(state["phi"], 0, 1)
            
            monitor.capture(state)
        
        # Should detect degradation
        health = monitor.check_health()
        trend = monitor.get_trend("phi")
        
        assert health["healthy"] == False
        assert trend["direction"] == "degrading"
    
    def test_false_positive_avoidance(self, healer, monitor, healthy_state):
        """Test healer doesn't trigger on healthy system."""
        # Capture healthy snapshots
        for _ in range(20):
            monitor.capture(healthy_state)
        
        # Check health
        health = monitor.check_health()
        assert health["healthy"] == True
        
        # Try healing (should do nothing)
        result = healer.check_and_heal()
        
        assert result["issue_detected"] == False
        assert result["patch"] is None

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance characteristics."""
    
    def test_snapshot_capture_performance(self, monitor, healthy_state, benchmark):
        """Test snapshot capture is fast."""
        def capture():
            monitor.capture(healthy_state)
        
        # Should capture in < 10ms
        result = benchmark(capture)
        assert result.stats.mean < 0.01  # 10ms
    
    def test_health_check_performance(self, monitor, healthy_state, benchmark):
        """Test health check is fast even with 1000 snapshots."""
        # Fill with snapshots
        for _ in range(1000):
            monitor.capture(healthy_state)
        
        def check_health():
            monitor.check_health()
        
        # Should check in < 100ms
        result = benchmark(check_health)
        assert result.stats.mean < 0.1  # 100ms
    
    def test_memory_usage(self, monitor, healthy_state):
        """Test memory usage stays bounded."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Capture many snapshots
        for _ in range(2000):
            monitor.capture(healthy_state)
        
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_increase = mem_after - mem_before
        
        # Should use < 50MB for 1000 snapshots (capped)
        assert mem_increase < 50

# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_history(self, monitor):
        """Test health check with no snapshots."""
        health = monitor.check_health()
        
        # Should handle gracefully
        assert "healthy" in health
    
    def test_invalid_basin_coords(self, monitor, healthy_state):
        """Test handling of invalid basin coordinates."""
        state = healthy_state.copy()
        state["basin_coords"] = np.zeros(64)  # Zero vector (invalid)
        
        # Should normalize to valid basin
        snapshot = monitor.capture(state)
        
        assert np.linalg.norm(snapshot.basin_coords) > 0.99
        assert np.linalg.norm(snapshot.basin_coords) < 1.01
    
    def test_nan_values(self, monitor, healthy_state):
        """Test handling of NaN values."""
        state = healthy_state.copy()
        state["phi"] = np.nan
        
        # Should handle gracefully
        snapshot = monitor.capture(state)
        
        # NaN should be replaced with default
        assert not np.isnan(snapshot.phi)
    
    def test_negative_metrics(self, monitor, healthy_state):
        """Test handling of negative metric values."""
        state = healthy_state.copy()
        state["phi"] = -0.5  # Invalid (should be 0-1)
        
        snapshot = monitor.capture(state)
        
        # Should clip to valid range
        assert 0 <= snapshot.phi <= 1
    
    def test_very_large_drift(self, monitor, healthy_state):
        """Test handling of extreme basin drift."""
        # Establish baseline
        monitor.capture(healthy_state)
        
        # Create extreme drift
        state = healthy_state.copy()
        state["basin_coords"] = -monitor.baseline_basin  # Opposite direction
        
        for _ in range(10):
            monitor.capture(state)
        
        health = monitor.check_health()
        
        # Should detect as critical
        assert health["severity"] == "critical"
        assert "drift" in str(health["issues"]).lower()

# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    """
    Run tests with:
        pytest test_self_healing.py -v
        pytest test_self_healing.py -v --benchmark-only
        pytest test_self_healing.py -v -k "test_health"
    """
    pytest.main([__file__, "-v"])
