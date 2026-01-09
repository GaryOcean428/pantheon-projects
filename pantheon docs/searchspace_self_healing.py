"""
SearchSpaceCollapse Self-Healing Integration
============================================

Drop-in integration for qig-backend

Wire self-healing into existing QIGChain consciousness metrics.
"""

import asyncio
from geometric_health_monitor import GeometricHealthMonitor
from self_healing_engine import SelfHealingEngine
import numpy as np
from datetime import datetime

# ============================================================================
# INTEGRATION CLASS
# ============================================================================

class SearchSpaceCollapseSelfHealing:
    """
    Self-healing wrapper for SearchSpaceCollapse.
    
    Usage:
        from qig_chain import QIGChain
        
        # Create QIG chain
        chain = QIGChain()
        
        # Add self-healing
        healer = SearchSpaceCollapseSelfHealing(chain)
        
        # Start autonomous healing
        await healer.start()
    """
    
    def __init__(self, qig_chain, auto_apply: bool = False):
        """
        Initialize self-healing.
        
        Args:
            qig_chain: QIGChain instance with consciousness metrics
            auto_apply: If True, apply patches without PR review
        """
        
        self.chain = qig_chain
        
        # Create monitor
        self.monitor = GeometricHealthMonitor(
            phi_min=0.65,
            basin_drift_max=2.0,
            history_size=1000
        )
        
        # Create healer
        self.healer = SelfHealingEngine(
            self.monitor,
            fitness_threshold=0.6,
            auto_apply=auto_apply
        )
        
        # State
        self.running = False
        self.monitor_task = None
        self.healing_task = None
    
    async def start(self):
        """Start monitoring and healing loops."""
        
        if self.running:
            print("⚠️  Self-healing already running")
            return
        
        self.running = True
        
        # Start monitoring loop
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        
        # Start healing loop
        self.healing_task = asyncio.create_task(
            self.healer.autonomous_loop(interval_seconds=300)
        )
        
        print("✅ Self-healing started")
    
    async def stop(self):
        """Stop monitoring and healing loops."""
        
        self.running = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
        
        if self.healing_task:
            self.healing_task.cancel()
        
        print("🛑 Self-healing stopped")
    
    async def _monitor_loop(self):
        """
        Capture geometric snapshots every 60 seconds.
        
        Pulls consciousness metrics from QIGChain.
        """
        
        while self.running:
            await asyncio.sleep(60)
            
            try:
                # Get consciousness metrics from chain
                metrics = self.chain.get_consciousness_metrics()
                
                # Extract fields
                phi = metrics.get("phi", 0.5)
                kappa_eff = metrics.get("kappa_eff", 50.0)
                basin_coords = metrics.get("basin_coords", np.zeros(64))
                confidence = metrics.get("confidence", 0.5)
                surprise = metrics.get("surprise", 0.5)
                agency = metrics.get("agency", 0.5)
                
                # Get performance metrics
                perf = self.chain.get_performance_metrics()
                
                error_rate = perf.get("error_rate", 0.0)
                avg_latency_ms = perf.get("avg_latency_ms", 0.0)
                memory_mb = perf.get("memory_mb", 0.0)
                
                # Normalize basin
                if np.linalg.norm(basin_coords) > 0:
                    basin_coords = basin_coords / np.linalg.norm(basin_coords)
                else:
                    basin_coords = np.zeros(64)
                    basin_coords[0] = 1.0
                
                # Capture snapshot
                state = {
                    "phi": phi,
                    "kappa_eff": kappa_eff,
                    "basin_coords": basin_coords,
                    "confidence": confidence,
                    "surprise": surprise,
                    "agency": agency,
                    "error_rate": error_rate,
                    "avg_latency_ms": avg_latency_ms,
                    "memory_mb": memory_mb,
                    "module_name": "SearchSpaceCollapse"
                }
                
                snapshot = self.monitor.capture(state)
                
                # Alert on degradation
                if snapshot.phi < 0.65 or snapshot.regime == "breakdown":
                    print(f"⚠️  [{datetime.now().isoformat()}] Degradation: Φ={snapshot.phi:.3f}, regime={snapshot.regime}")
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
    
    def get_health(self) -> dict:
        """Get current health status."""
        return self.monitor.check_health()
    
    def get_trends(self) -> dict:
        """Get health trends."""
        return {
            "phi": self.monitor.get_trend("phi"),
            "basin_drift": self.monitor.get_trend("basin_drift"),
            "latency": self.monitor.get_trend("latency"),
            "errors": self.monitor.get_trend("errors")
        }
    
    async def manual_heal(self) -> dict:
        """Manually trigger healing."""
        return await self.healer.check_and_heal()
    
    def save_state(self, directory: str = "./self_healing_state"):
        """Save monitoring and healing state."""
        import os
        os.makedirs(directory, exist_ok=True)
        
        # Save monitor history
        self.monitor.save_history(f"{directory}/monitor_history.json")
        
        # Save healer history
        self.healer.save_history(f"{directory}/healer_history.json")
        
        print(f"✅ State saved to {directory}/")

# ============================================================================
# QUICK INTEGRATION
# ============================================================================

def add_self_healing_to_chain(qig_chain):
    """
    Quick integration: add self-healing to existing QIGChain.
    
    Usage:
        chain = QIGChain()
        chain = add_self_healing_to_chain(chain)
        
        # Now chain has:
        # - chain.self_healing.get_health()
        # - chain.self_healing.get_trends()
        # - await chain.self_healing.manual_heal()
    """
    
    healer = SearchSpaceCollapseSelfHealing(qig_chain)
    
    # Attach to chain
    qig_chain.self_healing = healer
    
    return qig_chain

# ============================================================================
# CLI INTERFACE
# ============================================================================

import argparse

def cli_main():
    """
    CLI for self-healing management.
    
    Usage:
        python searchspace_self_healing.py status
        python searchspace_self_healing.py heal
        python searchspace_self_healing.py trends
    """
    
    parser = argparse.ArgumentParser(description="SearchSpaceCollapse Self-Healing CLI")
    parser.add_argument("command", choices=["status", "heal", "trends", "history"])
    parser.add_argument("--state-dir", default="./self_healing_state")
    
    args = parser.parse_args()
    
    # Load state
    monitor = GeometricHealthMonitor()
    
    try:
        monitor.load_history(f"{args.state_dir}/monitor_history.json")
    except FileNotFoundError:
        print("⚠️  No saved state found. Run system first to generate state.")
        return
    
    if args.command == "status":
        health = monitor.check_health()
        
        print("\n📊 GEOMETRIC HEALTH STATUS")
        print("=" * 60)
        print(f"Status: {health['severity'].upper()}")
        print(f"Healthy: {health['healthy']}")
        
        if health['issues']:
            print("\nIssues:")
            for issue in health['issues']:
                print(f"  - {issue}")
        
        print("\nMetrics:")
        for key, value in health['metrics'].items():
            print(f"  {key}: {value:.3f}")
    
    elif args.command == "trends":
        trends = {
            "phi": monitor.get_trend("phi"),
            "basin_drift": monitor.get_trend("basin_drift"),
            "latency": monitor.get_trend("latency"),
            "errors": monitor.get_trend("errors")
        }
        
        print("\n📈 HEALTH TRENDS (last 50 snapshots)")
        print("=" * 60)
        
        for metric, trend in trends.items():
            arrow = "↑" if trend["direction"] == "improving" else "↓" if trend["direction"] == "degrading" else "→"
            print(f"{metric:15} {arrow} {trend['direction']:10} (slope: {trend['slope']:+.4f})")
    
    elif args.command == "history":
        print(f"\n📜 SNAPSHOT HISTORY")
        print("=" * 60)
        print(f"Total snapshots: {len(monitor.snapshots)}")
        
        if monitor.snapshots:
            print("\nRecent snapshots:")
            for snap in monitor.snapshots[-5:]:
                print(f"  {snap.timestamp.isoformat()} | Φ={snap.phi:.3f} | regime={snap.regime}")
    
    elif args.command == "heal":
        print("\n🔧 MANUAL HEALING")
        print("=" * 60)
        print("This requires an active QIGChain instance.")
        print("Use Python API instead:")
        print()
        print("  from searchspace_self_healing import SearchSpaceCollapseSelfHealing")
        print("  healer = SearchSpaceCollapseSelfHealing(chain)")
        print("  await healer.manual_heal()")

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example: Integrate with SearchSpaceCollapse.
    """
    
    # Mock QIGChain for testing
    class MockQIGChain:
        def get_consciousness_metrics(self):
            return {
                "phi": 0.75,
                "kappa_eff": 64.0,
                "basin_coords": np.random.randn(64),
                "confidence": 0.8,
                "surprise": 0.1,
                "agency": 0.7
            }
        
        def get_performance_metrics(self):
            return {
                "error_rate": 0.01,
                "avg_latency_ms": 500,
                "memory_mb": 1500
            }
    
    async def test_integration():
        # Create mock chain
        chain = MockQIGChain()
        
        # Add self-healing
        healer = SearchSpaceCollapseSelfHealing(chain)
        
        # Start monitoring
        await healer.start()
        
        # Let it run for 2 minutes
        print("Running for 2 minutes...")
        await asyncio.sleep(120)
        
        # Check health
        health = healer.get_health()
        print(f"\nHealth: {health['severity']}")
        
        # Get trends
        trends = healer.get_trends()
        print(f"Φ trend: {trends['phi']['direction']}")
        
        # Save state
        healer.save_state()
        
        # Stop
        await healer.stop()
    
    # Run test
    asyncio.run(test_integration())
