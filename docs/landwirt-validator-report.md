# AgroLens — Landwirt-Validator-Report
**Version 1.0 | Erstellt: Mai 2026 | Autor: Landwirt-Validator-Agent**

---

## Hintergrund: So sieht der echte Spritzgang eines 65-Hektar-Betriebs aus

Bevor wir AgroLens bewerten, muss das Team verstehen, wie ein typischer mittelgroßer Ackerbauer in Deutschland heute tatsächlich arbeitet. Nur dann können wir beurteilen, ob unser Produkt in seinen Alltag passt oder ob es daran vorbeientworfen wurde.

### Das Gerät

Ein Betrieb mit 65 Hektar setzt in der Regel auf eine **angehängte oder selbstfahrende Feldspritze mit 2.000–4.000 Liter Tankvolumen und 18–24 m Arbeitsbreite** (z.B. Amazone UF 1501, Horsch Leeb, LEMKEN Sirius). Neugeräte ab ca. 2018 haben standardmäßig ISOBUS (ISO 11783). Ältere Geräte können für 2.500–4.500 Euro nachgerüstet werden. **Section Control (TC-SC)** ist heute weitgehend Standard. **Variable-Rate-Applikation über TC-GEO** — also das Laden einer Applikationskarte mit zonenbasierter Dosierung — ist technisch möglich, aber in der Praxis auf 65-Hektar-Betrieben noch die Ausnahme, nicht die Regel.

### Der Workflow

Ein typischer Spritzgang sieht so aus:

1. **Entscheidungsphase (1–5 Tage vorher):** Der Landwirt oder sein Lohnunternehmer entscheidet auf Basis von Wetterfenstern (Windstärke unter 3 m/s, kein Regen, Temperatur 10–25°C), Beratungshinweisen des Pflanzenschutzdienstes (z.B. ISIP-Warndienstnachrichten), und eigener Schlagbegehung. Tools wie proPlant expert, Sencrop-Wetterdaten oder Spritzwetter-Apps (Syngenta) fließen ein. Satellitendaten spielen aktuell **keine direkte Rolle** in dieser Phase — sie fehlen im typischen Entscheidungs-Stack des kleinen Betriebs.

2. **Vorbereitung:** Bestellung beim Händler (häufig Raiffeisen, Agravis), Befüllung der Spritze, Einstellen der Ausbringmenge am Terminal. Bei ISOBUS-Betrieb: Aufruf des gespeicherten "Tasks" am ISOBUS-Terminal (z.B. John Deere GreenStar, Trimble GFX, Topcon).

3. **Ausbringung:** Fahrt über alle Schläge, meist mit GPS-Lenksystem und automatischer Teilbreitenschaltung (Section Control). Variable Ausbringmengen per Karte (TC-GEO) werden nur genutzt, wenn eine Applikationskarte vorliegt — und die muss in einem vom Terminal lesbaren Format importiert werden.

4. **Dokumentation (gesetzliche Pflicht):** Unmittelbar nach dem Spritzgang oder spätestens innerhalb von 3 Werktagen muss der Landwirt das Anwendungsprotokoll nach §67 PflSchG ausfüllen. **Ab 2026 gelten verschärfte Anforderungen** (siehe Check D). Dies geschieht heute meist in der Ackerschlagkartei (365FarmNet/CLAAS Connect, NEXT Farming, Bayer xarvio Field Manager, Auguron, eigene Excel-Tabellen).

### Digitale Tools im Einsatz

Auf 65-Hektar-Betrieben sind folgende Tools realistisch verbreitet:

- **Ackerschlagkartei/FMIS:** 365FarmNet (läuft Ende November 2026 aus, Nachfolger CLAAS Connect), NEXT Farming, agri-Con, Bayer xarvio. Viele Kleinbetriebe nutzen noch Excel oder Papier.
- **Wetterdaten:** Syngenta Spritzwetter, proPlant, Sencrop, DWD-App.
- **Pflanzenschutzberatung:** ISIP-Warndienst (kostenlos, bundesweit), regionale Landwirtschaftskammern.
- **Precision-Farming-Plattformen:** Auf 65-Hektar-Betrieben sehr selten. Die Adoptionsrate von Precision Farming liegt bei Betrieben unter 100 Hektar bei circa 9 %.

### Gesetzliche Pflichten im Überblick

| Pflicht | Rechtsgrundlage | Stand 2026 |
|---|---|---|
| Anwendungsprotokoll (wer, was, wo, wann, Menge) | §67 PflSchG / EU-VO 1107/2009 Art. 67 | Pflicht seit 2011, ab 2026 erweitert |
| Neue Felder ab 2026: EPPO-Code, BBCH-Stadium, Georeferenzierung (FLIK oder GPS) | Durchführungsverordnung (EU) 2023/564 | Gilt ab 01.01.2026 |
| Elektronisch/maschinenlesbar | EU-VO 2023/564 | Pflicht ab 01.01.2027 (um 1 Jahr verschoben) |
| Cross-Compliance / Konditionalität | GAP-Reform 2023, AgrarZahlVerpflV | Kontrolle im Rahmen der Direktzahlungen |
| Sachkundenachweis | §9 PflSchG | Pflicht für alle beruflichen Verwender |

Aufzeichnungen müssen **mindestens 3 Jahre** aufbewahrt werden. Verstöße können zu Kürzungen der GAP-Direktzahlungen führen.

---

## Check A — Exportformat (Shapefile/ISOBUS): Passt es zu echten Feldspritzgeräten?

**PROBLEM:** AgroLens exportiert ein ESRI Shapefile (.shp/.dbf/.prj/.shx) in WGS84 und nennt es "ISOBUS-kompatibel". Das ist technisch unvollständig und in der Praxis problematisch.

**REALITÄT:**
ISOBUS-Terminals (ISO 11783 Task Controller) lesen keine Shapefiles direkt. Der Standard für Applikationskarten in der Landmaschinen-Praxis ist das **ISO 11783-10 Task Data (TASKDATA.XML)**-Format, nicht Shapefile. Shapefile ist ein GIS-Format, das am PC in Precision-Farming-Software (z.B. NEXT Farming, agri-Con, John Deere Operations Center) geöffnet und dort in das gerätelesbare Format konvertiert werden muss. Einige Terminals (John Deere GreenStar 3) können Shapefiles direkt importieren, aber das ist herstellerspezifisch und keine ISOBUS-Norm.

Der praktische Workflow heute:
1. Landwirt öffnet Shapefile in FMIS-Software (PC/Web)
2. FMIS konvertiert in TASKDATA.XML
3. TASKDATA.XML wird auf USB-Stick geladen und am Terminal eingelesen — oder direkt per ISOBUS-WiFi/4G übertragen (neuere Geräte)

Für einen 65-Hektar-Betrieb ohne dediziertes Precision-Farming-Setup bedeutet das: Er kann das AgroLens-Shapefile nicht direkt an der Spritze verwenden. Er braucht einen Zwischenschritt in Software, die er möglicherweise nicht hat.

**VORSCHLAG:**

1. Export in drei Formaten anbieten: (a) Shapefile für GIS-Nutzer und FMIS-Import, (b) **ISO 11783-10 TASKDATA.XML** als direkter ISOBUS-Export, (c) ein herstellerspezifisches Format nach Bedarf (John Deere, CNH).
2. In der Benutzeroberfläche einen klaren Hinweis zeigen: "Für direkte Verwendung an ISOBUS-Terminalen TASKDATA.XML herunterladen. Das Shapefile eignet sich für den Import in 365FarmNet/CLAAS Connect, NEXT Farming oder agri-Con."
3. Eine Partnerschaft mit einer FMIS-Plattform anstreben (z.B. NEXT Farming API), um den Konversionschritt für den Landwirt zu eliminieren. Priorität: hoch — ohne diese Integration ist der letzte Meter zur Spritze nicht überbrückt.

---

## Check B — 10-Tage-Composite-Rhythmus: Realistisch für Spritzzeitfenster?

**PROBLEM:** Das System produziert alle 10 Tage ein neues Vegetationsindex-Composite als Basis für Empfehlungen. Dieser Rhythmus ist für die operative Spritzentscheidung zu langsam.

**REALITÄT:**
Pflanzenschutzzeitfenster im deutschen Ackerbau sind eng und werden von schnell wechselnden Faktoren gesteuert:

- **Fungizide in Getreide (z.B. Septoria, Gelbrost):** Entscheidungsfenster beträgt oft 3–7 Tage nach dem Warndienstaufruf. Der Schaderreger-Befallsdruck kann sich innerhalb einer Woche dramatisch verändern.
- **Herbizide im Frühjahr:** Abhängig vom Unkraut-Entwicklungsstadium; das optimale Zeitfenster für viele Mittel liegt bei 2–4 Blattstadien — oft ein Fenster von 7–10 Tagen.
- **Insektizide (z.B. Rapsglanzkäfer, Blattläuse):** Befallsschwellen können innerhalb von 2–3 Tagen überschritten werden.

Ein 10-Tage-Composite aus Sentinel-2 sagt mir, **wo** Stress vorlag — aber nicht **ob heute** gespritzt werden soll. Außerdem kann ein 10-Tage-Composite durch Bewölkung aus Daten von vor 14–21 Tagen bestehen, wenn keine wolkenfreien Szenen verfügbar waren (in Norddeutschland realistisch in April/Mai). Dann ist das "aktuelle" Bild real bereits 3 Wochen alt — für eine operative Spritzentscheidung wertlos.

Die Kernverwirrung: AgroLens positioniert VRA-Karten als Input für den Spritzgang, aber der Spritzgang-Zeitpunkt wird durch andere Signale bestimmt (Warndienst, Befallsschwellen, Wetter). Das Composite gibt die räumliche Verteilung des Drucks, aber keine zeitliche Dringlichkeit.

**VORSCHLAG:**

1. Das Composite klar **repositionieren**: Es zeigt "historische Stressmuster als Grundlage für räumliche Dosierungs-Zonen" — nicht "Entscheidung ob und wann gespritzt werden soll". Diesen Unterschied im UI explizit kommunizieren.
2. Für den Zeitpunkt-Aspekt: Integration von Wetterdaten (z.B. DWD-API, kostenfrei) und Warndienstdaten (ISIP-API, prüfen ob verfügbar) als ergänzenden Layer. Dann kann AgroLens sagen: "Warndienst meldet erhöhten Septoria-Druck in Ihrer Region — hier ist Ihre VRA-Karte für die bereits geplante Behandlung."
3. Das 10-Tage-Composite beibehalten, aber einen "Vertrauensindikator" anzeigen: Datum der jüngsten genutzten Szene + Prozent-gültige-Pixel. Wenn die jüngste Szene älter als 14 Tage ist, automatisch auf "Uniform-Rate empfohlen" schalten.
4. Für Betriebe mit höherem Budget: Planet Labs 3m Daily als Premium-Add-on für aktuelle Einschätzungen (bereits im CEO-Dokument erwähnt — schnell umsetzen).

---

## Check C — 3-Zonen-Modell (Low/Medium/High): Deckt es den echten Bedarf ab?

**PROBLEM:** Das k-Means-Clustering in 3 Zonen vereinfacht die Realität stark. Für viele Anwendungsfälle ist das ausreichend — für einige kritisch ist es nicht ausreichend.

**REALITÄT:**
In der Praxis unterscheidet der Landwirt und sein Berater bei Pflanzenschutz nach **Anwendungsart und Wirkungsmechanismus:**

- **Fungizide:** Zonenbasierte Reduktion macht Sinn. Aber die Dosierungs-Spreizung von 0.6x bis 1.3x (wie im MVP) ist agrarwissenschaftlich grenzwertig. Fungizid-Aufwandmengen haben häufig eine **Mindestaufwandmenge aus der Zulassung** (z.B. "nicht unter 0,5 l/ha"). Eine 0.6x-Reduktion auf Basis von NDVI-Stress-Zonen ohne Kenntnis des tatsächlichen Befalls und der Zulassungsaufwandmenge kann die gesetzliche Minimalaufwandmenge unterschreiten — das ist ein **Haftungsrisiko**.
- **Herbizide:** Hier ist zonenbasierte Ausbringung am sinnvollsten (Unkrautdruck ist räumlich sehr variabel), aber NDVI/NDRE misst keinen Unkrautdruck direkt — es misst Kulturpflanzenstress. Ein niedriger NDVI bedeutet nicht zwingend hoher Unkrautbesatz; er kann auch auf Bodenverdichtung, Nährstoffmangel oder Trockenstress hinweisen. 3 undifferenzierte Zonen können hier zu Fehlapplikationen führen.
- **Insektizide:** Zonenbasierte Ausbringung ist bei mobilen Insekten (Blattläuse, Rapsglanzkäfer) kaum sinnvoll, da Befallsschwerpunkte sich täglich verschieben. Die Multiplikatoren 0.5x bis 1.5x für Insektizide wirken in der Praxis wie eine Black Box für den Landwirt.

Außerdem: Für Betriebe mit geneigtem Gelände, heterogenen Böden oder ausgeprägten Feuchtigkeitsgradienten können 3 Zonen schlicht zu grob sein. Umgekehrt sind 3 Zonen für kleine Schläge (< 5 ha) oft zu kleinteilig — ein Schlag mit 2 ha besteht dann aus Zonen von je 0,7 ha, was keine sinnvolle Spritztechnologie auflöst.

**VORSCHLAG:**

1. **Agronomische Validierung der Multiplikatoren** mit einem Pflanzenbauberater (DLG, Landwirtschaftskammer) durchführen, bevor Phase 3 gebaut wird. Insbesondere prüfen: Welche Mittel haben Zulassungsaufwandmengen, die durch die 0.6x-Reduktion unterschritten werden könnten?
2. **Zonenzahl konfigurierbar machen:** 2, 3 oder 5 Zonen — der Landwirt oder Agronomist soll wählen können. Das ist eine kleine Änderung im Code (k=2 oder k=5 in k-Means), aber ein großer Unterschied für die Praxis.
3. **Disclaimer in der Applikation:** "Die Aufwandmengen müssen innerhalb der genehmigten Spanne der Zulassung liegen. Bitte prüfen Sie die Mindest- und Höchstaufwandmenge des Mittels." Diese Aussage muss **im Export-PDF stehen** und im Dashboard sichtbar sein.
4. **Für Herbizide:** Einen separaten Weed-Mapping-Hinweis einfügen, dass NDVI-basierte Zonen Kulturpflanzenstress messen, nicht Unkrautdruck. Weed Pressure Mapping sollte als separate Funktion in V1 klar markiert werden.
5. **Minimale Zonengröße auf 1 ha erhöhen** (aktuell 0,5 ha) für Schläge unter 10 ha. Bei kleineren Zonen hat die Spritze keine Zeit, die Dosierung anzupassen (Reaktionszeit der Mengensteuerung beachten).

---

## Check D — Gesetzliche Dokumentationspflicht: Fehlt sie im Produkt?

**PROBLEM:** AgroLens hat im MVP **keine einzige Zeile** zum gesetzlich vorgeschriebenen Pflanzenschutz-Anwendungsprotokoll nach §67 PflSchG. Das ist die gravierendste Lücke im aktuellen Produktkonzept.

**REALITÄT:**
Ab dem 1. Januar 2026 müssen alle professionellen Verwender (also alle Landwirte) bei jeder Pflanzenschutzmittelanwendung folgende Angaben aufzeichnen und **mindestens 3 Jahre aufbewahren:**

| Pflichtfeld (ab 2026) | Status in AgroLens |
|---|---|
| Datum und ggf. Uhrzeit der Anwendung | Fehlt — MVP hat nur "manuelle Nutzungsprotokoll-Einträge" |
| Feldname + Georeferenzierung (FLIK-Nr. oder GPS-Punkt) | Feldgeometrie vorhanden, FLIK-Nr. fehlt |
| Kulturpflanze mit EPPO-Code | Crop-Type-Dropdown ohne EPPO-Code |
| BBCH-Stadium der Kultur bei Anwendung | Fehlt komplett |
| Schaderreger/Zielorganismus mit EPPO-Code | Fehlt komplett |
| Produktname + Zulassungsnummer des PSM | Fehlt — kein PSM-Datenbankzugang |
| Tatsächlich ausgebrachte Aufwandmenge (L/ha oder kg/ha) | Fehlt — nur "base rate" als Input |
| Art der Anwendung (Agrarfläche, Saatgut etc.) | Fehlt |
| Behandelte Fläche in Hektar | Vorhanden (Feldgeometrie) |

Ab **01.01.2027** muss die Dokumentation **elektronisch und maschinenlesbar** erfolgen. Das bedeutet: Der Landwirt braucht eine Software, die das rechtskonform erledigt. AgroLens hat alle Voraussetzungen dafür (Feldgeometrien, Prescriptions, Datenbankstruktur) — nutzt sie aber nicht.

Diese Lücke ist strategisch doppelt fatal: Erstens, weil der Landwirt ohnehin eine Lösung für die Dokumentation braucht und sie heute woanders beschafft (FMIS, Ackerschlagkartei). Zweitens, weil AgroLens als "EU regulatory compliance built in from day one" positioniert ist (CEO-Dokument) — aber die einzige Compliance-Pflicht, die zu 100% jeden deutschen Landwirt betrifft, fehlt im Produkt.

**VORSCHLAG:**

1. **Sofort:** Einen "Spritzgang-Erfassungs"-Screen im MVP ergänzen, der nach der Prescription-Erstellung die Pflichtfelder abfragt: PSM-Name (Freitext + Zulassungsnummer), BBCH-Stadium (Dropdown), Schaderreger (Freitext), tatsächliche Aufwandmenge, Anwendungsdatum/Uhrzeit. Das ist kein großer Entwicklungsaufwand.
2. **FLIK-Nummer** als optionales Feld im Feldprofil ergänzen (für InVeKoS-Verknüpfung). Georeferenzierung ist durch Feldgeometrie bereits gegeben.
3. **EPPO-Code-Lookup:** Entweder eigene Datenbank oder Link auf gd.eppo.int. EPPO-Codes müssen ab 2026 im Protokoll stehen.
4. **Export:** Das PDF-Bericht-Format erweitern, so dass es als rechtskonformes Anwendungsprotokoll nach §67 PflSchG exportiert werden kann. Das macht AgroLens zur einzigen Lösung, die Prescription-Map und Dokumentation in einem Schritt erledigt — ein erheblicher Mehrwert.
5. **DiPAgE-Kompatibilität:** Das BMEL arbeitet 2026 an DiPAgE (Digitale Pflanzenschutz-Anwendungsdaten-Erfassung) als kostenloser Bundeslösung. AgroLens sollte die DiPAgE-Schnittstelle implementieren, sobald sie verfügbar ist, um einen Datenexport dorthin zu ermöglichen. Das ist ein echter Mehrwert gegenüber reinen Papier-Lösungen.

---

## Check E — Preismodell (€8/ha/Jahr): Realistisch für 65-Hektar-Betriebe?

**PROBLEM:** Das blended ARPU von €8/ha/Jahr passt nicht zur Realität eines 65-Hektar-Betriebs. Der Starter-Plan kostet €49/Monat (€470/Jahr) für bis zu 100 ha — das entspricht **€7,23/ha/Jahr** bei 65 ha. Das ist der günstigste Plan.

**REALITÄT:**
Ein Betrieb mit 65 Hektar hat folgende ökonomische Rahmenbedingungen:
- Gesamter Pflanzenschutz-Mitteleinsatz (ohne Arbeit/Maschine): ca. **€60–100/ha/Jahr** für Ackerkulturen in Deutschland, also **€3.900–6.500 gesamt**.
- Mögliche Einsparung durch VRA (10–20% realistisch, bei optimalem Einsatz): **€6–20/ha = €390–1.300 gesamt**.
- Aber: Die Einsparung realisiert sich nur, wenn der Landwirt auch tatsächlich variabel ausbringt — was TC-GEO-fähige Hardware voraussetzt. Auf 65-Hektar-Betrieben ist das selten (Adoptionsrate < 9% für Precision Farming auf Betrieben unter 100 ha).
- AgroLens kostet €470/Jahr für einen 65-Hektar-Betrieb. Das sind **7,23% der möglichen Höchsteinsparung** — bei optimalem Setup. Bei einem Betrieb ohne VRA-Hardware ist die ROI-Rechnung noch ungünstiger.
- Zum Vergleich: 365FarmNet war für viele Nutzer **kostenlos** (Basisversion). CLAAS Connect wird ebenfalls Basisversion kostenlos anbieten. Der Wettbewerb für FMIS-Funktionen ist stark preisgedrückt.

Der CEO-Plan nennt als Primärzielgruppe **200–2.000 ha Betriebe**. Ein 65-Hektar-Betrieb liegt unterhalb dieser Schwelle. Das ist kein Fehler — aber es zeigt, dass Preis und Produktpositionierung für diese Betriebsgröße nicht validiert sind.

**VORSCHLAG:**

1. **Zielgruppenfokus schärfen:** Der Starter-Plan (€49/Monat, 100 ha) ist für 65-Hektar-Betriebe am Limit der Zahlungsbereitschaft. Für die MVP-Phase sollte das Team ehrlich entscheiden: Ist der Kleinbetrieb (< 100 ha) wirklich die Zielgruppe, oder sind es die 200–500 ha Betriebe des Farmer-Plans?
2. **Kostenloser Einstieg über Dokumentations-Feature:** Wenn AgroLens die Pflanzenschutz-Dokumentationspflicht (Check D) löst, rechtfertigt das einen separaten Einstiegspunkt: Eine kostenlose Basis-Doku-Version (ohne VRA-Maps) zieht auch Kleinbetriebe an, die dann auf den Paid-Plan upgraden, wenn sie VRA-fähige Hardware anschaffen.
3. **Genossenschafts-Modell:** Wenn Kooperativen die Software für ihre Mitglieder lizenzieren (Segment 3 im CEO-Dokument), können die Kosten auf €2–4/ha sinken — das wäre für Kleinbetriebe akzeptabel und für AgroLens trotzdem profitabel.
4. **ROI-Rechner im Onboarding:** Konkret zeigen: "Bei Ihren 65 ha und durchschnittlichem Fungizideinsatz von X l/ha können Sie ca. Y € pro Jahr sparen — bei einer Investition von €470 in AgroLens." Wenn der ROI unter 1:2 liegt (weniger als €940 Einsparung), sollte das System ehrlich sagen: "Für vollen Nutzen brauchen Sie TC-GEO-fähige Hardware."

---

## Integration in den realen Spritzgang: Wo passt AgroLens hinein?

Hier ist der ehrliche Befund, wo AgroLens sich in den Workflow integriert und wo nicht:

```
Realer Spritzgang eines deutschen Ackerbauers:

 [Schlag-  ] --> [Warndienst/ ] --> [Wetterfenster] --> [SPRITZGANG] --> [Dokumentation]
 [begehung ]     [Beratung    ]     [Syngenta-App ]     [Feldspritze]    [§67 PflSchG  ]
      |                |                                     ^                  ^
      |                |                                     |                  |
   AgroLens         AgroLens                           AgroLens VRA-       FEHLT in
   kann hier        kann hier                          Karte (ISOBUS/     AgroLens
   NDVI-Zonen       Druck-Trend                        TASKDATA)          (Check D)
   liefern          anzeigen
```

**AgroLens passt heute in den Workflow — aber nur als räumliches Entscheidungs-Support-Tool**, nicht als vollständiger Spritz-Assistent. Der Landwirt entscheidet weiterhin selbst (oder mit Berater), ob, was und wann gespritzt wird. AgroLens sagt ihm, wo er welche Menge anwenden soll, wenn er bereits spritzen will.

**Konkretes Automatisierungspotenzial:**

| Prozessschritt | Heute | Mit AgroLens (Potenzial) |
|---|---|---|
| Wo im Feld sind Stressherde? | Feldbegehung (zeitaufwändig) | Automatisch via NDVI-Dashboard |
| Wie viel in welcher Zone? | Einheitsmenge für ganzen Schlag | VRA-Karte aus Prescription Engine |
| VRA-Karte in die Spritze laden | Shapefile via FMIS konvertieren | Direkt TASKDATA.XML → USB oder Cloud |
| Protokoll ausfüllen | Manuelle Eingabe FMIS oder Papier | Automatisch aus Prescription-Daten (Check D) |
| Wirksamkeit nachverfolgen | Keine | NDVI-Vergleich vor/nach Behandlung |

Der letzte Punkt — **Before/After-NDVI-Vergleich pro Zone** — ist ein ungenutztes Feature mit echtem Mehrwert: Landwirt kann sehen, ob die Behandlung in der "High"-Zone tatsächlich gewirkt hat. Das fehlt komplett im aktuellen Produkt und wäre ein starker Retention-Treiber.

---

## Priorisierung: Was muss vor Phase 3 (Prescription Engine) geändert werden?

Phase 3 baut die Prescription Engine — das Herzstück des Produkts. Wenn diese Engine ohne die folgenden Korrekturen gebaut wird, wird sie an der Praxis vorbeientworfen sein. Hier ist die Muss-Liste, sortiert nach Priorität:

---

### PRIORITÄT 1 — Blockiert Phase 3 direkt

**1.1: Agronomische Validierung der Multiplikatoren (vor REQ-05)**

PROBLEM: Die Multiplikatoren (Fungizid Low=0.6x, High=1.3x etc.) wurden ohne agronomischen Fachexperten festgelegt.
REALITÄT: Zulassungen schreiben Mindestaufwandmengen vor. 0.6x kann illegal sein.
VORSCHLAG: Bevor Task 3.2 implementiert wird — einen Pflanzenbauberater (Landwirtschaftskammer oder unabhängiger Berater) beauftragen, die Multiplikatoren für die 5 Hauptkulturen und 3 Anwendungstypen zu validieren. Ergebnis: eine validierte Multiplikatoren-Tabelle mit Kultur/Mittelklasse-spezifischen Grenzen.

**1.2: TASKDATA.XML-Export zusätzlich zu Shapefile (Task 3.3)**

PROBLEM: Shapefile allein ist kein direktes ISOBUS-Format.
REALITÄT: Ohne TASKDATA.XML-Export kommt die Prescription-Karte nicht an die Spritze.
VORSCHLAG: In Task 3.3 neben Shapefile zwingend auch ISO 11783-10 TASKDATA.XML exportieren. Bibliothek: agroxml oder eigene Implementierung nach ISO-Standard. Ohne diesen Export ist Check A nicht bestanden.

---

### PRIORITÄT 2 — Muss vor dem ersten Pilot-Einsatz live sein

**2.1: Spritzgang-Dokumentationsmodul (neues Feature, vor Phase 4)**

PROBLEM: §67 PflSchG Dokumentation fehlt vollständig.
REALITÄT: Jeder Landwirt, der AgroLens nutzt, braucht trotzdem ein Anwendungsprotokoll. Er führt es aktuell woanders. AgroLens kann diese Funktion übernehmen und damit einen echten Lock-in erzeugen.
VORSCHLAG: Einfaches Formular nach Prescription-Generierung: PSM-Name, Zulassungsnummer, BBCH-Stadium, Schaderreger, tatsächliche Aufwandmenge, Datum/Uhrzeit. Export als PDF-Anwendungsprotokoll. Datenbankmodell: ca. 1 Tag Aufwand. UI: ca. 2 Tage. Sehr gutes ROI-Verhältnis für den Entwicklungsaufwand.

**2.2: FLIK-Nummer und EPPO-Code in Feldprofil**

PROBLEM: Georeferenzierung per FLIK und EPPO-Codes sind ab 2026 Pflicht im Protokoll.
REALITÄT: Ohne FLIK-Verknüpfung ist das AgroLens-Protokoll nicht rechtskonform.
VORSCHLAG: FLIK-Nummern-Feld im Field-Model ergänzen (Task 1.2 nachpatchen). EPPO-Code-Lookup-Tabelle für Kulturen und häufigste Schaderreger integrieren. Beides ist Datenbankarbeit, kein Algorithmus.

---

### PRIORITÄT 3 — Wichtig für Marktfähigkeit, aber nicht Phase-3-Blocker

**3.1: Zonengröße und -anzahl konfigurierbar**

PROBLEM: k=3 fest codiert, Mindestzonengröße 0,5 ha — beides suboptimal.
REALITÄT: Kleine Schläge brauchen weniger Zonen, große Schläge mit heterogenen Böden brauchen mehr.
VORSCHLAG: k=2, 3 oder 5 wählbar (Dropdown in UI). Mindestzonengröße auf 1 ha für Schläge < 10 ha automatisch erhöhen. Vor Phase 3: k als konfigurierbaren Parameter in Task 3.1 implementieren — das ist eine einzeilige Änderung im Code.

**3.2: Before/After-NDVI-Analyse pro Zone**

PROBLEM: Wirksamkeit der Behandlung ist nach dem Spritzgang unsichtbar.
REALITÄT: Dieses Feature hätte hohen Mehrwert für Retention und ROI-Nachweis (CEO-Goal 5).
VORSCHLAG: Nach einer dokumentierten Behandlung automatisch das nächste NDVI-Composite mit dem Pre-Treatment-Composite vergleichen und eine "Behandlungs-Wirksamkeit"-Ansicht im Dashboard zeigen. Dieses Feature direkt in Phase 3/4 einplanen.

**3.3: Vertrauensindikator für Composite-Aktualität**

PROBLEM: Kein Signal, wenn das Composite veraltet ist.
REALITÄT: Landwirt muss wissen, ob die Karte auf Daten von gestern oder vor 3 Wochen basiert.
VORSCHLAG: Im Dashboard und im Shapefile/PDF-Export immer anzeigen: "Jüngste Satellitenszene: [Datum]. Gültige Pixel: [X]%. Qualität: [Gut/Mittel/Schlecht]." Bei Qualität "Schlecht" automatisch auf "Einheitliche Aufwandmenge empfohlen" schalten.

---

## Zusammenfassung: Kritische Punkte auf einen Blick

| Check | Bewertung | Blockiert Phase 3? |
|---|---|---|
| A: Exportformat (Shapefile/ISOBUS) | Unvollständig — Shapefile ohne TASKDATA.XML kommt nicht an die Spritze | Ja |
| B: 10-Tage-Composite-Rhythmus | Zu langsam für operative Entscheidungen, aber richtig für räumliche Zonen | Teilweise — Repositionierung nötig |
| C: 3-Zonen-Modell | Agronomisch nicht validiert, Haftungsrisiko bei Mindestaufwandmengen | Ja |
| D: Dokumentationspflicht | Komplett fehlend — größte strategische Lücke | Nein (Phase 3 direkt), aber vor Pilot nötig |
| E: Preismodell €8/ha | Grenzwertig für < 100 ha Betriebe ohne VRA-Hardware | Nein, aber für Go-to-Market relevant |

**Fazit:** Phase 3 kann starten, aber nur wenn Punkte 1.1 (Multiplikatoren-Validierung) und 1.2 (TASKDATA.XML-Export) vorher gelöst werden. Punkt 2.1 (Dokumentationsmodul) sollte parallel zu Phase 3 entwickelt werden, weil er keine Phase-3-Abhängigkeiten hat und beim ersten Piloten direkt gebraucht wird.

---

*Quellen und Recherche-Grundlage: Landwirtschaftskammer Niedersachsen (Dokumentationspflicht 2026), Bayerischer Bauernverband, ISIP, LfL Bayern, myagrar.de, pflanzenschutzdienst-niedersachsen.de, agrarheute.com, CLAAS/365FarmNet-Abschaltungsankündigung, BMEL DiPAgE, DLG-ISOBUS-Tests, geo-konzept.de (TC-GEO), Durchführungsverordnung (EU) 2023/564.*
