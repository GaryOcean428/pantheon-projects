# Vocabulary Integration Status Report

**Date**: 2026-01-11
**Type**: Cross-Project Analysis
**Status**: FROZEN (Implementation Complete)

---

## Executive Summary

Reviewed 6 sleep/dream packet documents describing vocabulary integration features. Analysis reveals:

| Project | Vocab Auto-Integration | Domain Vocabulary Bias | Word Relationships | Status |
|---------|------------------------|------------------------|-------------------|--------|
| **pantheon-replit** | ✅ IMPLEMENTED | ✅ IMPLEMENTED | ✅ IMPLEMENTED | **COMPLETE** |
| **pantheon-chat** | ❌ MISSING | ❌ MISSING | ❌ MISSING | **NEEDS WORK** |
| **SearchSpaceCollapse** | ❌ MISSING | ❌ MISSING | ❌ MISSING | **NEEDS WORK** |

**Critical Finding**: All features documented in sleep packets are **fully implemented in pantheon-replit** but missing from the other two projects.

---

## Feature Analysis

### Feature 1: Auto-Integration of Learned Vocabulary

**Document**: `SLEEP_PACKET_vocabulary_auto_integration.md`

**What It Does**:

- Queries `learned_words` table every 5 minutes
- Finds high-Φ words (avg_phi >= 0.65) that aren't integrated
- Adds them to active coordizer vocabulary
- Marks as `is_integrated = TRUE`

**Implementation Status**:

- **pantheon-replit**: ✅ Full implementation in `qig_generation.py:555-600`
  - `_should_integrate_vocabulary()` checks timing
  - `_integrate_pending_vocabulary()` does the work
  - Called from `generate()` before encoding
- **pantheon-chat**: ❌ Not implemented
  - Has `learned_words` table (NO `is_integrated` column)
  - No integration logic in `qig_generation.py`
- **SearchSpaceCollapse**: ❌ Not implemented

### Feature 2: Domain Vocabulary Bias (Per-Kernel Specialization)

**Document**: `SLEEP_PACKET_domain_vocabulary_bias.md`

**What It Does**:

- Each kernel (Athena, Ares, Apollo, etc.) has domain-specific vocabulary
- Stored in `god_vocabulary_profiles` table
- Uses Fisher-Rao weighted mean to bias toward domain vocabulary
- 30% bias strength (geodesic interpolation)

**Implementation Status**:

- **pantheon-replit**: ✅ Full implementation in `qig_generation.py:671-750`
  - `_get_kernel_domain_vocabulary()` queries table with caching (10min TTL)
  - `_apply_domain_vocabulary_bias()` uses Fisher-Rao geometry
  - Applied in `_query_kernels()` during generation
- **pantheon-chat**: ❌ Not implemented
  - NO `god_vocabulary_profiles` table in schema
  - No domain bias logic
- **SearchSpaceCollapse**: ❌ Not implemented

### Feature 3: Word Relationships for Coherence

**Document**: `SLEEP_PACKET_word_relationships_coherence.md`

**What It Does**:

- Tracks word co-occurrence in `word_relationships` table
- During decode, boosts candidates based on recent context (5-word window)
- Scoring: 60% geometric + 40% relationship
- Prevents random token jumps, improves multi-word coherence

**Implementation Status**:

- **pantheon-replit**: ✅ Full implementation in `qig_generation.py:814-920`
  - `_boost_via_word_relationships()` queries relationships
  - Applied in `_decode_basins()` with 5-word context window
  - Uses existing table structure (word, neighbor, cooccurrence_count)
- **pantheon-chat**: ❌ Not implemented
  - NO `word_relationships` table in schema
  - No relationship boosting logic
- **SearchSpaceCollapse**: ❌ Not implemented

---

## Database Schema Comparison

### pantheon-replit (COMPLETE)

```typescript
// learned_words - HAS is_integrated column
export const learnedWords = pgTable("learned_words", {
  id: serial("id").primaryKey(),
  word: text("word").notNull(),
  frequency: integer("frequency").default(1),
  avgPhi: real("avg_phi").default(0.5),
  maxPhi: real("max_phi").default(0.5),
  source: text("source"),
  isIntegrated: boolean("is_integrated"),  // ✅ CRITICAL COLUMN
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// word_relationships - EXISTS
export const wordRelationships = pgTable("word_relationships", {
  id: serial("id").primaryKey(),
  word: text("word").notNull(),
  neighbor: text("neighbor").notNull(),
  cooccurrenceCount: real("cooccurrence_count").default(1),
  strength: real("strength").default(0),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// god_vocabulary_profiles - NEEDS TO BE ADDED
// (Code exists but table schema missing from schema.ts)
```

### pantheon-chat (INCOMPLETE)

```typescript
// learned_words - MISSING is_integrated column
export const learnedWords = pgTable("learned_words", {
  id: serial("id").primaryKey(),
  word: text("word").notNull(),
  frequency: integer("frequency").default(1),
  avgPhi: real("avg_phi").default(0.5),
  maxPhi: real("max_phi").default(0.5),
  source: text("source"),
  // ❌ NO isIntegrated column
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// ❌ NO wordRelationships table
// ❌ NO god_vocabulary_profiles table
```

---

## Implementation Requirements

### For pantheon-chat

**Schema Changes Required** (`shared/schema.ts`):

1. Add `isIntegrated` + `integratedAt` to `learnedWords`
2. Add `wordRelationships` table (complete structure from pantheon-replit)
3. Add `godVocabularyProfiles` table (new, from sleep packet spec)

**Code Changes Required** (`qig-backend/qig_generation.py`):

1. Copy vocabulary integration methods from pantheon-replit:
   - `_should_integrate_vocabulary()`
   - `_integrate_pending_vocabulary()`
   - `_get_kernel_domain_vocabulary()`
   - `_apply_domain_vocabulary_bias()`
   - `_fisher_rao_weighted_mean()`
   - `_boost_via_word_relationships()`

2. Update `__init__()` to add:
   - Vocabulary integration tracking variables
   - Domain vocabulary cache
   - Database URL handling

3. Update `generate()` to call `_integrate_pending_vocabulary()`

4. Update `_query_kernels()` to apply domain bias

5. Update `_decode_basins()` to use relationship boosting

**Migration Required**:

```sql
-- Add columns to learned_words
ALTER TABLE learned_words ADD COLUMN is_integrated BOOLEAN DEFAULT FALSE;
ALTER TABLE learned_words ADD COLUMN integrated_at TIMESTAMP;
ALTER TABLE learned_words ADD COLUMN basin_coords vector(64);

-- Create word_relationships table
CREATE TABLE word_relationships (
  id SERIAL PRIMARY KEY,
  word_a TEXT NOT NULL,
  word_b TEXT NOT NULL,
  co_occurrence INT DEFAULT 1,
  fisher_distance REAL,
  avg_phi REAL DEFAULT 0.5,
  max_phi REAL DEFAULT 0.5,
  contexts TEXT[],
  first_seen TIMESTAMP DEFAULT NOW(),
  last_seen TIMESTAMP DEFAULT NOW(),
  UNIQUE(word_a, word_b)
);

CREATE INDEX idx_word_rel_word_a_phi ON word_relationships(word_a, avg_phi DESC, co_occurrence DESC);

-- Create god_vocabulary_profiles table
CREATE TABLE god_vocabulary_profiles (
  id SERIAL PRIMARY KEY,
  god_name TEXT NOT NULL,
  word TEXT NOT NULL,
  relevance_score REAL NOT NULL,
  usage_count INT DEFAULT 0,
  last_used TIMESTAMP DEFAULT NOW(),
  learned_from_phi REAL,
  basin_distance REAL,
  UNIQUE(god_name, word)
);

CREATE INDEX idx_god_vocab_god_relevance ON god_vocabulary_profiles(god_name, relevance_score DESC, usage_count DESC);
```

### For SearchSpaceCollapse

**Same requirements as pantheon-chat** - needs all three features.

---

## Key Architectural Insights

### From DREAM_PACKET_disconnected_infrastructure_pattern.md

**Pattern Identified**: "Disconnected Infrastructure Pattern" (DIP)

**Symptoms**:

- Infrastructure exists ✅
- Infrastructure works ✅
- Use case identified ✅
- **Connection never made** ❌

**Example**: In original discovery (pantheon-chat ancestor), `VocabularyCoordinator.integrate_pending_vocabulary()` existed but was **never called** during generation.

**Lesson**: When adding new features, explicitly wire them into execution flow—don't assume automatic integration.

---

## QIG Purity Validation

All implementations maintain QIG purity:

✅ **Fisher-Rao Distance**: All geometric operations use `fisher_rao_distance()`
✅ **No External LLMs**: Pure QIG generation
✅ **Φ-Based Criteria**: Integration threshold is avg_phi >= 0.65
✅ **Natural Emergence**: Domain vocabularies learned from usage
✅ **Geodesic Interpolation**: No Euclidean averaging

---

## Next Actions

### Priority 1: pantheon-chat (Production)

1. ✅ Create migration SQL for schema changes
2. ✅ Add table definitions to `shared/schema.ts`
3. ✅ Copy vocabulary integration code from pantheon-replit
4. ✅ Test on staging/local before production
5. ✅ Run migration on Railway production DB

### Priority 2: SearchSpaceCollapse (Bitcoin Recovery)

1. Same steps as pantheon-chat
2. Coordinate with separate Neon database (us-west-2)

### Priority 3: Documentation

1. Mark sleep packets as DEPLOYED in pantheon-replit
2. Create implementation guide for pantheon-chat
3. Update project status docs

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Schema changes break existing code | Test migration on dev DB first |
| Performance impact from extra queries | Caching (10min TTL for domain vocab) |
| Database growth (word_relationships) | Monitor size, add cleanup cron if needed |
| Fisher-Rao computation overhead | Already optimized in pantheon-replit |

---

## References

**Sleep Packets**:

- `SLEEP_PACKET_vocabulary_auto_integration.md`
- `SLEEP_PACKET_domain_vocabulary_bias.md`
- `SLEEP_PACKET_word_relationships_coherence.md`
- `SLEEP_PACKET_sql_vocabulary_schema.md`
- `DEEP_SLEEP_PACKET_vocabulary_integration_v1.md`
- `DREAM_PACKET_disconnected_infrastructure_pattern.md`

**Code Locations**:

- pantheon-replit: `qig-backend/qig_generation.py` (lines 550-920)
- pantheon-chat: `qig-backend/qig_generation.py` (needs implementation)
- SearchSpaceCollapse: (needs implementation)

---

**Status**: Ready for implementation in pantheon-chat and SearchSpaceCollapse
**Implementation Time Estimate**: 4-6 hours per project (schema + code + testing)
