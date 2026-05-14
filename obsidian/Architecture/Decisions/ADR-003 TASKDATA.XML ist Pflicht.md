# ADR-003: TASKDATA.XML neben Shapefile ist Pflicht

**Status:** Entschieden  
**Datum:** 2026-05-13  
**Auslöser:** Landwirt-Validator-Report v1.0

---

## Kontext

AgroLens exportiert Prescription Maps. Der erste MVP-Entwurf sah nur Shapefile (.shp) als "ISOBUS-Export" vor.

## Problem

ISOBUS-Terminals (ISO 11783 Task Controller) können **keine Shapefiles direkt lesen**. Shapefile ist ein GIS-Format, das erst in einer FMIS-Software (365FarmNet, NEXT Farming, agri-Con) in das tatsächliche Terminal-Format konvertiert werden muss.

Das Terminal-Format ist **ISO 11783-10 TASKDATA.XML** — ein ZIP-Paket mit `TASKDATA.XML` + binären Grid-Dateien (`.bin`).

Ohne TASKDATA.XML:
- Landwirt mit John Deere GreenStar / Fendt Variotronic kann die Karte **nicht direkt laden**
- Braucht Zwischensoftware (die auf 65-Hektar-Betrieben oft fehlt)
- AgroLens ist de facto nicht ISOBUS-kompatibel

## Entscheidung

**Jeder Prescription-Export bietet immer beide Formate an:**
1. Shapefile (.zip mit .shp/.dbf/.prj/.shx) — für GIS-Nutzer und FMIS-Import
2. TASKDATA.XML (.zip nach ISO 11783-10) — für direkte ISOBUS-Terminal-Nutzung

TASKDATA.XML enthält:
- `<FRM>` (Farm), `<CTR>` (Landwirt), `<PDT>` (Produkt mit Zulassungsnummer)
- `<PFD>` (Schlag mit GPS-Koordinaten + FLIK-Nummer)
- `<TSK>` mit `<TZN>` (Treatment Zones) und `<GRD>` (Grid-Referenz)
- Binäre `.bin`-Datei mit Zonen-Index pro Grid-Zelle (Type 1)

## Agronomist-Disclaimer

Pflicht in jedem Export (PDF, TASKDATA, Shapefile-Metadaten):

> "Die Applikationsmengen basieren auf agronomischen Faustregeln und wurden nicht für jeden Kulturtyp und jede Region validiert. Bitte prüfen Sie die Empfehlungen mit einem zugelassenen Pflanzenschutzberater, bevor Sie die Applikation vornehmen."

## Konsequenz

- `services/export/taskdata_xml.py` ist kein optionales Feature — es ist Kern-Infrastruktur
- Checker-Checkliste und Landwirt-Validator prüfen TASKDATA.XML-Validität bei jedem Phase-Review
- UI zeigt klaren Hinweis: "TASKDATA.XML für ISOBUS-Terminals, Shapefile für FMIS-Import"
