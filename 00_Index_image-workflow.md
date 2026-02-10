---
tags:
  - map/project
  - p/image-workflow
  - type/evergreen
  - domain/image-processing
  - status/active
  - tech/python
  - high-volume
  - mission-critical
created: 2025-12-31
---

# image-workflow

High-volume image processing pipeline that handles 10,000+ images per day through multiple quality control passes. This production system processes 5,000-7,000 real people images plus 4,500 AI-generated images daily, with comprehensive safety systems and disaster recovery built from 2.5+ months of battle-testing. The workflow includes face grouping, version selection, character sorting, pair comparison, and automated cropping with a web dashboard for activity tracking.

## Key Components

### Main Scripts
- `scripts/` - Core processing scripts (237 Python files)
  - Image quality filtering
  - Face grouping algorithms
  - Version selection tools
  - Character sorter
  - Pair comparison engine
  - Crop automation

### Documentation
- `Documents/` - Comprehensive documentation (178 MD files)
  - Architecture guides
  - Safety systems
  - Disaster recovery procedures
  - Session archives

### Tools
- Web dashboard for progress tracking
- Activity timer integration
- Companion file system (PNG+YAML pairs)
- Safety monitoring and alerts

### Data Management
- YAML configuration system
- Session snapshots
- Backup systems
- Archive management

## Status

**Tags:** #map/project #p/image-workflow  
**Status:** #status/active #status/production  
**Last Major Update:** December 2025 (actively maintained)  
**Priority:** #mission-critical #high-volume



## Recent Activity

- **2026-01-01 22:36**: analyze_backups.py: .

- **2026-01-01 22:36**: incremental_backup.py: .

- **2026-01-01 22:37**: incremental_backup.py: .

- **2026-01-01 22:37**: analyze_backups.py: .

- **2026-01-01 22:37**: analyze_backups.py: .

- **2026-01-01 22:38**: incremental_backup.py: .

- **2026-01-01 22:38**: incremental_backup.py: .

- **2026-01-01 22:38**: incremental_backup.py: .

- **2026-01-01 22:38**: analyze_backups.py: .

- **2026-01-01 22:38**: analyze_backups.py: .

- **2026-01-01 22:38**: analyze_backups.py: .

- **2026-01-01 22:39**: analyze_backups.py: .

- **2026-01-01 22:39**: analyze_backups.py: .

- **2026-01-01 22:45**: train_ranker_v3.py: .

- **2026-01-01 22:45**: train_ranker_v3.py: .

- **2026-01-01 22:47**: train_crop_proposer_v2.py: .

- **2026-01-01 22:47**: test_models.py: .

- **2026-01-01 22:47**: extract_all_historical_training.py: .

- **2026-01-01 22:47**: recover_all_code.py: .

- **2026-01-01 22:47**: recover_data_from_backup.py: .

- **2026-01-01 22:47**: train_ranker_v2.py: .

- **2026-01-01 22:47**: extract_mojo1_training.py: .

- **2026-01-01 22:47**: analyze_mojo1_crops.py: .

- **2026-01-01 22:47**: train_ranker_v2.py: .

- **2026-01-01 22:47**: train_ranker_v2.py: .

- **2026-01-01 22:48**: compute_mojo1_embeddings.py: .

- **2026-01-01 22:48**: compute_mojo1_embeddings.py: .

- **2026-01-01 22:48**: extract_project_training.py: .

- **2026-01-01 22:48**: train_ranker_v3.py: .

- **2026-01-01 22:49**: train_ranker_v2.py: .

- **2026-01-01 22:49**: train_crop_proposer_v2.py: .

- **2026-01-01 22:49**: extract_all_historical_training.py: .

- **2026-01-01 22:49**: analyze_mojo1_crops.py: .

- **2026-01-01 22:50**: extract_project_training.py: .

- **2026-01-01 22:50**: train_ranker_v2.py: .

- **2026-01-01 22:50**: train_crop_proposer_v2.py: .

- **2026-01-01 22:50**: analyze_mojo1_crops.py: .

- **2026-01-01 22:52**: analyze_mojo1_crops.py: .

- **2026-01-01 22:52**: compute_mojo1_embeddings.py: .

- **2026-01-01 22:52**: extract_all_historical_training.py: .

- **2026-01-01 22:52**: extract_mojo1_training.py: .

- **2026-01-01 22:52**: extract_project_training.py: .

- **2026-01-01 22:52**: test_models.py: .

- **2026-01-01 22:52**: train_crop_proposer_v2.py: .

- **2026-01-01 22:52**: train_ranker_v2.py: .

- **2026-01-01 22:52**: train_ranker_v3.py: .

- **2026-01-01 22:52**: recover_all_code.py: .

- **2026-01-01 22:52**: recover_data_from_backup.py: .


scaffolding_version: 1.0.0
scaffolding_date: 2026-01-27

## Related Documentation

- [Automation Reliability](patterns/automation-reliability.md) - automation
- [README](README) - Image Workflow

<!-- LIBRARIAN-INDEX-START -->

### Subdirectories

| Directory | Files | Description |
| :--- | :---: | :--- |
| [Documents/](Documents/README.md) | 4 | **Last Updated:** 2026-01-15 |
| [__character_group_1/](__character_group_1/) | 0 | No description available. |
| [__character_group_2/](__character_group_2/) | 0 | No description available. |
| [__character_group_3/](__character_group_3/) | 0 | No description available. |
| [__crop/](__crop/) | 0 | No description available. |
| [__crop_auto/](__crop_auto/) | 0 | No description available. |
| [__cropped/](__cropped/) | 0 | No description available. |
| [__delete_staging/](__delete_staging/) | 0 | No description available. |
| [__selected/](__selected/) | 0 | No description available. |
| [prompts/](prompts/README.md) | 7 | **Purpose:** Three-phase reliability review system to catch silent failures before they reach produc... |
| [sandbox/](sandbox/) | 0 | No description available. |
| [training data/](training data/) | 0 | No description available. |

### Files

| File | Description |
| :--- | :--- |
| [AGENTS.md](AGENTS.md) | > The single source of truth for hierarchy, workflow, and AI collaboration philosophy. |
| [CLAUDE.md](CLAUDE.md) | Brief description of the project's purpose |
| [CODEOWNERS](CODEOWNERS) | No description available. |
| [CODE_CONVENTIONS.md](CODE_CONVENTIONS.md) | This document defines coding standards for the image-workflow-scripts project. Following these conve... |
| [DECISIONS.md](DECISIONS.md) | > *Documenting WHY we made decisions, not just WHAT we built.* |
| [Documents/INCREMENTAL_BACKUP_GUIDE.md](Documents/INCREMENTAL_BACKUP_GUIDE.md) | The old backup system copied **ALL files every single night**, even when nothing changed: |
| [Documents/PROJECT_LIFECYCLE_SCRIPTS.md](Documents/PROJECT_LIFECYCLE_SCRIPTS.md) | These scripts standardize project creation and completion to ensure consistent manifests, proper tim... |
| [Documents/README.md](Documents/README.md) | *Auto-generated index. Last updated: 2026-01-24* |
| [Documents/REVIEWS_AND_GOVERNANCE_PROTOCOL.md](Documents/REVIEWS_AND_GOVERNANCE_PROTOCOL.md) | **Date:** 2026-01-07 |
| [Documents/ai/AI_ASSISTED_REVIEWER.md](Documents/ai/AI_ASSISTED_REVIEWER.md) | **Last Updated:** 2025-10-26 |
| [Documents/ai/AI_DOCUMENTS_INDEX.md](Documents/ai/AI_DOCUMENTS_INDEX.md) | **Last Updated:** 2026-01-15 |
| [Documents/ai/AI_TRAINING_DATA_ANALYSIS.md](Documents/ai/AI_TRAINING_DATA_ANALYSIS.md) | **Date:** October 31, 2025 |
| [Documents/ai/AI_TRAINING_DATA_STRUCTURE.md](Documents/ai/AI_TRAINING_DATA_STRUCTURE.md) | **Status:** Active |
| [Documents/ai/AI_TRAINING_GUIDE.md](Documents/ai/AI_TRAINING_GUIDE.md) | **Last Updated:** 2025-10-26 |
| [Documents/ai/AI_TRAINING_REFERENCE.md](Documents/ai/AI_TRAINING_REFERENCE.md) | **Last Updated:** 2025-10-26 |
| [Documents/core/ARCHITECTURE_OVERVIEW.md](Documents/core/ARCHITECTURE_OVERVIEW.md) | **Status:** Active |
| [Documents/core/DISASTER_RECOVERY_GUIDE.md](Documents/core/DISASTER_RECOVERY_GUIDE.md) | **Status:** Active |
| [Documents/core/OPERATIONS_GUIDE.md](Documents/core/OPERATIONS_GUIDE.md) | **Status:** Active |
| [Documents/core/PROJECT_LIFECYCLE_SCRIPTS.md](Documents/core/PROJECT_LIFECYCLE_SCRIPTS.md) | **Status:** Active |
| [Documents/dashboard/DASHBOARD_API.md](Documents/dashboard/DASHBOARD_API.md) | **Last Updated:** 2025-10-26 |
| [Documents/dashboard/DASHBOARD_GUIDE.md](Documents/dashboard/DASHBOARD_GUIDE.md) | **Status:** Active |
| [Documents/dashboard/dashboard-ideas.md](Documents/dashboard/dashboard-ideas.md) | This document collects dashboard visualization ideas without immediately building them. Think of it ... |
| [Documents/design/PHASE_4_TRACKING.md](Documents/design/PHASE_4_TRACKING.md) | - [ ] Add `.sandbox_marker` file to sandbox directories |
| [Documents/examples/SAMPLE_REPORT.md](Documents/examples/SAMPLE_REPORT.md) | *Source:* `SAMPLE_TODO.md` |
| [Documents/examples/SAMPLE_TODO.md](Documents/examples/SAMPLE_TODO.md) | - [ ] Add logging and remove bare except in file_tracker write path |
| [Documents/guides/15_MINUTE_BINS_GUIDE.md](Documents/guides/15_MINUTE_BINS_GUIDE.md) | **Audience:** Developers, Operators |
| [Documents/guides/AI_PREDICTIONS_BATCH_PLAN.md](Documents/guides/AI_PREDICTIONS_BATCH_PLAN.md) | **Generated:** 2025-11-01 |
| [Documents/guides/AI_TO_AI_PR_REVIEW_WORKFLOW.md](Documents/guides/AI_TO_AI_PR_REVIEW_WORKFLOW.md) | Purpose: Eliminate confusion in handoffs between assistants by using one repeatable flow, one place ... |
| [Documents/guides/AUDIT_FILES_VS_DB_GUIDE.md](Documents/guides/AUDIT_FILES_VS_DB_GUIDE.md) | **Last Updated:** 2025-10-26 |
| [Documents/guides/BACKFILL_QUICK_START.md](Documents/guides/BACKFILL_QUICK_START.md) | **Status:** Active (Updated 2025-10-31) |
| [Documents/guides/COMPANION_FILE_SYSTEM_GUIDE.md](Documents/guides/COMPANION_FILE_SYSTEM_GUIDE.md) | **Status:** Active |
| [Documents/guides/CROP_QUEUE_SUMMARY.md](Documents/guides/CROP_QUEUE_SUMMARY.md) | A **queue-based cropping system** that decouples the interactive UI from image processing, allowing ... |
| [Documents/guides/CROP_TIMER_USER_GUIDE.md](Documents/guides/CROP_TIMER_USER_GUIDE.md) | **Last Updated:** 2025-10-26 |
| [Documents/guides/ERROR_HANDLING_AND_ALERTS.md](Documents/guides/ERROR_HANDLING_AND_ALERTS.md) | **Status:** Active |
| [Documents/guides/INLINE_VALIDATION_GUIDE.md](Documents/guides/INLINE_VALIDATION_GUIDE.md) | **Audience:** Developers, Operators |
| [Documents/guides/QUEUE_MODE_GUIDE.md](Documents/guides/QUEUE_MODE_GUIDE.md) | Queue Mode decouples the **interactive cropping** (setting coordinates) from the **image processing*... |
| [Documents/guides/QUEUE_QUICKSTART_AND_ANALYZER_GUIDE.md](Documents/guides/QUEUE_QUICKSTART_AND_ANALYZER_GUIDE.md) | **Last Updated:** 2025-10-26 |
| [Documents/guides/README.md](Documents/guides/README.md) | Step-by-step instructions for common tasks and complex workflows in the image automation system. |
| [Documents/guides/README_todo_agent_planner.md](Documents/guides/README_todo_agent_planner.md) | Generate a token-aware plan from a Markdown to-do list. It assigns each task a **model recommendatio... |
| [Documents/guides/WORK_TIME_CALCULATION_GUIDE.md](Documents/guides/WORK_TIME_CALCULATION_GUIDE.md) | **Status:** Active |
| [Documents/guides/ZIP_DATABASE_MAPPING.md](Documents/guides/ZIP_DATABASE_MAPPING.md) | **Generated:** 2025-11-01 |
| [Documents/patterns/code-review-standard.md](Documents/patterns/code-review-standard.md) | **Status:** Proven Pattern |
| [Documents/patterns/learning-loop-pattern.md](Documents/patterns/learning-loop-pattern.md) | > **Purpose:** Guide for creating reinforcement learning cycles in any project |
| [Documents/reference/CASE_STUDIES.md](Documents/reference/CASE_STUDIES.md) | **Status:** Active |
| [Documents/reference/CODE_QUALITY_RULES.md](Documents/reference/CODE_QUALITY_RULES.md) | **Audience:** Developers & AI Assistants |
| [Documents/reference/CROP_TIMER_IMPLEMENTATION_PLAN.md](Documents/reference/CROP_TIMER_IMPLEMENTATION_PLAN.md) | Status: Draft (planning only) |
| [Documents/reference/LOCAL_MODEL_LEARNINGS.md](Documents/reference/LOCAL_MODEL_LEARNINGS.md) | > **Purpose:** Institutional memory for working with local AI models (Ollama) |
| [Documents/reference/MAPPING_TABLE_BEST_PRACTICE.md](Documents/reference/MAPPING_TABLE_BEST_PRACTICE.md) | **Date:** 2025-11-01 |
| [Documents/reference/TECHNICAL_KNOWLEDGE_BASE.md](Documents/reference/TECHNICAL_KNOWLEDGE_BASE.md) | **Status:** Active |
| [Documents/reference/WEB_STYLE_GUIDE.md](Documents/reference/WEB_STYLE_GUIDE.md) | **Status:** Active |
| [Documents/reviews/CHATGPT_CODE_REVIEW_PROMPT.md](Documents/reviews/CHATGPT_CODE_REVIEW_PROMPT.md) | You are reviewing a queue-based cropping system that was implemented by Claude. All critical issues ... |
| [Documents/reviews/CLAUDE_REVIEW_EXTRACTION_2025-11-01.md](Documents/reviews/CLAUDE_REVIEW_EXTRACTION_2025-11-01.md) | **Review Date:** 2025-11-01 |
| [Documents/reviews/CODE_REVIEW__claude_improve-cropping-utility.md](Documents/reviews/CODE_REVIEW__claude_improve-cropping-utility.md) | Reviewer: GPT-5 (Cursor assistant) |
| [Documents/reviews/DASHBOARD_FIXES_SUMMARY_2025-11-01.md](Documents/reviews/DASHBOARD_FIXES_SUMMARY_2025-11-01.md) | **Date:** 2025-11-01 |
| [Documents/reviews/QUEUE_CROPPING_REVIEW_2025-10-26.md](Documents/reviews/QUEUE_CROPPING_REVIEW_2025-10-26.md) | Branch: `claude/improve-cropping-utility-011CUVyPBdu7xPiYowp39Lvi` |
| [Documents/reviews/REVIEW_THESE_COMMITS.md](Documents/reviews/REVIEW_THESE_COMMITS.md) | **Branch:** `claude/improve-cropping-utility-011CUVyPBdu7xPiYowp39Lvi` |
| [Documents/reviews/REVIEW_claude_queue_dashboard_2025-10-26.md](Documents/reviews/REVIEW_claude_queue_dashboard_2025-10-26.md) | Branch: `claude/queue-dashboard-011CUVyPBdu7xPiYowp39Lvi` |
| [Documents/reviews/REVIEW_f5970b9_2025-10-26.md](Documents/reviews/REVIEW_f5970b9_2025-10-26.md) | Commit: f5970b9 – "fix: address ChatGPT code review findings - race conditions, imports, and validat... |
| [Documents/safety/DATA_CONSOLIDATION_SYSTEM.md](Documents/safety/DATA_CONSOLIDATION_SYSTEM.md) | > **Last Updated:** December 2025 |
| [Documents/safety/FILE_SAFETY_CHECKLIST.md](Documents/safety/FILE_SAFETY_CHECKLIST.md) | **Status:** Active |
| [Documents/safety/FILE_SAFETY_SYSTEM.md](Documents/safety/FILE_SAFETY_SYSTEM.md) | **Status:** Active |
| [Documents/safety/PROJECT_DELIVERABLES_POLICY.md](Documents/safety/PROJECT_DELIVERABLES_POLICY.md) | **Status:** Active |
| [Documents/safety/REPOSITORY_CLEANUP_GUIDE.md](Documents/safety/REPOSITORY_CLEANUP_GUIDE.md) | **Last Updated:** 2025-10-26 |
| [Documents/testing/QUICKSTART_TESTING.md](Documents/testing/QUICKSTART_TESTING.md) | **TL;DR:** Run a test project through all your tools safely using sandbox mode. |
| [Documents/testing/SANDBOX_MODE_GUIDE.md](Documents/testing/SANDBOX_MODE_GUIDE.md) | **Last Updated:** 2025-11-03 |
| [Documents/testing/TESTS_GUIDE.md](Documents/testing/TESTS_GUIDE.md) | **Last Updated:** 2025-10-26 |
| [Documents/testing/TEST_PROJECT_GUIDE.md](Documents/testing/TEST_PROJECT_GUIDE.md) | **Last Updated:** 2025-11-03 |
| [Documents/video_creation/README.md](Documents/video_creation/README.md) | **Status:** Ready for Phase 0 (Model Shootout) |
| [Documents/video_creation/image-to-video-blueprint.md](Documents/video_creation/image-to-video-blueprint.md) | Your current image-workflow system is **exceptionally well-positioned** for video generation. The ke... |
| [Documents/video_creation/setup-local-ai.md](Documents/video_creation/setup-local-ai.md) | --- |
| [Documents/video_creation/three-model-shootout-plan.md](Documents/video_creation/three-model-shootout-plan.md) | This plan outlines the steps to perform a cost-effective A/B/C test using temporary cloud GPU resour... |
| [Documents/video_creation/transition-to-video.md](Documents/video_creation/transition-to-video.md) | The Audit and Blueprint document is **excellent, highly detailed, and commercially sound**. It succe... |
| [README.md](README.md) | [Brief 2-3 sentence description of the project.] |
| [cursor_global_rules_kit.md](cursor_global_rules_kit.md) | A one-file kit you can paste into **Cursor → Settings → AI/Rules** (global), or drop per-project in ... |
| [prompts/README.md](prompts/README.md) | **Purpose:** Three-phase reliability review system to catch silent failures before they reach produc... |
| [prompts/raptor-light.md](prompts/raptor-light.md) | Cheap, single‑pass reliability review designed to cut token usage by **70–80%** while keeping the im... |
| [prompts/raptor_meta.md](prompts/raptor_meta.md) | You are the META-PROMPT RAPTOR: a coordinator that runs three structured review passes over a codeba... |
| [prompts/raptor_phase_1_Claude_sonnet_MAX.md](prompts/raptor_phase_1_Claude_sonnet_MAX.md) | You are acting as a senior software reliability engineer and reviewer for a solo developer's project... |
| [prompts/raptor_phase_2_ChatGPT5_codex.md](prompts/raptor_phase_2_ChatGPT5_codex.md) | You are GPT-5 Codex, acting as a senior code verifier and test auditor for the project "image-workfl... |
| [prompts/raptor_phase_3_ChatGPT5_MAX.md](prompts/raptor_phase_3_ChatGPT5_MAX.md) | You are acting as a seasoned human engineer performing a final review before merging code to main. |
| [prompts/token-lean-raptor-scan.md](prompts/token-lean-raptor-scan.md) | This document outlines how to continue your reliability hardening (Raptor‑style) for **underlying sc... |
| [pyproject.toml](pyproject.toml) | No description available. |
| [requirements_ai_training.txt](requirements_ai_training.txt) | No description available. |
| [requirements_crop_tool.txt](requirements_crop_tool.txt) | No description available. |
| [sandbox/mojo2/runs/20251023T054412Z_A-conservative/manifest.json](sandbox/mojo2/runs/20251023T054412Z_A-conservative/manifest.json) | No description available. |
| [sandbox/mojo2/runs/20251023T140103Z_A-conservative/manifest.json](sandbox/mojo2/runs/20251023T140103Z_A-conservative/manifest.json) | No description available. |
| [sandbox/mojo2/runs/20251206T183638Z_A-conservative/manifest.json](sandbox/mojo2/runs/20251206T183638Z_A-conservative/manifest.json) | No description available. |
| [sandbox/mojo2/runs/20251206T183749Z_A-conservative/manifest.json](sandbox/mojo2/runs/20251206T183749Z_A-conservative/manifest.json) | No description available. |
| [sandbox/mojo2/runs/20251206T183955Z_A-conservative/manifest.json](sandbox/mojo2/runs/20251206T183955Z_A-conservative/manifest.json) | No description available. |
| [sandbox/mojo2/runs/20251207T013948Z_A-conservative/manifest.json](sandbox/mojo2/runs/20251207T013948Z_A-conservative/manifest.json) | No description available. |
| [sandbox/mojo2/runs/20251207T014151Z_A-conservative/manifest.json](sandbox/mojo2/runs/20251207T014151Z_A-conservative/manifest.json) | No description available. |
| [sandbox/mojo2/runs/20251207T014323Z_A-conservative/manifest.json](sandbox/mojo2/runs/20251207T014323Z_A-conservative/manifest.json) | No description available. |
| [sandbox/mojo2/runs/20251207T014420Z_A-conservative/manifest.json](sandbox/mojo2/runs/20251207T014420Z_A-conservative/manifest.json) | No description available. |
| [sandbox/mojo2/runs/20251207T030516Z_A-conservative/manifest.json](sandbox/mojo2/runs/20251207T030516Z_A-conservative/manifest.json) | No description available. |
| [sandbox/mojo2/runs/20251207T030751Z_A-conservative/manifest.json](sandbox/mojo2/runs/20251207T030751Z_A-conservative/manifest.json) | No description available. |

<!-- LIBRARIAN-INDEX-END -->