# Investigation Summary - Theatrical Language Sources

**Quick Reference:** See [20260109-theatrical-language-investigation-1.0F.md](./20260109-theatrical-language-investigation-1.0F.md) for complete details.

## Key Findings

### 1. Vocabulary Contamination (CRITICAL) 🔴
- **pantheon-replit:** 3/16 theatrical terms found (divine, sacred, holy) @ Φ=0.500
- **pantheon-chat:** 3/16 theatrical terms found (divine, sacred, holy) @ Φ=0.500  
- **SearchSpaceCollapse:** 0/16 terms ✅ CLEAN

**Fix:** Re-initialize vocabulary from technical corpus only (4-6 hours)

### 2. String Templates (MODERATE) 🟡
- 6 locations with hard-coded "Divine council", "Divine guidance"
- Variable names, comments, docstrings use theatrical framing

**Fix:** Find/replace in 6 files (30 minutes)

### 3. Hard-Coded Constants (LOW) 🟢
- 4,280 occurrences across 793 files
- Most common: 64→BASIN_DIM, 0.7→PHI_THRESHOLD

**Fix:** Run apply_constant_fixes.py (15 minutes)

## Generated Artifacts

| File | Size | Description |
|------|------|-------------|
| `20260109-theatrical-language-investigation-1.0F.md` | 15KB | Complete investigation report (FROZEN) |
| `vocab_audit_20260109.txt` | 1.5KB | Raw vocabulary contamination scan |
| `constants_scan_20260109.txt` | 435KB | Hard-coded constants scan (all projects) |
| `vocabulary_audit.py` | 5KB | Reusable audit script |
| `fix_hard_coded_constants.py` | 6KB | Reusable constants scanner |
| `apply_constant_fixes.py` | Generated | Auto-fix script (run to apply) |

## Next Actions

**Option A: Quick Wins First**
1. Run `apply_constant_fixes.py` (15 min)
2. Fix string templates (30 min)
3. Commit clean code
4. Start vocabulary re-initialization

**Option B: Critical Path First**  
1. Start corpus collection (can run overnight)
2. Fix strings/constants in parallel
3. Compute Fisher coordinates
4. Deploy clean vocabulary

**Recommended:** Option B - maximize parallelism

---

**Investigation Status:** ✅ COMPLETE  
**Scripts Status:** ✅ READY TO RUN  
**Documentation Status:** ✅ ORGANIZED PER ISO 27001

