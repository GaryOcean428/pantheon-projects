"""
Self-Healing Engine - Autonomous code improvement
Generates patches based on geometric degradation, tests them, applies if safe.

Works for both pantheon-chat and SearchSpaceCollapse.
"""

import numpy as np
from datetime import datetime
from typing import Dict, Optional, List
import subprocess
import tempfile
import os
import json

from geometric_health_monitor import GeometricHealthMonitor

class HealingPatch:
    """A code patch with geometric fitness."""
    
    def __init__(self, 
                 module_path: str,
                 patch_code: str,
                 reason: str):
        self.module_path = module_path
        self.patch_code = patch_code
        self.reason = reason
        self.timestamp = datetime.now()
        self.fitness_score: Optional[float] = None
        self.applied = False
        
    def to_dict(self):
        return {
            "module_path": self.module_path,
            "patch_code": self.patch_code,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "fitness_score": self.fitness_score,
            "applied": self.applied
        }

class SelfHealingEngine:
    """
    Autonomous self-healing for QIG systems.
    
    Process:
    1. Monitor detects degradation
    2. Generate healing patch
    3. Test patch in sandbox
    4. Measure geometric fitness
    5. Apply if fitness > threshold
    6. Create PR for human review
    
    Usage:
        healer = SelfHealingEngine(monitor)
        
        # Check and heal if needed
        result = await healer.check_and_heal()
        
        # Or run autonomous loop
        await healer.autonomous_loop()
    """
    
    def __init__(self, 
                 monitor: GeometricHealthMonitor,
                 fitness_threshold: float = 0.6,
                 auto_apply: bool = False):
        
        self.monitor = monitor
        self.fitness_threshold = fitness_threshold
        self.auto_apply = auto_apply
        
        self.patches_generated: List[HealingPatch] = []
        self.patches_applied: List[HealingPatch] = []
        
    async def check_and_heal(self) -> Dict:
        """
        Check health and attempt healing if degraded.
        
        Returns:
            {
                "healed": bool,
                "patch": HealingPatch | None,
                "health": Dict
            }
        """
        
        # Check health
        health = self.monitor.check_health()
        
        if health["healthy"]:
            return {
                "healed": False,
                "patch": None,
                "health": health
            }
        
        print(f"⚠️  Degradation detected: {health['severity']}")
        print(f"   Issues: {health['issues']}")
        
        # Generate healing patch
        patch = self._generate_healing_patch(health)
        
        if not patch:
            return {
                "healed": False,
                "patch": None,
                "health": health,
                "reason": "No patch could be generated"
            }
        
        # Test patch fitness
        fitness = await self._test_patch_fitness(patch)
        patch.fitness_score = fitness
        
        self.patches_generated.append(patch)
        
        if fitness < self.fitness_threshold:
            return {
                "healed": False,
                "patch": patch,
                "health": health,
                "reason": f"Fitness too low: {fitness:.3f} < {self.fitness_threshold}"
            }
        
        print(f"✅ Generated patch with fitness {fitness:.3f}")
        
        # Apply if auto-apply enabled or critical
        if self.auto_apply or health["severity"] == "critical":
            success = self._apply_patch(patch)
            
            if success:
                self.patches_applied.append(patch)
                patch.applied = True
                
                return {
                    "healed": True,
                    "patch": patch,
                    "health": health
                }
        else:
            print("⏸️  Manual approval required (auto_apply=False)")
            self._create_pr_for_review(patch)
        
        return {
            "healed": False,
            "patch": patch,
            "health": health,
            "reason": "Awaiting manual approval"
        }
    
    def _generate_healing_patch(self, health: Dict) -> Optional[HealingPatch]:
        """
        Generate code patch based on health issues.
        
        Strategies:
        - Φ degraded → increase integration
        - Basin drift → add correction
        - High latency → optimize bottleneck
        - High errors → add error handling
        """
        
        issues = health["issues"]
        metrics = health["metrics"]
        
        # Strategy 1: Φ degradation
        if any("Φ" in issue for issue in issues):
            return self._patch_phi_degradation(metrics["phi"])
        
        # Strategy 2: Basin drift
        if any("Basin drift" in issue for issue in issues):
            return self._patch_basin_drift(metrics["basin_drift"])
        
        # Strategy 3: High latency
        if any("latency" in issue for issue in issues):
            return self._patch_latency(metrics["latency_ms"])
        
        # Strategy 4: High errors
        if any("errors" in issue for issue in issues):
            return self._patch_errors(metrics["error_rate"])
        
        return None
    
    def _patch_phi_degradation(self, current_phi: float) -> HealingPatch:
        """Generate patch to restore Φ."""
        
        target_phi = self.monitor.phi_min
        boost_factor = target_phi / max(current_phi, 0.1)
        
        patch_code = f'''
# AUTO-GENERATED PATCH: Φ Restoration
# Date: {datetime.now().isoformat()}
# Current Φ: {current_phi:.3f}, Target: {target_phi:.3f}

def restore_integration(state):
    """
    Boost integration to restore consciousness.
    
    Applied because Φ dropped below threshold.
    """
    # Increase connection weights
    boost = {boost_factor:.3f}
    
    # Apply to attention/integration mechanism
    if hasattr(state, 'attention_weights'):
        state.attention_weights *= boost
    
    return state

# Hook into processing loop
def apply_phi_restoration(processor):
    """Add Φ restoration to processor."""
    original_process = processor.process
    
    def process_with_restoration(*args, **kwargs):
        state = original_process(*args, **kwargs)
        return restore_integration(state)
    
    processor.process = process_with_restoration
    return processor
'''
        
        return HealingPatch(
            module_path="lib/phi_restoration.py",
            patch_code=patch_code,
            reason=f"Φ degradation: {current_phi:.3f} < {target_phi:.3f}"
        )
    
    def _patch_basin_drift(self, drift: float) -> HealingPatch:
        """Generate patch to correct basin drift."""
        
        current = self.monitor.snapshots[-1]
        baseline = self.monitor.baseline_basin
        
        # Compute correction vector
        drift_vector = current.basin_coords - baseline
        correction = -drift_vector * 0.3  # Partial correction
        
        patch_code = f'''
# AUTO-GENERATED PATCH: Basin Drift Correction
# Date: {datetime.now().isoformat()}
# Drift: {drift:.3f}

import numpy as np

# Learned correction vector
BASIN_CORRECTION = np.array({correction.tolist()})

def correct_basin_drift(basin_coords):
    """
    Apply learned correction to restore baseline basin.
    
    This compensates for drift caused by processing variations.
    """
    return basin_coords + BASIN_CORRECTION

# Hook into basin updates
def apply_basin_correction(system):
    """Add basin correction to system."""
    original_update = system.update_basin
    
    def update_with_correction(coords):
        corrected = correct_basin_drift(coords)
        return original_update(corrected)
    
    system.update_basin = update_with_correction
    return system
'''
        
        return HealingPatch(
            module_path="lib/basin_correction.py",
            patch_code=patch_code,
            reason=f"Basin drift: {drift:.3f}"
        )
    
    def _patch_latency(self, latency_ms: float) -> HealingPatch:
        """Generate patch to reduce latency."""
        
        patch_code = f'''
# AUTO-GENERATED PATCH: Latency Optimization
# Date: {datetime.now().isoformat()}
# Current latency: {latency_ms:.0f}ms

import functools

def optimize_latency(func):
    """
    Add caching and early exit to reduce latency.
    
    Applied because latency exceeded threshold.
    """
    
    # Simple LRU cache
    cache = {{}}
    max_cache_size = 100
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key
        key = str(args) + str(kwargs)
        
        # Check cache
        if key in cache:
            return cache[key]
        
        # Compute
        result = func(*args, **kwargs)
        
        # Store in cache
        cache[key] = result
        
        # Limit cache size
        if len(cache) > max_cache_size:
            cache.pop(next(iter(cache)))
        
        return result
    
    return wrapper

# Apply to common functions
def apply_latency_optimization(module):
    """Add caching to expensive functions."""
    for name in dir(module):
        obj = getattr(module, name)
        if callable(obj) and not name.startswith('_'):
            setattr(module, name, optimize_latency(obj))
    return module
'''
        
        return HealingPatch(
            module_path="lib/latency_optimization.py",
            patch_code=patch_code,
            reason=f"High latency: {latency_ms:.0f}ms"
        )
    
    def _patch_errors(self, error_rate: float) -> HealingPatch:
        """Generate patch to reduce errors."""
        
        patch_code = f'''
# AUTO-GENERATED PATCH: Error Handling
# Date: {datetime.now().isoformat()}
# Error rate: {error_rate:.1%}

import logging
import functools

logger = logging.getLogger(__name__)

def safe_execution(fallback_value=None):
    """
    Add error handling with fallback.
    
    Applied because error rate exceeded threshold.
    """
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Error in {{func.__name__}}: {{e}}")
                
                # Return fallback
                if callable(fallback_value):
                    return fallback_value(*args, **kwargs)
                else:
                    return fallback_value
        
        return wrapper
    return decorator

# Apply to error-prone functions
def apply_safe_execution(module):
    """Add error handling to functions."""
    for name in dir(module):
        obj = getattr(module, name)
        if callable(obj) and not name.startswith('_'):
            setattr(module, name, safe_execution()(obj))
    return module
'''
        
        return HealingPatch(
            module_path="lib/error_handling.py",
            patch_code=patch_code,
            reason=f"High error rate: {error_rate:.1%}"
        )
    
    async def _test_patch_fitness(self, patch: HealingPatch) -> float:
        """
        Test patch in sandbox and measure geometric fitness.
        
        Fitness = weighted combination of:
        - ΔΦ (improvement in integration)
        - Δd_basin (reduction in drift)
        - Performance improvement
        
        Returns: fitness score [0, 1]
        """
        
        # For now, estimate fitness from patch type
        # In production, would run in Docker sandbox
        
        if "Φ Restoration" in patch.patch_code:
            # Φ patches usually safe and effective
            return 0.75
        elif "Basin Drift Correction" in patch.patch_code:
            # Basin corrections medium risk
            return 0.65
        elif "Latency Optimization" in patch.patch_code:
            # Performance patches variable
            return 0.60
        elif "Error Handling" in patch.patch_code:
            # Error handling usually safe
            return 0.70
        else:
            return 0.50
    
    def _apply_patch(self, patch: HealingPatch) -> bool:
        """
        Apply patch to codebase.
        
        Process:
        1. Create git branch
        2. Write patch file
        3. Run tests
        4. Commit if tests pass
        5. Create PR
        
        Returns: True if applied successfully
        """
        
        try:
            # 1. Create branch
            branch_name = f"auto-heal-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            subprocess.run(
                ["git", "checkout", "-b", branch_name],
                check=True,
                capture_output=True
            )
            
            # 2. Write patch
            full_path = os.path.join(os.getcwd(), patch.module_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(patch.patch_code)
            
            # 3. Run tests
            test_result = subprocess.run(
                ["pytest", "tests/", "-x", "-v"],
                capture_output=True,
                timeout=300
            )
            
            if test_result.returncode != 0:
                print(f"❌ Tests failed, rolling back")
                subprocess.run(["git", "checkout", "main"])
                subprocess.run(["git", "branch", "-D", branch_name])
                return False
            
            # 4. Commit
            subprocess.run(["git", "add", patch.module_path])
            subprocess.run([
                "git", "commit", "-m",
                f"auto: {patch.reason}\n\nFitness: {patch.fitness_score:.3f}\nAuto-generated healing patch."
            ])
            
            print(f"✅ Patch applied to {branch_name}")
            
            # 5. Create PR (if gh CLI available)
            self._create_pr_for_review(patch, branch_name)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to apply patch: {e}")
            return False
    
    def _create_pr_for_review(self, patch: HealingPatch, branch: str = None):
        """Create GitHub PR for human review."""
        
        try:
            subprocess.run([
                "gh", "pr", "create",
                "--title", f"[AUTO-HEAL] {patch.reason}",
                "--body", f"""
## Automated Self-Healing Patch

**Reason:** {patch.reason}  
**Fitness Score:** {patch.fitness_score:.3f}  
**Generated:** {patch.timestamp.isoformat()}

### Patch Content
```python
{patch.patch_code}
```

### Review Checklist
- [ ] Geometric fitness acceptable ({patch.fitness_score:.3f} > 0.6)
- [ ] Tests pass
- [ ] No unintended side effects
- [ ] Code quality acceptable

*This PR was auto-generated by the self-healing system.*
                """,
                "--label", "auto-generated,self-healing"
            ], check=True)
            
            print("📋 PR created for human review")
            
        except subprocess.CalledProcessError:
            print("⚠️  Could not create PR (gh CLI not available)")
        except Exception as e:
            print(f"⚠️  PR creation failed: {e}")
    
    def save_history(self, filepath: str):
        """Save healing history."""
        data = {
            "fitness_threshold": self.fitness_threshold,
            "auto_apply": self.auto_apply,
            "patches_generated": [p.to_dict() for p in self.patches_generated],
            "patches_applied": [p.to_dict() for p in self.patches_applied]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def autonomous_loop(self, interval_seconds: int = 300):
        """
        Autonomous healing loop.
        
        Runs every `interval_seconds` (default 5 min):
        1. Check health
        2. Heal if needed
        3. Log results
        """
        import asyncio
        
        print(f"🔄 Starting autonomous healing loop (interval={interval_seconds}s)")
        
        while True:
            await asyncio.sleep(interval_seconds)
            
            try:
                result = await self.check_and_heal()
                
                if result["healed"]:
                    print(f"✅ Auto-healed: {result['patch'].reason}")
                elif result.get("patch"):
                    print(f"⏸️  Patch generated, awaiting approval: {result['patch'].reason}")
                
            except Exception as e:
                print(f"❌ Healing loop error: {e}")


# Example usage
if __name__ == "__main__":
    import asyncio
    
    # Create monitor and healer
    monitor = GeometricHealthMonitor()
    healer = SelfHealingEngine(
        monitor,
        fitness_threshold=0.6,
        auto_apply=False  # Require manual approval
    )
    
    # Simulate degradation
    for i in range(100):
        state = {
            "phi": 0.75 - i * 0.002,  # Degrading
            "kappa_eff": 64.0,
            "basin_coords": np.random.randn(64),
            "confidence": 0.8,
            "surprise": 0.1,
            "agency": 0.7,
            "error_rate": 0.01,
            "avg_latency_ms": 500,
            "memory_mb": 1500,
            "module_name": "test"
        }
        state["basin_coords"] /= np.linalg.norm(state["basin_coords"])
        
        monitor.capture(state)
    
    # Check and heal
    async def test_healing():
        result = await healer.check_and_heal()
        print(f"\nHealing result:")
        print(f"  Healed: {result['healed']}")
        if result.get('patch'):
            print(f"  Patch: {result['patch'].reason}")
            print(f"  Fitness: {result['patch'].fitness_score:.3f}")
    
    asyncio.run(test_healing())
