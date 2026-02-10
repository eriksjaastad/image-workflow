# Phase 4 & 5 - Sandbox Integration Tracking

## Phase 4: FileTracker Integration

### Must Do
- [ ] Add `.sandbox_marker` file to sandbox directories
  - Create marker when SandboxConfig creates sandbox dirs
  - Verify marker exists before cleanup_sandbox.py deletes
  - Fail safe: refuse to delete if no marker found
- [ ] Update FileTracker to accept `sandbox_config` parameter. See [FILE_SAFETY_SYSTEM](../safety/FILE_SAFETY_SYSTEM.md).
- [ ] Make FileTracker use `sandbox_config.logs_dir` for log paths
- [ ] Test FileTracker writes logs to correct location (prod vs sandbox)

### Minor Issues from Phase 3 Code Review (Optional)
- [ ] **Case-sensitivity**: `TEST-demo` vs `test-demo`
  - Current: case-sensitive (TEST- required exactly)
  - Option: Normalize to uppercase in `validate_project_id()`
  - Decision: Document as case-sensitive for now (add to README)
- [ ] **Size calculation efficiency** in cleanup_sandbox.py
  - Current: `rglob("*")` walks tree, then `is_file()` checks each
  - Optimization: Not urgent, < 0.1s overhead even with thousands of files
  - Decision: Skip optimization unless users complain

## Phase 5: Example Integration

### Must Do
- [ ] Pick one workflow script to add `--sandbox` flag. See [PROJECT_LIFECYCLE_SCRIPTS](../PROJECT_LIFECYCLE_SCRIPTS.md).
  - Recommendation: `00_start_project.py` (simple, clear example)
- [ ] Add `--sandbox` argument
- [ ] Create SandboxConfig from args
- [ ] Use `sandbox.projects_dir` for manifest path
- [ ] Validate project ID with `sandbox.validate_project_id()`
- [ ] Pass SandboxConfig to FileTracker
- [ ] Test end-to-end with real workflow

---

## Related Documentation

- [ARCHITECTURE_OVERVIEW](../core/ARCHITECTURE_OVERVIEW.md) - High-level system design.
- [FILE_SAFETY_SYSTEM](../safety/FILE_SAFETY_SYSTEM.md) - Rules for sandbox and FileTracker.
- [PROJECT_LIFECYCLE_SCRIPTS](../PROJECT_LIFECYCLE_SCRIPTS.md) - Workflow scripts targeted for integration.
- [Code Review Anti-Patterns](Documents/reference/CODE_REVIEW_ANTI_PATTERNS.md) - code review
- [AI Model Cost Comparison](Documents/reference/MODEL_COST_COMPARISON.md) - AI models

## Code Review Notes

**From:** `claude/sandbox-integration-011CUjG3hJq3WnUVmCS7aE46` review
**Date:** 2025-11-03
**Status:** ✅ Approved - Ready to merge

**Key Points:**
- SandboxConfig design is solid
- Cleanup utility is production-grade
- Backward compatibility maintained
- Documentation is excellent

**Follow-up Items:**
- Sandbox marker files (safety feature)
- Integration example (Phase 5 will provide this)
- Test coverage (can add later if needed)

- [ARCHITECTURE_OVERVIEW](../core/ARCHITECTURE_OVERVIEW.md) - High-level system design.
- [FILE_SAFETY_SYSTEM](../safety/FILE_SAFETY_SYSTEM.md) - Rules for sandbox and FileTracker.
- [PROJECT_LIFECYCLE_SCRIPTS](../PROJECT_LIFECYCLE_SCRIPTS.md) - Workflow scripts targeted for integration.

---
*See also: [PROJECT_STRUCTURE_STANDARDS](../../../project-scaffolding/Documents/PROJECT_STRUCTURE_STANDARDS.md) and [Doppler Secrets Management](Documents/reference/DOPPLER_SECRETS_MANAGEMENT.md).*

### Nice to Have
- [ ] Add example to `scripts/examples/demo_with_sandbox.py`
- [ ] Document sandbox workflow in README or guide
- [ ] Add `--list` option to cleanup_sandbox.py (may be redundant with --dry-run)

## Code Review Notes

**From:** `claude/sandbox-integration-011CUjG3hJq3WnUVmCS7aE46` review
**Date:** 2025-11-03
**Status:** ✅ Approved - Ready to merge

**Key Points:**
- SandboxConfig design is solid
- Cleanup utility is production-grade
- Backward compatibility maintained
- Documentation is excellent

**Follow-up Items:**
- Sandbox marker files (safety feature)
- Integration example (Phase 5 will provide this)
- Test coverage (can add later if needed)

- [ARCHITECTURE_OVERVIEW](../core/ARCHITECTURE_OVERVIEW.md) - High-level system design.
- [FILE_SAFETY_SYSTEM](../safety/FILE_SAFETY_SYSTEM.md) - Rules for sandbox and FileTracker.
- [PROJECT_LIFECYCLE_SCRIPTS](../PROJECT_LIFECYCLE_SCRIPTS.md) - Workflow scripts targeted for integration.

---
*See also: [PROJECT_STRUCTURE_STANDARDS](../../../project-scaffolding/Documents/PROJECT_STRUCTURE_STANDARDS.md) and [Doppler Secrets Management](Documents/reference/DOPPLER_SECRETS_MANAGEMENT.md).*

### Nice to Have
- [ ] Add example to `scripts/examples/demo_with_sandbox.py`
- [ ] Document sandbox workflow in README or guide
- [ ] Add `--list` option to cleanup_sandbox.py (may be redundant with --dry-run)

- [Code Review Anti-Patterns](Documents/reference/CODE_REVIEW_ANTI_PATTERNS.md) - code review
## Code Review Notes

**From:** `claude/sandbox-integration-011CUjG3hJq3WnUVmCS7aE46` review
**Date:** 2025-11-03
**Status:** ✅ Approved - Ready to merge

**Key Points:**
- SandboxConfig design is solid
- Cleanup utility is production-grade
- Backward compatibility maintained
- Documentation is excellent

**Follow-up Items:**
- Sandbox marker files (safety feature)
- Integration example (Phase 5 will provide this)
- Test coverage (can add later if needed)

- [ARCHITECTURE_OVERVIEW](../core/ARCHITECTURE_OVERVIEW.md) - High-level system design.
- [FILE_SAFETY_SYSTEM](../safety/FILE_SAFETY_SYSTEM.md) - Rules for sandbox and FileTracker.
- [PROJECT_LIFECYCLE_SCRIPTS](../PROJECT_LIFECYCLE_SCRIPTS.md) - Workflow scripts targeted for integration.

---
*See also: [PROJECT_STRUCTURE_STANDARDS](../../../project-scaffolding/Documents/PROJECT_STRUCTURE_STANDARDS.md) and [Doppler Secrets Management](Documents/reference/DOPPLER_SECRETS_MANAGEMENT.md).*

### Nice to Have
- [ ] Add example to `scripts/examples/demo_with_sandbox.py`
- [ ] Document sandbox workflow in README or guide
- [ ] Add `--list` option to cleanup_sandbox.py (may be redundant with --dry-run)

## Code Review Notes

**From:** `claude/sandbox-integration-011CUjG3hJq3WnUVmCS7aE46` review
**Date:** 2025-11-03
**Status:** ✅ Approved - Ready to merge

**Key Points:**
- SandboxConfig design is solid
- Cleanup utility is production-grade
- Backward compatibility maintained
- Documentation is excellent

**Follow-up Items:**
- Sandbox marker files (safety feature)
- Integration example (Phase 5 will provide this)
- Test coverage (can add later if needed)

- [ARCHITECTURE_OVERVIEW](../core/ARCHITECTURE_OVERVIEW.md) - High-level system design.
- [FILE_SAFETY_SYSTEM](../safety/FILE_SAFETY_SYSTEM.md) - Rules for sandbox and FileTracker.
- [PROJECT_LIFECYCLE_SCRIPTS](../PROJECT_LIFECYCLE_SCRIPTS.md) - Workflow scripts targeted for integration.

---
*See also: [PROJECT_STRUCTURE_STANDARDS](../../../project-scaffolding/Documents/PROJECT_STRUCTURE_STANDARDS.md) and [Doppler Secrets Management](Documents/reference/DOPPLER_SECRETS_MANAGEMENT.md).*

### Nice to Have
- [ ] Add example to `scripts/examples/demo_with_sandbox.py`
- [ ] Document sandbox workflow in README or guide
- [ ] Add `--list` option to cleanup_sandbox.py (may be redundant with --dry-run)

- [Code Review Anti-Patterns](Documents/reference/CODE_REVIEW_ANTI_PATTERNS.md) - code review
## Code Review Notes

**From:** `claude/sandbox-integration-011CUjG3hJq3WnUVmCS7aE46` review
**Date:** 2025-11-03
**Status:** ✅ Approved - Ready to merge

**Key Points:**
- SandboxConfig design is solid
- Cleanup utility is production-grade
- Backward compatibility maintained
- Documentation is excellent

**Follow-up Items:**
- Sandbox marker files (safety feature)
- Integration example (Phase 5 will provide this)
- Test coverage (can add later if needed)

- [ARCHITECTURE_OVERVIEW](../core/ARCHITECTURE_OVERVIEW.md) - High-level system design.
- [FILE_SAFETY_SYSTEM](../safety/FILE_SAFETY_SYSTEM.md) - Rules for sandbox and FileTracker.
- [PROJECT_LIFECYCLE_SCRIPTS](../PROJECT_LIFECYCLE_SCRIPTS.md) - Workflow scripts targeted for integration.

---
*See also: [PROJECT_STRUCTURE_STANDARDS](../../../project-scaffolding/Documents/PROJECT_STRUCTURE_STANDARDS.md) and [Doppler Secrets Management](Documents/reference/DOPPLER_SECRETS_MANAGEMENT.md).*

### Nice to Have
- [ ] Add example to `scripts/examples/demo_with_sandbox.py`
- [ ] Document sandbox workflow in README or guide
- [ ] Add `--list` option to cleanup_sandbox.py (may be redundant with --dry-run)

## Code Review Notes

**From:** `claude/sandbox-integration-011CUjG3hJq3WnUVmCS7aE46` review
**Date:** 2025-11-03
**Status:** ✅ Approved - Ready to merge

**Key Points:**
- SandboxConfig design is solid
- Cleanup utility is production-grade
- Backward compatibility maintained
- Documentation is excellent

**Follow-up Items:**
- Sandbox marker files (safety feature)
- Integration example (Phase 5 will provide this)
- Test coverage (can add later if needed)

- [ARCHITECTURE_OVERVIEW](../core/ARCHITECTURE_OVERVIEW.md) - High-level system design.
- [FILE_SAFETY_SYSTEM](../safety/FILE_SAFETY_SYSTEM.md) - Rules for sandbox and FileTracker.
- [PROJECT_LIFECYCLE_SCRIPTS](../PROJECT_LIFECYCLE_SCRIPTS.md) - Workflow scripts targeted for integration.

---
*See also: [PROJECT_STRUCTURE_STANDARDS](../../../project-scaffolding/Documents/PROJECT_STRUCTURE_STANDARDS.md) and [Doppler Secrets Management](Documents/reference/DOPPLER_SECRETS_MANAGEMENT.md).*

### Nice to Have
- [ ] Add example to `scripts/examples/demo_with_sandbox.py`
- [ ] Document sandbox workflow in README or guide
- [ ] Add `--list` option to cleanup_sandbox.py (may be redundant with --dry-run)

- [Code Review Anti-Patterns](Documents/reference/CODE_REVIEW_ANTI_PATTERNS.md) - code review
## Code Review Notes

**From:** `claude/sandbox-integration-011CUjG3hJq3WnUVmCS7aE46` review
**Date:** 2025-11-03
**Status:** ✅ Approved - Ready to merge

**Key Points:**
- SandboxConfig design is solid
- Cleanup utility is production-grade
- Backward compatibility maintained
- Documentation is excellent

**Follow-up Items:**
- Sandbox marker files (safety feature)
- Integration example (Phase 5 will provide this)
- Test coverage (can add later if needed)

- [ARCHITECTURE_OVERVIEW](../core/ARCHITECTURE_OVERVIEW.md) - High-level system design.
- [FILE_SAFETY_SYSTEM](../safety/FILE_SAFETY_SYSTEM.md) - Rules for sandbox and FileTracker.
- [PROJECT_LIFECYCLE_SCRIPTS](../PROJECT_LIFECYCLE_SCRIPTS.md) - Workflow scripts targeted for integration.

---
*See also: [PROJECT_STRUCTURE_STANDARDS](../../../project-scaffolding/Documents/PROJECT_STRUCTURE_STANDARDS.md) and [Doppler Secrets Management](Documents/reference/DOPPLER_SECRETS_MANAGEMENT.md).*

### Nice to Have
- [ ] Add example to `scripts/examples/demo_with_sandbox.py`
- [ ] Document sandbox workflow in README or guide
- [ ] Add `--list` option to cleanup_sandbox.py (may be redundant with --dry-run)

## Code Review Notes

**From:** `claude/sandbox-integration-011CUjG3hJq3WnUVmCS7aE46` review
**Date:** 2025-11-03
**Status:** ✅ Approved - Ready to merge

**Key Points:**
- SandboxConfig design is solid
- Cleanup utility is production-grade
- Backward compatibility maintained
- Documentation is excellent

**Follow-up Items:**
- Sandbox marker files (safety feature)
- Integration example (Phase 5 will provide this)
- Test coverage (can add later if needed)
