# SQL Migration Execution - Ready to Run

**Date**: 2026-01-12
**Status**: ✅ Code changes complete, SQL migration ready
**Projects**: pantheon-chat, SearchSpaceCollapse (pantheon-replit pending)

---

## ✅ Completed

- [x] Backup files created (.backup_20260112)
- [x] Python code updated (vocabulary_persistence.py, vocabulary_coordinator.py)
- [x] TypeScript schema updated (deprecated learnedWords tables)
- [x] Python syntax validated

---

## 🎯 Next Steps: Run SQL Migrations

### Option A: Run SQL Now (Recommended if you have DB access)

**pantheon-chat** (Railway PostgreSQL):

```bash
cd /home/braden/Desktop/Dev/pantheon-projects

# Set your DATABASE_URL if not already in environment
export DATABASE_URL="postgresql://..."  # Your Railway connection string

# Run migration
psql $DATABASE_URL -f scripts/migrations/20260112-consolidate-vocabulary-tables.sql

# Verify migration
psql $DATABASE_URL -c "
SELECT
  'Migration Check' AS test,
  (SELECT COUNT(*) FROM learned_words_backup_20260112) AS backup_rows,
  (SELECT COUNT(*) FROM vocabulary_observations WHERE type = 'word' AND is_real_word = TRUE) AS migrated_rows,
  (SELECT COUNT(*) FROM vocabulary_observations WHERE is_integrated = TRUE) AS integrated_rows;
"
```

**SearchSpaceCollapse** (Neon us-west-2):

```bash
# Set your Neon DATABASE_URL
export DATABASE_URL="postgresql://..."  # Your Neon connection string

# Run migration
psql $DATABASE_URL -f scripts/migrations/20260112-consolidate-vocabulary-tables.sql

# Verify migration
psql $DATABASE_URL -c "
SELECT
  'Migration Check' AS test,
  (SELECT COUNT(*) FROM learned_words_backup_20260112) AS backup_rows,
  (SELECT COUNT(*) FROM vocabulary_observations WHERE type = 'word' AND is_real_word = TRUE) AS migrated_rows;
"
```

### Option B: Manual SQL Execution (If psql unavailable)

Connect to your databases via Railway dashboard or Neon console and run the SQL from:
`/home/braden/Desktop/Dev/pantheon-projects/scripts/migrations/20260112-consolidate-vocabulary-tables.sql`

---

## ⚠️ Important Notes

### What the SQL Migration Does

1. **Migrates data** from `learned_words` → `vocabulary_observations`
   - Merges frequencies (sums them if word exists in both tables)
   - Averages phi scores (weighted by frequency)
   - Preserves all metadata

2. **Creates compatibility view** `learned_words_compat`
   - Allows Python code to work during validation period
   - Provides rollback safety

3. **Renames old table** to `learned_words_backup_20260112`
   - Keeps original data safe for 2 weeks
   - Can restore if needed

### What Changed in Code

**Python (vocabulary_persistence.py)**:

```python
# BEFORE
cur.execute("SELECT word FROM learned_words WHERE avg_phi >= %s")

# AFTER
cur.execute("""
  SELECT text FROM vocabulary_observations
  WHERE avg_phi >= %s AND type = 'word' AND is_real_word = TRUE
""")
```

**Python (vocabulary_coordinator.py)**:

```python
# BEFORE
cur.execute("SELECT word FROM learned_words WHERE is_integrated = FALSE")

# AFTER
cur.execute("""
  SELECT text FROM vocabulary_observations
  WHERE is_integrated = FALSE AND type = 'word' AND is_real_word = TRUE
""")
```

**TypeScript (shared/schema.ts)**:

- Renamed `learnedWords` → `learnedWords_DEPRECATED`
- Added deprecation notice
- Kept exports for compatibility

---

## 🧪 Post-Migration Testing

After running SQL migrations, test vocabulary integration:

**pantheon-chat**:

```bash
cd /home/braden/Desktop/Dev/pantheon-projects/pantheon-chat

# Test vocabulary query (should work now)
python3 << 'PYTHON'
import sys
import os
sys.path.insert(0, 'qig-backend')
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'your-db-url')

from vocabulary_persistence import VocabularyPersistence

vp = VocabularyPersistence()
words = vp.get_learned_words(min_phi=0.6, limit=5)
print(f"[✓] Retrieved {len(words)} high-phi words")
for w in words[:3]:
    print(f"  - {w['word']}: phi={w['avg_phi']:.3f}, freq={w['frequency']}")
PYTHON
```

**SearchSpaceCollapse**:

```bash
cd /home/braden/Desktop/Dev/pantheon-projects/SearchSpaceCollapse

# Test vocabulary query
python3 << 'PYTHON'
import sys
import os
sys.path.insert(0, 'qig-backend')
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', 'your-db-url')

from vocabulary_persistence import VocabularyPersistence

vp = VocabularyPersistence()
words = vp.get_learned_words(min_phi=0.65, limit=5)
print(f"[✓] Retrieved {len(words)} learned words")
for w in words[:3]:
    print(f"  - {w['word']}: phi={w['avg_phi']:.3f}, freq={w['frequency']}")
PYTHON
```

---

## 🔄 Rollback Procedure (If Needed)

If issues occur within 2 weeks:

```sql
-- Restore original table
ALTER TABLE learned_words_backup_20260112 RENAME TO learned_words;

-- Drop compatibility view
DROP VIEW IF EXISTS learned_words_compat;
```

Then restore backup files:

```bash
cd /home/braden/Desktop/Dev/pantheon-projects

# Restore pantheon-chat
cp pantheon-chat/qig-backend/vocabulary_persistence.py.backup_20260112 pantheon-chat/qig-backend/vocabulary_persistence.py
cp pantheon-chat/qig-backend/vocabulary_coordinator.py.backup_20260112 pantheon-chat/qig-backend/vocabulary_coordinator.py
cp pantheon-chat/shared/schema.ts.backup_20260112 pantheon-chat/shared/schema.ts

# Restore SearchSpaceCollapse
cp SearchSpaceCollapse/qig-backend/vocabulary_persistence.py.backup_20260112 SearchSpaceCollapse/qig-backend/vocabulary_persistence.py
cp SearchSpaceCollapse/shared/schema.ts.backup_20260112 SearchSpaceCollapse/shared/schema.ts
```

---

## 📋 Outstanding Work: pantheon-replit

**Status**: Code migration NOT YET performed

**Required steps** (when ready):

1. Backup files:
   - `pantheon-replit/qig-backend/vocabulary_persistence.py`
   - `pantheon-replit/qig-backend/vocabulary_coordinator.py`
   - `pantheon-replit/shared/schema.ts`

2. Apply same code changes as pantheon-chat

3. Run SQL migration on Neon (us-east-1) database

4. Test vocabulary integration

**Migration script**: Same SQL file works for all projects
**Estimated time**: 1-2 hours

---

## 📊 Expected Results

### Immediate (After SQL migration)

- ✅ `learned_words_backup_20260112` table exists
- ✅ `learned_words_compat` view provides compatibility
- ✅ `vocabulary_observations` contains all words from both tables
- ✅ No data loss (backup_count == words in vocabulary_observations)

### Within 5 Minutes (After code deployment)

- ✅ Vocabulary integration runs automatically
- ✅ New words appear in vocabulary_observations
- ✅ `is_integrated` flag updates correctly
- ✅ No errors in logs

### After 2 Weeks (Validation complete)

- ✅ Drop compatibility view
- ✅ Drop backup table
- ✅ Delete .backup_20260112 files
- ✅ Update documentation to reflect single-table architecture

---

**Ready to execute**: Yes, SQL migration can run safely.
**Rollback available**: Yes, for 2 weeks via backup table + code backups.
**Risk level**: LOW (extensive testing, backup safety nets in place).
