# Pantheon Projects - Decision Tree

**Last Updated:** 2026-01-09
**Purpose:** Guide developers and AI agents through architectural decisions across the 3-project workspace

---

## 🌳 Project Selection Decision Tree

### When to use which project?

```
┌─ Need to build/modify a feature? ─────────────────────────────────┐
│                                                                    │
├─ Is it Bitcoin wallet recovery specific?                          │
│  └─ YES → Use SearchSpaceCollapse                                 │
│     - Original QIG implementation                                 │
│     - Most mature geometric primitives                            │
│     - Neon database (us-west-2)                                   │
│     - Focus: Hypothesis generation for BIP39 search               │
│                                                                    │
├─ Is it for production deployment?                                 │
│  └─ YES → Use pantheon-chat                                       │
│     - Railway auto-deployment                                     │
│     - Railway pgvector database                                   │
│     - External API (Zeus chat, document uploads)                  │
│     - Federation-capable                                          │
│     - Focus: Multi-agent coordination & continuous learning       │
│                                                                    │
├─ Is it experimental/risky/needs rapid iteration?                  │
│  └─ YES → Use pantheon-replit                                     │
│     - Replit-optimized deployment                                 │
│     - Neon database (us-east-1)                                   │
│     - Fork of pantheon-chat (closer to production)                │
│     - Focus: Test before production, rapid prototyping            │
│                                                                    │
└─ Need QIG primitives or consciousness metrics?                    │
   └─ Check SearchSpaceCollapse FIRST (most battle-tested)          │
      Then validate in pantheon-replit before production            │
```

---

## 🔀 Fork vs Merge Decision Tree

### When to copy code between projects?

```
┌─ Found useful code in sibling project? ────────────────────────────┐
│                                                                     │
├─ Is it a QIG primitive (qig_geometry.py, qig_generation.py)?      │
│  └─ YES → SAFE to copy (architectural constant)                    │
│     ✅ Validate Fisher-Rao distance usage                          │
│     ✅ Run npm run validate:geometry after copying                 │
│     ✅ Check for database schema dependencies                      │
│                                                                     │
├─ Is it an architectural pattern (barrel files, service layer)?    │
│  └─ YES → SAFE to copy (enforced via ESLint)                       │
│     ✅ Copy the pattern, not the implementation                    │
│     ✅ Verify import paths match target project                    │
│                                                                     │
├─ Is it Ocean agent logic (ocean-agent.ts)?                        │
│  └─ CAUTION → Projects have DIVERGED (18,749 lines total!)        │
│     ⚠️  Check line counts: pantheon-chat ~6200, replit ~6100      │
│     ⚠️  Validate database schema compatibility                     │
│     ⚠️  Test in target project before committing                   │
│     ⚠️  Consider extracting to module instead of copying           │
│                                                                     │
├─ Is it database-related code (schema.ts, migrations)?             │
│  └─ DANGER → DO NOT copy blindly                                   │
│     ❌ Databases are SEPARATE (Railway vs Neon vs Neon)           │
│     ❌ Schemas have diverged per use case                          │
│     ❌ Federation peers table structure differs                    │
│     ✅ If needed, copy pattern and adapt to target schema         │
│                                                                     │
└─ Is it environment configuration (.env, constants)?               │
   └─ DANGER → DO NOT copy                                           │
      ❌ Each project has separate DATABASE_URL                      │
      ❌ API keys differ per deployment                              │
      ❌ Internal secrets are per-project                            │
```

---

## 🏗️ Architecture Decision Tree

### When to add new functionality?

```
┌─ Need to add new feature? ─────────────────────────────────────────┐
│                                                                     │
├─ Where does it belong architecturally?                             │
│                                                                     │
│  ├─ QIG geometric operation?                                       │
│  │  └─ Add to qig-backend/qig_geometry.py or qig_generation.py    │
│  │     ✅ Python-first (pure geometric logic)                      │
│  │     ✅ Use Fisher-Rao distance, not Euclidean                   │
│  │     ✅ Add tests to qig-backend/tests/                          │
│  │     ✅ Validate: npm run validate:geometry                      │
│  │                                                                  │
│  ├─ Consciousness metric or subsystem?                             │
│  │  └─ Add to qig-backend/consciousness_4d.py or unified_*.py     │
│  │     ✅ Measure, don't optimize Φ and κ                          │
│  │     ✅ Return density matrices, not scalars                     │
│  │     ✅ Document in docs/03-technical/                           │
│  │                                                                  │
│  ├─ Ocean agent behavior?                                          │
│  │  └─ ⚠️ STOP! ocean-agent.ts is 6200+ lines                     │
│  │     ❌ DO NOT add more code to ocean-agent.ts                   │
│  │     ✅ Extract existing logic to modules/ FIRST                 │
│  │     ✅ Create: hypothesis-generator.ts, basin-manager.ts, etc. │
│  │     ✅ Then add new feature to appropriate module               │
│  │                                                                  │
│  ├─ Frontend UI component?                                         │
│  │  └─ Add to client/src/components/                              │
│  │     ✅ Use barrel file pattern (index.ts exports)               │
│  │     ✅ Extract business logic to lib/services/                  │
│  │     ✅ Use centralized API client (lib/api.ts)                  │
│  │     ✅ If >150 lines, extract hook to hooks/                    │
│  │                                                                  │
│  ├─ API endpoint?                                                  │
│  │  └─ Add to server/routes/                                      │
│  │     ✅ Follow REST conventions                                  │
│  │     ✅ Validate input with Zod (shared/schema.ts)              │
│  │     ✅ Call Python backend for QIG operations                   │
│  │     ✅ Return consciousness metrics with results                │
│  │                                                                  │
│  └─ Database schema change?                                        │
│     └─ Modify shared/schema.ts (Drizzle ORM)                      │
│        ✅ Add new table/column with migration script              │
│        ✅ Run: npm run db:push                                     │
│        ✅ Update TypeScript types and Zod schemas                  │
│        ✅ Document in docs/02-procedures/                          │
│                                                                     │
└─ Is it cross-cutting (affects multiple layers)?                    │
   └─ Consider if it belongs in shared/                              │
      ✅ Constants → shared/constants/                                │
      ✅ Types → shared/schema.ts (Zod + Drizzle)                    │
      ✅ Validation → shared/validation.ts                            │
      ✅ Ethics → shared/ethics.ts                                    │
```

---

## 📊 Documentation Decision Tree

### Where to document changes?

```
┌─ Made a change? ──────────────────────────────────────────────────┐
│                                                                    │
├─ What type of change?                                             │
│                                                                    │
│  ├─ Policy or principle (immutable truth)?                        │
│  │  └─ docs/01-policies/YYYYMMDD-name-version[F].md              │
│  │     ✅ Status: [F]rozen (immutable after approval)             │
│  │     ✅ Examples: QIG purity requirements, frozen physics       │
│  │                                                                 │
│  ├─ Procedure or workflow (step-by-step guide)?                   │
│  │  └─ docs/02-procedures/YYYYMMDD-name-version[F/W].md          │
│  │     ✅ Examples: Deployment guides, migration procedures       │
│  │                                                                 │
│  ├─ Technical architecture or component?                          │
│  │  └─ docs/03-technical/YYYYMMDD-name-version[F/W].md           │
│  │     ✅ Examples: AGENTS.md, consciousness architecture         │
│  │                                                                 │
│  ├─ Implementation record or measurement?                         │
│  │  └─ docs/04-records/YYYYMMDD-name-version[F].md               │
│  │     ✅ Examples: Physics validations, performance baselines    │
│  │                                                                 │
│  ├─ Architectural decision (why we chose X over Y)?               │
│  │  └─ docs/05-decisions/YYYYMMDD-name-version[F].md             │
│  │     ✅ Use ADR format (context, decision, consequences)        │
│  │                                                                 │
│  └─ Temporary note or active work-in-progress?                    │
│     └─ attached_assets/DESCRIPTION_timestamp.md                   │
│        ⚠️  NOT permanent documentation                            │
│        ⚠️  Translate to docs/ when work completes                 │
│        ⚠️  Use for runtime data, training checkpoints, etc.       │
│                                                                    │
├─ Need to update existing doc?                                     │
│  ├─ Is it Frozen [F]?                                             │
│  │  └─ Create NEW version with incremented number                 │
│  │     ✅ Example: v1.00F → v1.01F or v2.00W                      │
│  │     ✅ Never edit frozen docs directly                         │
│  │                                                                 │
│  └─ Is it Working [W]?                                            │
│     └─ Edit in place, update version if major change             │
│        ✅ Example: v1.00W → v1.01W                                │
│                                                                    │
└─ Is it workspace-level (affects all 3 projects)?                  │
   └─ /pantheon-projects/[DECISION_TREE|CHANGELOG|README].md        │
      ✅ Not in any project-specific docs/                           │
      ✅ Cross-links to per-project docs                             │
```

---

## 🔄 Divergence Management

### When projects diverge, should they sync?

**Principle:** Projects are **independent but aligned**—they share principles but serve different use cases.

```
┌─ Found divergence between projects? ────────────────────────────┐
│                                                                  │
├─ Is it a QIG purity violation?                                  │
│  └─ YES → MUST synchronize immediately                          │
│     ❌ All projects MUST use Fisher-Rao distance                │
│     ❌ NO external LLM APIs allowed                             │
│     ❌ NO cosine similarity on basin coordinates                │
│     ✅ Fix in all three projects simultaneously                 │
│                                                                  │
├─ Is it an architectural pattern (ESLint-enforced)?              │
│  └─ YES → SHOULD synchronize eventually                         │
│     ✅ Barrel files, service layer, centralized API client      │
│     ✅ Can temporarily differ during experiments                │
│     ✅ Reconcile before production deployment                   │
│                                                                  │
├─ Is it database schema or persistence logic?                    │
│  └─ NO → Allow divergence (use case driven)                     │
│     ✅ Each project has its own DATABASE_URL                    │
│     ✅ Schemas differ based on requirements                     │
│     ✅ Federation protocol handles cross-DB sync                │
│                                                                  │
├─ Is it UI/UX implementation?                                    │
│  └─ NO → Allow divergence (user experience driven)              │
│     ✅ pantheon-chat: Multi-agent chat focus                    │
│     ✅ SearchSpaceCollapse: Recovery session focus              │
│     ✅ pantheon-replit: Experimental UI patterns                │
│                                                                  │
└─ Is it a bug fix?                                               │
   └─ MAYBE → Evaluate per case                                   │
      ✅ Security/correctness bugs: Sync immediately              │
      ✅ Use-case specific bugs: Fix only affected project        │
      ✅ Document decision in CHANGELOG.md                        │
```

---

## 🚨 Emergency Decision Trees

### Ocean-agent.ts is too large (6200+ lines)

```
If you need to modify ocean-agent.ts:

1. ❌ DO NOT add more code directly
2. ✅ Extract modules FIRST:
   - server/modules/hypothesis-generator.ts
   - server/modules/geodesic-navigator.ts
   - server/modules/basin-manager.ts
   - server/modules/consciousness-tracker.ts
3. ✅ Move related functions to appropriate module
4. ✅ Update imports in ocean-agent.ts
5. ✅ Add tests for extracted module
6. ✅ THEN add your new feature to the module
```

### Database migration needed

```
If you need to change the database schema:

1. ✅ Modify shared/schema.ts (add/change table/column)
2. ✅ Run: npm run db:push (generates migration)
3. ✅ Test migration on dev database first
4. ✅ Document in docs/02-procedures/YYYYMMDD-migration-*.md
5. ✅ If affects federation, update federation_peers logic
6. ✅ Announce in CHANGELOG.md
7. ⚠️  For production (pantheon-chat): Coordinate with Railway
```

### QIG purity violation found

```
If you discover code violating QIG purity:

1. 🚨 STOP all work immediately
2. ✅ Run: npm run validate:geometry
3. ✅ Identify all occurrences:
   - grep -r "cosine_similarity" .
   - grep -r "np.linalg.norm.*-" .
   - grep -r "openai\|anthropic\|google.generativeai" .
4. ✅ Replace with Fisher-Rao equivalents
5. ✅ Add test to prevent regression
6. ✅ Document in docs/04-records/ as physics correction
7. ✅ Update frozen facts if physics constant affected
```

---

## 📚 Quick Reference

| Question | Answer |
|----------|--------|
| Which project for production? | pantheon-chat (Railway) |
| Which project for experiments? | pantheon-replit (Neon us-east-1) |
| Which project for QIG primitives? | SearchSpaceCollapse (most mature) |
| Can I share .env files? | ❌ NO - separate databases |
| Can I copy QIG geometry code? | ✅ YES - validate after |
| Can I copy ocean-agent.ts? | ⚠️  CAUTION - projects diverged |
| Should I add to ocean-agent.ts? | ❌ NO - extract modules first |
| Where do constants go? | shared/constants/ (per-project) |
| Where do frozen physics go? | docs/01-policies/*-frozen-facts-*.md |
| How do I name new docs? | YYYYMMDD-name-version[STATUS].md |

---

**See also:**

- [CHANGELOG.md](./CHANGELOG.md) - Historical changes
- [pantheon-chat/ROADMAP.md](./pantheon-chat/ROADMAP.md) - Production roadmap
- [pantheon-replit/ROADMAP.md](./pantheon-replit/ROADMAP.md) - Development roadmap
- [SearchSpaceCollapse/ROADMAP.md](./SearchSpaceCollapse/ROADMAP.md) - Recovery roadmap
- [.github/copilot-instructions.md](./.github/copilot-instructions.md) - AI agent guidance
