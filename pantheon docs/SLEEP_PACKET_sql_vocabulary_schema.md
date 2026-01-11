# SLEEP PACKET: Vocabulary Integration SQL Schema
**Type**: Database Architecture  
**Domain**: PostgreSQL Schema for QIG Vocabulary  
**Status**: Specification Ready (for replit agent)  
**Date**: 2026-01-11

---

## Core Concept

Complete SQL schema specifications for vocabulary integration, supporting:
1. Auto-integration of learned words
2. Per-kernel domain vocabularies
3. Word relationship tracking

**File Reference**: `SQL_SPECS_FOR_REPLIT_AGENT.md` (comprehensive implementation guide)

---

## Table 1: `learned_words` (Enhanced)

**Purpose**: Store learned vocabulary with integration tracking

```sql
CREATE TABLE IF NOT EXISTS learned_words (
    id SERIAL PRIMARY KEY,
    word TEXT UNIQUE NOT NULL,
    frequency INT DEFAULT 1,
    avg_phi REAL DEFAULT 0.0,
    max_phi REAL DEFAULT 0.0,
    source TEXT NOT NULL,
    learned_from TEXT,
    contexts TEXT[],
    first_seen TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    
    -- CRITICAL ADDITIONS
    is_integrated BOOLEAN DEFAULT FALSE,
    integrated_at TIMESTAMP,
    basin_coords vector(64),
    last_used_in_generation TIMESTAMP
);
```

**Critical Indexes**:
```sql
-- High-phi pending integration (CRITICAL - used every 5 min)
CREATE INDEX idx_learned_words_pending_integration 
ON learned_words(avg_phi DESC, frequency DESC) 
WHERE is_integrated = FALSE;

-- Integration tracking
CREATE INDEX idx_learned_words_integrated_at 
ON learned_words(integrated_at DESC) 
WHERE integrated_at IS NOT NULL;
```

---

## Table 2: `god_vocabulary_profiles` (Enhanced)

**Purpose**: Per-kernel domain-specific vocabulary

```sql
CREATE TABLE IF NOT EXISTS god_vocabulary_profiles (
    id SERIAL PRIMARY KEY,
    god_name TEXT NOT NULL,
    word TEXT NOT NULL,
    relevance_score REAL NOT NULL,  -- 0.0 to 1.0 (Φ-based)
    usage_count INT DEFAULT 0,
    last_used TIMESTAMP DEFAULT NOW(),
    
    -- CRITICAL ADDITIONS
    learned_from_phi REAL,
    basin_distance REAL,
    
    UNIQUE(god_name, word)
);
```

**Critical Indexes**:
```sql
-- Per-god relevance queries (CRITICAL - used every generation)
CREATE INDEX idx_god_vocab_god_relevance 
ON god_vocabulary_profiles(god_name, relevance_score DESC, usage_count DESC);

-- High-relevance only
CREATE INDEX idx_god_vocab_high_relevance 
ON god_vocabulary_profiles(relevance_score DESC, usage_count DESC) 
WHERE relevance_score >= 0.5;
```

---

## Table 3: `word_relationships` (New)

**Purpose**: Track word co-occurrence for coherence

```sql
CREATE TABLE IF NOT EXISTS word_relationships (
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
```

**Critical Indexes**:
```sql
-- Forward lookup (CRITICAL - used during decode)
CREATE INDEX idx_word_rel_word_a_phi 
ON word_relationships(word_a, avg_phi DESC, co_occurrence DESC);

-- High-phi relationships
CREATE INDEX idx_word_rel_high_phi 
ON word_relationships(avg_phi DESC, co_occurrence DESC) 
WHERE avg_phi >= 0.6;
```

---

## Helper Function 1: Get Pending Vocabulary

```sql
CREATE OR REPLACE FUNCTION get_pending_vocabulary_for_integration(
    p_min_phi REAL DEFAULT 0.65,
    p_limit INT DEFAULT 100
) RETURNS TABLE (
    word TEXT,
    avg_phi REAL,
    max_phi REAL,
    frequency INT,
    source TEXT,
    basin_coords vector
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        lw.word, lw.avg_phi, lw.max_phi, lw.frequency,
        lw.source, lw.basin_coords
    FROM learned_words lw
    WHERE lw.is_integrated = FALSE
      AND lw.avg_phi >= p_min_phi
    ORDER BY lw.avg_phi DESC, lw.frequency DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
```

**Usage**:
```python
# Called during generation every 5 min
pending = db.query("SELECT * FROM get_pending_vocabulary_for_integration(0.65, 100)")
```

---

## Helper Function 2: Mark Integrated

```sql
CREATE OR REPLACE FUNCTION mark_vocabulary_integrated(
    p_words TEXT[]
) RETURNS INT AS $$
DECLARE
    rows_updated INT;
BEGIN
    UPDATE learned_words
    SET 
        is_integrated = TRUE,
        integrated_at = NOW()
    WHERE word = ANY(p_words);
    
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    RETURN rows_updated;
END;
$$ LANGUAGE plpgsql;
```

**Usage**:
```python
# After adding to coordizer
db.execute("SELECT mark_vocabulary_integrated(%s)", (integrated_words,))
```

---

## Helper Function 3: Get God Domain Vocabulary

```sql
CREATE OR REPLACE FUNCTION get_god_domain_vocabulary(
    p_god_name TEXT,
    p_min_relevance REAL DEFAULT 0.5,
    p_limit INT DEFAULT 50
) RETURNS TABLE (
    word TEXT,
    relevance_score REAL,
    usage_count INT,
    basin_distance REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        gvp.word, gvp.relevance_score, gvp.usage_count, gvp.basin_distance
    FROM god_vocabulary_profiles gvp
    WHERE gvp.god_name = p_god_name
      AND gvp.relevance_score >= p_min_relevance
    ORDER BY gvp.relevance_score DESC, gvp.usage_count DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
```

**Usage**:
```python
# Called during _query_kernels (with caching)
domain_vocab = db.query("SELECT * FROM get_god_domain_vocabulary('athena', 0.5, 50)")
```

---

## Helper Function 4: Get Word Relationships

```sql
CREATE OR REPLACE FUNCTION get_word_relationships(
    p_context_words TEXT[],
    p_min_phi REAL DEFAULT 0.5,
    p_limit INT DEFAULT 50
) RETURNS TABLE (
    word_b TEXT,
    co_occurrence INT,
    fisher_distance REAL,
    avg_phi REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        wr.word_b, wr.co_occurrence, wr.fisher_distance, wr.avg_phi
    FROM word_relationships wr
    WHERE wr.word_a = ANY(p_context_words)
      AND wr.avg_phi >= p_min_phi
    ORDER BY wr.avg_phi DESC, wr.co_occurrence DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
```

**Usage**:
```python
# Called during _decode_basins
relationships = db.query(
    "SELECT * FROM get_word_relationships(%s, 0.5, 50)",
    (recent_words,)
)
```

---

## Helper Function 5: Record Co-occurrence

```sql
CREATE OR REPLACE FUNCTION record_word_cooccurrence(
    p_word_a TEXT,
    p_word_b TEXT,
    p_phi REAL DEFAULT 0.5,
    p_fisher_distance REAL DEFAULT NULL,
    p_context TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO word_relationships (
        word_a, word_b, co_occurrence, avg_phi, max_phi,
        fisher_distance, contexts
    )
    VALUES (
        p_word_a, p_word_b, 1, p_phi, p_phi,
        p_fisher_distance,
        CASE WHEN p_context IS NOT NULL THEN ARRAY[p_context] ELSE NULL END
    )
    ON CONFLICT (word_a, word_b) DO UPDATE SET
        co_occurrence = word_relationships.co_occurrence + 1,
        avg_phi = (word_relationships.avg_phi * word_relationships.co_occurrence + p_phi) 
                  / (word_relationships.co_occurrence + 1),
        max_phi = GREATEST(word_relationships.max_phi, p_phi),
        last_seen = NOW(),
        contexts = CASE 
            WHEN p_context IS NOT NULL 
                 AND array_length(word_relationships.contexts, 1) < 10 
            THEN word_relationships.contexts || p_context
            ELSE word_relationships.contexts
        END;
END;
$$ LANGUAGE plpgsql;
```

**Usage**:
```python
# Called when observing word pairs in generation
db.execute(
    "SELECT record_word_cooccurrence(%s, %s, %s, %s, %s)",
    (word_a, word_b, phi, fisher_dist, context)
)
```

---

## Bootstrap Procedure

### Step 1: Validate Existing Data
```sql
SELECT COUNT(*) as total,
       COUNT(*) FILTER (WHERE is_integrated = TRUE) as integrated,
       COUNT(*) FILTER (WHERE avg_phi >= 0.65) as high_phi_pending
FROM learned_words;
```

### Step 2: Seed God Vocabularies
```sql
-- From learned_words
INSERT INTO god_vocabulary_profiles (god_name, word, relevance_score, learned_from_phi)
SELECT learned_from, word, LEAST(avg_phi, 1.0), avg_phi
FROM learned_words
WHERE learned_from IS NOT NULL
  AND avg_phi >= 0.5
  AND NOT EXISTS (
      SELECT 1 FROM god_vocabulary_profiles gvp 
      WHERE gvp.god_name = learned_words.learned_from 
        AND gvp.word = learned_words.word
  )
LIMIT 1000;

-- Core domain words
INSERT INTO god_vocabulary_profiles (god_name, word, relevance_score) VALUES
    ('athena', 'strategy', 0.95),
    ('athena', 'wisdom', 0.90),
    ('ares', 'attack', 0.95),
    ('ares', 'force', 0.90)
ON CONFLICT DO NOTHING;
```

### Step 3: Build Initial Relationships
```sql
-- Bootstrap from contexts (one-time, may take minutes)
SELECT bootstrap_word_relationships();
```

### Step 4: Optimize
```sql
ANALYZE learned_words;
ANALYZE god_vocabulary_profiles;
ANALYZE word_relationships;
```

---

## Monitoring Queries

**Integration Health**:
```sql
SELECT 
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE is_integrated = TRUE) as integrated,
    COUNT(*) FILTER (WHERE is_integrated = FALSE) as pending,
    AVG(avg_phi) as avg_phi
FROM learned_words;
```

**God Vocabulary Coverage**:
```sql
SELECT god_name, COUNT(*) as vocab_size, AVG(relevance_score) as avg_relevance
FROM god_vocabulary_profiles
GROUP BY god_name
ORDER BY vocab_size DESC;
```

**Relationship Growth**:
```sql
SELECT 
    COUNT(*) as total,
    AVG(co_occurrence) as avg_cooccurrence,
    AVG(avg_phi) as avg_phi
FROM word_relationships;
```

---

## Performance Tuning

**Index Usage Check**:
```sql
SELECT tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND tablename IN ('learned_words', 'god_vocabulary_profiles', 'word_relationships')
ORDER BY idx_scan DESC;
```

**Reindex if Slow**:
```sql
REINDEX TABLE learned_words;
REINDEX TABLE god_vocabulary_profiles;
REINDEX TABLE word_relationships;
```

---

## Implementation Checklist

For replit agent:
- [ ] Add missing columns to `learned_words`
- [ ] Add missing columns to `god_vocabulary_profiles`
- [ ] Create `word_relationships` table
- [ ] Create all 5 helper functions
- [ ] Create all indexes
- [ ] Run bootstrap procedure
- [ ] Test all helper functions
- [ ] Run ANALYZE on all tables
- [ ] Verify Python can query successfully

---

## Expected Metrics (24 Hours)

**learned_words**:
- Total: 15,000+
- Integrated: 8,000+ (50%+)
- Avg Φ: 0.55+

**god_vocabulary_profiles**:
- Athena: 150+ words
- Ares: 120+ words
- Apollo: 130+ words

**word_relationships**:
- Total: 1,000+
- High-Φ (>0.7): 400+
- Avg co-occurrence: 3-5

---

## Critical Success Factor

Schema enables:
1. ✅ High-performance queries (<5ms)
2. ✅ Φ-validated data quality
3. ✅ Incremental growth over time
4. ✅ QIG-pure geometric operations

**All operations use PostgreSQL native functions** - no external dependencies.

---

## Related Concepts

- Auto-Integration (SLEEP_PACKET_vocabulary_auto_integration.md)
- Domain Bias (SLEEP_PACKET_domain_vocabulary_bias.md)
- Word Relationships (SLEEP_PACKET_word_relationships_coherence.md)

---

## File Locations

- **Full Specs**: `SQL_SPECS_FOR_REPLIT_AGENT.md`
- **Python Integration**: `qig_generation.py` (database queries)
- **Production Database**: `DATABASE_URL` environment variable

---

## Wake Instruction

When resuming SQL work:
1. Check replit agent implementation status
2. Verify all tables/columns exist
3. Test all 5 helper functions
4. Run monitoring queries
5. Validate index performance
6. Confirm Python code can query successfully

The database schema is **COMPLETE** and **QIG-PURE**.
