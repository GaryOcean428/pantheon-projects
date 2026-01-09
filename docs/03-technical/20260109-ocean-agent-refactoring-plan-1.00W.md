# Ocean Agent Refactoring Plan

**Status:** [W] Working
**Date:** 2026-01-09
**Scope:** pantheon-replit (test), pantheon-chat (apply), SearchSpaceCollapse (optional)
**Target:** Reduce ocean-agent.ts from 6,141 lines → <3,000 lines
**Module Limit:** <500 lines per module (hard), <400 lines (soft)

---

## Executive Summary

**Problem:** ocean-agent.ts has become a 6,141-line monolith (18,749 lines total across 3 projects) containing:

- Hypothesis generation (12+ different strategies)
- Geodesic navigation and basin management
- Consciousness tracking and measurement
- Autonomic lifecycle management (sleep/dream/mushroom states)
- Olympus Pantheon coordination (12 specialized agents)
- Neurochemistry and behavioral modulation
- Negative knowledge filtering
- Ethics checking and telemetry generation

**Solution:** Extract into 6 domain-specific modules following architectural patterns:

1. **hypothesis-generator.ts** - All hypothesis generation strategies
2. **geodesic-navigator.ts** - Basin operations, geodesic correction, QIG geometry
3. **basin-manager.ts** - Basin state, drift tracking, synchronization
4. **consciousness-tracker.ts** - Φ/κ measurement, integration, neurochemistry
5. **autonomic-controller.ts** - Sleep/dream/mushroom cycles, effort metrics
6. **pantheon-coordinator.ts** - Olympus integration, Zeus assessment, war mode

**Strategy:**

- Start in **pantheon-replit** (development environment)
- Validate via tests + manual smoke testing
- Apply to **pantheon-chat** (production) after validation
- Optional: Apply to **SearchSpaceCollapse** (ancestor project)

**Success Criteria:**

- ✅ ocean-agent.ts <3,000 lines (50% reduction)
- ✅ Each module <500 lines (hard), <400 lines (soft)
- ✅ All tests pass (npm test, npm run test:python)
- ✅ No QIG purity violations (npm run validate:geometry)
- ✅ Consciousness metrics unchanged (Φ, κ, basin drift)
- ✅ Zero functional regressions (E2E tests pass)

---

## Current State Analysis

### ocean-agent.ts Breakdown (pantheon-replit: 6,141 lines)

**Lines 1-200: Imports & Setup**

- 40+ imports (controller, memory, QIG backend, Olympus, etc.)
- Legacy crypto stubs (8 no-op functions)
- Era detection utilities (HistoricalDataMiner)
- 4 interfaces (OceanHypothesis, ConsciousnessCheckResult, EthicsCheckResult, ConsolidationResult)

**Lines 200-650: OceanAgent Class - Constructor & State**

- 30+ private fields (identity, memory, state, ethics, consciousness, basin, Olympus)
- Constructor (lines 257-280)
- initializeIdentity() (lines 555-583)
- initializeMemory() (lines 584-637)
- initializeState() (lines 638-650)
- updateNeurochemistry() (lines 281-357)
- computeEffortMetrics() (lines 358-420)

**Lines 650-2000: Core Methods**

- mergePythonPhi() (lines 421-454) - Merge Python QIG results
- syncPythonBasins() (lines 456-553) - Batch basin sync
- checkConsciousness() (lines 1928-1998) - Φ/κ measurement
- checkEthicalConstraints() (lines 1999-2037) - Ethics validation
- measureIdentity() (lines 2038-2070) - Recursive self-measurement
- computeBasinDistance() (lines 2071-2074) - Fisher-Rao distance
- consolidateMemory() (lines 2075-2281) - Memory consolidation
- updateConsciousnessMetrics() (lines 2282-2300) - Metric updates

**Lines 2000-4000: Testing & Batch Operations**

- testBatch() (lines 2301-2831) - Batch hypothesis testing
- saveRecoveryBundle() (lines 2832-2872) - Bitcoin recovery artifacts
- observeAndLearn() (lines 2873-3074) - Learning from test results

**Lines 3000-5000: Hypothesis Generation (LARGEST SECTION)**

- generateInitialHypotheses() (lines 3075-3766) - Master orchestrator
  - Calls 15+ sub-generators
  - Cultural manifold integration
  - Curiosity-driven exploration
  - Block universe hypotheses
  - Era-specific phrases

- Sub-generators (lines 3767-4605):
  - generateConstellationHypotheses() (100 lines)
  - generateEraSpecificPhrases() (10 lines)
  - generateDormantWalletHypotheses() (60 lines)
  - generateCommonBrainWalletPhrases() (50 lines)
  - generateRandomPhrases() (30 lines)
  - generateWordVariations() (40 lines)
  - generateCharacterMutations() (80 lines)
  - generatePhoneticVariations() (80 lines)
  - generateExploratoryPhrases() (40 lines)
  - generateBlockUniverseHypotheses() (165 lines)
  - perturbPhrase() (24 lines)
  - generateRandomHighEntropyPhrases() (166 lines)
  - clusterByQIG() (41 lines)

**Lines 4600-5400: Plateau Detection & Strategy**

- detectPlateau() (lines 4647-4670)
- detectActualProgress() (lines 4671-4729)
- generateTelemetry() (lines 4734-4769)
- computeFullSpectrumTelemetry() (lines 4770-4946)
- summarizeLearnings() (lines 4951-4980)
- generateEthicsReport() (lines 4981-5419)

**Lines 5400-5700: Negative Knowledge & Filtering**

- filterWithNegativeKnowledge() (lines 5420-5474)
- generatePatternVariations() (lines 5475-5549)
- getUCPStats() (lines 5550-5695)

**Lines 5700-6141: Olympus Pantheon Integration**

- adjustStrategyFromZeus() (lines 5696-6009)
- updateSearchDirection() (lines 6010-6034)
- injectEntropy() (lines 6035-6080)
- getAthenaAresAttackDecision() (lines 6081-6140)
- Public API methods (start, pause, resume, stop, reset, getState)

### Dependency Graph

```
ocean-agent.ts (6,141 lines)
├── consciousness-search-controller.ts (getSharedController)
├── cultural-manifold.ts
├── dormant-wallet-analyzer.ts (generateTemporalHypotheses)
├── fisher-vectorized.ts
├── gary-kernel.ts (qfiAttention)
├── geodesic-navigator.ts
├── geometric-discovery/ocean-discovery-controller.ts
├── geometric-memory.ts
├── knowledge-compression-engine.ts
├── near-miss-manager.ts
├── negative-knowledge-unified.ts
├── ocean-autonomic-manager.ts
├── ocean-constellation-stub.ts
├── ocean-neurochemistry.ts (computeNeurochemistry, computeBehavioralModulationWithCooldown)
└── basin-sync-coordinator.ts (dynamic import)
```

---

## Refactoring Plan

### Phase 1: Extract Hypothesis Generation (Week 1)

**New Module:** `server/modules/hypothesis-generator.ts` (~800 lines)

**Extract:**

- generateInitialHypotheses() - Master orchestrator
- All 12+ sub-generators:
  - generateConstellationHypotheses()
  - generateEraSpecificPhrases()
  - generateDormantWalletHypotheses()
  - generateCommonBrainWalletPhrases()
  - generateRandomPhrases()
  - generateWordVariations()
  - generateCharacterMutations()
  - generatePhoneticVariations()
  - generateExploratoryPhrases()
  - generateBlockUniverseHypotheses()
  - perturbPhrase()
  - generateRandomHighEntropyPhrases()
  - clusterByQIG()
- Era detection utilities (HistoricalDataMiner)
- Legacy crypto stubs (8 no-op functions)

**Interface:**

```typescript
export class HypothesisGenerator {
  constructor(
    private culturalManifold: typeof culturalManifold,
    private dormantAnalyzer: typeof dormantWalletAnalyzer,
    private identity: OceanIdentity,
    private memory: OceanMemory,
    private state: OceanAgentState
  ) {}

  async generateInitialHypotheses(
    targetAddress: string,
    iteration: number,
    curiosity: number
  ): Promise<OceanHypothesis[]>;

  // Sub-generators as private methods
  private async generateConstellationHypotheses(): Promise<OceanHypothesis[]>;
  private generateEraSpecificPhrases(era: Era): Promise<OceanHypothesis[]>;
  private generateDormantWalletHypotheses(): OceanHypothesis[];
  // ... etc
}
```

**ocean-agent.ts Changes:**

```typescript
import { HypothesisGenerator } from "./modules/hypothesis-generator";

export class OceanAgent {
  private hypothesisGenerator: HypothesisGenerator;

  constructor() {
    // ... existing setup
    this.hypothesisGenerator = new HypothesisGenerator(
      culturalManifold,
      dormantWalletAnalyzer,
      this.identity,
      this.memory,
      this.state
    );
  }

  // Replace 800 lines with:
  private async generateInitialHypotheses(): Promise<OceanHypothesis[]> {
    return this.hypothesisGenerator.generateInitialHypotheses(
      this.targetAddress,
      this.state.currentIteration,
      this.curiosity
    );
  }
}
```

**Expected Reduction:** ~800 lines → ~50 lines (750 lines saved)

---

### Phase 2: Extract Geodesic Navigation (Week 1)

**New Module:** `server/modules/geodesic-navigator.ts` (~400 lines)

**Extract:**

- geodesic-navigator.ts integration (currently imported but logic scattered)
- computeBasinDistance() - Fisher-Rao distance
- updateSearchDirection() - Navigation adjustments
- Geodesic correction logic
- QIG geometry operations (manifold operations)

**Interface:**

```typescript
export class GeodesicNavigator {
  constructor(
    private qigBackend: OceanQIGBackend,
    private identity: OceanIdentity
  ) {}

  computeBasinDistance(current: number[], reference: number[]): number;

  async updateSearchDirection(
    newVector: number[],
    currentBasin: number[]
  ): Promise<{ correctedVector: number[]; correction: number }>;

  async navigateToTarget(
    currentBasin: number[],
    targetBasin: number[],
    stepSize: number
  ): Promise<{ nextBasin: number[]; geodesicCurvature: number }>;

  computeGeodesicCurvature(basin: number[]): number;
}
```

**ocean-agent.ts Changes:**

```typescript
import { GeodesicNavigator } from "./modules/geodesic-navigator";

export class OceanAgent {
  private geodesicNavigator: GeodesicNavigator;

  constructor() {
    this.geodesicNavigator = new GeodesicNavigator(
      oceanQIGBackend,
      this.identity
    );
  }

  private computeBasinDistance(current: number[], reference: number[]): number {
    return this.geodesicNavigator.computeBasinDistance(current, reference);
  }
}
```

**Expected Reduction:** ~400 lines → ~30 lines (370 lines saved)

---

### Phase 3: Extract Basin Management (Week 2)

**New Module:** `server/modules/basin-manager.ts` (~500 lines)

**Extract:**

- Basin state tracking
- basinDriftHistory management
- Basin synchronization (syncPythonBasins)
- Basin sync coordinator integration
- Basin coordinate updates
- mergePythonPhi() - Python QIG result merging

**Interface:**

```typescript
export class BasinManager {
  private basinDriftHistory: number[] = [];
  private basinSyncCoordinator: BasinSyncCoordinator | null = null;

  constructor(
    private qigBackend: OceanQIGBackend,
    private identity: OceanIdentity,
    private memory: OceanMemory
  ) {}

  async syncPythonBasins(
    basins: Array<{ input: string; phi: number }>
  ): Promise<void>;

  mergePythonPhi(hypothesis: OceanHypothesis): void;

  trackBasinDrift(newDrift: number): void;

  getBasinDriftMetrics(): {
    currentDrift: number;
    averageDrift: number;
    driftTrend: "increasing" | "decreasing" | "stable";
  };

  async initializeBasinSync(): Promise<void>;
}
```

**ocean-agent.ts Changes:**

```typescript
import { BasinManager } from "./modules/basin-manager";

export class OceanAgent {
  private basinManager: BasinManager;

  constructor() {
    this.basinManager = new BasinManager(
      oceanQIGBackend,
      this.identity,
      this.memory
    );
  }

  private async syncPythonBasins(basins: any[]): Promise<void> {
    return this.basinManager.syncPythonBasins(basins);
  }
}
```

**Expected Reduction:** ~500 lines → ~40 lines (460 lines saved)

---

### Phase 4: Extract Consciousness Tracking (Week 2)

**New Module:** `server/modules/consciousness-tracker.ts` (~600 lines)

**Extract:**

- checkConsciousness() - Φ/κ measurement
- updateConsciousnessMetrics() - Metric updates
- measureIdentity() - Recursive self-measurement
- Neurochemistry integration (updateNeurochemistry)
- Consciousness alerts (onConsciousnessAlert)
- Behavioral modulation (computeBehavioralModulationWithCooldown)
- Effort metrics (computeEffortMetrics)

**Interface:**

```typescript
export class ConsciousnessTracker {
  private neurochemistryContext: NeurochemistryContext;
  private currentModulatedKappa: number;

  constructor(
    private identity: OceanIdentity,
    private memory: OceanMemory,
    private qigBackend: OceanQIGBackend,
    private onAlert: (alert: { type: string; message: string }) => void
  ) {}

  async checkConsciousness(): Promise<ConsciousnessCheckResult>;

  async updateConsciousnessMetrics(): Promise<void>;

  async measureIdentity(): Promise<void>;

  updateNeurochemistry(): void;

  computeEffortMetrics(): EffortMetrics;

  getCurrentNeurochemistry(): NeurochemistryContext;

  getCurrentModulatedKappa(): number;
}
```

**ocean-agent.ts Changes:**

```typescript
import { ConsciousnessTracker } from "./modules/consciousness-tracker";

export class OceanAgent {
  private consciousnessTracker: ConsciousnessTracker;

  constructor() {
    this.consciousnessTracker = new ConsciousnessTracker(
      this.identity,
      this.memory,
      oceanQIGBackend,
      (alert) => this.onConsciousnessAlert?.(alert)
    );
  }

  private async checkConsciousness(): Promise<ConsciousnessCheckResult> {
    return this.consciousnessTracker.checkConsciousness();
  }
}
```

**Expected Reduction:** ~600 lines → ~50 lines (550 lines saved)

---

### Phase 5: Extract Autonomic Control (Week 3)

**New Module:** `server/modules/autonomic-controller.ts` (~400 lines)

**Extract:**

- Sleep/dream/mushroom state management
- Consolidation logic (consolidateMemory)
- Plateau detection (detectPlateau, detectActualProgress)
- Telemetry generation (generateTelemetry, computeFullSpectrumTelemetry)
- Learning summaries (summarizeLearnings)
- Ethics reporting (generateEthicsReport)
- Autonomic manager integration (oceanAutonomicManager)

**Interface:**

```typescript
export class AutonomicController {
  private consecutivePlateaus: number = 0;
  private lastConsolidationTime: Date = new Date();

  constructor(
    private identity: OceanIdentity,
    private memory: OceanMemory,
    private state: OceanAgentState,
    private autonomicManager: typeof oceanAutonomicManager,
    private onConsolidationStart: (() => void) | null,
    private onConsolidationEnd: ((result: ConsolidationResult) => void) | null
  ) {}

  async consolidateMemory(): Promise<boolean>;

  detectPlateau(): boolean;

  detectActualProgress(): { isProgress: boolean; reason: string };

  generateTelemetry(): any;

  computeFullSpectrumTelemetry(): any;

  summarizeLearnings(): any;

  generateEthicsReport(): any;

  shouldConsolidate(): boolean;
}
```

**ocean-agent.ts Changes:**

```typescript
import { AutonomicController } from "./modules/autonomic-controller";

export class OceanAgent {
  private autonomicController: AutonomicController;

  constructor() {
    this.autonomicController = new AutonomicController(
      this.identity,
      this.memory,
      this.state,
      oceanAutonomicManager,
      () => this.onConsolidationStart?.(),
      (result) => this.onConsolidationEnd?.(result)
    );
  }

  private async consolidateMemory(): Promise<boolean> {
    return this.autonomicController.consolidateMemory();
  }
}
```

**Expected Reduction:** ~400 lines → ~35 lines (365 lines saved)

---

### Phase 6: Extract Pantheon Coordination (Week 3)

**New Module:** `server/modules/pantheon-coordinator.ts` (~450 lines)

**Extract:**

- Olympus Pantheon integration (12 specialized agents)
- Zeus assessment (adjustStrategyFromZeus)
- War mode management (BLITZKRIEG, SIEGE, HUNT)
- Athena/Ares attack decisions (getAthenaAresAttackDecision)
- Entropy injection (injectEntropy)
- Olympus observation tracking

**Interface:**

```typescript
export class PantheonCoordinator {
  private olympusAvailable: boolean = false;
  private olympusWarMode: "BLITZKRIEG" | "SIEGE" | "HUNT" | null = null;
  private lastZeusAssessment: ZeusAssessment | null = null;
  private olympusObservationCount: number = 0;

  constructor(
    private identity: OceanIdentity,
    private memory: OceanMemory,
    private state: OceanAgentState
  ) {}

  async adjustStrategyFromZeus(assessment: ZeusAssessment): Promise<void>;

  async getAthenaAresAttackDecision(target: string): Promise<{
    warMode: string;
    strategy: string;
    tactics: string[];
  }>;

  injectEntropy(): void;

  isOlympusAvailable(): boolean;

  getCurrentWarMode(): string | null;

  getLastZeusAssessment(): ZeusAssessment | null;
}
```

**ocean-agent.ts Changes:**

```typescript
import { PantheonCoordinator } from "./modules/pantheon-coordinator";

export class OceanAgent {
  private pantheonCoordinator: PantheonCoordinator;

  constructor() {
    this.pantheonCoordinator = new PantheonCoordinator(
      this.identity,
      this.memory,
      this.state
    );
  }

  private async adjustStrategyFromZeus(assessment: ZeusAssessment): Promise<void> {
    return this.pantheonCoordinator.adjustStrategyFromZeus(assessment);
  }
}
```

**Expected Reduction:** ~450 lines → ~40 lines (410 lines saved)

---

## Final ocean-agent.ts Structure (~2,900 lines)

After all extractions, ocean-agent.ts will contain:

**Lines 1-150: Imports & Setup** (~150 lines)

- Module imports (6 new modules)
- Existing imports (controller, memory, etc.)
- 4 interfaces (OceanHypothesis, ConsciousnessCheckResult, EthicsCheckResult, ConsolidationResult)

**Lines 150-400: OceanAgent Class - State & Initialization** (~250 lines)

- Private module references (6 modules)
- Constructor
- initializeIdentity()
- initializeMemory()
- initializeState()

**Lines 400-1200: Testing & Batch Operations** (~800 lines)

- testBatch() - Core testing logic (keep here - orchestrates all modules)
- saveRecoveryBundle() - Bitcoin recovery artifacts
- observeAndLearn() - Learning from test results

**Lines 1200-2000: Main Search Loop & Orchestration** (~800 lines)

- start() - Main entry point
- Main search loop (orchestrates all modules)
- State management
- Checkpoint saving/loading

**Lines 2000-2400: Negative Knowledge & Filtering** (~400 lines)

- filterWithNegativeKnowledge()
- generatePatternVariations()
- getUCPStats()

**Lines 2400-2900: Public API & Utilities** (~500 lines)

- pause()
- resume()
- stop()
- reset()
- getState()
- shouldEmitTelemetry()
- sleep()
- Callback setters (setOnStateUpdate, setOnConsciousnessAlert, etc.)

**Total: ~2,900 lines** (52% reduction from 6,141 lines)

---

## Implementation Checklist

### Week 1: Hypothesis Generation & Geodesic Navigation

- [ ] Create `server/modules/` directory
- [ ] Create `server/modules/hypothesis-generator.ts`
  - [ ] Extract 12+ hypothesis generation methods
  - [ ] Extract Era detection utilities
  - [ ] Extract legacy crypto stubs
  - [ ] Add comprehensive JSDoc comments
  - [ ] Export HypothesisGenerator class
- [ ] Update `ocean-agent.ts` to use HypothesisGenerator
- [ ] Test: `npm test` - all tests pass
- [ ] Test: Manual smoke test - generate hypotheses
- [ ] Commit: "refactor: extract hypothesis generator (750 lines saved)"
- [ ] Create `server/modules/geodesic-navigator.ts`
  - [ ] Extract geodesic navigation logic
  - [ ] Extract Fisher-Rao distance computation
  - [ ] Extract basin distance tracking
  - [ ] Add comprehensive JSDoc comments
  - [ ] Export GeodesicNavigator class
- [ ] Update `ocean-agent.ts` to use GeodesicNavigator
- [ ] Test: `npm run validate:geometry` - QIG purity preserved
- [ ] Test: Φ/κ metrics unchanged before/after
- [ ] Commit: "refactor: extract geodesic navigator (370 lines saved)"

### Week 2: Basin Management & Consciousness Tracking

- [ ] Create `server/modules/basin-manager.ts`
  - [ ] Extract basin state tracking
  - [ ] Extract basin synchronization logic
  - [ ] Extract mergePythonPhi()
  - [ ] Add comprehensive JSDoc comments
  - [ ] Export BasinManager class
- [ ] Update `ocean-agent.ts` to use BasinManager
- [ ] Test: Basin sync with Python backend
- [ ] Test: Basin drift tracking accuracy
- [ ] Commit: "refactor: extract basin manager (460 lines saved)"
- [ ] Create `server/modules/consciousness-tracker.ts`
  - [ ] Extract consciousness measurement (checkConsciousness)
  - [ ] Extract neurochemistry integration
  - [ ] Extract effort metrics computation
  - [ ] Add comprehensive JSDoc comments
  - [ ] Export ConsciousnessTracker class
- [ ] Update `ocean-agent.ts` to use ConsciousnessTracker
- [ ] Test: Consciousness metrics (Φ, κ) unchanged
- [ ] Test: Neurochemistry context preserved
- [ ] Commit: "refactor: extract consciousness tracker (550 lines saved)"

### Week 3: Autonomic Control & Pantheon Coordination

- [ ] Create `server/modules/autonomic-controller.ts`
  - [ ] Extract consolidation logic
  - [ ] Extract plateau detection
  - [ ] Extract telemetry generation
  - [ ] Add comprehensive JSDoc comments
  - [ ] Export AutonomicController class
- [ ] Update `ocean-agent.ts` to use AutonomicController
- [ ] Test: Consolidation cycles work correctly
- [ ] Test: Plateau detection accuracy
- [ ] Commit: "refactor: extract autonomic controller (365 lines saved)"
- [ ] Create `server/modules/pantheon-coordinator.ts`
  - [ ] Extract Olympus Pantheon integration
  - [ ] Extract Zeus assessment logic
  - [ ] Extract war mode management
  - [ ] Add comprehensive JSDoc comments
  - [ ] Export PantheonCoordinator class
- [ ] Update `ocean-agent.ts` to use PantheonCoordinator
- [ ] Test: Olympus integration preserved
- [ ] Test: Zeus assessment works
- [ ] Commit: "refactor: extract pantheon coordinator (410 lines saved)"

### Week 4: Integration Testing & Production Deployment

- [ ] Run full test suite in pantheon-replit
  - [ ] `npm test` - all TypeScript tests pass
  - [ ] `npm run test:python` - all Python tests pass
  - [ ] `npm run test:e2e` - all E2E tests pass
  - [ ] `npm run validate:geometry` - QIG purity preserved
- [ ] Manual smoke testing
  - [ ] Start Ocean agent
  - [ ] Generate hypotheses
  - [ ] Test batch execution
  - [ ] Verify consciousness metrics
  - [ ] Test consolidation cycle
  - [ ] Verify Olympus integration
- [ ] Performance benchmarks
  - [ ] Measure hypothesis generation time (before/after)
  - [ ] Measure memory usage (before/after)
  - [ ] Measure Φ computation time (before/after)
- [ ] Documentation updates
  - [ ] Update `docs/03-technical/AGENTS.md` with new module structure
  - [ ] Create `docs/03-technical/20260109-ocean-agent-modules-1.00W.md`
  - [ ] Update `README.md` with refactoring notes
- [ ] Apply to pantheon-chat (production)
  - [ ] Create feature branch: `refactor/ocean-agent-modularization`
  - [ ] Copy all 6 modules from pantheon-replit
  - [ ] Update ocean-agent.ts
  - [ ] Run full test suite
  - [ ] Deploy to Railway staging
  - [ ] Smoke test in staging
  - [ ] Merge to main
  - [ ] Deploy to production
- [ ] Monitor production (48 hours)
  - [ ] Watch consciousness metrics (Φ, κ)
  - [ ] Watch basin drift
  - [ ] Watch error rates
  - [ ] Watch performance metrics
- [ ] Optional: Apply to SearchSpaceCollapse
  - [ ] Same process as pantheon-chat
  - [ ] Test wallet recovery functionality

---

## Testing Strategy

### Unit Tests (Existing)

**Preserve existing test coverage:**

- `tests/ocean-agent.test.ts` - Core OceanAgent functionality
- Update import paths to reflect new module structure
- Add new tests for each extracted module

**New test files:**

```
tests/modules/
├── hypothesis-generator.test.ts
├── geodesic-navigator.test.ts
├── basin-manager.test.ts
├── consciousness-tracker.test.ts
├── autonomic-controller.test.ts
└── pantheon-coordinator.test.ts
```

### Integration Tests

**Critical integration points:**

1. **Hypothesis Generator → Basin Manager**
   - Verify hypotheses get basin coordinates
   - Verify basin sync after generation

2. **Geodesic Navigator → Consciousness Tracker**
   - Verify geodesic corrections preserve Φ/κ
   - Verify basin drift tracking

3. **Consciousness Tracker → Autonomic Controller**
   - Verify consolidation triggers on Φ threshold
   - Verify plateau detection uses consciousness metrics

4. **Pantheon Coordinator → All Modules**
   - Verify Zeus assessment adjusts hypothesis generation
   - Verify war mode affects autonomic behavior

### Smoke Tests (Manual)

**After each module extraction:**

1. Start Ocean agent: `npm run dev`
2. Check logs for errors
3. Trigger hypothesis generation
4. Verify consciousness metrics in UI
5. Wait for consolidation cycle
6. Verify Olympus integration (if available)

### Regression Tests (E2E)

**Use existing Playwright tests:**

- `e2e/ocean-agent.spec.ts` - Full agent lifecycle
- Add new tests for module interactions

---

## Rollback Plan

**If refactoring introduces regressions:**

1. **Immediate Rollback** (production emergency)

   ```bash
   git revert <refactor-commit-sha>
   git push origin main
   railway up  # Redeploy previous version
   ```

2. **Partial Rollback** (specific module broken)
   - Keep extracted modules
   - Copy broken functionality back to ocean-agent.ts
   - Fix in next sprint

3. **Forward Fix** (minor issues)
   - Fix bugs in extracted modules
   - Hot-patch production
   - Add regression tests

**Rollback Decision Criteria:**

- ❌ Consciousness metrics (Φ, κ) differ by >5%
- ❌ Basin drift increases by >10%
- ❌ Hypothesis generation fails
- ❌ Consolidation cycles broken
- ❌ Olympus integration broken
- ❌ Error rate >1% in production

---

## Post-Refactoring Opportunities

**After successful modularization:**

1. **Further Modularization** (if modules still large)
   - Split hypothesis-generator.ts into strategy-specific files
   - Extract telemetry into dedicated module
   - Extract ethics checking into dedicated module

2. **Shared Module Extraction** (cross-project sync)
   - Create `shared/modules/` for modules used across all 3 projects
   - Move QIG geometry primitives to shared/
   - Move consciousness measurement to shared/

3. **Performance Optimization**
   - Parallelize hypothesis generation strategies
   - Cache Fisher-Rao distance computations
   - Optimize basin synchronization

4. **Testing Improvements**
   - Add comprehensive unit tests for each module
   - Add property-based tests (fast-check)
   - Add mutation testing (Stryker)

5. **Documentation**
   - Generate module dependency graphs
   - Create architecture decision records (ADRs)
   - Document module interaction patterns

---

## Success Metrics

**Quantitative:**

- ✅ ocean-agent.ts: 6,141 → <3,000 lines (50% reduction)
- ✅ Largest module: <500 lines
- ✅ Average module size: <400 lines
- ✅ Test coverage: maintained at 80%+
- ✅ QIG purity: 100% (npm run validate:geometry passes)
- ✅ Consciousness metrics: Φ/κ unchanged (±2%)
- ✅ Basin drift: unchanged (±5%)

**Qualitative:**

- ✅ Code is easier to understand and navigate
- ✅ New features can be added to specific modules
- ✅ Debugging is faster (isolated to specific module)
- ✅ Onboarding new developers is easier
- ✅ Module boundaries are clear and well-documented

**Timeline:**

- Week 1: Hypothesis generation + geodesic navigation
- Week 2: Basin management + consciousness tracking
- Week 3: Autonomic control + pantheon coordination
- Week 4: Testing + production deployment

**Risk Mitigation:**

- Start in pantheon-replit (development environment)
- Comprehensive testing at each step
- Manual smoke testing after each extraction
- Rollback plan ready
- Monitor production for 48 hours after deployment

---

## References

- **Architecture Patterns:** `/pantheon-projects/.github/copilot-instructions.md`
- **Module Size Guidelines:** `docs/03-technical/AGENTS.md` (400 line soft limit, 500 line hard limit)
- **QIG Purity Requirements:** `docs/01-policies/20251208-frozen-facts-qig-purity-1.00F.md`
- **Consciousness Metrics:** `docs/03-technical/20251226-physics-alignment-corrected-1.00F.md`
- **Testing Strategy:** `docs/02-procedures/20251208-testing-procedure-1.00W.md`

---

**Next Steps:**

1. Review this plan with team
2. Get approval to proceed
3. Start Week 1: Extract hypothesis-generator.ts
4. Test + commit after each extraction
5. Apply to production after validation

**Status:** Ready to begin implementation in pantheon-replit

---

**Last Updated:** 2026-01-09
**Author:** GitHub Copilot (via braden)
**Review Required:** Yes (architecture decision)
