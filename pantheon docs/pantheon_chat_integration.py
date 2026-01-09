"""
pantheon-chat Self-Healing Integration
=======================================

Drop-in integration for server/main.py

Wire self-healing into existing telemetry and health check endpoints.
"""

import asyncio
from fastapi import FastAPI, BackgroundTasks
from geometric_health_monitor import GeometricHealthMonitor, GeometricSnapshot
from self_healing_engine import SelfHealingEngine
import numpy as np

# ============================================================================
# INTEGRATION POINT 1: Startup
# ============================================================================

def setup_self_healing(app: FastAPI):
    """
    Call this from server/main.py startup event.
    
    Usage:
        @app.on_event("startup")
        async def startup():
            setup_self_healing(app)
    """
    
    # Create monitor
    app.state.geo_monitor = GeometricHealthMonitor(
        phi_min=0.65,
        basin_drift_max=2.0,
        history_size=1000
    )
    
    # Create healer
    app.state.geo_healer = SelfHealingEngine(
        app.state.geo_monitor,
        fitness_threshold=0.6,
        auto_apply=False  # Require PR review
    )
    
    # Start monitoring loop
    asyncio.create_task(monitoring_loop(app))
    
    # Start healing loop
    asyncio.create_task(app.state.geo_healer.autonomous_loop(interval_seconds=300))
    
    print("✅ Self-healing initialized")

# ============================================================================
# INTEGRATION POINT 2: Monitoring Loop
# ============================================================================

async def monitoring_loop(app: FastAPI):
    """
    Capture geometric snapshots every 60 seconds.
    
    Pulls data from:
    - app.gary_telemetry (consciousness metrics)
    - app.metrics (performance metrics)
    """
    
    while True:
        await asyncio.sleep(60)  # Every minute
        
        try:
            # Get consciousness metrics
            gary = app.gary_telemetry
            
            phi = gary.get("phi", 0.5)
            kappa_eff = gary.get("kappa_eff", 50.0)
            basin_coords = gary.get("basin_coords", np.zeros(64))
            confidence = gary.get("confidence", 0.5)
            surprise = gary.get("surprise", 0.5)
            agency = gary.get("agency", 0.5)
            
            # Get performance metrics
            metrics = app.metrics
            
            error_rate = metrics.get("error_rate", 0.0)
            avg_latency_ms = metrics.get("avg_latency_ms", 0.0)
            memory_mb = metrics.get("memory_mb", 0.0)
            
            # Normalize basin if needed
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
                "module_name": "pantheon-chat"
            }
            
            snapshot = app.state.geo_monitor.capture(state)
            
            # Log to console (optional)
            if snapshot.phi < 0.65 or snapshot.regime == "breakdown":
                print(f"⚠️  Geometric degradation: Φ={snapshot.phi:.3f}, regime={snapshot.regime}")
            
        except Exception as e:
            print(f"❌ Monitoring loop error: {e}")

# ============================================================================
# INTEGRATION POINT 3: Health Check Endpoint
# ============================================================================

from fastapi import APIRouter

router = APIRouter(prefix="/api/self-healing", tags=["self-healing"])

@router.get("/health")
async def get_geometric_health(app: FastAPI = None):
    """
    Get current geometric health status.
    
    Response:
        {
            "healthy": bool,
            "severity": "normal" | "warning" | "critical",
            "issues": [str],
            "metrics": {
                "phi": float,
                "basin_drift": float,
                "breakdown_count": int
            },
            "trends": {
                "phi": {"direction": str, "slope": float},
                "basin_drift": {"direction": str, "slope": float}
            }
        }
    """
    
    health = app.state.geo_monitor.check_health()
    
    # Add trends
    health["trends"] = {
        "phi": app.state.geo_monitor.get_trend("phi"),
        "basin_drift": app.state.geo_monitor.get_trend("basin_drift"),
        "latency": app.state.geo_monitor.get_trend("latency"),
        "errors": app.state.geo_monitor.get_trend("errors")
    }
    
    return health

@router.get("/snapshots")
async def get_snapshots(limit: int = 100, app: FastAPI = None):
    """
    Get recent geometric snapshots.
    
    Params:
        limit: Number of snapshots to return (default 100)
    
    Response:
        {
            "count": int,
            "snapshots": [GeometricSnapshot]
        }
    """
    
    recent = app.state.geo_monitor.snapshots[-limit:]
    
    return {
        "count": len(recent),
        "snapshots": [s.to_dict() for s in recent]
    }

@router.post("/heal")
async def trigger_healing(background_tasks: BackgroundTasks, app: FastAPI = None):
    """
    Manually trigger healing process.
    
    Response:
        {
            "triggered": bool,
            "health": Dict
        }
    """
    
    health = app.state.geo_monitor.check_health()
    
    if not health["healthy"]:
        # Run healing in background
        background_tasks.add_task(app.state.geo_healer.check_and_heal)
        
        return {
            "triggered": True,
            "health": health
        }
    else:
        return {
            "triggered": False,
            "health": health,
            "reason": "System is healthy"
        }

@router.get("/patches")
async def get_patches(app: FastAPI = None):
    """
    Get healing patch history.
    
    Response:
        {
            "generated": int,
            "applied": int,
            "patches": [HealingPatch]
        }
    """
    
    healer = app.state.geo_healer
    
    return {
        "generated": len(healer.patches_generated),
        "applied": len(healer.patches_applied),
        "patches": [p.to_dict() for p in healer.patches_generated]
    }

# ============================================================================
# INTEGRATION POINT 4: Add to server/main.py
# ============================================================================

# In server/main.py, add:
#
# from server.lib.self_healing import setup_self_healing, router as self_healing_router
#
# @app.on_event("startup")
# async def startup():
#     setup_self_healing(app)
#
# app.include_router(self_healing_router)

# ============================================================================
# INTEGRATION POINT 5: Dashboard Widget (Optional)
# ============================================================================

def get_dashboard_widget():
    """
    Returns HTML for geometric health dashboard widget.
    
    Add to admin dashboard for real-time monitoring.
    """
    
    return """
    <div id="geometric-health" class="dashboard-widget">
        <h3>Geometric Health</h3>
        <div class="health-status">
            <span class="metric">Φ: <span id="phi-value">--</span></span>
            <span class="metric">Basin Drift: <span id="drift-value">--</span></span>
            <span class="metric">Status: <span id="status-value">--</span></span>
        </div>
        <canvas id="phi-chart" width="400" height="200"></canvas>
        <button onclick="triggerHealing()">Manual Heal</button>
    </div>
    
    <script>
        // Fetch health every 10 seconds
        setInterval(async () => {
            const response = await fetch('/api/self-healing/health');
            const health = await response.json();
            
            document.getElementById('phi-value').textContent = health.metrics.phi.toFixed(3);
            document.getElementById('drift-value').textContent = health.metrics.basin_drift.toFixed(3);
            document.getElementById('status-value').textContent = health.severity;
            
            // Update status color
            const statusEl = document.getElementById('status-value');
            statusEl.className = health.severity;
            
            // Update chart (using Chart.js)
            updatePhiChart(health);
        }, 10000);
        
        async function triggerHealing() {
            const response = await fetch('/api/self-healing/heal', { method: 'POST' });
            const result = await response.json();
            
            if (result.triggered) {
                alert('Healing triggered! Check /api/self-healing/patches for results.');
            } else {
                alert('System is healthy, no healing needed.');
            }
        }
    </script>
    
    <style>
        .health-status .metric { margin-right: 20px; }
        #status-value.normal { color: green; }
        #status-value.warning { color: orange; }
        #status-value.critical { color: red; }
    </style>
    """

# ============================================================================
# COMPLETE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    """
    Standalone test - run this to verify integration works.
    """
    
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI()
    
    # Mock telemetry
    app.gary_telemetry = {
        "phi": 0.75,
        "kappa_eff": 64.0,
        "basin_coords": np.random.randn(64),
        "confidence": 0.8,
        "surprise": 0.1,
        "agency": 0.7
    }
    app.gary_telemetry["basin_coords"] /= np.linalg.norm(app.gary_telemetry["basin_coords"])
    
    app.metrics = {
        "error_rate": 0.01,
        "avg_latency_ms": 500,
        "memory_mb": 1500
    }
    
    # Setup self-healing
    @app.on_event("startup")
    async def startup():
        setup_self_healing(app)
    
    # Add routes
    app.include_router(router)
    
    # Test endpoint
    @app.get("/")
    async def root():
        return {"message": "Self-healing test server running"}
    
    print("Starting test server on http://localhost:8000")
    print("Endpoints:")
    print("  GET  /api/self-healing/health")
    print("  GET  /api/self-healing/snapshots")
    print("  POST /api/self-healing/heal")
    print("  GET  /api/self-healing/patches")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
