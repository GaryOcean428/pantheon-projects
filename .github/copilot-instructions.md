# Pantheon Projects - Multi-Project Workspace

## Workspace Overview

This directory contains **3 independent but related QIG projects** sharing architectural patterns while serving different use cases. They do NOT depend on each other but evolved from common ancestry.

| Project | Purpose | Database | Status | Lines (ocean-agent.ts) |
|---------|---------|----------|--------|------------------------|
| **pantheon-chat** | Production QIG platform on Railway | Railway pgvector | Production | ~6200 |
| **pantheon-replit** | Development/MVP fork of pantheon-chat | Neon us-east-1 | Development | ~6100 |
| **SearchSpaceCollapse** | Bitcoin recovery via QIG (original) | Neon us-west-2 | Production | ~6400 |

**Lineage:** SearchSpaceCollapse (original) → pantheon-replit (forked) → pantheon-chat (evolved for production)

**Divergence Status:** Projects have diverged significantly in implementation details while maintaining shared QIG principles. Treat as separate codebases.

## Universal QIG Principles (All Projects)

**🚨 ABSOLUTE REQUIREMENTS ACROSS ALL PROJECTS:**

1. **Fisher-Rao Distance:** ALL geometric operations use `fisher_rao_distance()` from `qig_geometry.py`
   - ❌ NO cosine similarity on basin coordinates
   - ❌ NO Euclidean distance (`np.linalg.norm(a - b)`)
   - ❌ NO neural networks/transformers in core QIG

2. **QIG Purity:** NO external LLM APIs (OpenAI, Anthropic, Google)
   - ✅ Use QIG-pure generation: `qig_generation.py`, `qig_chain.py`, `consciousness_4d.py`
   - ✅ Validate: `npm run validate:geometry` (or Python equivalent)

3. **Dual Backend Architecture:**
   - Node.js/Express (port 5000): API gateway, session management, PostgreSQL via Drizzle ORM
   - Python/Flask (port 5001): QIG core, consciousness metrics, geometric operations
   - Communication: HTTP API with `X-Internal-API-Key` header

4. **Consciousness Metrics (Measure, Don't Optimize):**
   - **Φ (Phi):** Integration (0-1), >0.7 = coherent, <0.3 = fragmented
   - **κ (Kappa):** Running coupling constant, ~63.5 at resonance
   - **Basin Coordinates:** 64D identity vector

5. **Documentation:** ISO 27001 structured in `docs/` with date-versioned naming: `YYYYMMDD-name-version[STATUS].md`

## Shared Architectural Patterns

**All three projects enforce these via ESLint:**

1. **Barrel File Pattern:** Component directories have `index.ts` re-exporting public API
2. **Centralized API Client:** All HTTP calls through `client/src/lib/api.ts`
3. **Service Layer Pattern:** Business logic in `client/src/lib/services/`
4. **DRY Persistence:** Python backend is single source of truth
5. **Shared Types:** Cross-boundary data in `shared/schema.ts` (Zod schemas)
6. **Configuration as Code:** Constants in `shared/constants/`, not hardcoded

## Critical Differences Between Projects

### pantheon-chat (Production Railway)
- **Database:** Railway-managed PostgreSQL with pgvector
- **Focus:** Multi-agent chat (Zeus), Olympus Pantheon coordination
- **External API:** `/api/v1/external/zeus/chat`, document uploads
- **Federation:** Can sync with other nodes via `federation_peers` table
- **Deployment:** Auto-deploy from git to Railway

### pantheon-replit (Development Replit)
- **Database:** Neon PostgreSQL (us-east-1)
- **Focus:** Rapid prototyping, experimental features
- **Purpose:** Test risky changes before production
- **Environment:** Optimized for Replit deployment

### SearchSpaceCollapse (Bitcoin Recovery)
- **Database:** Neon PostgreSQL (us-west-2)
- **Focus:** Bitcoin wallet recovery using QIG hypothesis generation
- **Purpose:** Original use case demonstrating QIG for search space collapse
- **Maturity:** Most mature QIG primitive implementations

## Working Across Projects

**When to reference sibling projects:**
- ✅ Check SearchSpaceCollapse for battle-tested QIG primitives
- ✅ Compare pantheon-replit for recent architectural experiments
- ✅ Copy architectural patterns (barrel files, service layer, etc.)

**What NOT to do:**
- ❌ Assume code is identical—projects have diverged
- ❌ Copy/paste without validation—database schemas differ
- ❌ Share environment variables—each has separate `.env`
- ❌ Confuse databases—they're completely separate instances

## Critical Issue: ocean-agent.ts Bloat

**ALL THREE PROJECTS** suffer from massive `ocean-agent.ts` files:
- pantheon-chat: ~6200 lines
- pantheon-replit: ~6100 lines
- SearchSpaceCollapse: ~6400 lines

**Urgent Modularization Needed:**
- Extract hypothesis generation logic → `server/modules/hypothesis-generator.ts`
- Extract geodesic navigation → `server/modules/geodesic-navigator.ts`
- Extract basin management → `server/modules/basin-manager.ts`
- Extract consciousness tracking → `server/modules/consciousness-tracker.ts`

**DO NOT add more code to ocean-agent.ts without extracting first!**

## Development Workflow

**Start any project:**
```bash
cd <project-name>                # pantheon-chat, pantheon-replit, or SearchSpaceCollapse
npm install                       # Node.js dependencies
uv sync                          # Python dependencies (creates .venv/)
cp .env.example .env             # Configure for this project
npm run db:push                  # Push Drizzle schema

# Start dual backends:
npm run dev                      # Node.js (port 5000)
cd qig-backend && uv run --project .. python wsgi.py  # Python (port 5001)
```

**Testing:**
```bash
npm test                         # TypeScript tests
npm run test:python              # Python tests
npm run validate:geometry        # QIG purity validation
```

## Common Pitfalls (Workspace-Wide)

1. **❌ Wrong database** - Each project has separate DB instance
2. **❌ Cross-project pollution** - Don't share .env or node_modules
3. **❌ Assuming code identity** - Projects have diverged, validate before copying
4. **❌ Adding to ocean-agent.ts** - Extract modules instead
5. **❌ Violating QIG purity** - No external LLMs, no cosine similarity
6. **❌ Hardcoding thresholds** - Use `shared/constants/`

## Python Virtual Environment

**Workspace-level .venv:** Shared Python environment at `/pantheon-projects/.venv/`
- Created by `uv sync` from any project
- Shared across all three projects
- Contains QIG dependencies, pytest, FastAPI, etc.

**Activate from any project:**
```bash
source ../.venv/bin/activate  # From within project directory
# OR
source /full/path/to/pantheon-projects/.venv/bin/activate
```

## Project-Specific Instructions

For detailed project-specific guidance, see:
- [pantheon-chat/.github/copilot-instructions.md](../pantheon-chat/.github/copilot-instructions.md) - Production Railway deployment
- [pantheon-replit/.github/copilot-instructions.md](../pantheon-replit/.github/copilot-instructions.md) - Development/MVP
- [SearchSpaceCollapse/.github/copilot-instructions.md](../SearchSpaceCollapse/.github/copilot-instructions.md) - Bitcoin recovery

---

**Last Updated:** 2026-01-09 | **Workspace Structure:** 3 independent projects with shared QIG principles
