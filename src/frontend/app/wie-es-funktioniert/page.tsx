/**
 * AgroLens — "So funktioniert's" informational page.
 *
 * Public server component (no auth required, no client-side state).
 * Explains the AgroLens satellite analysis pipeline at a farmer-accessible level.
 * German-language throughout; no fake statistics or unverified claims.
 *
 * Sections:
 *   Nav → Page header → Five explanation steps → FAQ → Dark CTA → Footer
 */

import type { Metadata } from "next";
import Link from "next/link";

// ---------------------------------------------------------------------------
// SEO metadata
// ---------------------------------------------------------------------------

export const metadata: Metadata = {
  title: "So funktioniert AgroLens — Satellitenanalyse für Landwirte",
  description:
    "Wie AgroLens Sentinel-2-Satellitendaten in präzise Ausbringungskarten verwandelt — verständlich erklärt für Landwirte, nicht für Informatiker.",
  openGraph: {
    title: "So funktioniert AgroLens",
    description:
      "Satellitendaten, verständlich erklärt — für Landwirte, nicht für Informatiker.",
    type: "website",
  },
};

// ---------------------------------------------------------------------------
// Shared inline SVG components — no external icon libraries
// ---------------------------------------------------------------------------

function LogoIcon() {
  return (
    <svg
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden="true"
      className="h-full w-full"
    >
      <rect width="32" height="32" rx="8" fill="#16a34a" />
      <path
        d="M8 22 C8 14 14 8 22 8"
        stroke="white"
        strokeWidth="2.5"
        strokeLinecap="round"
        fill="none"
        opacity="0.5"
      />
      <path
        d="M8 22 C8 17 12 12 18 10"
        stroke="white"
        strokeWidth="2.5"
        strokeLinecap="round"
        fill="none"
        opacity="0.75"
      />
      <circle cx="8" cy="22" r="2.5" fill="white" />
      <line
        x1="14"
        y1="16"
        x2="20"
        y2="10"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
        opacity="0.9"
      />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
      className="h-5 w-5 flex-shrink-0 text-agrolens-600"
    >
      <path
        fillRule="evenodd"
        d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function XMarkIcon() {
  return (
    <svg
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
      className="h-5 w-5 flex-shrink-0 text-red-400"
    >
      <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Step-specific SVG illustrations
// ---------------------------------------------------------------------------

/** Step 01 — Satellite illustration */
function SatelliteIllustration() {
  return (
    <svg
      viewBox="0 0 400 260"
      className="w-full h-auto"
      aria-hidden="true"
      role="presentation"
    >
      <rect width="400" height="260" fill="#0a1f0f" rx="8" />
      {/* Orbit arc */}
      <ellipse
        cx="200"
        cy="30"
        rx="170"
        ry="90"
        fill="none"
        stroke="#22c55e"
        strokeWidth="1"
        strokeDasharray="5,7"
        opacity="0.35"
      />
      {/* Satellite body */}
      <g transform="translate(355, 8)">
        <rect x="0" y="5" width="20" height="12" rx="2" fill="#86efac" opacity="0.9" />
        {/* Solar panels */}
        <rect x="-16" y="8" width="12" height="5" rx="1" fill="#4ade80" opacity="0.75" />
        <rect x="20" y="8" width="12" height="5" rx="1" fill="#4ade80" opacity="0.75" />
        {/* Panel cells */}
        <line x1="-10" y1="8" x2="-10" y2="13" stroke="#052e16" strokeWidth="0.8" opacity="0.6" />
        <line x1="-6" y1="8" x2="-6" y2="13" stroke="#052e16" strokeWidth="0.8" opacity="0.6" />
        <line x1="26" y1="8" x2="26" y2="13" stroke="#052e16" strokeWidth="0.8" opacity="0.6" />
        <line x1="30" y1="8" x2="30" y2="13" stroke="#052e16" strokeWidth="0.8" opacity="0.6" />
      </g>
      {/* Scan beam from satellite to field */}
      <polygon points="364,18 120,170 220,170" fill="#22c55e" opacity="0.04" />
      <line x1="364" y1="18" x2="120" y2="170" stroke="#22c55e" strokeWidth="1" opacity="0.25" strokeDasharray="4,6" />
      <line x1="364" y1="18" x2="220" y2="170" stroke="#22c55e" strokeWidth="1" opacity="0.25" strokeDasharray="4,6" />
      {/* Field on the ground */}
      <polygon points="80,155 280,145 300,230 70,235" fill="#16a34a" opacity="0.55" />
      <polygon points="280,145 370,160 360,230 300,230" fill="#f59e0b" opacity="0.45" />
      {/* IR wavelength label */}
      <rect x="20" y="100" width="130" height="32" rx="6" fill="#052e16" opacity="0.85" />
      <text x="35" y="116" fill="#86efac" fontSize="9" fontFamily="monospace">Sichtbares Licht</text>
      <text x="35" y="128" fill="#4ade80" fontSize="9" fontFamily="monospace">+ Nahes Infrarot (NIR)</text>
      {/* EU / Copernicus badge */}
      <rect x="290" y="195" width="100" height="36" rx="6" fill="#1e3a5f" opacity="0.9" />
      <text x="340" y="209" textAnchor="middle" fill="#93c5fd" fontSize="8" fontFamily="monospace" fontWeight="600">Copernicus</text>
      <text x="340" y="221" textAnchor="middle" fill="#93c5fd" fontSize="7" fontFamily="monospace">EU-Programm · kostenlos</text>
      <text x="340" y="230" textAnchor="middle" fill="#60a5fa" fontSize="7" fontFamily="monospace">Sentinel-2</text>
    </svg>
  );
}

/** Step 02 — NDVI gradient bar illustration */
function NdviBarIllustration() {
  return (
    <svg
      viewBox="0 0 400 200"
      className="w-full h-auto"
      aria-hidden="true"
      role="presentation"
    >
      <rect width="400" height="200" fill="#f0fdf4" rx="8" />
      {/* Gradient bar */}
      <defs>
        <linearGradient id="ndviGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#ef4444" />
          <stop offset="30%" stopColor="#f97316" />
          <stop offset="55%" stopColor="#f59e0b" />
          <stop offset="75%" stopColor="#84cc16" />
          <stop offset="100%" stopColor="#16a34a" />
        </linearGradient>
      </defs>
      <rect x="40" y="60" width="320" height="40" rx="6" fill="url(#ndviGrad)" />
      {/* Value markers on bar */}
      <line x1="40" y1="100" x2="40" y2="112" stroke="#374151" strokeWidth="1.5" />
      <text x="40" y="126" textAnchor="middle" fill="#374151" fontSize="10" fontFamily="monospace">−1</text>
      <line x1="200" y1="100" x2="200" y2="112" stroke="#374151" strokeWidth="1.5" />
      <text x="200" y="126" textAnchor="middle" fill="#374151" fontSize="10" fontFamily="monospace">0</text>
      <line x1="280" y1="100" x2="280" y2="112" stroke="#374151" strokeWidth="1.5" />
      <text x="280" y="126" textAnchor="middle" fill="#374151" fontSize="10" fontFamily="monospace">0.5</text>
      <line x1="360" y1="100" x2="360" y2="112" stroke="#374151" strokeWidth="1.5" />
      <text x="360" y="126" textAnchor="middle" fill="#374151" fontSize="10" fontFamily="monospace">+1</text>
      {/* Labels above bar */}
      <text x="80" y="48" textAnchor="middle" fill="#dc2626" fontSize="11" fontFamily="sans-serif" fontWeight="600">Stress / kahl</text>
      <text x="200" y="48" textAnchor="middle" fill="#d97706" fontSize="11" fontFamily="sans-serif" fontWeight="600">Mittel</text>
      <text x="330" y="48" textAnchor="middle" fill="#16a34a" fontSize="11" fontFamily="sans-serif" fontWeight="600">Gesund</text>
      {/* Example pointer — healthy crop */}
      <line x1="316" y1="60" x2="316" y2="30" stroke="#16a34a" strokeWidth="1.5" strokeDasharray="3,3" />
      <circle cx="316" cy="24" r="5" fill="#16a34a" />
      <text x="316" y="14" textAnchor="middle" fill="#15803d" fontSize="9" fontFamily="monospace">0.72 (Weizen)</text>
      {/* Example pointer — stress */}
      <line x1="152" y1="100" x2="152" y2="150" stroke="#f59e0b" strokeWidth="1.5" strokeDasharray="3,3" />
      <circle cx="152" cy="156" r="5" fill="#f59e0b" />
      <text x="152" y="172" textAnchor="middle" fill="#92400e" fontSize="9" fontFamily="monospace">0.34 (Stress)</text>
      {/* Pixel resolution note */}
      <rect x="20" y="178" width="360" height="16" rx="4" fill="#d1fae5" opacity="0.7" />
      <text x="200" y="190" textAnchor="middle" fill="#166534" fontSize="9" fontFamily="monospace">Berechnet pro 10 × 10 m Pixel — für jede Stelle auf Ihrem Feld</text>
    </svg>
  );
}

/** Step 03 — Zone clustering map illustration */
function ZoneMapIllustration() {
  return (
    <svg
      viewBox="0 0 400 260"
      className="w-full h-auto"
      aria-hidden="true"
      role="presentation"
    >
      <rect width="400" height="260" fill="#0a1f0f" rx="8" />
      {/* Zone A — healthy, dark green */}
      <polygon points="50,50 190,40 210,160 40,170" fill="#16a34a" opacity="0.8" />
      {/* Zone B — mild stress, amber */}
      <polygon points="190,40 330,55 320,165 210,160" fill="#f59e0b" opacity="0.7" />
      {/* Zone C — stress, red */}
      <polygon points="330,55 380,70 375,175 320,165" fill="#ef4444" opacity="0.6" />
      {/* Zone labels */}
      <rect x="65" y="92" width="100" height="24" rx="4" fill="#052e16" opacity="0.9" />
      <text x="115" y="108" textAnchor="middle" fill="#86efac" fontSize="10" fontFamily="monospace">Zone A · NDVI 0.71</text>
      <rect x="205" y="92" width="100" height="24" rx="4" fill="#052e16" opacity="0.9" />
      <text x="255" y="108" textAnchor="middle" fill="#fde047" fontSize="10" fontFamily="monospace">Zone B · NDVI 0.47</text>
      <rect x="320" y="92" width="60" height="24" rx="4" fill="#052e16" opacity="0.9" />
      <text x="350" y="108" textAnchor="middle" fill="#fca5a5" fontSize="10" fontFamily="monospace">Zone C</text>
      {/* K-Means label */}
      <rect x="30" y="188" width="200" height="30" rx="6" fill="#1e3a5f" opacity="0.85" />
      <text x="130" y="203" textAnchor="middle" fill="#93c5fd" fontSize="9" fontFamily="monospace">K-Means-Clustering</text>
      <text x="130" y="214" textAnchor="middle" fill="#60a5fa" fontSize="8" fontFamily="monospace">Automatisch · keine Begehung nötig</text>
      {/* Min zone size note */}
      <rect x="240" y="188" width="150" height="30" rx="6" fill="#14532d" opacity="0.85" />
      <text x="315" y="203" textAnchor="middle" fill="#86efac" fontSize="8" fontFamily="monospace">Mindestzonen &gt; 0,5 ha</text>
      <text x="315" y="214" textAnchor="middle" fill="#4ade80" fontSize="8" fontFamily="monospace">werden automatisch zusammengeführt</text>
    </svg>
  );
}

/** Step 04 — Export formats illustration */
function ExportIllustration() {
  return (
    <svg
      viewBox="0 0 400 260"
      className="w-full h-auto"
      aria-hidden="true"
      role="presentation"
    >
      <rect width="400" height="260" fill="#f8fafc" rx="8" />
      {/* USB stick icon */}
      <rect x="170" y="20" width="60" height="30" rx="4" fill="#374151" />
      <rect x="180" y="50" width="40" height="15" rx="0" fill="#6b7280" />
      <rect x="188" y="25" width="8" height="20" rx="1" fill="#9ca3af" />
      <rect x="202" y="25" width="8" height="20" rx="1" fill="#9ca3af" />
      <text x="200" y="80" textAnchor="middle" fill="#374151" fontSize="9" fontFamily="sans-serif">USB-Stick</text>
      {/* Arrow down */}
      <line x1="200" y1="88" x2="200" y2="108" stroke="#9ca3af" strokeWidth="1.5" />
      <polygon points="195,106 205,106 200,114" fill="#9ca3af" />
      {/* ISOBUS terminal */}
      <rect x="100" y="120" width="200" height="50" rx="6" fill="#1e293b" />
      <rect x="110" y="128" width="180" height="34" rx="3" fill="#0f172a" />
      <text x="200" y="143" textAnchor="middle" fill="#22c55e" fontSize="9" fontFamily="monospace">ISOBUS-Terminal</text>
      <text x="200" y="155" textAnchor="middle" fill="#4ade80" fontSize="8" fontFamily="monospace">Applikationskarte geladen</text>
      {/* File chips at bottom */}
      <rect x="30" y="188" width="80" height="32" rx="6" fill="#dcfce7" stroke="#bbf7d0" strokeWidth="1" />
      <text x="70" y="201" textAnchor="middle" fill="#166534" fontSize="9" fontFamily="monospace" fontWeight="700">TASKDATA</text>
      <text x="70" y="213" textAnchor="middle" fill="#166534" fontSize="8" fontFamily="monospace">.XML · ISOBUS</text>
      <rect x="125" y="188" width="70" height="32" rx="6" fill="#dcfce7" stroke="#bbf7d0" strokeWidth="1" />
      <text x="160" y="201" textAnchor="middle" fill="#166534" fontSize="9" fontFamily="monospace" fontWeight="700">.SHP</text>
      <text x="160" y="213" textAnchor="middle" fill="#166534" fontSize="8" fontFamily="monospace">Shapefile</text>
      <rect x="205" y="188" width="65" height="32" rx="6" fill="#fef9c3" stroke="#fef08a" strokeWidth="1" />
      <text x="237" y="201" textAnchor="middle" fill="#854d0e" fontSize="9" fontFamily="monospace" fontWeight="700">.PDF</text>
      <text x="237" y="213" textAnchor="middle" fill="#854d0e" fontSize="8" fontFamily="monospace">Bericht</text>
      <rect x="280" y="188" width="90" height="32" rx="6" fill="#fef3c7" stroke="#fde68a" strokeWidth="1" />
      <text x="325" y="201" textAnchor="middle" fill="#92400e" fontSize="8" fontFamily="monospace" fontWeight="700">§67 PflSchG</text>
      <text x="325" y="213" textAnchor="middle" fill="#92400e" fontSize="8" fontFamily="monospace">Protokoll</text>
      {/* Disclaimer stripe */}
      <rect x="30" y="228" width="340" height="20" rx="4" fill="#fef9c3" opacity="0.85" />
      <text x="200" y="241" textAnchor="middle" fill="#854d0e" fontSize="7.5" fontFamily="sans-serif">Alle Exporte enthalten den agronomischen Disclaimer</text>
    </svg>
  );
}

/** Step 05 — Requirements checklist illustration */
function RequirementsIllustration() {
  return (
    <svg
      viewBox="0 0 400 220"
      className="w-full h-auto"
      aria-hidden="true"
      role="presentation"
    >
      <rect width="400" height="220" fill="#f0fdf4" rx="8" />
      {/* Need list */}
      <text x="30" y="30" fill="#15803d" fontSize="11" fontFamily="sans-serif" fontWeight="700">Sie brauchen:</text>
      {[
        "Computer, Tablet oder Smartphone",
        "Feldgrenzen (Shapefile, GeoJSON oder Maus)",
        "Optional: FLIK-Nummern",
        "Optional: ISOBUS-Feldspritze für Auto-Export",
      ].map((item, i) => (
        <g key={item} transform={`translate(30, ${48 + i * 22})`}>
          <circle cx="6" cy="0" r="5" fill="#16a34a" opacity="0.9" />
          <line x1="3.5" y1="0.2" x2="5.5" y2="2.5" stroke="white" strokeWidth="1.2" strokeLinecap="round" />
          <line x1="5.5" y1="2.5" x2="9" y2="-2" stroke="white" strokeWidth="1.2" strokeLinecap="round" />
          <text x="18" y="4" fill="#374151" fontSize="10" fontFamily="sans-serif">{item}</text>
        </g>
      ))}
      {/* Divider */}
      <line x1="30" y1="148" x2="370" y2="148" stroke="#bbf7d0" strokeWidth="1" />
      {/* Not needed list */}
      <text x="30" y="168" fill="#dc2626" fontSize="11" fontFamily="sans-serif" fontWeight="700">Sie brauchen NICHT:</text>
      {[
        "Eigene Sensoren oder Hardware",
        "Technisches Vorwissen",
      ].map((item, i) => (
        <g key={item} transform={`translate(30, ${186 + i * 22})`}>
          <circle cx="6" cy="0" r="5" fill="#ef4444" opacity="0.7" />
          <line x1="3.5" y1="-2" x2="8.5" y2="2.5" stroke="white" strokeWidth="1.2" strokeLinecap="round" />
          <line x1="8.5" y1="-2" x2="3.5" y2="2.5" stroke="white" strokeWidth="1.2" strokeLinecap="round" />
          <text x="18" y="4" fill="#374151" fontSize="10" fontFamily="sans-serif">{item}</text>
        </g>
      ))}
    </svg>
  );
}

// ---------------------------------------------------------------------------
// FAQ data
// ---------------------------------------------------------------------------

interface FaqItem {
  question: string;
  answer: string;
}

const faqItems: FaqItem[] = [
  {
    question: "Wie oft wird mein Feld analysiert?",
    answer:
      "Sobald Sentinel-2 eine wolkenfreie Aufnahme liefert — in der Regel alle 5 bis 10 Tage. Bei starker Bewölkung kann es länger dauern. AgroLens zeigt immer das Datum der letzten Aufnahme.",
  },
  {
    question: "Funktioniert das auch für kleine Betriebe?",
    answer:
      "Ja. Der kostenlose Basis-Plan erlaubt ein Feld bis zu 15 ha. Für kleine und mittlere Betriebe gibt es den Starter-Plan ab 49 €/Monat.",
  },
  {
    question: "Was passiert, wenn Wolken das Bild verdecken?",
    answer:
      "AgroLens erkennt Wolken automatisch und wartet auf das nächste wolkenfreie Bild. Bedeckte Pixel werden aus der Analyse ausgeschlossen.",
  },
  {
    question: "Muss ich an meiner Maschine etwas umrüsten?",
    answer:
      "Nein. ISOBUS ist ein internationaler Standard, den die meisten modernen Feldspritzen und Traktoren bereits unterstützen. Wenn Ihre Maschine ISOBUS hat, können Sie die Datei einfach per USB-Stick übertragen. Ältere Maschinen nutzen die PDF-Variante.",
  },
  {
    question: "Sind meine Felddaten sicher?",
    answer:
      "Ja. Alle Daten werden ausschließlich auf EU-Servern gespeichert (DSGVO-konform). Niemand außer Ihnen hat Zugriff auf Ihre Felddaten.",
  },
];

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

export default function WieEsFunktioniertPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* ====================================================================
          NAVIGATION — identical sticky nav to landing page
          ==================================================================== */}
      <nav className="sticky top-0 z-50 border-b border-gray-100 backdrop-blur-sm bg-white/90">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2.5 group">
              <div className="h-8 w-8 flex-shrink-0 transition-transform duration-200 group-hover:scale-105">
                <LogoIcon />
              </div>
              <span
                className="text-xl font-bold text-gray-900 tracking-tight"
                style={{ letterSpacing: "-0.02em" }}
              >
                AgroLens
              </span>
            </Link>

            {/* Nav links */}
            <div className="hidden sm:flex items-center gap-6">
              <Link
                href="/wie-es-funktioniert"
                className="text-sm font-medium text-gray-900 transition-colors duration-150"
                aria-current="page"
              >
                So funktioniert&apos;s
              </Link>
              <Link
                href="/#preise"
                className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors duration-150"
              >
                Preise
              </Link>
            </div>

            {/* CTA group */}
            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors duration-150"
              >
                Anmelden
              </Link>
              <Link
                href="/signup"
                className="inline-flex items-center rounded-lg bg-agrolens-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-agrolens-700 focus:outline-none focus:ring-2 focus:ring-agrolens-500 focus:ring-offset-2 transition-all duration-150"
              >
                Kostenlos starten
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main>
        {/* ====================================================================
            PAGE HEADER
            ==================================================================== */}
        <section className="bg-white py-20 lg:py-28">
          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
            <p className="text-sm font-semibold uppercase tracking-widest text-agrolens-600 mb-4">
              So funktioniert&apos;s
            </p>
            <h1
              className="text-4xl font-extrabold text-gray-900 sm:text-5xl lg:text-6xl"
              style={{ letterSpacing: "-0.03em" }}
            >
              So funktioniert AgroLens
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-gray-600">
              Satellitendaten, verständlich erklärt — für Landwirte, nicht für Informatiker.
            </p>
          </div>
        </section>

        {/* ====================================================================
            FIVE EXPLANATION STEPS
            ==================================================================== */}
        <section className="bg-white py-4 pb-20 lg:pb-28">
          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
            <div className="space-y-28">

              {/* STEP 01 */}
              <div>
                <div className="relative mb-8">
                  <span
                    className="absolute -top-6 -left-4 select-none text-8xl font-black text-agrolens-100 leading-none pointer-events-none"
                    aria-hidden="true"
                  >
                    01
                  </span>
                  <div className="relative pt-6">
                    <h2
                      className="text-2xl font-bold text-gray-900 sm:text-3xl"
                      style={{ letterSpacing: "-0.02em" }}
                    >
                      Der Satellit macht das Bild
                    </h2>
                  </div>
                </div>
                <div className="grid grid-cols-1 items-start gap-10 lg:grid-cols-2">
                  <div className="space-y-4 text-base leading-relaxed text-gray-600">
                    <p>
                      Der europäische Sentinel-2-Satellit fliegt alle 5 bis 10 Tage über
                      Deutschland und fotografiert die Felder. Diese Aufnahmen sind kostenlos
                      verfügbar — finanziert durch die EU im Rahmen des Copernicus-Programms.
                      AgroLens lädt die Bilder automatisch herunter, sobald eine neue Aufnahme
                      vorliegt.
                    </p>
                    <p>
                      Anders als normale Fotos sieht der Satellit auch Wellenlängen, die für
                      das menschliche Auge unsichtbar sind — insbesondere nahes Infrarotlicht.
                      Gesunde Pflanzen reflektieren dieses Infrarotlicht viel stärker als
                      kranke oder gestresste Pflanzen.
                    </p>
                  </div>
                  <div className="rounded-2xl border border-agrolens-100 bg-agrolens-50 p-4 shadow-sm">
                    <SatelliteIllustration />
                  </div>
                </div>
              </div>

              {/* STEP 02 */}
              <div>
                <div className="relative mb-8">
                  <span
                    className="absolute -top-6 -left-4 select-none text-8xl font-black text-agrolens-100 leading-none pointer-events-none"
                    aria-hidden="true"
                  >
                    02
                  </span>
                  <div className="relative pt-6">
                    <h2
                      className="text-2xl font-bold text-gray-900 sm:text-3xl"
                      style={{ letterSpacing: "-0.02em" }}
                    >
                      NDVI: Wie gesund ist die Pflanze?
                    </h2>
                  </div>
                </div>
                <div className="grid grid-cols-1 items-start gap-10 lg:grid-cols-2">
                  <div className="space-y-4 text-base leading-relaxed text-gray-600 lg:order-last">
                    <p>
                      Aus den Satellitendaten berechnet AgroLens den NDVI (Normalized
                      Difference Vegetation Index). Das ist eine einfache Zahl zwischen
                      −1 und +1:
                    </p>
                    <ul className="space-y-2.5">
                      <li className="flex items-start gap-3">
                        <span className="mt-1 h-3 w-3 flex-shrink-0 rounded-full bg-agrolens-600" aria-hidden="true" />
                        <span>
                          <strong className="text-gray-800">Wert nahe +1 (dunkelgrün):</strong>{" "}
                          Pflanze ist gesund und wächst gut
                        </span>
                      </li>
                      <li className="flex items-start gap-3">
                        <span className="mt-1 h-3 w-3 flex-shrink-0 rounded-full bg-amber-400" aria-hidden="true" />
                        <span>
                          <strong className="text-gray-800">Wert um 0,4–0,6 (hellgrün/gelb):</strong>{" "}
                          leichter Stress, erhöhte Aufmerksamkeit nötig
                        </span>
                      </li>
                      <li className="flex items-start gap-3">
                        <span className="mt-1 h-3 w-3 flex-shrink-0 rounded-full bg-red-500" aria-hidden="true" />
                        <span>
                          <strong className="text-gray-800">Wert unter 0,3 (orange/rot):</strong>{" "}
                          deutlicher Stress, möglicher Schaden oder Befall
                        </span>
                      </li>
                    </ul>
                    <p>
                      Das Besondere: AgroLens berechnet diese Werte nicht nur für das gesamte
                      Feld, sondern für jeden einzelnen 10&thinsp;&times;&thinsp;10-Meter-Bereich.
                      So sehen Sie auf einen Blick, wo auf Ihrem Feld es Probleme gibt —
                      und wo nicht.
                    </p>
                  </div>
                  <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm lg:order-first">
                    <NdviBarIllustration />
                  </div>
                </div>
              </div>

              {/* STEP 03 */}
              <div>
                <div className="relative mb-8">
                  <span
                    className="absolute -top-6 -left-4 select-none text-8xl font-black text-agrolens-100 leading-none pointer-events-none"
                    aria-hidden="true"
                  >
                    03
                  </span>
                  <div className="relative pt-6">
                    <h2
                      className="text-2xl font-bold text-gray-900 sm:text-3xl"
                      style={{ letterSpacing: "-0.02em" }}
                    >
                      Bewirtschaftungszonen: Das Feld wird aufgeteilt
                    </h2>
                  </div>
                </div>
                <div className="grid grid-cols-1 items-start gap-10 lg:grid-cols-2">
                  <div className="space-y-4 text-base leading-relaxed text-gray-600">
                    <p>
                      Kein Feld ist gleichmäßig. Es gibt Stellen mit besserem Boden,
                      mehr Feuchtigkeit oder weniger Nährstoffen. AgroLens erkennt diese
                      Unterschiede automatisch und teilt das Feld in 2 bis 5
                      Bewirtschaftungszonen ein.
                    </p>
                    <p>
                      Das funktioniert mit einem mathematischen Verfahren namens
                      K-Means-Clustering: Bereiche mit ähnlichem NDVI-Wert werden zu
                      einer Zone zusammengefasst. Das Ergebnis ist eine Karte, die klar
                      zeigt, welche Teile des Feldes gleich behandelt werden können.
                    </p>
                    <p>
                      Früher war dafür ein aufwendiges Bodengutachten oder eine manuelle
                      Begehung nötig. Mit AgroLens geschieht das vollautomatisch, auf
                      Basis aktueller Satellitendaten — ohne dass jemand auf das Feld
                      muss.
                    </p>
                  </div>
                  <div className="rounded-2xl border border-agrolens-100 bg-agrolens-50 p-4 shadow-sm">
                    <ZoneMapIllustration />
                  </div>
                </div>
              </div>

              {/* STEP 04 */}
              <div>
                <div className="relative mb-8">
                  <span
                    className="absolute -top-6 -left-4 select-none text-8xl font-black text-agrolens-100 leading-none pointer-events-none"
                    aria-hidden="true"
                  >
                    04
                  </span>
                  <div className="relative pt-6">
                    <h2
                      className="text-2xl font-bold text-gray-900 sm:text-3xl"
                      style={{ letterSpacing: "-0.02em" }}
                    >
                      Die Ausbringungskarte für die Maschine
                    </h2>
                  </div>
                </div>
                <div className="grid grid-cols-1 items-start gap-10 lg:grid-cols-2">
                  <div className="space-y-4 text-base leading-relaxed text-gray-600 lg:order-last">
                    <p>
                      Für jede Bewirtschaftungszone berechnet AgroLens, wie viel
                      Pflanzenschutzmittel sinnvoll ist. Zonen mit geringem Stress
                      erhalten eine reduzierte Menge, Stresszonen die volle oder leicht
                      erhöhte Menge.
                    </p>
                    <p>
                      Das Ergebnis wird als Datei exportiert, die direkt in Ihren
                      Feldspritzcomputer geladen werden kann:
                    </p>
                    <ul className="space-y-3">
                      <li className="flex items-start gap-3">
                        <CheckIcon />
                        <span>
                          <strong className="text-gray-800">TASKDATA.XML (ISOBUS ISO&nbsp;11783-10):</strong>{" "}
                          Für alle modernen ISOBUS&#174;-fähigen Maschinen. Einfach per
                          USB-Stick übertragen. (ISOBUS&#174; ist ein eingetragenes Warenzeichen
                          der AEF.)
                        </span>
                      </li>
                      <li className="flex items-start gap-3">
                        <CheckIcon />
                        <span>
                          <strong className="text-gray-800">Shapefile (.SHP):</strong>{" "}
                          Für GIS-fähige Steuergeräte und Beratungssoftware.
                        </span>
                      </li>
                      <li className="flex items-start gap-3">
                        <CheckIcon />
                        <span>
                          <strong className="text-gray-800">PDF-Bericht:</strong>{" "}
                          Für Betriebe ohne digitale Steuergeräte — zur manuellen
                          Einstellung oder für den Pflanzenschutzberater.
                        </span>
                      </li>
                    </ul>
                    <p className="text-sm text-gray-500">
                      Alle Exporte enthalten den agronomischen Disclaimer und sind
                      §67-PflSchG-konform dokumentiert.
                    </p>
                  </div>
                  <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm lg:order-first">
                    <ExportIllustration />
                  </div>
                </div>
              </div>

              {/* STEP 05 */}
              <div>
                <div className="relative mb-8">
                  <span
                    className="absolute -top-6 -left-4 select-none text-8xl font-black text-agrolens-100 leading-none pointer-events-none"
                    aria-hidden="true"
                  >
                    05
                  </span>
                  <div className="relative pt-6">
                    <h2
                      className="text-2xl font-bold text-gray-900 sm:text-3xl"
                      style={{ letterSpacing: "-0.02em" }}
                    >
                      Was Sie brauchen, um zu starten
                    </h2>
                  </div>
                </div>
                <div className="grid grid-cols-1 items-start gap-10 lg:grid-cols-2">
                  <div className="space-y-6 text-base leading-relaxed text-gray-600">
                    <div>
                      <p className="font-semibold text-gray-900 mb-3">Sie brauchen:</p>
                      <ul className="space-y-2.5">
                        {[
                          "Einen Computer, ein Tablet oder Smartphone",
                          "Die Grenzen Ihrer Felder (Shapefile, GeoJSON oder per Maus einzeichnen)",
                          "Optional: Ihre FLIK-Nummern aus dem InVeKoS-System",
                          "Für den automatischen Export: eine ISOBUS&#174;-fähige Feldspritze",
                        ].map((item) => (
                          <li key={item} className="flex items-start gap-3">
                            <CheckIcon />
                            <span dangerouslySetInnerHTML={{ __html: item }} />
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 mb-3">
                        Sie brauchen <strong className="text-red-600">nicht</strong>:
                      </p>
                      <ul className="space-y-2.5">
                        {[
                          "Eigene Hardware oder Sensoren",
                          "Technisches Vorwissen",
                          "Eine Kreditkarte für den Basis-Plan",
                        ].map((item) => (
                          <li key={item} className="flex items-start gap-3">
                            <XMarkIcon />
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  <div className="rounded-2xl border border-agrolens-100 bg-agrolens-50 p-4 shadow-sm">
                    <RequirementsIllustration />
                  </div>
                </div>
              </div>

            </div>
          </div>
        </section>

        {/* ====================================================================
            FAQ
            ==================================================================== */}
        <section className="bg-gray-50 py-20 lg:py-28">
          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
            <div className="mx-auto mb-14 text-center">
              <p className="text-sm font-semibold uppercase tracking-widest text-agrolens-600 mb-3">
                Häufige Fragen
              </p>
              <h2
                className="text-3xl font-extrabold text-gray-900 sm:text-4xl"
                style={{ letterSpacing: "-0.02em" }}
              >
                Noch Fragen?
              </h2>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {faqItems.map((item) => (
                <div
                  key={item.question}
                  className="rounded-xl bg-white ring-1 ring-gray-200 p-6"
                >
                  <h3 className="text-base font-semibold text-gray-900 mb-3">
                    {item.question}
                  </h3>
                  <p className="text-sm leading-relaxed text-gray-600">{item.answer}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ====================================================================
            DARK CTA
            ==================================================================== */}
        <section className="bg-agrolens-950 py-24 lg:py-32">
          <div className="mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8">
            <p className="mb-6 text-sm font-semibold uppercase tracking-widest text-agrolens-600">
              Jetzt starten
            </p>
            <h2
              className="text-4xl font-extrabold text-white sm:text-5xl"
              style={{ letterSpacing: "-0.03em" }}
            >
              Überzeugt?
            </h2>
            <p className="mx-auto mt-6 max-w-xl text-lg text-agrolens-300">
              Starten Sie kostenlos — Ihr erstes Feld in wenigen Minuten eingerichtet.
            </p>
            <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <Link
                href="/signup"
                className="inline-flex items-center rounded-xl bg-white px-8 py-4 text-base font-semibold text-agrolens-700 shadow-lg hover:bg-agrolens-50 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-agrolens-950 transition-all duration-150"
              >
                Kostenlos starten
              </Link>
              <Link
                href="/"
                className="inline-flex items-center rounded-xl border border-agrolens-700 px-8 py-4 text-base font-semibold text-agrolens-300 hover:border-agrolens-500 hover:text-white focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-agrolens-950 transition-all duration-150"
              >
                Zur&uuml;ck zur Startseite
              </Link>
            </div>
          </div>
        </section>

        {/* ====================================================================
            FOOTER — identical to landing page
            ==================================================================== */}
        <footer className="bg-agrolens-950 border-t border-agrolens-900">
          <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
            <div className="flex flex-col items-start justify-between gap-8 sm:flex-row sm:items-center">
              {/* Logo + tagline */}
              <div>
                <div className="flex items-center gap-2.5">
                  <div className="h-7 w-7 flex-shrink-0">
                    <LogoIcon />
                  </div>
                  <span
                    className="text-lg font-bold text-white"
                    style={{ letterSpacing: "-0.02em" }}
                  >
                    AgroLens
                  </span>
                </div>
                <p className="mt-2 text-sm text-agrolens-500 max-w-xs">
                  Satellitengest&uuml;tzte Pr&auml;zisionslandwirtschaft f&uuml;r
                  europ&auml;ische Betriebe.
                </p>
              </div>

              {/* Nav links */}
              <nav
                className="flex flex-wrap gap-x-6 gap-y-2"
                aria-label="Footer-Navigation"
              >
                {[
                  { label: "Datenschutz", href: "/datenschutz" },
                  { label: "Impressum", href: "/impressum" },
                  { label: "AGB", href: "/agb" },
                  { label: "Kontakt", href: "/contact" },
                ].map((link) => (
                  <Link
                    key={link.label}
                    href={link.href}
                    className="text-sm text-agrolens-500 hover:text-agrolens-300 transition-colors duration-150"
                  >
                    {link.label}
                  </Link>
                ))}
              </nav>
            </div>

            {/* Bottom bar */}
            <div className="mt-10 border-t border-agrolens-900 pt-8 flex flex-col gap-2 sm:flex-row sm:justify-between">
              <p className="text-xs text-agrolens-600">
                &copy; {new Date().getFullYear()} AgroLens. Alle Rechte vorbehalten.
              </p>
              <p className="text-xs text-agrolens-700">
                Contains modified Copernicus Sentinel data {new Date().getFullYear()}.
                &middot; ISOBUS&reg; ist ein eingetragenes Warenzeichen der AEF.
              </p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
