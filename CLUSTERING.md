# Photo Clustering Algorithm

This document describes how the auto-clustering algorithm groups racing photos by identifying the same person across multiple images.

## Overview

The clustering algorithm uses a **two-stage priority system** to group photos of the same racer:

1. **Shot Date/Time (HIGHEST PRIORITY)** - Photos taken seconds apart
2. **Visual Similarity** - Outfit appearance (helmet, boots, clothing)

**Note:** Bib numbers are detected and used for **cluster naming** (e.g., `Racer_Bib_23`) but are **NOT used for matching**. Only timestamp and visual appearance determine clustering.

## Priority Hierarchy

### 1. Shot Date/Time (⏱️ HIGHEST PRIORITY)

Photos taken within seconds of each other are **automatically clustered together**, based on the assumption that photographers capture multiple shots of the same racer in rapid succession.

**EXIF Field Used:**
- Primary: `DateTimeOriginal` (EXIF standard, cross-platform)
- Fallback: `kMDItemContentCreationDate` (macOS extended attributes, for DxO-processed files)

**Rules:**
- **≤ 10 seconds apart** → **AUTOMATIC 1.0 MATCH**
  - Immediate clustering without visual comparison
  - Treats photos as guaranteed same person
  - Typical for burst mode photography

- **≤ 30 seconds apart** → **HIGH PRIORITY 0.85 MINIMUM**
  - Still performs visual comparison
  - Takes the higher of timestamp score (0.85) or visual score
  - Very likely same racer (sequential shots through gates)

- **> 30 seconds apart OR no timestamp** → Falls back to visual similarity only

**Example Scenarios:**

```
Scenario 1: Burst Photography
Photo A: 14:23:45.123
Photo B: 14:23:45.456 (0.3 seconds later)
Photo C: 14:23:46.789 (1.6 seconds after A)
→ All three AUTOMATICALLY clustered (score: 1.0)

Scenario 2: Sequential Gate Photos
Photo A: 14:23:45
Photo B: 14:24:08 (23 seconds later)
Photo C: 14:24:32 (47 seconds after A)
→ A and B clustered (0.85 minimum)
→ C uses visual comparison only

Scenario 3: Different Racers
Photo A: 14:23:45 (Racer #1)
Photo B: 14:25:30 (Racer #2, 105 seconds later)
→ Uses visual similarity only
```

**Why This Works:**
- Photographers typically shoot 3-10 frames per racer
- Burst mode captures 0.1-1 second intervals
- Sequential shots (different gates) are 5-30 seconds apart
- Different racers are usually 60-300 seconds apart

**Note on DxO PhotoLab Files:**
If EXIF `DateTimeOriginal` is missing (common with DxO-processed files), the system automatically falls back to macOS extended attributes (`kMDItemContentCreationDate`) which preserves the original shot date. This fallback only works on macOS.

---

### 2. Bib Numbers (🎫 FOR NAMING ONLY)

Racing bib numbers are **detected but NOT used for matching**.

**How Bib Numbers Are Used:**
- ✅ **Cluster Naming**: If detected, cluster is named `Racer_Bib_23` instead of `Outfit_1_white_blue`
- ❌ **NOT for Matching**: Bib numbers do NOT influence clustering decisions
- ❌ **NOT for Comparison**: Two photos with same/different bibs are compared by visual similarity only

**Why Not Match on Bib Numbers?**
- Bib detection can be unreliable (angles, blur, occlusion)
- Risk of false matches/splits if detection is wrong
- Timestamp + visual similarity is more robust
- Bib numbers still useful for identifying clusters after organization

**Clarity Requirements (for naming):**
A bib number is only recorded if:
- ✅ ALL digits are completely clear and unambiguous
- ✅ Number is in sharp focus
- ✅ Not partially obscured by arms, poles, or other objects
- ✅ Not at an extreme angle making digits ambiguous
- ❌ If ANY doubt about ANY digit → set to `null`

**Example:**
```
Photo A: Bib #23 visible, blue helmet, white boots
Photo B: Bib #23 visible, blue helmet, white boots
→ Matched by VISUAL + TIMESTAMP similarity (bib not considered)
→ Cluster named: Racer_Bib_23

Photo A: Bib #23 visible, blue helmet
Photo B: No bib visible, blue helmet
→ Matched by VISUAL + TIMESTAMP similarity
→ Both in same cluster (bib from Photo A used for naming)

Photo A: Bib #23, blue helmet
Photo B: Bib #45, blue helmet
→ Still MATCHED if visual similarity is high (bibs ignored for matching)
→ Cluster named using first photo's bib: Racer_Bib_23
→ Warning: This might indicate detection error or actual match
```

---

### 3. Visual Similarity (👁️ PRIMARY MATCHING METHOD)

When timestamp-based clustering doesn't apply (>30s apart or no timestamps), the system uses **visual appearance matching** based on outfit details. This is the primary method for determining if two photos show the same racer.

**Weighted Components:**

| Component | Weight | Description |
|-----------|--------|-------------|
| **Helmet (Complete)** | 30% | **Most visible identifier** - includes helmet brand (SMITH, Giro, POC), helmet colors/patterns, **goggle lens color**, **goggle strap color**, goggle brand |
| **Ski Boot Colors & Brand** | 25% | Highly visible (white, black, red boots; Lange, Salomon, etc.) |
| **Clothing Patterns** | 25% | Stripes, graphics, solid colors on suits |
| **Clothing Colors** | 15% | Primary and accent colors |
| **Equipment Brands** | 5% | Supporting evidence (ski brand, pole brand) |

**Helmet Matching Details (Critical):**
The helmet is the most distinctive visual element. Pay particular attention to:
- **Helmet brand** (SMITH vs Giro vs POC are very different)
- **Goggle lens color** (clear vs orange-tinted vs mirrored vs blue)
- **Goggle strap colors and patterns** (solid vs striped vs branded)
- **Helmet colors and patterns** (metallic blue, matte black, racing stripes)

**Scoring Guidelines:**

```
0.9-1.0: Nearly identical
        - Same helmet colors/patterns
        - Same boot colors
        - Same suit patterns/colors

0.7-0.9: Very similar
        - Matching helmet colors with similar patterns
        - OR same base helmet color + similar boots

0.5-0.7: Moderately similar
        - Similar helmet colors even if patterns differ
        - OR similar overall color scheme

0.3-0.5: Somewhat similar
        - Some color overlap in helmet or suit

0.0-0.3: Very different
        - Completely different color schemes
```

**Visual Matching Examples:**

```
Example 1: Strong Visual Match (Including Goggles)
Photo A: White SMITH helmet, orange-tinted goggles with black strap, white Lange boots, blue striped suit
Photo B: White SMITH helmet, orange-tinted goggles with black strap, white Lange boots, blue striped suit
→ Similarity: 0.95 (near perfect match - helmet brand, goggle details, boots all match)

Example 2: Same Helmet Brand & Color, Different Goggles
Photo A: White SMITH helmet, orange-tinted goggles
Photo B: White SMITH helmet, mirrored goggles
→ Similarity: 0.80 (helmet brand/color match, but goggle difference reduces score)

Example 3: Helmet Match, Boots Differ
Photo A: Metallic blue POC helmet, clear goggles, white boots
Photo B: Metallic blue POC helmet, clear goggles, red boots
→ Similarity: 0.70 (helmet and goggles match, boots differ)

Example 4: Similar Helmet Colors, Different Brands
Photo A: Blue SMITH helmet with stripes, blue suit
Photo B: Navy Giro helmet solid, dark blue suit
→ Similarity: 0.60 (similar colors but different brands and patterns)

Example 5: Same Brands, Different Appearance
Photo A: SMITH helmet (white) with clear goggles, HEAD skis
Photo B: SMITH helmet (black) with mirrored goggles, HEAD skis
→ Similarity: 0.40 (brands match, but visual appearance very different)
```

---

## Complete Priority Flow

```
┌─────────────────────────────────────────┐
│  New Photo Detected                     │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Extract:                               │
│  • Shot Date (EXIF DateTimeOriginal)    │
│  • Bib Number (for naming only)         │
│  • Outfit Description (helmet, boots)   │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Compare Against Each Existing Cluster  │
└─────────────┬───────────────────────────┘
              │
              ▼
      ┌───────────────┐
      │ Shot Dates    │
      │ ≤10s apart?   │
      └───┬───────┬───┘
          │ YES   │ NO
          ▼       ▼
    ┌─────────┐  ┌──────────────┐
    │MATCH 1.0│  │ Shot Dates   │
    │(DONE)   │  │ ≤30s apart?  │
    └─────────┘  └───┬──────┬───┘
                     │ YES  │ NO
                     ▼      ▼
               ┌──────────┐ ┌──────────┐
               │min(0.85, │ │  Visual  │
               │ visual)  │ │Similarity│
               └──────────┘ └──────────┘
              │
              ▼
    ┌─────────────────┐
    │ Best Score ≥    │
    │ Threshold?      │
    └───┬─────────┬───┘
        │ YES     │ NO
        ▼         ▼
   ┌─────────┐  ┌──────────────┐
   │Add to   │  │Create New    │
   │Cluster  │  │Cluster       │
   └─────────┘  └──────────────┘
                     │
                     ▼
              ┌────────────────┐
              │ Name cluster:  │
              │ • Racer_Bib_XX │
              │   (if bib found)│
              │ • Outfit_N_... │
              │   (otherwise)  │
              └────────────────┘
```

---

## Configuration

### Environment Variables (.env file)

```bash
# Visual similarity threshold (when timestamps >30s apart or missing)
CONFIDENCE_THRESHOLD=0.5
# Lower = more photos per cluster (looser grouping)
# Higher = fewer photos per cluster (stricter grouping)
# Recommended: 0.5 for balanced clustering

# Timestamp clustering windows
TIMESTAMP_EXACT_MATCH_SECONDS=10
# Photos within this window → AUTOMATIC 1.0 match
# Recommended values:
#   5-10 = Tight (only rapid burst shots)
#   10-15 = Balanced (typical burst mode)
#   15-30 = Loose (sequential shots)

TIMESTAMP_HIGH_PRIORITY_SECONDS=30
# Photos within this window → 0.85 minimum similarity
# Recommended values:
#   20-30 = Tight (sequential shots only)
#   30-60 = Balanced (same racer, different angles)
#   60-120 = Loose (same racer over longer sequence)

# Note: EXACT_MATCH must be ≤ HIGH_PRIORITY
```

### Hardcoded Values (in prompts.py)

Visual similarity weights for outfit matching:

```python
HELMET_WEIGHT = 30%  # Including goggles, brand, colors, patterns
BOOT_WEIGHT = 25%    # Brand and colors
CLOTHING_PATTERN_WEIGHT = 25%
CLOTHING_COLOR_WEIGHT = 15%
BRAND_WEIGHT = 5%    # Equipment brands (supporting evidence)
```

---

## Caching

**Outfit Detection Cache:** `.outfit_detection_cache.json`

The system caches Claude's outfit detection results to minimize API calls:

```json
{
  "/path/to/photo.jpg": [
    {
      "position": "center",
      "outfit_description": "...",
      "bib_number": "23",
      "helmet_colors": ["white", "blue"],
      "boot_brand": "Lange",
      ...
    }
  ]
}
```

**Cache Behavior:**
- Saved every 5 photos during processing
- Persists between runs
- Delete to force re-detection: `rm .outfit_detection_cache.json`

**Timestamps are NOT cached** - they are extracted from EXIF on every run (fast operation).

---

## Performance Optimizations

### 1. **Early Termination**
When a cluster match reaches ≥0.95 similarity, stop comparing against other clusters.

### 2. **Timestamp Short-Circuit**
Photos ≤10 seconds apart skip visual comparison entirely (immediate 1.0 match).

### 3. **API Call Reduction**
- Outfit detection cached across runs
- Timestamp extraction uses local EXIF (no API calls)
- Comparison uses text-only API calls (cheaper than image analysis)

### 4. **Parallel Processing Potential**
(Not yet implemented - future enhancement)
- Outfit detection could be parallelized across images
- Comparisons are independent and could run concurrently

---

## Example: Real-World Clustering

**Input:** 100 racing photos from a ski event

**Scenario:**
```
Photos 1-5:   14:23:45-14:23:48 (Racer A, bib #23, blue helmet)
Photos 6-10:  14:24:15-14:24:18 (Racer B, bib #45, red helmet)
Photos 11-15: 14:25:30-14:25:33 (Racer A, bib #23, blue helmet)
Photos 16-20: 14:26:45-14:26:48 (Racer C, bib #67, white helmet)
...
```

**Clustering Results:**

```
Cluster: Racer_Bib_23/
  ├── Photo_001.jpg (14:23:45) ← First cluster seed
  ├── Photo_002.jpg (14:23:46) ← Timestamp match (1s apart)
  ├── Photo_003.jpg (14:23:47) ← Timestamp match (2s apart)
  ├── Photo_004.jpg (14:23:48) ← Timestamp match (3s apart)
  ├── Photo_005.jpg (14:23:48) ← Timestamp match (3s apart)
  ├── Photo_011.jpg (14:25:30) ← Bib match OR visual match (0.95)
  ├── Photo_012.jpg (14:25:31) ← Timestamp match with photo 11
  └── ...

Cluster: Racer_Bib_45/
  ├── Photo_006.jpg (14:24:15)
  ├── Photo_007.jpg (14:24:16) ← Timestamp match
  └── ...

Cluster: Racer_Bib_67/
  ├── Photo_016.jpg (14:26:45)
  └── ...
```

**Statistics:**
- Timestamp-based matches: ~80% (burst shots)
- Bib-based matches: ~10% (different time windows, same bib)
- Visual-based matches: ~10% (bib unclear or missing)

---

## Troubleshooting

### Issue: Too Many Clusters (Same Person Split)

**Cause:** Confidence threshold too high

**Solution:**
```bash
# Lower the threshold in .env
CONFIDENCE_THRESHOLD=0.4  # was 0.5
```

### Issue: Wrong People Grouped Together

**Cause:** Confidence threshold too low OR timestamp window too wide

**Solution:**
```bash
# Raise the threshold in .env
CONFIDENCE_THRESHOLD=0.6  # was 0.5

# OR reduce timestamp window in code (v2/organizer.py):
TIMESTAMP_EXACT_MATCH = 5  # was 10 seconds
TIMESTAMP_HIGH_PRIORITY = 15  # was 30 seconds
```

### Issue: Photos Missing EXIF Timestamps

**Symptoms:** No timestamp-based clustering, relies only on visual

**Check:**
```bash
# Verify EXIF data exists
exiftool photo.jpg | grep "Date/Time Original"
```

**Solution:** If photos lack EXIF data, the system automatically falls back to visual similarity. This is expected behavior.

### Issue: Bib Numbers Not Detected

**Cause:** Claude being too strict with clarity requirements

**Check:** Look at debug output when processing photos:
```
>>> Photo: IMG_1234.jpg
    Bib number: null  ← Not detected
```

**Expected:** Bib detection is intentionally strict to avoid false matches. Only perfectly clear bibs are used.

---

## Testing & Validation

### Dry Run Mode
```bash
# Preview clustering without moving files
python -m v2.cli_organize /path/to/photos --mode auto-cluster --dry-run
```

### Debug Output

Enable debug by checking the first 5 comparisons:
- Shows timestamp differences
- Shows similarity scores
- Shows which matching method was used

### Manual Validation

After clustering:
```bash
# Review cluster contents
ls -lah organized_photos/Racer_Bib_23/
ls -lah organized_photos/Outfit_1_white_blue/

# Check if similar photos are grouped correctly
open organized_photos/Racer_Bib_23/*.jpg
```

---

## Future Enhancements

### Potential Improvements

1. **Configurable Timestamp Windows**
   - Move hardcoded 10s/30s to .env configuration
   - Allow per-event customization

2. **GPS Location Matching**
   - If photos have GPS EXIF data
   - Group by location (different race courses)

3. **Camera Serial Number Clustering**
   - Photos from same camera more likely to be sequential
   - Use as tiebreaker signal

4. **Machine Learning Refinement**
   - Train model on user corrections
   - Learn which signals matter most for specific photo sets

5. **Interactive Cluster Merging**
   - CLI tool to merge incorrectly split clusters
   - Update descriptions and re-cluster

---

## Credits

**Algorithm Design:** Multi-priority clustering for racing photography

**Implementation:** Claude Code (Anthropic)

**Vision Model:** Claude 3.5 Sonnet via Google Cloud Vertex AI
