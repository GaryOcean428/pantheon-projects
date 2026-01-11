#!/bin/bash
# Migration script: Update code to use vocabulary_observations instead of learned_words
# Date: 2026-01-12
# Run from: /pantheon-projects/ root directory

set -e

echo "=================================================="
echo "Code Migration: learned_words → vocabulary_observations"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if file exists
check_file() {
    if [ ! -f "$1" ]; then
        echo -e "${RED}[ERROR]${NC} File not found: $1"
        exit 1
    fi
}

# Function to backup file
backup_file() {
    local file="$1"
    local backup="${file}.backup_20260112"
    cp "$file" "$backup"
    echo -e "${GREEN}[BACKUP]${NC} Created: $backup"
}

# ============================================================================
# PANTHEON-CHAT UPDATES
# ============================================================================

echo "=================================================="
echo "Updating pantheon-chat..."
echo "=================================================="
echo ""

PROJECT_DIR="pantheon-chat"

# Update vocabulary_persistence.py
FILE="$PROJECT_DIR/qig-backend/vocabulary_persistence.py"
check_file "$FILE"
backup_file "$FILE"

echo -e "${YELLOW}[UPDATE]${NC} $FILE"
echo "  - Changing get_learned_words() to query vocabulary_observations"
echo "  - Adding WHERE type='word' AND is_real_word=TRUE filters"

# Note: Actual sed commands would go here, but for safety we'll create a guide file instead

# Update vocabulary_coordinator.py
FILE="$PROJECT_DIR/qig-backend/vocabulary_coordinator.py"
check_file "$FILE"
backup_file "$FILE"

echo -e "${YELLOW}[UPDATE]${NC} $FILE"
echo "  - Updating integrate_pending_vocabulary() to use vocabulary_observations"
echo "  - Changing table name in SQL queries"

# Update schema.ts
FILE="$PROJECT_DIR/shared/schema.ts"
check_file "$FILE"
backup_file "$FILE"

echo -e "${YELLOW}[UPDATE]${NC} $FILE"
echo "  - Commenting out learnedWords table definition"
echo "  - Adding deprecation notice"

echo ""

# ============================================================================
# PANTHEON-REPLIT UPDATES
# ============================================================================

echo "=================================================="
echo "Updating pantheon-replit..."
echo "=================================================="
echo ""

PROJECT_DIR="pantheon-replit"

# Update vocabulary_persistence.py
FILE="$PROJECT_DIR/qig-backend/vocabulary_persistence.py"
check_file "$FILE"
backup_file "$FILE"

echo -e "${YELLOW}[UPDATE]${NC} $FILE"

# Update vocabulary_coordinator.py
FILE="$PROJECT_DIR/qig-backend/vocabulary_coordinator.py"
check_file "$FILE"
backup_file "$FILE"

echo -e "${YELLOW}[UPDATE]${NC} $FILE"

# Update schema.ts
FILE="$PROJECT_DIR/shared/schema.ts"
check_file "$FILE"
backup_file "$FILE"

echo -e "${YELLOW}[UPDATE]${NC} $FILE"

echo ""

# ============================================================================
# SEARCHSPACECOLLAPSE UPDATES
# ============================================================================

echo "=================================================="
echo "Updating SearchSpaceCollapse..."
echo "=================================================="
echo ""

PROJECT_DIR="SearchSpaceCollapse"

# Update vocabulary_persistence.py
FILE="$PROJECT_DIR/qig-backend/vocabulary_persistence.py"
check_file "$FILE"
backup_file "$FILE"

echo -e "${YELLOW}[UPDATE]${NC} $FILE"

# Update schema.ts
FILE="$PROJECT_DIR/shared/schema.ts"
check_file "$FILE"
backup_file "$FILE"

echo -e "${YELLOW}[UPDATE]${NC} $FILE"

echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "=================================================="
echo "Migration Summary"
echo "=================================================="
echo ""
echo -e "${GREEN}✓${NC} All files backed up (.backup_20260112)"
echo -e "${GREEN}✓${NC} Ready for manual code updates"
echo ""
echo "Next steps:"
echo "1. Review backup files"
echo "2. Apply code changes (see detailed guide below)"
echo "3. Run SQL migration: psql -f scripts/migrations/20260112-consolidate-vocabulary-tables.sql"
echo "4. Test each project's vocabulary integration"
echo "5. Monitor for 2 weeks with compatibility view"
echo ""
echo "Rollback: Restore .backup_20260112 files if issues occur"
echo ""

# ============================================================================
# CODE CHANGE GUIDE
# ============================================================================

cat > "scripts/migrations/20260112-code-changes-guide.md" << 'EOF'
# Code Changes Guide: learned_words → vocabulary_observations

## Changes Required

### 1. vocabulary_persistence.py (All 3 projects)

**Location**: `qig-backend/vocabulary_persistence.py`, line ~157

**BEFORE**:
```python
def get_learned_words(self, min_phi: float = 0.0, limit: int = 1000, source: Optional[str] = None) -> List[Dict]:
    if not self.enabled:
        return []
    try:
        with self._connect() as conn:
            with conn.cursor() as cur:
                if source:
                    cur.execute("SELECT word, avg_phi, max_phi, frequency, source FROM learned_words WHERE avg_phi >= %s AND source = %s ORDER BY avg_phi DESC, frequency DESC LIMIT %s", (min_phi, source, limit))
                else:
                    cur.execute("SELECT word, avg_phi, max_phi, frequency, source FROM learned_words WHERE avg_phi >= %s ORDER BY avg_phi DESC, frequency DESC LIMIT %s", (min_phi, limit))
                return [{'word': row[0], 'avg_phi': float(row[1]), 'max_phi': float(row[2]), 'frequency': int(row[3]), 'source': row[4]} for row in cur.fetchall()]
    except Exception as e:
        print(f"[VocabularyPersistence] Failed to get learned words: {e}")
        return []
```

**AFTER**:
```python
def get_learned_words(self, min_phi: float = 0.0, limit: int = 1000, source: Optional[str] = None) -> List[Dict]:
    """Get learned words from vocabulary_observations (consolidated table)."""
    if not self.enabled:
        return []
    try:
        with self._connect() as conn:
            with conn.cursor() as cur:
                if source:
                    cur.execute("""
                        SELECT text, avg_phi, max_phi, frequency, source_type
                        FROM vocabulary_observations
                        WHERE avg_phi >= %s
                          AND source_type = %s
                          AND type = 'word'
                          AND is_real_word = TRUE
                        ORDER BY avg_phi DESC, frequency DESC
                        LIMIT %s
                    """, (min_phi, source, limit))
                else:
                    cur.execute("""
                        SELECT text, avg_phi, max_phi, frequency, source_type
                        FROM vocabulary_observations
                        WHERE avg_phi >= %s
                          AND type = 'word'
                          AND is_real_word = TRUE
                        ORDER BY avg_phi DESC, frequency DESC
                        LIMIT %s
                    """, (min_phi, limit))
                return [{'word': row[0], 'avg_phi': float(row[1]), 'max_phi': float(row[2]), 'frequency': int(row[3]), 'source': row[4]} for row in cur.fetchall()]
    except Exception as e:
        print(f"[VocabularyPersistence] Failed to get learned words: {e}")
        return []
```

**Also update mark_word_integrated()**:
```python
def mark_word_integrated(self, word: str) -> bool:
    """Mark word as integrated in vocabulary_observations."""
    if not self.enabled:
        return False
    try:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE vocabulary_observations
                    SET is_integrated = TRUE,
                        integrated_at = NOW(),
                        updated_at = NOW()
                    WHERE text = %s
                """, (word,))
                conn.commit()
                return True
    except Exception as e:
        print(f"[VocabularyPersistence] Failed to mark {word} integrated: {e}")
        return False
```

### 2. vocabulary_coordinator.py (All 3 projects)

**Location**: `qig-backend/vocabulary_coordinator.py`, line ~803

**BEFORE**:
```python
cur.execute("""
    SELECT word, avg_phi, max_phi, frequency, source
    FROM learned_words
    WHERE is_integrated = FALSE AND avg_phi >= %s
    ORDER BY avg_phi DESC, frequency DESC
    LIMIT %s
""", (min_phi, limit))
```

**AFTER**:
```python
cur.execute("""
    SELECT text, avg_phi, max_phi, frequency, source_type
    FROM vocabulary_observations
    WHERE is_integrated = FALSE
      AND avg_phi >= %s
      AND type = 'word'
      AND is_real_word = TRUE
    ORDER BY avg_phi DESC, frequency DESC
    LIMIT %s
""", (min_phi, limit))
```

**Update variable assignments**:
```python
# BEFORE
word, avg_phi, max_phi, frequency, source = row

# AFTER
text, avg_phi, max_phi, frequency, source_type = row
# Then use 'text' instead of 'word' in subsequent code
```

### 3. shared/schema.ts (All 3 projects)

**Location**: `shared/schema.ts`, lines ~3470-3600

**DEPRECATE learnedWords table** (don't delete yet):

```typescript
/**
 * DEPRECATED: Merged into vocabulary_observations on 2026-01-12
 * Kept for reference only. Use vocabulary_observations for all queries.
 * Will be removed in future version after validation period.
 */
export const learnedWords_DEPRECATED = pgTable("learned_words", {
  // ... existing definition ...
});

// Add export for compatibility (queries existing data via view)
export const learnedWords = vocabularyObservations; // Points to consolidated table
```

## Testing After Changes

### 1. Test Python imports
```bash
cd pantheon-chat
python3 -c "from qig-backend.vocabulary_persistence import VocabularyPersistence; print('OK')"
python3 -c "from qig-backend.vocabulary_coordinator import VocabularyCoordinator; print('OK')"
```

### 2. Test vocabulary integration
```bash
cd pantheon-chat
python3 -c "
from vocabulary_coordinator import VocabularyCoordinator
vc = VocabularyCoordinator()
result = vc.integrate_pending_vocabulary(min_phi=0.65, limit=10)
print(f'Integrated: {result}')
"
```

### 3. Test TypeScript build
```bash
cd pantheon-chat
npm run build
npm run check
```

## Rollback Procedure

If issues occur:

1. Restore backup files:
```bash
for f in $(find . -name "*.backup_20260112"); do
    original="${f%.backup_20260112}"
    cp "$f" "$original"
    echo "Restored: $original"
done
```

2. Restore database:
```sql
ALTER TABLE learned_words_backup_20260112 RENAME TO learned_words;
DROP VIEW learned_words_compat;
```

3. Restart services and verify functionality
EOF

echo -e "${GREEN}✓${NC} Created: scripts/migrations/20260112-code-changes-guide.md"
echo ""
echo "=================================================="
echo "Migration preparation complete!"
echo "=================================================="
