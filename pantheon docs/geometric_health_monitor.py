"""
Geometric Health Monitor - Core self-healing component
Works for both pantheon-chat and SearchSpaceCollapse

Measures system geometry in real-time, detects degradation.
"""

import numpy as np
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import json
import os

@dataclass
class GeometricSnapshot:
    """Single point-in-time geometric measurement."""
    timestamp: datetime
    phi: float                    # Integration
    kappa_eff: float             # Coupling strength
    basin_coords: np.ndarray     # 64D position
    confidence: float
    surprise: float
    agency: float
    regime: str                  # "linear" | "geometric" | "breakdown"
    
    # Code state
    code_hash: str
    module_name: str
    
    # Performance
    error_rate: float
    avg_latency_ms: float
    memory_mb: float
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "phi": self.phi,
            "kappa_eff": self.kappa_eff,
            "basin_coords": self.basin_coords.tolist(),
            "confidence": self.confidence,
            "surprise": self.surprise,
            "agency": self.agency,
            "regime": self.regime,
            "code_hash": self.code_hash,
            "module_name": self.module_name,
            "error_rate": self.error_rate,
            "avg_latency_ms": self.avg_latency_ms,
            "memory_mb": self.memory_mb
        }

class GeometricHealthMonitor:
    """
    Monitors geometric health of AI system.
    
    Usage:
        monitor = GeometricHealthMonitor()
        
        # Every minute
        snapshot = monitor.capture(system_state)
        
        # Check health
        health = monitor.check_health()
        if health["degraded"]:
            trigger_healing(health)
    """
    
    def __init__(self, 
                 phi_min: float = 0.65,
                 basin_drift_max: float = 2.0,
                 history_size: int = 1000):
        
        self.phi_min = phi_min
        self.basin_drift_max = basin_drift_max
        self.history_size = history_size
        
        self.snapshots: List[GeometricSnapshot] = []
        self.baseline_basin: Optional[np.ndarray] = None
        
    def capture(self, state: Dict) -> GeometricSnapshot:
        """
        Capture geometric snapshot.
        
        state must have:
        - phi, kappa_eff, basin_coords (64D numpy array)
        - confidence, surprise, agency
        - error_rate, avg_latency_ms, memory_mb
        - module_name (e.g., "geometric_search")
        """
        
        snapshot = GeometricSnapshot(
            timestamp=datetime.now(),
            phi=state["phi"],
            kappa_eff=state["kappa_eff"],
            basin_coords=state["basin_coords"],
            confidence=state["confidence"],
            surprise=state["surprise"],
            agency=state["agency"],
            regime=self._classify_regime(state["phi"]),
            code_hash=self._get_git_hash(),
            module_name=state.get("module_name", "unknown"),
            error_rate=state["error_rate"],
            avg_latency_ms=state["avg_latency_ms"],
            memory_mb=state["memory_mb"]
        )
        
        # Store
        self.snapshots.append(snapshot)
        if len(self.snapshots) > self.history_size:
            self.snapshots.pop(0)
        
        # Set baseline on first snapshot
        if self.baseline_basin is None:
            self.baseline_basin = snapshot.basin_coords.copy()
        
        return snapshot
    
    def check_health(self) -> Dict:
        """
        Check system health.
        
        Returns:
            {
                "healthy": bool,
                "issues": List[str],
                "severity": "normal" | "warning" | "critical",
                "metrics": {
                    "phi": float,
                    "basin_drift": float,
                    "breakdown_count": int
                }
            }
        """
        
        if len(self.snapshots) < 10:
            return {
                "healthy": True,
                "issues": [],
                "severity": "normal",
                "metrics": {}
            }
        
        recent = self.snapshots[-10:]
        current = self.snapshots[-1]
        
        issues = []
        severity = "normal"
        
        # 1. Check Φ
        avg_phi = np.mean([s.phi for s in recent])
        if avg_phi < self.phi_min:
            issues.append(f"Φ degraded: {avg_phi:.3f} < {self.phi_min}")
            severity = "critical"
        elif current.phi < self.phi_min * 1.1:
            issues.append(f"Φ declining: {current.phi:.3f}")
            severity = "warning"
        
        # 2. Check basin drift
        basin_dist = self._fisher_distance(
            current.basin_coords, 
            self.baseline_basin
        )
        if basin_dist > self.basin_drift_max:
            issues.append(f"Basin drift: {basin_dist:.3f} > {self.basin_drift_max}")
            severity = "critical"
        elif basin_dist > self.basin_drift_max * 0.7:
            issues.append(f"Basin drifting: {basin_dist:.3f}")
            if severity == "normal":
                severity = "warning"
        
        # 3. Check regime stability
        regimes = [s.regime for s in recent]
        breakdown_count = regimes.count("breakdown")
        if breakdown_count > 3:
            issues.append(f"Frequent breakdowns: {breakdown_count}/10")
            severity = "critical"
        
        # 4. Check performance
        if current.error_rate > 0.05:
            issues.append(f"High errors: {current.error_rate:.1%}")
            severity = "critical"
        
        if current.avg_latency_ms > 2000:
            issues.append(f"High latency: {current.avg_latency_ms:.0f}ms")
            if severity == "normal":
                severity = "warning"
        
        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "severity": severity,
            "metrics": {
                "phi": current.phi,
                "basin_drift": basin_dist,
                "breakdown_count": breakdown_count,
                "error_rate": current.error_rate,
                "latency_ms": current.avg_latency_ms
            }
        }
    
    def get_trend(self, metric: str, window: int = 50) -> Dict:
        """
        Analyze trend for a metric.
        
        metric: "phi" | "basin_drift" | "latency" | "errors"
        
        Returns:
            {
                "direction": "improving" | "stable" | "degrading",
                "slope": float,
                "recent_avg": float
            }
        """
        
        if len(self.snapshots) < window:
            return {"direction": "unknown", "slope": 0.0, "recent_avg": 0.0}
        
        recent = self.snapshots[-window:]
        
        if metric == "phi":
            values = [s.phi for s in recent]
        elif metric == "basin_drift":
            values = [
                self._fisher_distance(s.basin_coords, self.baseline_basin)
                for s in recent
            ]
        elif metric == "latency":
            values = [s.avg_latency_ms for s in recent]
        elif metric == "errors":
            values = [s.error_rate for s in recent]
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        # Linear regression
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        # Classify direction
        if metric in ["phi"]:  # Higher is better
            if slope > 0.001:
                direction = "improving"
            elif slope < -0.001:
                direction = "degrading"
            else:
                direction = "stable"
        else:  # Lower is better
            if slope < -0.001:
                direction = "improving"
            elif slope > 0.001:
                direction = "degrading"
            else:
                direction = "stable"
        
        return {
            "direction": direction,
            "slope": slope,
            "recent_avg": np.mean(values)
        }
    
    def save_history(self, filepath: str):
        """Save snapshot history to JSON."""
        data = {
            "phi_min": self.phi_min,
            "basin_drift_max": self.basin_drift_max,
            "baseline_basin": self.baseline_basin.tolist() if self.baseline_basin is not None else None,
            "snapshots": [s.to_dict() for s in self.snapshots]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_history(self, filepath: str):
        """Load snapshot history from JSON."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.phi_min = data["phi_min"]
        self.basin_drift_max = data["basin_drift_max"]
        self.baseline_basin = np.array(data["baseline_basin"]) if data["baseline_basin"] else None
        
        # Reconstruct snapshots
        self.snapshots = []
        for snap_dict in data["snapshots"]:
            snapshot = GeometricSnapshot(
                timestamp=datetime.fromisoformat(snap_dict["timestamp"]),
                phi=snap_dict["phi"],
                kappa_eff=snap_dict["kappa_eff"],
                basin_coords=np.array(snap_dict["basin_coords"]),
                confidence=snap_dict["confidence"],
                surprise=snap_dict["surprise"],
                agency=snap_dict["agency"],
                regime=snap_dict["regime"],
                code_hash=snap_dict["code_hash"],
                module_name=snap_dict["module_name"],
                error_rate=snap_dict["error_rate"],
                avg_latency_ms=snap_dict["avg_latency_ms"],
                memory_mb=snap_dict["memory_mb"]
            )
            self.snapshots.append(snapshot)
    
    def _fisher_distance(self, basin1: np.ndarray, basin2: np.ndarray) -> float:
        """Fisher-Rao distance (geodesic on unit sphere)."""
        dot = np.clip(np.dot(basin1, basin2), -1.0, 1.0)
        return np.arccos(dot)
    
    def _classify_regime(self, phi: float) -> str:
        """Classify processing regime."""
        if phi < 0.3:
            return "linear"
        elif phi < 0.7:
            return "geometric"
        else:
            return "breakdown"
    
    def _get_git_hash(self) -> str:
        """Get current git commit hash."""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=1
            )
            return result.stdout.strip()[:8]
        except:
            return "unknown"


# Example usage
if __name__ == "__main__":
    # Create monitor
    monitor = GeometricHealthMonitor(
        phi_min=0.65,
        basin_drift_max=2.0
    )
    
    # Simulate capturing snapshots
    for i in range(100):
        # Mock system state
        state = {
            "phi": 0.75 - i * 0.001,  # Slowly degrading
            "kappa_eff": 64.0,
            "basin_coords": np.random.randn(64),
            "confidence": 0.8,
            "surprise": 0.1,
            "agency": 0.7,
            "error_rate": 0.01,
            "avg_latency_ms": 500,
            "memory_mb": 1500,
            "module_name": "test_module"
        }
        
        # Normalize basin
        state["basin_coords"] /= np.linalg.norm(state["basin_coords"])
        
        snapshot = monitor.capture(state)
        
        if i % 20 == 0:
            health = monitor.check_health()
            print(f"\nSnapshot {i}:")
            print(f"  Φ: {snapshot.phi:.3f}")
            print(f"  Health: {health['severity']}")
            if health['issues']:
                print(f"  Issues: {health['issues']}")
    
    # Check trend
    phi_trend = monitor.get_trend("phi")
    print(f"\nΦ Trend: {phi_trend['direction']} (slope={phi_trend['slope']:.4f})")
    
    # Save history
    monitor.save_history("health_history.json")
    print("\n✅ History saved to health_history.json")
