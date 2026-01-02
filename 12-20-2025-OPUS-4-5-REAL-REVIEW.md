Fair. Let me redo this as a review of a **personal productivity tool built by a solo developer for their own use.**

---

## 1) Verdict: **Proceed with Major Changes**

This is a capable tool that does what you need, but it has accumulated significant technical debt and complexity that will bite you. The core workflow works. The surrounding infrastructure is overbuilt and fragile.

---

## 2) Tool Reality Check

### What It Actually Does Well

1. **Core image workflow works.** mojo3 processed 19,406 → 4,662 final images. The pipeline functions.
2. **File safety rules are well-designed.** The move-don't-modify philosophy, companion file handling, and trash-based deletion are smart data protection.
3. **SQLite v3 training system is solid.** ACID-compliant, per-project isolation, good schema design.
4. **AI models are trained and deployed.** Ranker v3 and crop proposer v3 exist and integrate into the reviewer.
5. **289 tests exist.** More coverage than most personal projects.

### What's Actually Problematic

1. **Complexity has outpaced your ability to maintain it.**

   - 234 Python files
   - 130+ documentation files
   - 1,336-line TODO.md that you haven't completed items from
   - TODO items dated "December 9, 2025" not done on December 20

2. **You don't know if the pipeline works right now.**

   - TODO explicitly states: "No idea if the full pipeline still works end-to-end"
   - Dashboard has 6+ known bugs listed in TODO
   - Dashboard tests fail consistently

3. **The AI accuracy claims are unvalidated.**

   - "94.4% anomaly accuracy" but trained on mojo1/mojo2, tested on... mojo1/mojo2
   - TODO admits: "Backfilling predictions on mojo1/mojo2 = testing on training data (not true accuracy test)"
   - No held-out test set validation completed

4. **Documentation rot is severe.**
   - "Last Updated" dates in docs are stale (October 2025)
   - Archives have 80+ files you'll never read again
   - Multiple TODO items about "prune TODO list" that haven't been done

---

## 3) Technical Teardown

### Things That Will Break Your Day

**Hardcoded paths in training scripts:**

```35:39:scripts/ai/train_ranker_v3.py
PROJECT_ROOT = Path("/Users/eriksjaastad/projects/image-workflow")
SELECTION_LOG = PROJECT_ROOT / "data/training/selection_only_log.csv"
```

If you ever rename this directory or move to a new machine, training scripts break. Easy fix but currently a landmine.

**Dashboard is half-broken:**

From your TODO:

- "Build vs Actual hours not working"
- "Project Productivity Table not populating"
- "Input vs Output panel empty for Mojo3"
- "Files Processed by Project looks wrong"
- Dashboard tests fail after 42-48 seconds consistently

You're maintaining a dashboard that doesn't show correct data. Either fix it or delete it.

**Log files grow unbounded:**

`data/file_operations_logs/*.log` has no rotation. Given your file operation volume, these will consume disk space over months.

**Flask runs in dev mode:**

No production server config. Works fine for local use, but the warnings are noise.

**21 separate SQLite databases:**

One per project. Cross-project analysis requires opening all of them. Fine for now, but awkward if you want aggregate stats.

### Things That Are Fine But Overengineered

**Raptor review process:** You built a 3-phase multi-AI review workflow that requires manual copy-paste between Claude and GPT. It produced good results (47 fixes) but took significant time and you haven't run it in 50 days. The TODO says "automate it" - either automate it or accept you won't do it again.

**Backup system:** Daily local backups + planned Google Drive sync + weekly rollups + health monitoring + alerts. This is more backup infrastructure than most production systems. It's good! But it's also a lot to maintain.

**Documentation architecture:** 6 levels of docs (`Documents/ai/`, `Documents/core/`, `Documents/guides/`, etc.) with cross-references, archive policies, and quarterly cleanup processes. For a single user, this is overkill. A single `NOTES.md` would suffice.

### Things That Are Actually Good

**File safety system:** The explicit rules about never modifying images, always using companions, logging all operations - this is production-grade thinking for a personal tool. It's saved you from data loss.

**AI training infrastructure:** The pipeline from selections → embeddings → training → inference is well-designed. The v3 SQLite schema with proper validation is solid.

**Test coverage for core utils:** `ai_training_decisions_v3.py` has 18 passing tests. Core utilities are tested.

**Focus timer integration design:** The TODO shows good thinking about work time accuracy. The phased approach (timer first, pattern detection later) is pragmatic.

---

## 4) Evidence-Based Critique

| Area                     | Evidence                                                                            | Assessment                                                        |
| ------------------------ | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| **Pipeline reliability** | TODO line 35: "No idea if full pipeline still works end-to-end"                     | Critical gap. You're planning to use tools you haven't validated. |
| **AI accuracy**          | TODO line 429: "Backfilling predictions on mojo1/mojo2 = testing on training data"  | Your 94.4% claim is meaningless without held-out validation.      |
| **Dashboard utility**    | TODO lines 925-937: 6 broken features listed                                        | You're maintaining broken software. Fix or delete.                |
| **Maintenance burden**   | TODO.md is 1,336 lines with items from October still open                           | Scope creep. You're adding faster than completing.                |
| **Code quality**         | Recent commits: "Fix 445 mypy errors", "Fix 42 test failures"                       | Tech debt accumulates, then requires cleanup sprints.             |
| **Backups**              | TODO line 76: "URGENT: Enable rclone Cloud Backups" - marked urgent, still not done | High priority items slip.                                         |

---

## 5) What You Should Actually Do

### Tier 1: Do This Week (Reliability)

| #   | Task                                   | Why                                   | Pass Criteria                                |
| --- | -------------------------------------- | ------------------------------------- | -------------------------------------------- |
| 1   | Run full pipeline on sandbox test data | You don't know if it works            | All 7 scripts complete without errors        |
| 2   | Enable rclone backup                   | Marked "URGENT" in your TODO          | Backup appears in Google Drive               |
| 3   | Fix or delete dashboard                | It's broken and you're maintaining it | Either all 6 bugs fixed OR dashboard removed |

### Tier 2: Do This Month (Technical Debt)

| #   | Task                                  | Why                                              | Pass Criteria                                         |
| --- | ------------------------------------- | ------------------------------------------------ | ----------------------------------------------------- |
| 4   | Remove hardcoded paths                | Training scripts will break on machine migration | `grep -r "eriksjaastad" scripts/ai/` returns 0        |
| 5   | Validate AI accuracy on held-out data | Your accuracy claims are unverified              | Document actual accuracy on mojo3 (never in training) |
| 6   | Prune TODO.md                         | 1,336 lines is unmanageable                      | < 100 lines, clear priorities                         |
| 7   | Delete or archive stale docs          | 80+ archive files, 40+ misc                      | Archives < 20 files total                             |

### Tier 3: Decide Whether to Keep (Complexity Audit)

Ask yourself for each:

| Component                  | Question                              | Recommendation                           |
| -------------------------- | ------------------------------------- | ---------------------------------------- |
| Dashboard                  | Do you actually look at these charts? | If no, delete. If yes, fix.              |
| Raptor reviews             | Will you run this again?              | If no, delete prompts. If yes, automate. |
| Phase 3/4 tracking in TODO | Will you build this?                  | If not in 30 days, delete from TODO.     |
| Historical crop extraction | "EXPERIMENT" status since October     | Kill it or do it.                        |
| Timer overlay for tools    | Phase 3, marked LOW priority          | Delete from TODO until you want it.      |

---

## 6) Specific File/Code Issues

**`scripts/01_ai_assisted_reviewer.py` - 2,551 lines:**
This is a monolith. It contains: Flask server, image grouping, AI inference, file operations, training data logging, UI generation, and hotkey handling. Splitting this would make debugging easier, but it's also working. Leave it until it breaks.

**`scripts/dashboard/productivity_dashboard.py` - 1,328 lines:**
Broken. The TODO lists 6 bugs. Either invest a day fixing it or delete it.

**`TODO.md` - 1,336 lines:**
This is a project management system, not a TODO list. The "Recently Completed" section alone is 100+ lines. Archive completed items to a separate file. Keep TODO.md under 100 lines.

**`data/training/ai_training_decisions/` - 21 databases:**
Fine for now. If you ever need cross-project analysis, consider a single DB with project_id column. Not urgent.

**`scripts/ai/train_ranker_v3.py` line 35:**

```python
PROJECT_ROOT = Path("/Users/eriksjaastad/projects/image-workflow")
```

Change to:

```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
```

---

## 7) Bottom Line

**What's working:** Core image pipeline, file safety, AI training infrastructure, test coverage for critical paths.

**What's broken:** Dashboard, AI accuracy validation, backup automation, TODO/doc maintenance.

**What's overbuilt:** Documentation architecture, backup monitoring, Raptor review process.

**Biggest risk:** You don't know if the pipeline works because you haven't tested it in 6+ weeks of changes.

**First action:** Run the end-to-end validation you listed in TODO. Today. Before your next real project.
