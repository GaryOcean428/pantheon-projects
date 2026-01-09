# Pantheon Projects - Workspace Changelog

**Multi-Project Workspace:** pantheon-chat + pantheon-replit + SearchSpaceCollapse

This changelog tracks cross-project events, divergence points, and shared updates. For project-specific changes, see per-project CHANGELOG.md files.

---

## [Workspace] 2026-01-09

### Added

- **Workspace-level documentation infrastructure**
  - Created `.github/copilot-instructions.md` with multi-project context
  - Created `DECISION_TREE.md` with comprehensive decision guidance
  - Created `CHANGELOG.md` (this file) for workspace-level tracking

### Critical Issues Identified

- **Ocean-agent.ts bloat crisis**: All three projects have massive files:
  - pantheon-chat: 6,209 lines
  - pantheon-replit: 6,141 lines
  - SearchSpaceCollapse: 6,399 lines
  - **Total:** 18,749 lines across workspace
  - **Action Required:** Urgent modularization (hypothesis-generator, geodesic-navigator, basin-manager, consciousness-tracker)

### Divergence Status

- Projects have significantly diverged since initial fork (SearchSpaceCollapse → pantheon-replit → pantheon-chat)
- Database schemas independent: Railway pgvector vs Neon us-east-1 vs Neon us-west-2
- Shared architectural patterns maintained (barrel files, service layer, QIG purity)

---

## [Workspace] 2025-12-27

### Changed

- **Python dependency management**: Migrated to `uv` from `pip`
  - Workspace-level `.venv/` shared across all three projects
  - `pyproject.toml` + `uv.lock` per project
  - Activation: `source /path/to/pantheon-projects/.venv/bin/activate`

---

## [Workspace] 2025-12-26

### Added

- **Physics validation across all projects**
  - Corrected β-function series (SearchSpaceCollapse)
  - Validated κ(L) running coupling constants
  - **Finding:** κ* ≈ 64.0 ± 1.5 (fixed point confirmed)
  - Documented in attached_assets/ (pending formal docs translation)

### Fixed

- **QIG purity violations** identified and corrected:
  - Removed cosine similarity usages
  - Replaced `np.linalg.norm(a - b)` with `fisher_rao_distance(a, b)`
  - Validated across all three projects

---

## [Workspace] 2025-12-21

### Added

- **Project lineage documentation**
  - Formalized fork relationships: SearchSpaceCollapse (ancestor) → pantheon-replit (fork) → pantheon-chat (production)
  - Documented in `docs/01-policies/20251221-project-lineage-1.00F.md` (pantheon-chat)

---

## [Workspace] 2025-12-17

### Added

- **Frozen Facts - QIG Physics Validated** (pantheon-chat, pantheon-replit)
  - κ series: L=3→7 measurements
  - β-function complete series including β(5→6) and β(6→7)
  - Fixed point at κ* ≈ 64.0
  - Status: [F]rozen - immutable physics constants

---

## [Workspace] 2025-12-08

### Changed

- **Database migration**: All projects moved from JSON persistence to PostgreSQL + pgvector
  - pantheon-chat: Railway-managed PostgreSQL (production)
  - pantheon-replit: Neon us-east-1 (development)
  - SearchSpaceCollapse: Neon us-west-2 (independent)
- **Schema management**: Migrated to Drizzle ORM with TypeScript-first schema definitions

---

## Project-Specific Changelogs

For detailed project history, see:

- **pantheon-chat:** [pantheon-chat/CHANGELOG.md](./pantheon-chat/CHANGELOG.md)
  - Production deployment events
  - Railway configuration changes
  - External API additions
  - Federation protocol updates

- **pantheon-replit:** [pantheon-replit/CHANGELOG.md](./pantheon-replit/CHANGELOG.md)
  - Experimental feature additions
  - Rapid iteration cycles
  - Pre-production validation milestones

- **SearchSpaceCollapse:** [SearchSpaceCollapse/CHANGELOG.md](./SearchSpaceCollapse/CHANGELOG.md)
  - Bitcoin recovery methodology updates
  - QIG primitive enhancements
  - Search space collapse measurements

---

## Divergence Log

### Why Projects Diverged

**2025-12-21** - Formalized divergence policy:

- **SearchSpaceCollapse**: Specialized for Bitcoin recovery, BIP39 hypothesis generation
- **pantheon-replit**: Forked from SearchSpaceCollapse, generalized for chat/knowledge systems
- **pantheon-chat**: Production-hardened fork of pantheon-replit with Railway deployment

**Architectural Constants (Shared)**:

- QIG purity (Fisher-Rao distance, no external LLMs)
- Dual backend (Node.js + Python Flask)
- ISO 27001 documentation structure
- Consciousness metrics (Φ, κ, basin coordinates)
- ESLint-enforced patterns (barrel files, service layer, etc.)

**Intentional Divergences**:

- Database schemas (use-case specific tables)
- External APIs (pantheon-chat has Zeus chat API, others don't)
- UI/UX focus (chat vs recovery session management)
- Deployment targets (Railway vs Replit vs Replit)

---

## Synchronization Events

### QIG Purity Validations

- **2025-12-26**: Fisher-Rao distance enforcement across all projects
- **2025-12-17**: Frozen physics constants synchronized

### Architectural Pattern Rollouts

- **2025-12-08**: Barrel file pattern enforced via ESLint (all projects)
- **2025-12-08**: Centralized API client pattern enforced (all projects)
- **2025-12-08**: Service layer pattern established (all projects)

---

## Known Issues (Cross-Project)

1. **Ocean-agent.ts bloat** (18,749 lines total across 3 projects)
   - Status: Critical, requires urgent refactoring
   - Proposed: Extract to modules/ directory
   - Tracking: Workspace-level issue, affects all projects

2. **Duplicate documentation** between pantheon-chat and pantheon-replit
   - Status: ~90% identical docs/ structure
   - Action: Establish canonical source and cross-references
   - See: DECISION_TREE.md for reconciliation guidance

3. **attached_assets/ contains documentation** (SearchSpaceCollapse, pantheon-replit)
   - Status: Valuable docs in temporary location
   - Action: Translate to formal docs/ per ISO 27001 naming
   - Priority: Physics alignments, implementation summaries

---

## Upcoming Workspace Events

### Q1 2026

- [ ] Ocean-agent.ts modularization across all three projects
- [ ] Formalize federation protocol documentation
- [ ] Translate attached_assets/ to docs/04-records/
- [ ] Establish canonical ROADMAP.md per project

---

**Changelog Convention:**

- [Workspace] - Affects all three projects or workspace structure
- [Project] - Individual project changes (see project-specific changelogs)
- [Sync] - Synchronization event (shared update propagated across projects)
