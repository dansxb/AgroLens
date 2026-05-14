# Project Overview

## What is AgroLens?

AgroLens helps German farmers apply pesticides precisely — only where plants are stressed, at the right rate — by analysing Sentinel-2 satellite imagery and generating Variable Rate Application (VRA) maps compatible with ISOBUS tractor terminals.

**Core value proposition:** Reduce pesticide use by 20–40% through satellite-driven prescription maps.

## How it works

1. **Sentinel-2 imagery** is fetched daily via the Sentinel Hub API for each registered field
2. **NDVI + NDRE indices** are computed from the raw bands (no ML training needed — pure physics)
3. **K-means clustering** (scikit-learn, k=2–5 zones) delineates management zones
4. **Prescription engine** assigns application rates per zone based on stress level
5. **Exports** in Shapefile, ISO 11783-10 TASKDATA.XML (ISOBUS), and PDF

## Regulatory context

- **§67 PflSchG** — German pesticide law requires documentation of every application → SprayingRecord model
- **FLIK-Nummer** — German field identifier for EU cross-compliance (InVeKoS)
- **ISOBUS** — Shapefile is NOT compatible with ISOBUS tractor terminals; TASKDATA.XML is mandatory

## Target users

German arable farmers with 50–500 ha, growing wheat/barley/rapeseed/sugar beet.

## Project root

`/Users/danielschaller/Desktop/CS Haus & Garten/Winter…/Claude Agents/`

## Related notes

- [[Architecture/System Overview]]
- [[Architecture/Data Model]]
- [[Architecture/ML Pipeline]]
