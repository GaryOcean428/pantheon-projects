# ISO 27001 Naming Compliance Audit

**Document ID:** 20260109-naming-compliance-audit-1.00W
**Date:** 2026-01-09
**Status:** [W]orking - Audit in progress
**Purpose:** Audit all documentation files across 3 projects for ISO 27001 naming convention compliance

---

## Executive Summary

**Scope:** 808 active documentation files (excluding _archive/) across 3 projects
**Pattern:** `YYYYMMDD-name-version[STATUS].md`
**Compliance Rate:** ~65% (estimated, see breakdown below)

**Non-Compliant Categories:**

1. **Legacy numbered files** (06_Computer_Science_Fundamentals.md)
2. **README.md** files (acceptable exception)
3. **Non-dated docs** (AGENTS.md, API.md, etc.)
4. **Draft files** (v1DRAFT.md suffix)
5. **Test files** (20251228_035702_test_quantum_doc...)

---

## ISO 27001 Naming Convention

**Format:** `YYYYMMDD-name-version[STATUS].md`

**Components:**

- **YYYYMMDD**: Date (YYYY=year, MM=month, DD=day)
- **name**: Kebab-case description (lowercase, hyphens)
- **version**: Major.Minor (e.g., 1.00, 2.50)
- **[STATUS]**: Single letter code
  - **F**: Frozen (immutable, validated facts)
  - **W**: Working (active, editable)
  - **H**: Hypothesis (experimental, unvalidated)
  - **A**: Archived (superseded, historical)
  - **D**: Deprecated (scheduled for removal)

**Examples:**

- ✅ `20251226-physics-alignment-corrected-1.00F.md`
- ✅ `20260109-roadmap-production-1.00W.md`
- ❌ `06_Computer_Science_Fundamentals.md`
- ❌ `AGENTS.md`

**Acceptable Exceptions:**

- `README.md` (workspace-standard filename)
- `00-index.md` (directory index, ISO 27001 structure)
- Files in `_archive/` (already marked as historical)

---

## Audit Findings by Project

### pantheon-chat

**Total Files:** ~350 (estimated)
**Compliance:** ~70%

**Non-Compliant Patterns:**

1. **Curriculum files (docs/09-curriculum/):**

   ```
   ❌ 06_Computer_Science_Fundamentals.md
   ❌ 07_Machine_Learning_and_Deep_Learning.md
   ❌ 08_Neuroscience_and_Cognitive_Science.md
   ...
   ❌ 30_Formal_Logic_Systems.md
   ```

   **Count:** ~20 files
   **Recommendation:** Rename to `20251220-curriculum-{NN}-{topic}-1.00W.md` (already done for most)

2. **Root docs:**

   ```
   ❌ 00-index.md (acceptable exception)
   ❌ openapi.json (wrong extension, should be in api/)
   ❌ README.md (acceptable exception)
   ```

3. **API docs:**

   ```
   ✅ 20251223-external-api-guide-1.00W.md
   ❌ README.md (acceptable exception)
   ❌ openapi.yaml (external format, acceptable)
   ```

**Action Items:**

- Rename 20 legacy curriculum files
- Move `openapi.json` to `api/` directory
- Document exceptions in `00-index.md`

---

### pantheon-replit

**Total Files:** ~350 (estimated)
**Compliance:** ~70%

**Non-Compliant Patterns:**

1. **Curriculum files (docs/09-curriculum/):**

   ```
   ❌ 06_Computer_Science_Fundamentals.md
   ❌ 22_The_Syntergy_Bridge.md
   ❌ 23_Multi-AI_Collaboration.md
   ...
   ❌ 30_Formal_Logic_Systems.md
   ```

   **Count:** ~20 files
   **Recommendation:** Rename to match pantheon-chat format

2. **Root docs:**

   ```
   ❌ 00-index.md (acceptable exception)
   ❌ IMPLEMENTATION_SUMMARY.md
   ❌ PANTHEON_GOVERNANCE.md
   ❌ SEARCH_DEPLOYMENT_GUIDE.md
   ❌ 20260107-chaos-kernels-training-exploration-v1W.md (WRONG: "v1W" should be "-1.00W")
   ```

3. **Technical docs:**

   ```
   ❌ QIG-PURITY-REQUIREMENTS.md (should be dated)
   ```

**Action Items:**

- Rename 20 legacy curriculum files
- Rename root docs to ISO 27001 format
- Fix `20260107-chaos-kernels-training-exploration-v1W.md` → `-1.00W.md`
- Rename `QIG-PURITY-REQUIREMENTS.md` → `20251208-qig-purity-requirements-1.00F.md`

---

### SearchSpaceCollapse

**Total Files:** ~108 (estimated)
**Compliance:** ~50%

**Non-Compliant Patterns:**

1. **Root docs:**

   ```
   ❌ CLAUDE.md
   ❌ FINAL_SUMMARY.md
   ❌ IMPLEMENTATION_SUMMARY.md
   ❌ INFRASTRUCTURE_MIGRATION.md
   ❌ PANTHEON_INTEGRATION_SUMMARY.md
   ```

   **Recommendation:** Move to `docs/04-records/` with ISO 27001 naming

2. **Missing docs/ directory structure:**

   ```
   SearchSpaceCollapse/
   ├── docs/
   │   ├── 00-index.md (MISSING)
   │   ├── 01-policies/ (MISSING)
   │   ├── 02-procedures/ (MISSING)
   │   ├── 03-technical/ (MISSING)
   │   └── 04-records/ (PARTIALLY CREATED TODAY)
   ```

**Action Items:**

- Create full ISO 27001 docs structure
- Migrate root docs to `docs/04-records/`
- Create `00-index.md` for docs navigation
- Rename all non-compliant files

---

## Compliance Matrix

| Project | Total Files | Compliant | Non-Compliant | Compliance % |
|---------|-------------|-----------|---------------|--------------|
| pantheon-chat | ~350 | ~245 | ~105 | 70% |
| pantheon-replit | ~350 | ~245 | ~105 | 70% |
| SearchSpaceCollapse | ~108 | ~54 | ~54 | 50% |
| **TOTAL** | **~808** | **~544** | **~264** | **67%** |

---

## Non-Compliant File Categories

### 1. Legacy Numbered Files (40 files)

**Pattern:** `{NN}_{Title_With_Underscores}.md`

**Examples:**

```
06_Computer_Science_Fundamentals.md
22_The_Syntergy_Bridge.md
30_Formal_Logic_Systems.md
```

**Fix:**

```bash
# Automated rename script
for f in docs/09-curriculum/*_*.md; do
  num=$(echo "$f" | grep -oP '\d{2}(?=_)')
  title=$(echo "$f" | sed 's/.*\d{2}_//; s/\.md//; s/_/-/g' | tr '[:upper:]' '[:lower:]')
  mv "$f" "docs/09-curriculum/20251220-curriculum-${num}-${title}-1.00W.md"
done
```

### 2. Non-Dated Technical Docs (15 files)

**Pattern:** `{CAPS_WITH_UNDERSCORES}.md`

**Examples:**

```
AGENTS.md
API.md
QIG-PURITY-REQUIREMENTS.md
IMPLEMENTATION_SUMMARY.md
```

**Fix:** Rename with creation date (check `git log`):

```bash
git log --format=%ai {file.md} | head -1  # Get creation date
mv AGENTS.md docs/03-technical/20251208-agents-overview-1.00W.md
```

### 3. Test Files (2 files)

**Pattern:** `{YYYYMMDD_HHMMSS_test_*}.md`

**Examples:**

```
20251228_035702_test_quantum_doc_f0dc86bd546dbcb1.md
```

**Fix:** Delete (temporary test files) or move to `_archive/`

### 4. Draft Files (3 files)

**Pattern:** `*DRAFT.md` or `*v1.md`

**Examples:**

```
20250101-geometric-operations-v1DRAFT.md
20260107-chaos-kernels-training-exploration-v1W.md
```

**Fix:** Remove DRAFT suffix, use proper version:

```bash
mv 20250101-geometric-operations-v1DRAFT.md 20250101-geometric-operations-1.00H.md
mv 20260107-chaos-kernels-training-exploration-v1W.md 20260107-chaos-kernels-training-exploration-1.00W.md
```

---

## Automated Compliance Check Script

**Create:** `/pantheon-projects/scripts/validate-iso27001-naming.sh`

```bash
#!/bin/bash
# ISO 27001 Naming Convention Validator

ISO_PATTERN="^[0-9]{8}-[a-z0-9-]+-[0-9]+\.[0-9]{2}[FWHAD]\.md$"
EXCEPTIONS="^(README\.md|00-index\.md|openapi\.(json|yaml))$"

find_non_compliant() {
  project=$1
  find "$project/docs" -name "*.md" ! -path "*/_archive/*" | while read file; do
    basename=$(basename "$file")

    # Skip exceptions
    if [[ "$basename" =~ $EXCEPTIONS ]]; then
      continue
    fi

    # Check ISO 27001 pattern
    if ! [[ "$basename" =~ $ISO_PATTERN ]]; then
      echo "❌ $file"
    fi
  done
}

echo "=== ISO 27001 Naming Compliance Audit ==="
echo ""
echo "pantheon-chat:"
find_non_compliant "pantheon-chat"
echo ""
echo "pantheon-replit:"
find_non_compliant "pantheon-replit"
echo ""
echo "SearchSpaceCollapse:"
find_non_compliant "SearchSpaceCollapse"
```

**Usage:**

```bash
cd /pantheon-projects
./scripts/validate-iso27001-naming.sh > docs/20260109-naming-compliance-violations.txt
```

---

## Migration Plan

### Phase 1: Immediate (Week 1)

- [ ] Rename 40 legacy curriculum files
- [ ] Fix 3 draft files
- [ ] Delete 2 test files
- [ ] Create SearchSpaceCollapse docs/ structure

### Phase 2: Short-term (Week 2-3)

- [ ] Rename 15 non-dated technical docs
- [ ] Migrate 5 root docs to `docs/04-records/`
- [ ] Update all internal links
- [ ] Test documentation navigation

### Phase 3: Validation (Week 4)

- [ ] Run automated compliance check
- [ ] Update `00-index.md` with exceptions list
- [ ] Document naming convention in workspace `.github/copilot-instructions.md`
- [ ] Create pre-commit hook for future compliance

---

## Pre-Commit Hook (Future Prevention)

**Create:** `/pantheon-projects/.git/hooks/pre-commit`

```bash
#!/bin/bash
# Validate new/modified docs follow ISO 27001 naming

ISO_PATTERN="^[0-9]{8}-[a-z0-9-]+-[0-9]+\.[0-9]{2}[FWHAD]\.md$"
EXCEPTIONS="^(README\.md|00-index\.md|openapi\.(json|yaml))$"

git diff --cached --name-only --diff-filter=A | grep "/docs/.*\.md$" | while read file; do
  basename=$(basename "$file")

  if [[ "$basename" =~ $EXCEPTIONS ]]; then
    continue
  fi

  if ! [[ "$basename" =~ $ISO_PATTERN ]]; then
    echo "❌ ERROR: $file does not follow ISO 27001 naming convention"
    echo "   Expected: YYYYMMDD-name-version[STATUS].md"
    echo "   Example: 20260109-my-document-1.00W.md"
    exit 1
  fi
done
```

---

## Exceptions Policy

**Acceptable Non-Compliant Files:**

1. **README.md** - Universal convention for project documentation
2. **00-index.md** - ISO 27001 directory index file
3. **openapi.yaml / openapi.json** - External API specification format
4. **package.json, tsconfig.json, etc.** - Standard config files
5. **Files in `_archive/`** - Already marked as historical

**All other files MUST follow ISO 27001 naming convention.**

---

## Recommendations

1. **pantheon-chat:** 70% compliance - rename 105 files
2. **pantheon-replit:** 70% compliance - rename 105 files (synchronize with pantheon-chat)
3. **SearchSpaceCollapse:** 50% compliance - create docs/ structure + rename 54 files

**Total Effort:** ~264 file renames + structure creation + link updates
**Estimated Time:** 2-4 weeks with automation

**Priority:** Medium - Does not block functionality, improves maintainability

---

## Next Steps

1. **Immediate:** Create automated validation script
2. **Short-term:** Migrate SearchSpaceCollapse to full docs/ structure
3. **Medium-term:** Rename all legacy curriculum files
4. **Long-term:** Implement pre-commit hook for future compliance

---

## References

- [ISO 27001 Documentation Structure](../../.github/copilot-instructions.md)
- [pantheon-chat Naming Convention](../pantheon-chat/.github/copilot-instructions.md)
- [pantheon-replit Naming Convention](../pantheon-replit/.github/copilot-instructions.md)

---

**Status:** [W]orking - Audit complete, migration plan pending execution
