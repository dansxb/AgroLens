# AgroLens — How Image Evaluation Works

## The Short Answer

AgroLens does NOT use a trained image-recognition AI (like a neural network
that "looks at" photos). Instead, it uses **physics-based index formulas**
on specific light wavelengths that satellites measure, combined with a
standard **clustering algorithm** (k-means) to group field zones.

No training data required. No labelling required. No GPU training runs.
The formulas are based on plant biology that has been scientifically
validated for decades.

---

## Why Plants Reveal Themselves in Satellite Data

A healthy plant absorbs red light (for photosynthesis) and strongly
reflects near-infrared (NIR) light. A stressed or dying plant does
the opposite — it reflects more red and less NIR.

Sentinel-2 satellites measure light in 13 specific wavelength bands.
AgroLens uses four of them:

| Band | Wavelength | What it measures |
|------|-----------|-----------------|
| B04  | 665 nm (Red)       | Absorbed by healthy chlorophyll |
| B05  | 705 nm (Red-Edge)  | Transition zone — sensitive to early stress |
| B08  | 842 nm (NIR)       | Strongly reflected by healthy leaves |
| SCL  | —                  | Scene Classification Layer (cloud/shadow mask) |

Because plant biology determines how much of each wavelength is reflected,
no "learning" is needed. The signal is directly in the physics.

---

## Step 1 — Cloud Masking (SCL Band)

Before any calculation, invalid pixels are removed using the Scene
Classification Layer (SCL) that Sentinel-2 produces automatically.

Pixels classified as cloud, cloud shadow, snow, or no-data are marked
invalid and excluded from all further calculations.

```
Invalid SCL classes: 0 (no data), 1 (saturated), 3 (cloud shadow),
                     8 (cloud medium), 9 (cloud high), 10 (thin cirrus),
                     11 (snow/ice)

Result: a boolean mask — True = valid pixel, False = skip this pixel
```

This step is fully automatic. No training needed.

---

## Step 2 — NDVI Calculation (Vegetation Health Index)

NDVI = Normalized Difference Vegetation Index.

```
         NIR (B08) - Red (B04)
NDVI  =  ─────────────────────
         NIR (B08) + Red (B04)
```

Result: a value between -1 and +1 for every pixel in the field.

| NDVI Value | Meaning |
|-----------|---------|
| > 0.5     | Dense, healthy vegetation |
| 0.2–0.5   | Moderate vegetation, possible mild stress |
| 0.0–0.2   | Sparse vegetation or bare soil |
| < 0.0     | Water, cloud, or non-vegetated surface |

This is pure arithmetic — one formula, applied to every pixel.
No AI, no training, no black box.

---

## Step 3 — NDRE Calculation (Early Stress Detection)

NDRE = Normalized Difference Red-Edge Index.

```
         Red-Edge (B05) - Red (B04)
NDRE  =  ──────────────────────────
         Red-Edge (B05) + Red (B04)
```

NDRE is more sensitive than NDVI to early-stage chlorophyll depletion.
While NDVI detects obvious stress (visually yellow/brown plants), NDRE
can detect stress before it becomes visible to the human eye — giving
farmers a 7–14 day earlier warning.

Together, NDVI and NDRE give a two-dimensional picture of field health.

---

## Step 4 — Temporal Compositing (Handling Clouds)

A single satellite pass may have cloud cover over part of a field.
To produce a clean, cloud-free image, AgroLens stacks multiple scenes
from a 10-day window and computes the **pixel-wise median**:

```
For each pixel (x, y):
  Take the NDVI value from all available cloud-free scenes in the window
  → Result = median value (robust against cloud residuals)
```

A median is used instead of a mean because it ignores outliers
(residual thin cloud) more reliably.

Result: one clean composite raster per field per 10-day window.

---

## Step 5 — Management Zone Delineation (k-means Clustering)

This is the only "machine learning" step in the pipeline — but it is
**unsupervised** (no labelled training data needed).

k-means clustering groups pixels into k=3 zones based on their
combined [NDVI, NDRE] values:

```
Input:  every pixel's [NDVI, NDRE] value pair
k:      3 clusters
Output: each pixel assigned to cluster Low, Medium, or High
```

The clusters are ordered by their NDVI centroid:
- **Low**:    lowest average NDVI → most stressed area → least pesticide needed
- **Medium**: middle range → baseline rate
- **High**:   highest NDVI → most vigorous growth → attention area (fungal risk)

Why k=3? Three zones match the precision capability of modern VRA
application equipment (variable-rate spreaders have 3 rate zones).
More zones would be illusory precision for current farm machinery.

**No training data needed** because k-means discovers structure directly
from the data — it does not need examples of what "stressed" looks like.
The algorithm just asks: "which pixels are most similar to each other?"

---

## Step 6 — Prescription Engine (Rule-Based, Not AI)

Once zones are defined, the prescription rates are applied using a
**fixed rule table** — not AI:

| Application Type | Low Zone | Medium Zone | High Zone |
|-----------------|----------|-------------|-----------|
| Fungicide       | 0.6×     | 1.0×        | 1.3×      |
| Herbicide       | 0.7×     | 1.0×        | 1.2×      |
| Insecticide     | 0.5×     | 1.0×        | 1.5×      |

The multipliers are applied to the farmer's base rate (L/ha):

```
Rate in zone = base_rate_l_ha × multiplier
```

These rates were defined by agronomists based on crop science literature.
They are not learned from data — they are expert rules.

---

## Why NOT Use a Neural Network?

A common question: why not train a CNN (convolutional neural network)
to classify "stressed" vs "healthy" pixels from satellite images?

| Approach          | Neural Network (CNN)       | AgroLens (Physics-based)    |
|-------------------|---------------------------|------------------------------|
| Training data     | Thousands of labelled fields | None required                |
| Labelling cost    | Very high (expert agronomists must label) | None |
| Explainability    | Black box                  | Fully explainable formula    |
| Regulatory risk   | High (farmers distrust black boxes) | Low |
| Generalisation    | Requires data from each crop/region | Works globally by physics |
| Compute cost      | High (GPU training)        | Low (numpy on CPU)           |
| Accuracy          | Potentially higher (with enough data) | Very good for MVP |

For the MVP, the physics-based approach is the correct choice:
- No data collection bottleneck before launch
- Farmers and agronomists can verify the logic
- Results are defensible in regulatory environments (EU pesticide regs)
- Works on any crop, any region, from day one

A neural network becomes worth exploring in Phase 6+ when you have
thousands of confirmed prescription outcomes to learn from.

---

## Complete Pipeline Summary

```
Sentinel-2 Satellite
        │
        ▼
   Band Download
   (B04, B05, B08, SCL)
        │
        ▼
   Cloud Masking          ← SCL band, rule-based
        │
        ▼
   NDVI + NDRE            ← Physics formulas, no training
        │
        ▼
   Temporal Composite     ← 10-day median stack
        │
        ▼
   k-means Clustering     ← Unsupervised ML, k=3
   (Low / Medium / High)
        │
        ▼
   Prescription Rules     ← Expert agronomist rules
        │
        ▼
   VRA Map (GeoJSON/SHP/PDF)
        │
        ▼
   Farmer's Tractor
```

---

## What "AI" Actually Means in AgroLens

The word "AI" in the product description refers to:

1. **The k-means algorithm** — discovers field zones automatically without
   manual drawing. Each field gets a unique zone map, not a template.

2. **The temporal analysis** — the system tracks NDVI trends over time and
   can flag anomalies (sudden NDVI drop = potential disease outbreak).

3. **Future ML** — in later phases, yield outcome data from farms can train
   a model that improves prescription multipliers per crop type and region.
   But this requires real-world data from pilot farms first.

The competitive advantage is not in having a more sophisticated AI than
competitors — it is in making satellite-derived prescriptions accessible
to small and medium farms that cannot afford the €50,000+/year solutions
from Taranis or Farmers Edge.
