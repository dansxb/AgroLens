# ML Pipeline

## How it works (no training needed)

AgroLens uses **physics-based vegetation indices** — not trained models. The "ML" is k-means clustering only.

### Index formulas

```
NDVI = (NIR - Red) / (NIR + Red)       # General plant health
NDRE = (RedEdge - Red) / (RedEdge + Red)  # Nitrogen / chlorophyll stress
```

Sentinel-2 bands used: B04 (Red), B08 (NIR), B05 (RedEdge)

### Zone delineation pipeline

```
1. Fetch NDVI + NDRE rasters from S3
2. Stack into [N, 2] feature matrix (one row per valid pixel)
3. k-means (scikit-learn, configurable k=2–5)
4. Re-order centroids by ascending NDVI (Low → High)
5. Apply minimum zone size filter:
   - ≥10 ha field: drop zones < 0.5 ha
   - <10 ha field: drop zones < 1.0 ha
   - Merge dropped zone into nearest centroid neighbour
6. Write ManagementZone geometries to PostGIS
```

### Prescription engine

Zone rates are computed using multipliers per application type:

| Zone | Fungicide | Herbicide | Insecticide |
|------|-----------|-----------|-------------|
| Low (stressed) | High rate | Low rate | High rate |
| Medium | Medium rate | Medium rate | Medium rate |
| High (healthy) | Low rate | High rate | Low rate |

- Floor warning if any zone rate < 50% of base rate
- Rates never go negative
- German agronomist disclaimer appended to every prescription (mandatory)

### Celery task

`compute_field_zones(field_id, field_area_ha, n_zones=3)` — triggered after each new VegetationIndex composite is stored.
