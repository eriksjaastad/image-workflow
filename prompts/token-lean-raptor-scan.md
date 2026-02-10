# Token‑Lean Raptor Scan Guide

This document outlines how to continue your reliability hardening (Raptor‑style) for **underlying scripts** in the `image-workflow-scripts` repo — while keeping token usage extremely low.

---

## 🎯 Goal
Identify and prioritize the remaining silent‑failure and audit‑visibility issues **without running heavy multi‑model reviews**.  
These commands let you do that locally, so you only spend tokens on focused diffs.

---

## 🧰 Local Token‑Lean Target Scan

```bash
# 1) Silent failure hotspots
rg -n "except Exception" scripts | tee .raptor_targets.txt
rg -n "# noqa:\s*BLE001" scripts >> .raptor_targets.txt
rg -n "(?s)except [^:]+:\s*\n\s*pass\b" -U scripts >> .raptor_targets.txt

# 2) Places that need read-after-write checks
rg -n "write_text\(|open\(.*['"]w" scripts >> .raptor_targets.txt

# 3) Scanners that should warn on unreadables
rg -n "rglob\(" scripts >> .raptor_targets.txt

# 4) Console prints that should be logger calls
rg -n "^\s*print\(" scripts >> .raptor_targets.txt

# 5) Mixed path hazards
rg -n "absolute|resolve\(\)|relative" scripts >> .raptor_targets.txt

# 6) FileTracker touchpoints (audit visibility)
rg -n "FileTracker|log_operation" scripts >> .raptor_targets.txt

# Summarize per-file hit counts (prioritize highest first)
awk -F: '{print $1}' .raptor_targets.txt | sort | uniq -c | sort -nr | head -40
```

---

## 📋 How to Use the Results
1. Review the top files in the summary — those with the most matches have the highest “risk density.”  
2. Start at the top and apply the **RAPTOR‑LITE** prompt (Haiku 4.5).  
3. Cap each patch at ≤120 changed lines.  
4. Test locally (`ruff --fix && black . && pytest -q`).  
5. Escalate to Sonnet 4.5 only when the logic path is truly ambiguous.

---

## 🧩 Prioritization Order
| Tier | Module Type | Reason |
|------|--------------|--------|
| 1 | `scripts/utils/**` | Shared helpers; highest fan‑in, so failures cascade. |
| 2 | `scripts/file_tracker.py` | Central audit mechanism. |
| 3 | Manifest / allowlist writers | Break downstream workflows if silent. |
| 4 | Directory scanners | Can hide missing files or perms errors. |
| 5 | CLI wrappers / batch runners | Low‑risk; safe to leave for last. |

---

## ⚙️ Daily Burn Control
- **Max 2–3 files per day.**  
- **One model per session.** Avoid “verification passes.”  
- **Diff + 5‑bullet test plan only.**  
- Avoid `MAX` mode — even on Sonnet.  
- If you must re‑ask, paste only the failed block (≤80 lines).

---

## 🧠 Bonus: Regression Tripwire
Run after every batch of patches:
```bash
ruff --fix && black . && pytest -q
```
If failures are non‑trivial, *then* do one Sonnet 4.5 pass with the RAPTOR‑LITE diff.

---

## 💡 Optional: Script It
Save those ripgrep commands as **`raptor_scan.sh`** to re‑run easily:
```bash
bash raptor_scan.sh > raptor_summary.txt
less raptor_summary.txt
```

---

*Designed for Erik’s image‑workflow‑scripts repo — continue reliability hardening at low cost.*

## Related Documentation

- [Cost Management](Documents/reference/MODEL_COST_COMPARISON.md) - cost management
- [Tiered AI Sprint Planning](patterns/tiered-ai-sprint-planning.md) - prompt engineering
- [AI Model Cost Comparison](Documents/reference/MODEL_COST_COMPARISON.md) - AI models
- [README](README) - Image Workflow
