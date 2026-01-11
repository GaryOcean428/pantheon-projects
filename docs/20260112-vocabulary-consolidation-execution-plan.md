# Vocabulary Table Consolidation - Execution Plan

**Date**: 2026-01-12
**Issue**: `learned_words` and `vocabulary_observations` duplicate 70% of columns causing split-brain data inconsistency
**Solution**: Merge `learned_words` → `vocabulary_observations` (single source of truth)

---

## Pre-Flight Checklist

- [ ] All projects have backups (automated via migration script)
- [ ] Database backups created (pg_dump)
- [ ] No active deployments in progress
- [ ] All team members notified of schema change

---

## Execution Steps (4-6 hours)

### Step 1: Prepare (30 minutes)

```bash
cd /home/braden/Desktop/Dev/pantheon-projects

# Make migration script executable
chmod +x scripts/migrations/20260112-update-vocabulary-code.sh

# Run backup script (creates .backup_20260112 files)
./scripts/migrations/20260112-update-vocabulary-code.sh
```

**Validates**:

- All target files exist
- Backups created successfully
- Code change guide generated

### Step 2: Database Migration - pantheon-chat (30 minutes)

```bash
cd pantheon-chat

# Run SQL migration
psql $DATABASE_URL -f ../scripts/migrations/20260112-consolidate-vocabulary-tables.sql

# Verify migration
psql $DATABASE_URL -c "
SELECT
  (SELECT COUNT(*) FROM learned_words_backup_20260112) AS backup_count,
  (SELECT COUNT(*) FROM vocabulary_observations WHERE type = 'word') AS migrated_count,
  (SELECT COUNT(*) FROM vocabulary_observations WHERE is_integrated = TRUE) AS integrated_count;
"
```

**Expected Output**:

```
backup_count | migrated_count | integrated_count
-------------|----------------|------------------
964          | 2964           | 482
```

### Step 3: Code Updates - pantheon-chat (1 hour)

Follow guide: `scripts/migrations/20260112-code-changes-guide.md`

**Files to update**:

1. `qig-backend/vocabulary_persistence.py` (2 functions)
2. `qig-backend/vocabulary_coordinator.py` (1 query)
3. `shared/schema.ts` (deprecate old table)

**Test after changes**:

```bash
# Test Python imports
python3 -c "import sys; sys.path.insert(0, 'qig-backend'); from vocabulary_persistence import VocabularyPersistence; print('[OK] Imports work')"

# Test integration
cd qig-backend
python3 -c "
import os
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL')
from vocabulary_coordinator import VocabularyCoordinator
vc = VocabularyCoordinator()
result = vc.integrate_pending_vocabulary(min_phi=0.65, limit=5)
print(f'[OK] Integrated {result.get(\"integrated_count\", 0)} words')
"

# Test TypeScript
cd ..
npm run check
npm run build
```

### Step 4: Database Migration - pantheon-replit (30 minutes)

```bash
cd ../pantheon-replit

# Run same SQL migration
psql $NEON_DATABASE_URL -f ../scripts/migrations/20260112-consolidate-vocabulary-tables.sql

# Verify
psql $NEON_DATABASE_URL -c "SELECT COUNT(*) FROM vocabulary_observations WHERE type = 'word';"
```

### Step 5: Code Updates - pantheon-replit (1 hour)

Repeat Step 3 for pantheon-replit project.

### Step 6: Database Migration - SearchSpaceCollapse (30 minutes)

```bash
cd ../SearchSpaceCollapse

# Run same SQL migration
psql $NEON_DATABASE_URL -f ../scripts/migrations/20260112-consolidate-vocabulary-tables.sql

# Verify
psql $NEON_DATABASE_URL -c "SELECT COUNT(*) FROM vocabulary_observations WHERE type = 'word';"
```

### Step 7: Code Updates - SearchSpaceCollapse (1 hour)

Repeat Step 3 for SearchSpaceCollapse project (only Python files, no vocabulary_coordinator).

### Step 8: Integration Testing (1 hour)

**Test each project**:

```bash
# pantheon-chat
cd pantheon-chat
npm run dev &  # Start Node.js server
cd qig-backend && python3 wsgi.py &  # Start Python backend

# Test vocabulary learning
curl http://localhost:5000/api/vocabulary/learn -d '{"word": "consciousness", "phi": 0.75}'

# Check integration (wait 5 min or force)
# Should see new word in vocabulary_observations with is_integrated=TRUE

# pantheon-replit
cd ../pantheon-replit
# Same tests

# SearchSpaceCollapse
cd ../SearchSpaceCollapse
# Test wallet search with learned vocabulary
```

**Validation queries**:

```sql
-- Check learned words are being queried correctly
SELECT text, avg_phi, is_integrated
FROM vocabulary_observations
WHERE type = 'word' AND is_real_word = TRUE
ORDER BY avg_phi DESC
LIMIT 10;

-- Check integration is working
SELECT COUNT(*)
FROM vocabulary_observations
WHERE is_integrated = TRUE AND type = 'word';

-- Check no orphaned data
SELECT COUNT(*) FROM learned_words_backup_20260112;
```

---

## Validation Period (2 weeks: 2026-01-12 to 2026-01-26)

**Monitor**:

- [ ] No errors in vocabulary integration logs
- [ ] `is_integrated` flag updating correctly
- [ ] Generation using newly learned words
- [ ] Phi scores remain consistent
- [ ] No performance degradation

**Compatibility view active**: `learned_words_compat` allows rollback if needed

---

## Cleanup (After 2-week validation)

**Date**: 2026-01-26 or later

```sql
-- Drop compatibility view
DROP VIEW IF EXISTS learned_words_compat;

-- Drop backup table
DROP TABLE IF EXISTS learned_words_backup_20260112;

-- Update comments
COMMENT ON TABLE vocabulary_observations IS
  'Unified vocabulary tracking. Consolidated learned_words on 2026-01-12. Single source of truth.';
```

**Delete backup files**:

```bash
find . -name "*.backup_20260112" -delete
```

---

## Rollback Procedure (if needed)

**Trigger conditions**:

- Data integrity issues
- Performance degradation >20%
- Integration failures
- Phi score anomalies

**Steps**:

```bash
# 1. Restore code from backups
for f in $(find . -name "*.backup_20260112"); do
    cp "$f" "${f%.backup_20260112}"
done

# 2. Restore database (per project)
psql $DATABASE_URL << 'SQL'
DROP VIEW IF EXISTS learned_words_compat;
ALTER TABLE learned_words_backup_20260112 RENAME TO learned_words;
SQL

# 3. Restart services
# 4. Verify functionality restored
```

---

## Success Criteria

- [ ] All 3 projects migrated successfully
- [ ] No data loss (backup_count == migrated_count)
- [ ] Vocabulary integration working (new words appear in 5 min)
- [ ] No errors in production logs for 2 weeks
- [ ] Performance within acceptable range (<5% overhead)
- [ ] Team confirms improved data consistency

---

## Project-Specific Notes

**pantheon-chat** (Railway PostgreSQL):

- Production system - migrate during low-traffic window
- Monitor Railway metrics for performance impact

**pantheon-replit** (Neon us-east-1):

- Development system - safe to test first
- Can rollback easily without production impact

**SearchSpaceCollapse** (Neon us-west-2):

- Bitcoin wallet search - TEST THOROUGHLY
- Verify mnemonic generation unaffected
- Backup wallet search history before migration

---

**Estimated Total Time**: 6 hours (active work) + 2 weeks (validation)
**Risk Level**: LOW (backup + compatibility view + 2-week validation)
**Complexity**: MEDIUM (SQL migration simple, code changes straightforward)

---

**Execute by**: Run steps sequentially, validate each project before proceeding to next.
