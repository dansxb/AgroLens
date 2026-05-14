# Checker Agent — Compliance & QA Reference

*Legal requirements, format specs, and GDPR obligations for AgroLens.*

---

## German PflSchG §67 — Spray Record Mandatory Fields

**Legal basis:** §67 Pflanzenschutzgesetz (PflSchG) + EU Reg. 1107/2009 Art. 67(1) + EU Implementing Reg. 2023/564

**Applies to:** All professional users (Berufsverwender)

**Mandatory fields from 1 January 2026:**

| Field | German | Notes |
|---|---|---|
| Type of use | Art der Verwendung | e.g. "Freiland", "Gewächshaus" |
| Product name | Bezeichnung des PSM | Full commercial name |
| Authorization number | Zulassungsnummer | 8-digit EU approval number |
| Application date | Anwendungsdatum | Specific calendar date |
| Start time | Uhrzeit | Required if product restricts application window (bee hazard etc.) |
| Applied quantity | Aufwandmenge | Actual amount in kg, g, L, or mL per ha |
| Crop | Kultur | Crop name |
| **EPPO code** | **EPPO-Code** | **NEW 2026 — 5-letter plant code (e.g. ZEAMX = maize)** |
| BBCH growth stage | BBCH-Stadium | Required if product use is growth-stage restricted |
| **Field identifier** | **FID / FLIK-Nummer** | **NEW 2026 — georeferenced ID or GPS coordinates** |
| Treated area | Behandelte Fläche | In hectares |
| Applicator name | Name des Anwenders | Full name |

**Retention:** 3 years from 1 January of following year.

**Electronic mandate timeline:**
- From 2026: Electronic documentation permitted (but not yet mandatory)
- **From 2027: Mandatory machine-readable electronic format**
- PDF explicitly **not permitted** from 2027 (not machine-readable under the regulation)
- Permitted: JSON, XML, CSV, digital farm record systems (365FarmNet, NEXT Farming, etc.)

**AgroLens `SprayingRecord` model must include:** `field_id`, `prescription_id`, `applied_at` (UTC), `product_name`, `product_reg_number` (Zulassungsnummer), `operator_name`, `equipment_id`, `actual_rate_l_ha`, `crop_eppo_code`, `bbch_stage` (nullable), `flik` (from field record)

---

## ISOXML / ISO 11783-10 TASKDATA.XML Structure

**Standard:** ISO 11783-10 (ISOBUS Part 10) — governs prescription map exchange between FMIS and tractor terminals.

**ZIP package structure:**
```
TASKDATA.ZIP
├── TASKDATA.XML      # main catalog + task definitions
├── GRD00001.bin      # grid prescription binary
├── TLG00001.xml      # time log header (as-applied)
└── TLG00001.bin      # time log binary
```

**Minimal valid TASKDATA.XML:**
```xml
<ISO11783_TaskData VersionMajor="4" VersionMinor="3"
    ManagementSoftwareManufacturer="AgroLens"
    ManagementSoftwareVersion="1.0" DataTransferOrigin="1">

  <FRM A="FRM1" B="Musterbetrieb GmbH"/>
  <CTR A="CTR1" B="Müller" C="Hans"/>
  <PDT A="PDT1" B="Roundup" C="12345678"/>  <!-- C = Zulassungsnummer -->
  <PFD A="PFD1" B="Nordschlag" C="CTR1" D="FRM1" K="12.3456" L="52.1234"/>

  <TSK A="TSK1" B="Herbizidbehandlung" E="PFD1" G="1">
    <TZN A="0" B="1">
      <PDV A="PDT1" B="2500" C="ml/ha" D="1"/>
    </TZN>
    <GRD A="52.10" B="12.34" C="0.0001" D="0.0001"
         E="100" F="80" G="GRD00001" I="1"/>
  </TSK>
</ISO11783_TaskData>
```

**Grid types:**

| Type | `GRD I=` | Binary content | Use case |
|---|---|---|---|
| Type 1 | `1` | 1-byte integers = TreatmentZone index | Zone-based VRA (AgroLens default) |
| Type 2 | `2` | 32-bit integers = direct rate value | Continuous variable rate |

**AgroLens uses Type 1** (k-means zones → TZN indices). Each grid cell maps to a zone, each zone has a `<PDV>` application rate.

**FMIS compatibility note:** ISOBUS terminals cannot read Shapefiles directly. AgroLens must always export TASKDATA.XML alongside Shapefile — Shapefile alone is NOT ISOBUS-compatible.

---

## GDPR + EU Data Act (in force September 2025)

**What is personal data in precision ag:**
- Personal: farmer name, contact, account data, GPS tracks tied to identifiable person
- Non-personal (generally): NDVI values, soil nutrients, yield maps, zone polygons

**Three farmer rights under EU Data Act (September 2025):**

| Right | What it means for AgroLens |
|---|---|
| **Access** | Farmers can access their own field data, machine-readable, free of charge |
| **Portability** | Export all field data in standard formats (JSON/XML/CSV) on request |
| **Third-party sharing** | Farmer can direct AgroLens to share data with agronomist / cooperative — must comply |

**Protected from sharing obligation:**
- Derived algorithmic outputs (your NDVI→recommendation model results are protected)
- Trade secrets (with proportionate technical measures)
- Data of SMEs (micro/small enterprise exemption)

**Checklist for AgroLens compliance:**
- [ ] Privacy Policy: list data categories, purpose, retention (GDPR Art. 13)
- [ ] Data export endpoint (Data Act portability) — already in ExportButtons
- [ ] Account deletion endpoint (GDPR Art. 17 right to erasure)
- [ ] Data Processing Agreement (DPA) template for B2B customers
- [ ] Document legal basis for each processing activity (consent vs. legitimate interest)
- [ ] DPIA if using US cloud services for personal data (post-Schrems II)

---

## Landwirt Validator Integration Points

The Landwirt Validator runs after every phase and checks:
1. Does the software actually match how a German farmer uses precision ag tools?
2. Are all PflSchG §67 required fields present in `SprayingRecord`?
3. Is the TASKDATA.XML export valid and ISOBUS-compatible?
4. Do the NDVI-based recommendations make agronomic sense?
5. Are disclaimers present and legally adequate?

See [[Dev Setup/Testing Guide]] for how to trigger a Landwirt Validator review.
