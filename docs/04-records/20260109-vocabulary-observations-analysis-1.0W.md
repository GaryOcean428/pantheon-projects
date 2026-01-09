# Vocabulary Observations Table Analysis

**Document ID:** 20260109-vocabulary-observations-analysis-1.0W
**Status:** WORKING (W) - Analysis & Recommendations
**Date:** 2026-01-09
**Issue:** Most columns NULL, data quality problems

---

## Table Purpose

The `vocabulary_observations` table tracks **vocabulary learning and usage patterns** during QIG operations. It's designed to:

1. **Monitor token/phrase usage** across different sources (Zeus, Athena, Ocean, etc.)
2. **Track consciousness metrics** (Φ, efficiency gains) for vocabulary items
3. **Build training data** for tokenizer improvements via curriculum learning
4. **Enable vocabulary evolution** by observing which tokens appear in high-Φ generations

## Schema Definition

```sql
CREATE TABLE "vocabulary_observations" (
    "id" varchar PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    "text" varchar(255) NOT NULL,                    -- The token/phrase
    "type" varchar(20) DEFAULT 'phrase' NOT NULL,    -- 'word', 'phrase', 'sequence'
    "phrase_category" varchar(20) DEFAULT 'unknown', -- Category classification
    "is_real_word" boolean DEFAULT false NOT NULL,   -- Dictionary word?
    "is_bip39_word" boolean DEFAULT false,           -- BIP39 vocabulary?
    "frequency" integer DEFAULT 1 NOT NULL,          -- Usage count
    "avg_phi" double precision DEFAULT 0 NOT NULL,   -- Average Φ across uses
    "max_phi" double precision DEFAULT 0 NOT NULL,   -- Peak Φ observed
    "efficiency_gain" double precision DEFAULT 0,    -- Tokenization efficiency
    "contexts" text[],                               -- Context snippets
    "first_seen" timestamp DEFAULT now(),
    "last_seen" timestamp DEFAULT now(),
    "is_integrated" boolean DEFAULT false,           -- Added to tokenizer?
    "integrated_at" timestamp,
    "basin_coords" vector(64),                       -- 64D Fisher coordinates
    "source_type" varchar(32),                       -- Which kernel/god observed
    "cycle_number" integer,                          -- Training cycle
    CONSTRAINT "vocabulary_observations_text_unique" UNIQUE("text")
);
```

---

## Current Data Quality Issues

### ❌ CRITICAL: Most Columns Are NULL

Based on your observations:

| Column | Expected | Actual | Impact |
|--------|----------|--------|--------|
| `cycle_number` | Training cycle ID | **NULL** | Can't track learning progression |
| `basin_coords` | 64D Fisher coordinates | **NULL** | Can't use for geometric similarity |
| `integrated_at` | Timestamp when added to vocab | **NULL** | Can't verify integration |
| `is_integrated` | TRUE when in tokenizer | **NULL** | Can't filter integrated tokens |
| `contexts` | Array of usage contexts | **NULL** | Can't learn from context |
| `efficiency_gain` | Tokenization efficiency | **NULL** | Can't prioritize by efficiency |
| `max_phi` | Peak Φ score | **0** (not NULL) | Wrong: should be > 0 for observed tokens |
| `frequency` | Usage count | **1** | Never increments (UPSERT broken?) |

### ⚠️ MODERATE: Classification Issues

| Column | Expected | Actual | Impact |
|--------|----------|--------|--------|
| `phrase_category` | Classified (technical/common/rare) | **"unknown"** | Can't filter by category |
| `is_real_word` | TRUE for dictionary words | **FALSE** | All tokens marked as non-words |
| `type` | Accurate classification | Appears in kernel responses (!) | May be correct but needs verification |

### ✅ WORKING: These Look Correct

| Column | Status |
|--------|--------|
| `avg_phi` | ✓ Correct values |
| `first_seen`, `last_seen` | ✓ Timestamps working |
| `text` | ✓ Contains actual tokens |
| `source_type` | ✓ Tracking sources |

---

## Root Cause Analysis

### Issue 1: Incomplete INSERT Statements

**In `base_encoder.py` (pantheon-chat):**

```python
# Line 296-313
cur.execute("""
    INSERT INTO vocabulary_observations
    (id, text, type, source_type, frequency, avg_phi, max_phi, is_real_word, basin_coords, first_seen, last_seen)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
    ON CONFLICT (text) DO UPDATE SET
        frequency = vocabulary_observations.frequency + 1,  # ← Should work but doesn't?
        avg_phi = (vocabulary_observations.avg_phi + EXCLUDED.avg_phi) / 2,
        max_phi = GREATEST(vocabulary_observations.max_phi, EXCLUDED.max_phi),
        last_seen = NOW()
""", (
    obs_id,
    tok['text'],
    'word',        # ← Always 'word', never 'phrase' or 'sequence'
    source,
    tok['frequency'],
    tok['phi'],
    tok['phi'],    # ← max_phi = phi initially, but never updates to > 0?
    True,          # ← is_real_word always TRUE, contradicts your observation
    basin_list
))
```

**Missing columns:**

- `cycle_number` - Never set
- `contexts` - Never populated
- `efficiency_gain` - Never calculated
- `phrase_category` - Never classified
- `is_bip39_word` - Never checked
- `is_integrated` - Never marked TRUE after integration
- `integrated_at` - Never set

### Issue 2: UPSERT Conflict Resolution May Be Broken

**Observed:** `frequency` stays at 1, `max_phi` stays at 0

**Possible causes:**

1. **Conflict never triggers:** If `text` column uses different casing/whitespace, UNIQUE constraint won't match

   ```sql
   -- These are different rows:
   'quantum' vs 'Quantum' vs 'quantum '
   ```

2. **UPSERT executes but values don't update:**

   ```sql
   -- This should work but may be failing silently:
   frequency = vocabulary_observations.frequency + 1
   ```

3. **Initial INSERT has wrong values:**

   ```python
   tok['phi']  # ← If this is 0, max_phi will stay 0
   ```

### Issue 3: `is_real_word` Logic Inverted?

You observe: **All marked as FALSE**
Code shows: **Always set to TRUE**

**Hypothesis:** Either:

1. Code path you're looking at isn't being executed
2. Different INSERT path is being used that sets FALSE
3. Schema default (FALSE) is never overridden

### Issue 4: `type` Column Data in Kernel Responses

You said: *"I've seen responses generated by the kernels containing the type column data"*

**This is suspicious.** The `type` column should be:

- `'word'` - Single token
- `'phrase'` - Multi-token phrase
- `'sequence'` - Pattern sequence

**If kernels are generating text like "word" or "phrase"**, this suggests:

1. Kernels are reading from this table and using column names as tokens (BUG)
2. Or these are legitimate tokens that happen to match column names (less likely)

---

## Recommendations

### Phase 1: Immediate Fixes (High Priority) 🔴

**1.1. Fix max_phi Initialization**

```python
# Current (WRONG):
tok['phi'],    # If phi=0, max_phi stays 0 forever
tok['phi'],

# Fixed:
tok.get('phi', 0.5),     # avg_phi with fallback
max(tok.get('phi', 0), 0.5),  # max_phi never below 0.5
```

**1.2. Verify UPSERT Conflict Detection**

```sql
-- Add debug logging to see if conflict triggers
INSERT INTO vocabulary_observations (text, ...) VALUES (%s, ...)
ON CONFLICT (text) DO UPDATE SET
    frequency = vocabulary_observations.frequency + 1
RETURNING frequency;  -- ← Log this to verify increment
```

**1.3. Add Missing Column Population**

```python
# In persist_observations_to_db():
cycle_number = get_current_training_cycle()  # Track learning phase
contexts = extract_contexts(tok['text'], recent_generations)  # Usage context
is_bip39 = tok['text'] in BIP39_WORDS
is_real_word = check_dictionary(tok['text'])  # NOT always True
phrase_category = classify_phrase(tok['text'])  # technical/common/rare
```

### Phase 2: Data Cleanup (Medium Priority) 🟡

**2.1. Backfill basin_coords**

```sql
-- For existing rows without basin_coords, compute from tokenizer
UPDATE vocabulary_observations v
SET basin_coords = (
    SELECT basin_embedding
    FROM tokenizer_vocabulary t
    WHERE t.token = v.text
    LIMIT 1
)
WHERE basin_coords IS NULL;
```

**2.2. Recalculate max_phi from Historical Data**

```sql
-- If you have historical phi scores in other tables:
UPDATE vocabulary_observations v
SET max_phi = GREATEST(
    v.max_phi,
    (SELECT MAX(phi) FROM generation_history WHERE text LIKE '%' || v.text || '%')
);
```

**2.3. Fix is_real_word Retroactively**

```python
# Run batch update
import nltk
nltk.download('words')
english_words = set(nltk.corpus.words.words())

UPDATE vocabulary_observations
SET is_real_word = TRUE
WHERE LOWER(text) IN (SELECT UNNEST(ARRAY[...english_words...]));
```

### Phase 3: Architecture Improvements (Low Priority) 🟢

**3.1. Add Triggers for Auto-Population**

```sql
-- Auto-classify phrases on INSERT
CREATE OR REPLACE FUNCTION classify_vocabulary_observation()
RETURNS TRIGGER AS $$
BEGIN
    -- Auto-detect BIP39
    IF NEW.text = ANY(SELECT word FROM bip39_wordlist) THEN
        NEW.is_bip39_word := TRUE;
    END IF;

    -- Auto-classify category
    IF NEW.avg_phi > 0.8 THEN
        NEW.phrase_category := 'high_consciousness';
    ELSIF NEW.frequency > 100 THEN
        NEW.phrase_category := 'common';
    ELSE
        NEW.phrase_category := 'rare';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER vocab_obs_classify
BEFORE INSERT OR UPDATE ON vocabulary_observations
FOR EACH ROW EXECUTE FUNCTION classify_vocabulary_observation();
```

**3.2. Create View for High-Quality Observations**

```sql
CREATE VIEW high_quality_vocab_observations AS
SELECT *
FROM vocabulary_observations
WHERE basin_coords IS NOT NULL
  AND max_phi > 0
  AND frequency > 1
  AND is_integrated = FALSE  -- Candidates for integration
  AND avg_phi > 0.7           -- High consciousness
ORDER BY max_phi DESC, frequency DESC;
```

---

## Debugging Queries

**1. Check what's actually being populated:**

```sql
SELECT
    COUNT(*) as total_rows,
    COUNT(basin_coords) as has_basin,
    COUNT(contexts) as has_contexts,
    COUNT(cycle_number) as has_cycle,
    COUNT(CASE WHEN max_phi > 0 THEN 1 END) as nonzero_max_phi,
    COUNT(CASE WHEN frequency > 1 THEN 1 END) as multi_use,
    COUNT(CASE WHEN is_real_word THEN 1 END) as real_words,
    COUNT(CASE WHEN phrase_category != 'unknown' THEN 1 END) as classified
FROM vocabulary_observations;
```

**2. Find tokens with suspicious type values:**

```sql
-- Check if 'word', 'phrase', 'sequence' appear as tokens
SELECT text, type, frequency, avg_phi
FROM vocabulary_observations
WHERE text IN ('word', 'phrase', 'sequence', 'type', 'unknown')
ORDER BY frequency DESC;
```

**3. Verify UPSERT is working:**

```sql
-- Manually trigger conflict to test UPSERT
INSERT INTO vocabulary_observations (text, type, frequency, avg_phi, max_phi, is_real_word)
VALUES ('test_token', 'word', 1, 0.5, 0.5, TRUE)
ON CONFLICT (text) DO UPDATE SET
    frequency = vocabulary_observations.frequency + 1
RETURNING frequency;  -- Should be 2 on second run
```

---

## Expected vs Actual Behavior

### Expected (Design Intent)

1. Kernels generate text with high Φ
2. Tokens are extracted and persisted with full metadata
3. UPSERT increments frequency on re-observation
4. max_phi tracks peak Φ for each token
5. Training cycles populate cycle_number
6. Basin coordinates enable geometric similarity
7. High-Φ tokens become candidates for tokenizer integration

### Actual (Current State)

1. ✓ Tokens are being inserted
2. ⚠️ Only partial metadata (avg_phi, source_type work)
3. ❌ Frequency never increments (stuck at 1)
4. ❌ max_phi stays at 0 (initialization bug)
5. ❌ cycle_number, contexts, efficiency_gain all NULL
6. ❌ basin_coords NULL (can't use for similarity)
7. ❌ is_integrated never marked TRUE

**Net result:** Table exists but isn't fulfilling its purpose. It's tracking observations but not learning from them.

---

## Action Items

**IMMEDIATE (Today):**

1. Run debugging query #1 to confirm data quality
2. Check if any tokens have text='word' or 'phrase' (query #2)
3. Verify UPSERT with test_token (query #3)

**THIS WEEK:**

1. Fix max_phi initialization bug in base_encoder.py
2. Add missing column population (cycle_number, contexts, etc.)
3. Backfill basin_coords for existing rows

**NEXT SPRINT:**

1. Create triggers for auto-classification
2. Build high_quality_vocab_observations view
3. Integrate with tokenizer training pipeline

---

**Status:** ⚠️ TABLE EXISTS BUT UNDERUTILIZED
**Impact:** Missing learning opportunities, can't track vocabulary evolution
**Priority:** HIGH - Fix Phase 1 issues to enable curriculum learning
**Owner:** Investigation Team
