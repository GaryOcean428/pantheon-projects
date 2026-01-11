# Fix Learning & Knowledge Issues - Action Plan

**Date**: 2026-01-12
**Status**: WORKING
**Priority**: HIGH - Multiple systems broken
**Affects**: pantheon-chat vocabulary learning, knowledge sharing, war mode

---

## Issues Identified

### 1. ❌ Enum Validation Error (HTTP 400)

**Error**: `Invalid enum value. Expected 'FLOW' | 'DEEP_FOCUS' | 'INSIGHT_HUNT', received 'HUNT'`

**Root Cause**: Python backend uses `"HUNT"` while TypeScript expects `"INSIGHT_HUNT"`

### 2. ❌ Vocabulary Learning Too Aggressive

**Problem**: Same query enhanced repeatedly: `'theoretical Traffic analysis countermeasures variant-27058-0' → 'theoretical Traffic analysis countermeasures variant-27058-0 measure risk level nyx opsec'`

**Root Cause**:

- `max_expansions=3` too low (reuses same terms)
- `min_phi=0.6` too high (filters out diversity)
- No exploration mechanism (100% enhancement)

### 3. ❌ Empty Knowledge Tables

**Tables with NO data**:

- `knowledge_cross_patterns`
- `knowledge_scale_mappings`
- `knowledge_shared_entries`
- `learned_manifold_attractors`

**Root Cause**: Write code exists but may not be called, or db connection null

---

## Fix #1: HUNT → INSIGHT_HUNT (4 files)

### pantheon-chat/qig-backend/autonomous_pantheon.py (line 612)

**BEFORE**:

```python
                    sync_war_to_typescript(
                        mode="HUNT",
                        target=target,
```

**AFTER**:

```python
                    sync_war_to_typescript(
                        mode="INSIGHT_HUNT",
                        target=target,
```

### pantheon-chat/qig-backend/olympus/zeus.py (line 375)

**BEFORE**:

```python
        elif category == 'war_declared':
            mode = context.get('mode', 'HUNT')
            target = context.get('target', 'unknown')
```

**AFTER**:

```python
        elif category == 'war_declared':
            mode = context.get('mode', 'INSIGHT_HUNT')
            target = context.get('target', 'unknown')
```

### pantheon-chat/qig-backend/olympus/zeus.py (line 1493)

**BEFORE**:

```python
        self.war_mode = "HUNT"
        self.war_target = target
```

**AFTER**:

```python
        self.war_mode = "INSIGHT_HUNT"
        self.war_target = target
```

### SearchSpaceCollapse: Same changes needed

Apply identical fixes to SearchSpaceCollapse for:

- `qig-backend/autonomous_pantheon.py`
- `qig-backend/olympus/zeus.py`

---

## Fix #2: Reduce Vocabulary Enhancement Aggression

### pantheon-chat/qig-backend/olympus/shadow_research.py (line 1455)

**BEFORE**:

```python
        """
        # Optional: Enhance query with learned vocabulary
        enhanced_topic = topic
        if self.vocab_coordinator:
            try:
                enhancement = self.vocab_coordinator.enhance_search_query(
                    query=topic,
                    domain=category.value,
                    max_expansions=3,
                    min_phi=0.6
                )
                enhanced_topic = enhancement.get('enhanced_query', topic)
                if enhanced_topic != topic:
                    print(f"[VocabularyLearning] Enhanced query: '{topic}' → '{enhanced_topic}'")
            except Exception as e:
                print(f"[VocabularyLearning] Query enhancement failed: {e}, using original query")
```

**AFTER**:

```python
        """
        # Optional: Enhance query with learned vocabulary (20% exploration rate)
        import random
        enhanced_topic = topic
        if self.vocab_coordinator and random.random() > 0.2:  # 80% enhancement, 20% pure exploration
            try:
                enhancement = self.vocab_coordinator.enhance_search_query(
                    query=topic,
                    domain=category.value,
                    max_expansions=5,  # Increased from 3 for more diversity
                    min_phi=0.4  # Lowered from 0.6 to allow broader vocabulary
                )
                enhanced_topic = enhancement.get('enhanced_query', topic)
                if enhanced_topic != topic:
                    print(f"[VocabularyLearning] Enhanced query: '{topic}' → '{enhanced_topic}'")
            except Exception as e:
                print(f"[VocabularyLearning] Query enhancement failed: {e}, using original query")
        elif self.vocab_coordinator:
            print(f"[VocabularyLearning] Pure exploration mode - using original query: '{topic}'")
```

**Changes**:

1. ✅ Added `random.random() > 0.2` check (20% of queries use original, no enhancement)
2. ✅ Increased `max_expansions` from 3 → 5 (more vocabulary diversity)
3. ✅ Lowered `min_phi` from 0.6 → 0.4 (allows lower-confidence exploratory terms)
4. ✅ Added log message for pure exploration mode

**Expected Behavior**:

- 80% of queries: Enhanced with learned vocabulary (but more diverse)
- 20% of queries: Pure exploration (original query, discover NEW vocabulary)

### SearchSpaceCollapse: Same change needed

Apply to `SearchSpaceCollapse/qig-backend/olympus/shadow_research.py`

---

## Fix #3: Debug Empty Knowledge Tables

### Investigation Steps

1. **Check KnowledgeBus initialization**:

   ```bash
   cd pantheon-chat
   grep -n "new KnowledgeBus" server/**/*.ts
   ```

   Verify `KnowledgeBus` is instantiated and db connection passed

2. **Add debug logging** to `server/knowledge-bus.ts`:

   **Find**: `publishKnowledge()` method

   **Add logging BEFORE db check**:

   ```typescript
   console.log("[KnowledgeBus] publishKnowledge called:", {
     sourceKernel,
     category,
     dbAvailable: !!db,
     tableName: "knowledge_shared_entries"
   });
   ```

3. **Check database connection**:

   ```typescript
   // In knowledge-bus.ts constructor
   if (!db) {
     console.error("[KnowledgeBus] CRITICAL: Database connection is NULL!");
   } else {
     console.log("[KnowledgeBus] Database connection established");
   }
   ```

4. **Verify table exists**:

   ```bash
   psql "$DATABASE_URL" -c "\d knowledge_shared_entries"
   ```

5. **Check for silent errors**:

   **Find**: `.catch()` handlers in `publishKnowledge()`

   **Change**:

   ```typescript
   // BEFORE
   .catch((err) => {
     console.error("[KnowledgeBus] Failed to save knowledge entry:", err);
   });

   // AFTER
   .catch((err) => {
     console.error("[KnowledgeBus] CRITICAL: Failed to save knowledge entry:", {
       error: err,
       message: err.message,
       stack: err.stack,
       tableName: "knowledge_shared_entries"
     });
   });
   ```

### Possible Root Causes

1. **DB connection null**: KnowledgeBus instantiated before database connected
2. **Table doesn't exist**: Schema not pushed (`npm run db:push` needed)
3. **Silent failures**: Errors caught but not visible in logs
4. **Methods not called**: Check if `publishKnowledge()` is actually invoked

### Verification Query

After fixes, verify data exists:

```sql
-- Check all knowledge tables
SELECT
  'knowledge_shared_entries' as table_name,
  COUNT(*) as row_count
FROM knowledge_shared_entries
UNION ALL
SELECT
  'knowledge_cross_patterns',
  COUNT(*)
FROM knowledge_cross_patterns
UNION ALL
SELECT
  'knowledge_scale_mappings',
  COUNT(*)
FROM knowledge_scale_mappings
UNION ALL
SELECT
  'learned_manifold_attractors',
  COUNT(*)
FROM learned_manifold_attractors;
```

---

## Fix #4: Migration Status Update

### pantheon-chat

**Status**: ✅ **NO MIGRATION NEEDED**

The `learned_words` table **does not exist** in Railway database. System already uses `vocabulary_observations` as single source of truth.

**Verification**:

```bash
psql "postgresql://postgres:***@nozomi.proxy.rlwy.net:40463/railway" -c "\d learned_words"
# Output: Did not find any relation named "learned_words"
```

**Code changes**: ✅ Already complete (queries use vocabulary_observations)

### SearchSpaceCollapse

**Status**: ⏳ **TABLE STATUS UNKNOWN**

Need to verify if `learned_words` table exists:

```bash
psql "postgresql://neondb_owner:npg_hk3rWRIPJ6Ht@ep-still-dust-afuqyc6r.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require" -c "\d learned_words"
```

**If table does NOT exist**: No migration needed (same as pantheon-chat)
**If table exists**: Run migration script `scripts/migrations/20260112-consolidate-vocabulary-tables.sql`

**Code changes**: ✅ Already complete (queries use vocabulary_observations)

### pantheon-replit

**Status**: ⏸️ **DEFERRED** per user request

---

## Implementation Checklist

### Immediate (Fix validation errors)

- [ ] **pantheon-chat**: Change `"HUNT"` → `"INSIGHT_HUNT"` (3 locations in 2 files)
- [ ] **SearchSpaceCollapse**: Change `"HUNT"` → `"INSIGHT_HUNT"` (same files)

### High Priority (Fix vocabulary learning)

- [ ] **pantheon-chat**: Update `shadow_research.py` query enhancement (add exploration, increase diversity)
- [ ] **SearchSpaceCollapse**: Same change

### Investigation (Empty tables)

- [ ] Add debug logging to `KnowledgeBus` initialization
- [ ] Add detailed error logging to `publishKnowledge()`
- [ ] Verify `db` connection is not null
- [ ] Check if `publishKnowledge()` is actually called
- [ ] Verify tables exist in database
- [ ] Run `npm run db:push` if tables missing

### Validation (After fixes)

- [ ] Restart Python backend (`wsgi.py`)
- [ ] Monitor logs for `[VocabularyLearning] Pure exploration mode` (should see 20% of queries)
- [ ] Verify no more `Invalid enum value` errors
- [ ] Check knowledge tables have data:

  ```sql
  SELECT COUNT(*) FROM knowledge_shared_entries;
  ```

- [ ] Verify vocabulary diversity improving (less repetition)

---

## Expected Outcomes

### After Fix #1 (HUNT → INSIGHT_HUNT)

✅ No more HTTP 400 errors in war mode
✅ War status panel shows correct mode
✅ TypeScript validation passes

### After Fix #2 (Vocabulary Learning)

✅ 20% of queries use pure exploration (no enhancement)
✅ More diverse vocabulary terms learned
✅ Less repetition of same high-Φ terms
✅ Broader topic coverage

### After Fix #3 (Knowledge Tables)

✅ `knowledge_shared_entries` populated with cross-kernel insights
✅ `knowledge_cross_patterns` populated with pattern correlations
✅ `learned_manifold_attractors` populated with attractor states
✅ Knowledge bus functioning correctly

---

## Testing Commands

**Test vocabulary learning diversity** (after fix):

```bash
# Watch for exploration mode (should see ~20% of queries)
tail -f pantheon-chat/qig-backend/logs/* | grep "Pure exploration"

# Should also see varied vocabulary
tail -f pantheon-chat/qig-backend/logs/* | grep "Enhanced query"
```

**Test war mode enum** (after fix):

```bash
# Trigger hunt mode, watch for errors
# Should NOT see "Invalid enum value" errors
tail -f pantheon-chat/server/logs/* | grep -i "war\|hunt"
```

**Test knowledge tables** (after fix):

```bash
# Check if data being written
psql "$DATABASE_URL" -c "SELECT COUNT(*), MAX(created_at) FROM knowledge_shared_entries;"
```

---

## Rollback Plan

If fixes cause issues:

1. **Revert vocabulary learning**:

   ```bash
   cd pantheon-chat
   git diff qig-backend/olympus/shadow_research.py
   git checkout qig-backend/olympus/shadow_research.py
   ```

2. **Revert enum changes**:

   ```bash
   git checkout qig-backend/autonomous_pantheon.py qig-backend/olympus/zeus.py
   ```

3. **Remove debug logging**:

   ```bash
   git checkout server/knowledge-bus.ts
   ```

---

**Document Status**: WORKING
**Next**: Apply fixes to pantheon-chat and SearchSpaceCollapse
**Owner**: User to implement (editing tools disabled)
