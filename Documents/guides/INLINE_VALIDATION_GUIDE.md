# Inline Training Data Validation - Integration Guide
**Audience:** Developers, Operators

**Last Updated:** 2025-10-26


**Created:** October 21, 2025  
**Status:** ✅ **ACTIVE - INTEGRATED INTO ALL DATA COLLECTION TOOLS**

---

## 🎯 **What This Is**

Automatic data validation that **catches training data errors immediately** as they're written. No manual steps required.

### **The Problem This Solves**

In October 2025, we lost **thousands of training examples** because the AI Desktop Multi-Crop Tool logged invalid dimensions `(0, 0)` instead of actual image sizes. This wasn't discovered until weeks later during AI training.

### **The Solution**

**Inline validation** added directly to the logging functions. Bad data is rejected **instantly** with clear error messages.

---

## ✅ **What's Validated**

### **1. Crop Data (`log_select_crop_entry`)**

| Check | Error Caught | Impact |
|-------|-------------|---------|
| ✅ **Image dimensions > 0** | `width=0, height=0` | **THE BUG WE HIT** - Prevents unusable crop coordinates |
| ✅ **Crop coordinates valid** | `x1 >= x2` or out of range | Prevents invalid crop boxes |
| ✅ **Data types correct** | Wrong tuple format | Prevents parsing errors |

### **2. Selection Data (`log_selection_only_entry`)**

| Check | Error Caught | Impact |
|-------|-------------|---------|
| ✅ **Chosen path not empty** | Empty winner path | Prevents invalid training pairs |
| ✅ **Negative paths is list** | Wrong data type | Prevents JSON serialization errors |

---

## 🔧 **Where It's Integrated**

### **Tools That Write Training Data:**

| Script | Writes To | Validation Active |
|--------|-----------|-------------------|
| `01_ai_assisted_reviewer.py` | `selection_only_log.csv` | ✅ YES |
| `02_ai_desktop_multi_crop.py` | `select_crop_log.csv` | ✅ YES |

**Tools 02, 03, 05, 06** don't write training data, so no validation needed.

---

## 🚨 **What Happens When Validation Fails**

### **Example: Zero Dimensions Bug**

```python
# AI Desktop Multi-Crop Tool tries to log bad data:
log_select_crop_entry(
    session_id="20251021_150000",
    set_id="batch_42",
    directory="crop/",
    image_paths=["image1.png"],
    image_stages=["stage2"],
    image_sizes=[(0, 0)],  # BUG: Should be (1920, 1080)
    chosen_index=0,
    crop_norm=(0.1, 0.1, 0.9, 0.9)
)
```

### **Immediate Error (Tool Stops):**

```
======================================================================
❌ CRITICAL TRAINING DATA ERROR - Invalid Image Dimensions!
======================================================================
Image 0: crop/image1.png
Dimensions: 0 x 0

This would corrupt AI training data with unusable crop coordinates.
The bug is in the calling code that logged dimensions as (0, 0).

🔧 FIX: Check the code that calls log_select_crop_entry().
   Ensure it passes actual image dimensions, not (0, 0).
======================================================================
```

### **Result:**
- ✅ Tool stops immediately (doesn't process thousands more)
- ✅ Clear error message points to the bug
- ✅ Zero bad data written to CSV
- ✅ You fix the bug before continuing

---

## 💻 **Implementation Details**

### **Location:**
`scripts/utils/companion_file_utils.py`

### **Functions Modified:**
- `log_select_crop_entry()` - Lines 662-756
- `log_selection_only_entry()` - Lines 759-820

### **Validation Logic:**

```python
def log_select_crop_entry(...):
    # ========================================================================
    # INLINE VALIDATION - Catches data integrity errors immediately
    # ========================================================================
    
    # 1. Validate image dimensions
    for i, (w, h) in enumerate(image_sizes):
        if w <= 0 or h <= 0:
            raise ValueError(...)  # Clear error message with fix instructions
    
    # 2. Validate crop coordinates
    if crop_norm is not None:
        x1, y1, x2, y2 = crop_norm
        if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
            raise ValueError(...)
    
    # ========================================================================
    # Write CSV (only reached if validation passed)
    # ========================================================================
    _append_csv_row(csv_path, header, row)
```

### **Key Design Decisions:**

1. **Fail Fast:** Validation happens BEFORE writing to CSV
2. **Clear Errors:** Error messages include:
   - What failed
   - Why it matters
   - How to fix it
3. **Zero Performance Impact:** Simple checks (< 1ms)
4. **No Manual Steps:** Runs automatically on every write

---

## 🧪 **Testing**

### **Run Validation Tests:**

```bash
python scripts/tests/test_inline_validation.py
```

### **Tests Included:**

1. ✅ Catches 0x0 dimensions (the bug we hit)
2. ✅ Catches invalid crop coordinates
3. ✅ Catches empty chosen paths
4. ✅ Catches wrong data types

### **Test Output:**

```
======================================================================
✅ ALL TESTS PASSED (4/4)

Inline validation is working correctly!
Bad training data will be caught immediately during collection.
======================================================================
```

---

## 📊 **Benefits vs. Alternatives**

### **Our Approach: Inline Validation**

| Aspect | Result |
|--------|--------|
| **Feedback Time** | Instant (first bad write) |
| **Lost Work** | None (caught before accumulating) |
| **Infrastructure** | Minimal (5-10 lines per function) |
| **Manual Steps** | Zero (automatic) |
| **Performance** | Negligible (< 1ms per write) |

### **Alternative: Post-Batch Validation**

| Aspect | Result |
|--------|--------|
| **Feedback Time** | Hours later (end of session) |
| **Lost Work** | Entire session's work quarantined |
| **Infrastructure** | Complex (staging/promotion system) |
| **Manual Steps** | Must remember to run validator |
| **Performance** | Same |

---

## 🔄 **Integration History**

### **October 21, 2025 - Initial Integration**

- ✅ Added inline validation to `log_select_crop_entry()`
- ✅ Added inline validation to `log_selection_only_entry()`
- ✅ Created test suite with 4 test cases
- ✅ All tests passing
- ✅ Zero linter errors
- ✅ Documentation complete

### **Impact:**

The Desktop Multi-Crop bug that lost thousands of training examples would have been caught on the **FIRST** image with a clear error message pointing to the exact fix.

---

## 🛠️ **For Developers: Adding New Validation**

### **Template:**

```python
def log_training_data(...):
    """Log training data.
    
    Raises:
        ValueError: If data validation fails
    """
    # ========================================================================
    # INLINE VALIDATION
    # ========================================================================
    
    # Add your validation checks here
    if some_field_is_invalid:
        raise ValueError(
            f"\n{'='*70}\n"
            f"❌ CRITICAL TRAINING DATA ERROR - [Description]!\n"
            f"{'='*70}\n"
            f"[What's wrong]\n"
            f"\n"
            f"[Why it matters]\n"
            f"\n"
            f"🔧 FIX: [How to fix it]\n"
            f"{'='*70}\n"
        )
    
    # ========================================================================
    # Write data (only reached if validation passed)
    # ========================================================================
    _append_csv_row(...)
```

### **Guidelines:**

1. **Validate BEFORE writing** - Never write bad data
2. **Clear error messages** - Include what/why/how
3. **Fail fast** - Don't continue processing
4. **Add tests** - Update `test_inline_validation.py`

---

## 📝 **Related Documents**

- **`AI_DATA_COLLECTION_LESSONS_LEARNED.md`** - What went wrong and why
- **`scripts/ai/validate_training_data.py`** - Batch validator (still useful for pre-training checks)
- **`scripts/tests/test_inline_validation.py`** - Test suite

---

## ✅ **Verification Checklist**

Before considering inline validation complete:

- [x] Validation added to all logging functions
- [x] Tests written and passing
- [x] Error messages are clear and actionable
- [x] Zero linter errors
- [x] Documentation complete
- [x] Integrated into actual tools (not standalone)

---

**Status:** ✅ **COMPLETE AND ACTIVE**

All training data collection now has automatic validation. No manual steps required.

## Related Documentation

