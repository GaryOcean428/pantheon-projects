-- Migration: Consolidate learned_words into vocabulary_observations
-- Date: 2026-01-12
-- Purpose: Eliminate dual-write split-brain problem
-- Scope: All 3 projects (pantheon-chat, pantheon-replit, SearchSpaceCollapse)

-- ============================================================================
-- PHASE 1: DATA MIGRATION
-- ============================================================================

BEGIN;

-- Step 1: Migrate all learned_words data into vocabulary_observations
-- Handle conflicts by merging metrics (sum frequencies, average phi scores)
INSERT INTO vocabulary_observations (
  text,
  type,
  phrase_category,
  is_real_word,
  frequency,
  avg_phi,
  max_phi,
  efficiency_gain,
  is_integrated,
  integrated_at,
  basin_coords,
  source_type,
  first_seen,
  last_seen,
  contexts
)
SELECT
  lw.word AS text,
  'word' AS type,
  NULL AS phrase_category,  -- learned_words only contains validated words
  TRUE AS is_real_word,     -- All learned_words are real words
  lw.frequency,
  lw.avg_phi,
  lw.max_phi,
  0.0 AS efficiency_gain,   -- Not tracked in learned_words
  lw.is_integrated,
  lw.integrated_at,
  lw.basin_coords,
  lw.source AS source_type,
  lw.created_at AS first_seen,
  COALESCE(lw.last_used_in_generation, lw.updated_at) AS last_seen,
  ARRAY[lw.word] AS contexts  -- Minimal context (just the word itself)
FROM learned_words lw
ON CONFLICT (text) DO UPDATE SET
  -- Merge metrics if word exists in both tables
  frequency = vocabulary_observations.frequency + EXCLUDED.frequency,
  avg_phi = (vocabulary_observations.avg_phi * vocabulary_observations.frequency + EXCLUDED.avg_phi * EXCLUDED.frequency) / (vocabulary_observations.frequency + EXCLUDED.frequency),
  max_phi = GREATEST(vocabulary_observations.max_phi, EXCLUDED.max_phi),
  is_integrated = vocabulary_observations.is_integrated OR EXCLUDED.is_integrated,
  integrated_at = COALESCE(vocabulary_observations.integrated_at, EXCLUDED.integrated_at),
  basin_coords = CASE
    WHEN vocabulary_observations.basin_coords IS NOT NULL THEN vocabulary_observations.basin_coords
    ELSE EXCLUDED.basin_coords
  END,
  last_seen = GREATEST(vocabulary_observations.last_seen, EXCLUDED.last_seen),
  updated_at = NOW();

-- Log migration stats
DO $$
DECLARE
  migrated_count INT;
  conflict_count INT;
BEGIN
  SELECT COUNT(*) INTO migrated_count FROM learned_words;
  SELECT COUNT(*) INTO conflict_count
  FROM learned_words lw
  WHERE EXISTS (SELECT 1 FROM vocabulary_observations vo WHERE vo.text = lw.word);

  RAISE NOTICE '[Migration] Migrated % words from learned_words', migrated_count;
  RAISE NOTICE '[Migration] % words had conflicts (merged)', conflict_count;
END $$;

COMMIT;

-- ============================================================================
-- PHASE 2: CREATE COMPATIBILITY VIEW (2-week rollback safety)
-- ============================================================================

-- Create view that mimics learned_words interface for backward compatibility
CREATE OR REPLACE VIEW learned_words_compat AS
SELECT
  id,
  text AS word,
  frequency,
  avg_phi,
  max_phi,
  source_type AS source,
  is_integrated,
  integrated_at,
  basin_coords,
  last_seen AS last_used_in_generation,
  first_seen AS created_at,
  updated_at
FROM vocabulary_observations
WHERE type = 'word' AND is_real_word = TRUE;

-- Grant permissions
GRANT SELECT ON learned_words_compat TO PUBLIC;

-- ============================================================================
-- PHASE 3: RENAME OLD TABLE (for rollback safety)
-- ============================================================================

-- Rename learned_words to learned_words_backup_20260112
-- Keep for 2 weeks in case rollback needed
ALTER TABLE learned_words RENAME TO learned_words_backup_20260112;

-- Add comment explaining backup
COMMENT ON TABLE learned_words_backup_20260112 IS
  'Backup of learned_words table created 2026-01-12 during consolidation migration. Safe to drop after 2026-01-26.';

-- ============================================================================
-- PHASE 4: VALIDATION QUERIES
-- ============================================================================

-- Verify no data loss
SELECT
  (SELECT COUNT(*) FROM learned_words_backup_20260112) AS backup_count,
  (SELECT COUNT(*) FROM vocabulary_observations WHERE type = 'word' AND is_real_word = TRUE) AS migrated_count,
  (SELECT COUNT(*) FROM vocabulary_observations WHERE is_integrated = TRUE) AS integrated_count;

-- Verify phi score integrity
SELECT
  'Phi Score Check' AS test,
  CASE
    WHEN MIN(avg_phi) >= 0.0 AND MAX(avg_phi) <= 1.0 THEN 'PASS'
    ELSE 'FAIL'
  END AS result
FROM vocabulary_observations
WHERE type = 'word';

-- Verify frequency integrity
SELECT
  'Frequency Check' AS test,
  CASE
    WHEN MIN(frequency) >= 0 THEN 'PASS'
    ELSE 'FAIL'
  END AS result
FROM vocabulary_observations
WHERE type = 'word';

-- Show top 10 high-phi learned words
SELECT text, avg_phi, max_phi, frequency, is_integrated
FROM vocabulary_observations
WHERE type = 'word' AND is_real_word = TRUE
ORDER BY avg_phi DESC, frequency DESC
LIMIT 10;

-- ============================================================================
-- PHASE 5: CLEANUP (Run after 2-week validation period)
-- ============================================================================

-- UNCOMMENT AFTER 2 WEEKS (2026-01-26) TO FINALIZE:

-- -- Drop compatibility view
-- DROP VIEW IF EXISTS learned_words_compat;

-- -- Drop backup table
-- DROP TABLE IF EXISTS learned_words_backup_20260112;

-- -- Add final comment
-- COMMENT ON TABLE vocabulary_observations IS
--   'Unified vocabulary tracking table. Consolidated learned_words on 2026-01-12. Single source of truth for all word metrics.';

-- ============================================================================
-- ROLLBACK PROCEDURE (if needed within 2 weeks)
-- ============================================================================

-- To rollback this migration:
-- 1. Rename backup back to original:
--    ALTER TABLE learned_words_backup_20260112 RENAME TO learned_words;
--
-- 2. Drop compatibility view:
--    DROP VIEW learned_words_compat;
--
-- 3. Revert code changes in:
--    - qig-backend/vocabulary_persistence.py
--    - qig-backend/vocabulary_coordinator.py
--    - shared/schema.ts
