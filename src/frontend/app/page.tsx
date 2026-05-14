"use client";

/**
 * AgroLens public landing page.
 *
 * Full redesign: German-language, agriculture-specific, conversion-optimised.
 * Sections: Nav → Hero → Trust bar → How it works → Pricing → Dark CTA → Footer
 *
 * Uses "use client" because the pricing section has a monthly/annual toggle (useState).
 */

import Link from "next/link";
import { useState } from "react";

// ---------------------------------------------------------------------------
// Inline SVG icon components — no external icon library dependency
// ---------------------------------------------------------------------------

function LogoIcon() {
  return (
    <svg
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden="true"
      className="h-full w-full"
    >
      {/* Satellite dish stylised as a leaf / field shape */}
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

function XIcon() {
  return (
    <svg
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
      className="h-5 w-5 flex-shrink-0 text-gray-300"
    >
      <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Pricing data
// ---------------------------------------------------------------------------

const plans = [
  {
    name: "Starter",
    description: "Für Einsteiger und kleine Betriebe",
    limits: "Bis zu 5 Felder · 100 ha",
    monthlyPrice: 49,
    annualPrice: 470,
    cta: "Kostenlos starten",
    href: "/signup",
    highlighted: false,
    badge: null,
    features: [
      { text: "NDVI-Analyse", included: true },
      { text: "3 Bewirtschaftungszonen / Feld", included: true },
      { text: "ISOBUS®-Export (Shapefile)", included: true },
      { text: "PDF-Applikationsberichte", included: true },
      { text: "E-Mail-Alerts", included: true },
      { text: "API-Zugang", included: false },
      { text: "Unbegrenzte Felder", included: false },
    ],
  },
  {
    name: "Farmer",
    description: "Für wachsende Betriebe — unser beliebtester Plan",
    limits: "Bis zu 50 Felder · 500 ha",
    monthlyPrice: 149,
    annualPrice: 1430,
    cta: "Kostenlos starten",
    href: "/signup",
    highlighted: true,
    badge: "Empfohlen",
    features: [
      { text: "NDVI-Analyse", included: true },
      { text: "3–5 Bewirtschaftungszonen / Feld", included: true },
      { text: "ISOBUS®-Export (Shapefile + TASKDATA.XML)", included: true },
      { text: "PDF-Applikationsberichte", included: true },
      { text: "E-Mail-Alerts", included: true },
      { text: "API-Zugang", included: true },
      { text: "Unbegrenzte Felder", included: false },
    ],
  },
  {
    name: "Pro",
    description: "Für große Betriebe und Lohnunternehmer",
    limits: "Unbegrenzte Felder & Fläche",
    monthlyPrice: 599,
    annualPrice: 5750,
    cta: "Vertrieb kontaktieren",
    href: "/signup",
    highlighted: false,
    badge: null,
    features: [
      { text: "NDVI-Analyse", included: true },
      { text: "Konfigurierbare Zonenzahl (2–5)", included: true },
      { text: "ISOBUS®-Export (Shapefile + TASKDATA.XML)", included: true },
      { text: "PDF-Applikationsberichte", included: true },
      { text: "E-Mail-Alerts", included: true },
      { text: "API-Zugang", included: true },
      { text: "Unbegrenzte Felder", included: true },
    ],
  },
];

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

export default function LandingPage() {
  const [annual, setAnnual] = useState(false);

  return (
    <div className="min-h-screen bg-white">
      {/* ====================================================================
          NAVIGATION
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
                className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors duration-150"
              >
                So funktioniert's
              </Link>
              <Link
                href="#preise"
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
        {/* ==================================================================
            HERO — full viewport
            ================================================================== */}
        <section
          className="relative min-h-screen flex flex-col justify-center overflow-hidden bg-white"
          style={{
            backgroundImage:
              "radial-gradient(circle, #d1fae5 1px, transparent 1px)",
            backgroundSize: "24px 24px",
          }}
        >
          {/* Fade edges over dot grid */}
          <div
            className="pointer-events-none absolute inset-0"
            style={{
              background:
                "radial-gradient(ellipse 80% 60% at 50% 50%, transparent 40%, white 100%)",
            }}
            aria-hidden="true"
          />

          <div className="relative mx-auto max-w-7xl px-4 pb-16 pt-24 sm:px-6 lg:px-8">
            {/* --- Text block --- */}
            <div className="mx-auto max-w-4xl text-center">
              {/* Badge */}
              <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-agrolens-200 bg-agrolens-50 px-4 py-1.5">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-agrolens-500 opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-agrolens-500" />
                </span>
                <span className="text-sm font-medium text-agrolens-700">
                  Sentinel-2 · 10 m Auflösung · Alle 5–10 Tage aktualisiert
                </span>
              </div>

              {/* Headline */}
              <h1 className="text-5xl font-extrabold leading-none sm:text-7xl" style={{ letterSpacing: "-0.03em" }}>
                <span className="block text-gray-900">Weniger Pestizide.</span>
                <span className="block text-agrolens-600 mt-1">Mehr Ertrag.</span>
              </h1>

              {/* Subheadline */}
              <p className="mx-auto mt-8 max-w-2xl text-lg leading-relaxed text-gray-600">
                AgroLens analysiert Sentinel-2-Satellitendaten für jedes Ihrer
                Felder und erzeugt präzise Ausbringungskarten — automatisch,
                ISOBUS-kompatibel, EU-konform.
              </p>

              {/* Stats row */}
              <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center sm:gap-0 sm:divide-x sm:divide-gray-200">
                {[
                  { value: "10 m", label: "Satelliten-Auflösung" },
                  { value: "5–10 Tage", label: "Analyse-Rhythmus" },
                  { value: "§67 PflSchG", label: "konform" },
                ].map((stat) => (
                  <div key={stat.label} className="px-8 text-center">
                    <p
                      className="text-2xl font-extrabold text-gray-900"
                      style={{ letterSpacing: "-0.02em" }}
                    >
                      {stat.value}
                    </p>
                    <p className="mt-0.5 text-sm text-gray-500">{stat.label}</p>
                  </div>
                ))}
              </div>

              {/* CTA buttons */}
              <div className="mt-10 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
                <Link
                  href="/signup"
                  className="inline-flex items-center rounded-xl bg-agrolens-600 px-8 py-4 text-base font-semibold text-white shadow-lg hover:bg-agrolens-700 focus:outline-none focus:ring-2 focus:ring-agrolens-500 focus:ring-offset-2 transition-all duration-150 hover:shadow-xl hover:-translate-y-0.5"
                >
                  Kostenlos starten
                </Link>
                <Link
                  href="#demo"
                  className="inline-flex items-center rounded-xl border border-gray-200 bg-white px-8 py-4 text-base font-semibold text-gray-700 shadow-sm hover:border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-agrolens-500 focus:ring-offset-2 transition-all duration-150"
                >
                  Demo ansehen
                </Link>
              </div>

              <p className="mt-4 text-sm text-gray-400">
                Kostenloser Basis-Plan verfügbar · Keine Kreditkarte für den Test erforderlich · Jederzeit kündbar
              </p>
            </div>

            {/* --- Product mockup --- */}
            <div className="relative mx-auto mt-16 max-w-5xl" id="demo">
              {/* Glow behind the mockup */}
              <div
                className="absolute -inset-4 rounded-3xl opacity-20 blur-2xl"
                style={{
                  background:
                    "radial-gradient(ellipse at center, #16a34a 0%, transparent 70%)",
                }}
                aria-hidden="true"
              />
              <div className="relative rounded-2xl bg-agrolens-950 shadow-2xl ring-1 ring-white/10 overflow-hidden">
                {/* Titlebar */}
                <div className="flex items-center gap-1.5 px-4 py-3 bg-agrolens-900/50 border-b border-white/10">
                  <div className="h-3 w-3 rounded-full bg-red-500/80" />
                  <div className="h-3 w-3 rounded-full bg-amber-500/80" />
                  <div className="h-3 w-3 rounded-full bg-green-500/80" />
                  <span className="ml-2 text-xs text-agrolens-300 font-mono">
                    AgroLens — Feldübersicht
                  </span>
                  <span className="ml-auto text-xs text-agrolens-500 font-mono hidden sm:block">
                    Betrieb: Musterhof GbR · 6 Felder · 142 ha
                  </span>
                </div>

                {/* Map area */}
                <div className="p-4 sm:p-6">
                  <svg
                    viewBox="0 0 800 400"
                    className="w-full h-auto rounded-lg"
                    aria-label="Satelliten-Feldübersicht mit NDVI-Zonen"
                    role="img"
                  >
                    {/* Dark ground */}
                    <rect width="800" height="400" fill="#0a1f0f" />

                    {/* Subtle terrain texture */}
                    <rect width="800" height="400" fill="url(#terrain)" opacity="0.15" />
                    <defs>
                      <pattern id="terrain" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
                        <circle cx="20" cy="20" r="1" fill="#22c55e" opacity="0.3" />
                      </pattern>
                    </defs>

                    {/* Field 1 — healthy, dark green */}
                    <polygon
                      points="80,60 280,40 320,180 100,200"
                      fill="#16a34a"
                      opacity="0.75"
                    />
                    {/* Field 2 — mild stress, amber */}
                    <polygon
                      points="340,30 560,50 540,190 320,180"
                      fill="#f59e0b"
                      opacity="0.65"
                    />
                    {/* Field 3 — healthy */}
                    <polygon
                      points="580,60 740,80 720,220 560,200"
                      fill="#22c55e"
                      opacity="0.70"
                    />
                    {/* Field 4 — stress alert, red */}
                    <polygon
                      points="100,220 300,210 280,360 80,370"
                      fill="#ef4444"
                      opacity="0.55"
                    />
                    {/* Field 5 — healthy */}
                    <polygon
                      points="320,200 530,210 510,360 300,350"
                      fill="#16a34a"
                      opacity="0.65"
                    />
                    {/* Field 6 — no data yet */}
                    <polygon
                      points="550,220 720,230 700,380 540,370"
                      fill="#94a3b8"
                      opacity="0.35"
                    />

                    {/* Grid overlay */}
                    <line x1="0" y1="133" x2="800" y2="133" stroke="white" strokeOpacity="0.04" />
                    <line x1="0" y1="266" x2="800" y2="266" stroke="white" strokeOpacity="0.04" />
                    <line x1="266" y1="0" x2="266" y2="400" stroke="white" strokeOpacity="0.04" />
                    <line x1="533" y1="0" x2="533" y2="400" stroke="white" strokeOpacity="0.04" />

                    {/* NDVI labels */}
                    <text x="190" y="118" textAnchor="middle" fill="white" fontSize="11" fontFamily="monospace" opacity="0.9">NDVI 0.72</text>
                    <text x="435" y="112" textAnchor="middle" fill="white" fontSize="11" fontFamily="monospace" opacity="0.9">NDVI 0.51</text>
                    <text x="648" y="138" textAnchor="middle" fill="white" fontSize="11" fontFamily="monospace" opacity="0.9">NDVI 0.68</text>
                    <text x="185" y="295" textAnchor="middle" fill="white" fontSize="11" fontFamily="monospace" opacity="0.9">NDVI 0.34</text>
                    <text x="412" y="288" textAnchor="middle" fill="white" fontSize="11" fontFamily="monospace" opacity="0.9">NDVI 0.71</text>
                    <text x="625" y="305" textAnchor="middle" fill="#94a3b8" fontSize="11" fontFamily="monospace" opacity="0.8">Kein Signal</text>

                    {/* Status dots next to labels */}
                    <circle cx="135" cy="115" r="4" fill="#22c55e" opacity="0.9" />
                    <circle cx="381" cy="109" r="4" fill="#f59e0b" opacity="0.9" />
                    <circle cx="594" cy="135" r="4" fill="#22c55e" opacity="0.9" />
                    <circle cx="131" cy="292" r="4" fill="#ef4444" opacity="0.9" />
                    <circle cx="358" cy="285" r="4" fill="#22c55e" opacity="0.9" />
                    <circle cx="571" cy="302" r="4" fill="#94a3b8" opacity="0.7" />

                    {/* Legend */}
                    <rect x="16" y="352" width="180" height="36" rx="6" fill="#052e16" opacity="0.8" />
                    <circle cx="30" cy="370" r="5" fill="#22c55e" />
                    <text x="40" y="374" fill="#d1fae5" fontSize="9" fontFamily="monospace">Gesund</text>
                    <circle cx="85" cy="370" r="5" fill="#f59e0b" />
                    <text x="95" y="374" fill="#d1fae5" fontSize="9" fontFamily="monospace">Stress</text>
                    <circle cx="138" cy="370" r="5" fill="#ef4444" />
                    <text x="148" y="374" fill="#d1fae5" fontSize="9" fontFamily="monospace">Alarm</text>
                  </svg>
                </div>

                {/* Bottom stats bar */}
                <div className="grid grid-cols-3 divide-x divide-white/10 border-t border-white/10 bg-agrolens-900/30">
                  <div className="px-4 py-3 sm:px-6 sm:py-4">
                    <p className="text-xs text-agrolens-400">Letzte Analyse</p>
                    <p className="text-sm font-semibold text-white mt-0.5">vor 2 Stunden</p>
                  </div>
                  <div className="px-4 py-3 sm:px-6 sm:py-4">
                    <p className="text-xs text-agrolens-400">Felder analysiert</p>
                    <p className="text-sm font-semibold text-white mt-0.5">6 von 6</p>
                  </div>
                  <div className="px-4 py-3 sm:px-6 sm:py-4">
                    <p className="text-xs text-agrolens-400">Einsparung (Beispiel)</p>
                    <p className="text-sm font-semibold text-earth-400 mt-0.5">Beispiel: € 3.200</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ==================================================================
            HOW IT WORKS — alternating layout
            ================================================================== */}
        <section
          id="wie-es-funktioniert"
          className="bg-white py-24 lg:py-32"
        >
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {/* Section header */}
            <div className="mx-auto max-w-2xl text-center mb-20">
              <p className="text-sm font-semibold uppercase tracking-widest text-agrolens-600 mb-3">
                Wie es funktioniert
              </p>
              <h2
                className="text-4xl font-extrabold text-gray-900 sm:text-5xl"
                style={{ letterSpacing: "-0.03em" }}
              >
                Von der Feldgrenze zur
                <br />
                <span className="text-agrolens-600">Ausbringungskarte</span>
              </h2>
              <p className="mt-5 text-lg text-gray-600">
                In drei Schritten — vollautomatisch, in unter 24 Stunden.
              </p>
            </div>

            {/* Steps */}
            <div className="space-y-24">
              {/* Step 1 */}
              <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
                <div className="relative">
                  <span
                    className="absolute -top-6 -left-4 select-none text-8xl font-black text-agrolens-100 leading-none pointer-events-none"
                    aria-hidden="true"
                  >
                    01
                  </span>
                  <div className="relative">
                    <p className="text-sm font-semibold uppercase tracking-widest text-agrolens-600 mb-3">
                      Schritt 1
                    </p>
                    <h3
                      className="text-2xl font-bold text-gray-900 mb-4"
                      style={{ letterSpacing: "-0.02em" }}
                    >
                      Feldgrenzen einzeichnen
                    </h3>
                    <p className="text-base leading-relaxed text-gray-600">
                      Zeichnen Sie Ihre Felder direkt auf der Karte ein, importieren
                      Sie eine GeoJSON- oder Shapefile-Datei, oder geben Sie Ihre
                      FLIK-Nummer ein. AgroLens beginnt sofort mit der Überwachung —
                      keine zusätzliche Hardware erforderlich.
                    </p>
                    <ul className="mt-6 space-y-2">
                      {[
                        "GeoJSON, KML, Shapefile-Import",
                        "FLIK-Nummern (InVeKoS) unterstützt",
                        "Automatische Flächenberechnung",
                      ].map((item) => (
                        <li key={item} className="flex items-center gap-2.5 text-sm text-gray-700">
                          <CheckIcon />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Step 1 visual */}
                <div className="rounded-2xl border border-agrolens-100 bg-agrolens-50 p-6 shadow-card">
                  <svg viewBox="0 0 400 260" className="w-full h-auto" aria-hidden="true">
                    <rect width="400" height="260" fill="#f0fdf4" rx="8" />
                    {/* Grid lines */}
                    {[65, 130, 195].map((y) => (
                      <line key={y} x1="0" y1={y} x2="400" y2={y} stroke="#bbf7d0" strokeWidth="1" />
                    ))}
                    {[100, 200, 300].map((x) => (
                      <line key={x} x1={x} y1="0" x2={x} y2="260" stroke="#bbf7d0" strokeWidth="1" />
                    ))}
                    {/* Field polygon being drawn */}
                    <polygon
                      points="80,40 270,30 300,160 60,175"
                      fill="#16a34a"
                      opacity="0.2"
                      stroke="#16a34a"
                      strokeWidth="2"
                      strokeDasharray="6,4"
                    />
                    {/* Vertices */}
                    {[[80,40],[270,30],[300,160],[60,175]].map(([cx, cy]) => (
                      <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r="5" fill="#16a34a" />
                    ))}
                    {/* Area label */}
                    <rect x="130" y="82" width="100" height="28" rx="6" fill="#16a34a" opacity="0.9" />
                    <text x="180" y="100" textAnchor="middle" fill="white" fontSize="12" fontFamily="sans-serif" fontWeight="600">24,7 ha</text>
                    {/* Cursor */}
                    <circle cx="300" cy="160" r="10" fill="none" stroke="#16a34a" strokeWidth="2" opacity="0.6" />
                    <circle cx="300" cy="160" r="3" fill="#16a34a" />
                    {/* Field name chip */}
                    <rect x="20" y="190" width="130" height="30" rx="8" fill="white" stroke="#bbf7d0" strokeWidth="1" />
                    <text x="85" y="209" textAnchor="middle" fill="#166534" fontSize="11" fontFamily="sans-serif">Schlag Nord · 24,7 ha</text>
                  </svg>
                </div>
              </div>

              {/* Step 2 — reversed */}
              <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
                {/* Step 2 visual — comes first on desktop (order-first) */}
                <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-card order-last lg:order-first">
                  <svg viewBox="0 0 400 260" className="w-full h-auto" aria-hidden="true">
                    <rect width="400" height="260" fill="#0a1f0f" rx="8" />
                    {/* Satellite orbit arc */}
                    <ellipse cx="200" cy="20" rx="160" ry="80" fill="none" stroke="#22c55e" strokeWidth="1" strokeDasharray="4,6" opacity="0.4" />
                    {/* Satellite icon */}
                    <g transform="translate(340, 10)">
                      <rect x="0" y="6" width="18" height="10" rx="2" fill="#86efac" opacity="0.9" />
                      <rect x="-14" y="9" width="10" height="4" rx="1" fill="#4ade80" opacity="0.7" />
                      <rect x="18" y="9" width="10" height="4" rx="1" fill="#4ade80" opacity="0.7" />
                    </g>
                    {/* Scan beam */}
                    <polygon points="348,20 160,120 240,120" fill="#22c55e" opacity="0.05" />
                    <line x1="348" y1="20" x2="160" y2="120" stroke="#22c55e" strokeWidth="1" opacity="0.3" strokeDasharray="3,5" />
                    <line x1="348" y1="20" x2="240" y2="120" stroke="#22c55e" strokeWidth="1" opacity="0.3" strokeDasharray="3,5" />
                    {/* NDVI heatmap zones */}
                    <polygon points="60,100 200,90 220,190 50,200" fill="#16a34a" opacity="0.7" />
                    <polygon points="200,90 330,100 320,195" fill="#f59e0b" opacity="0.6" />
                    {/* Zone labels */}
                    <rect x="90" y="128" width="80" height="22" rx="4" fill="#052e16" opacity="0.85" />
                    <text x="130" y="143" textAnchor="middle" fill="#86efac" fontSize="10" fontFamily="monospace">Zone A · NDVI 0.71</text>
                    <rect x="215" y="130" width="80" height="22" rx="4" fill="#052e16" opacity="0.85" />
                    <text x="255" y="145" textAnchor="middle" fill="#fde047" fontSize="10" fontFamily="monospace">Zone B · NDVI 0.49</text>
                    {/* Progress bar */}
                    <rect x="30" y="220" width="340" height="6" rx="3" fill="#14532d" />
                    <rect x="30" y="220" width="255" height="6" rx="3" fill="#22c55e" />
                    <text x="30" y="240" fill="#86efac" fontSize="9" fontFamily="monospace">Analyse läuft … 75 %</text>
                    <text x="380" y="240" textAnchor="end" fill="#4ade80" fontSize="9" fontFamily="monospace">∼ 3 min</text>
                  </svg>
                </div>

                <div className="relative order-first lg:order-last">
                  <span
                    className="absolute -top-6 -left-4 select-none text-8xl font-black text-agrolens-100 leading-none pointer-events-none"
                    aria-hidden="true"
                  >
                    02
                  </span>
                  <div className="relative">
                    <p className="text-sm font-semibold uppercase tracking-widest text-agrolens-600 mb-3">
                      Schritt 2
                    </p>
                    <h3
                      className="text-2xl font-bold text-gray-900 mb-4"
                      style={{ letterSpacing: "-0.02em" }}
                    >
                      KI-Satellitenanalyse
                    </h3>
                    <p className="text-base leading-relaxed text-gray-600">
                      Sobald Sentinel-2 über Ihr Gebiet fliegt, ruft AgroLens die
                      multispektralen Bilder automatisch ab. Unsere KI berechnet NDVI,
                      NDRE und weitere Indizes — und teilt jedes Feld in bis zu fünf
                      Bewirtschaftungszonen ein.
                    </p>
                    <ul className="mt-6 space-y-2">
                      {[
                        "NDVI, NDRE, EVI automatisch berechnet",
                        "K-Means-Clustering in 2–5 Zonen",
                        "Automatische Wolkenmaskierung",
                      ].map((item) => (
                        <li key={item} className="flex items-center gap-2.5 text-sm text-gray-700">
                          <CheckIcon />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Step 3 */}
              <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
                <div className="relative">
                  <span
                    className="absolute -top-6 -left-4 select-none text-8xl font-black text-agrolens-100 leading-none pointer-events-none"
                    aria-hidden="true"
                  >
                    03
                  </span>
                  <div className="relative">
                    <p className="text-sm font-semibold uppercase tracking-widest text-agrolens-600 mb-3">
                      Schritt 3
                    </p>
                    <h3
                      className="text-2xl font-bold text-gray-900 mb-4"
                      style={{ letterSpacing: "-0.02em" }}
                    >
                      Ausbringungskarte herunterladen
                    </h3>
                    <p className="text-base leading-relaxed text-gray-600">
                      Exportieren Sie ISOBUS-kompatible Shapefiles und TASKDATA.XML
                      direkt für Ihren Feldspritzcomputer. Oder laden Sie den
                      PDF-Bericht für Ihren Pflanzenschutzberater herunter — inklusive
                      agronomischem Disclaimer und §67-PflSchG-Konformitätsvermerk.
                    </p>
                    <ul className="mt-6 space-y-2">
                      {[
                        "Shapefile + ISO 11783-10 TASKDATA.XML",
                        "PDF-Bericht mit Agronomendisclaimer",
                        "§67 PflSchG Ausbringungsprotokoll",
                      ].map((item) => (
                        <li key={item} className="flex items-center gap-2.5 text-sm text-gray-700">
                          <CheckIcon />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Step 3 visual */}
                <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-card">
                  <svg viewBox="0 0 400 260" className="w-full h-auto" aria-hidden="true">
                    <rect width="400" height="260" fill="#f8fafc" rx="8" />
                    {/* Document icon */}
                    <rect x="60" y="20" width="120" height="150" rx="6" fill="white" stroke="#e2e8f0" strokeWidth="1.5" />
                    <rect x="60" y="20" width="120" height="32" rx="6" fill="#16a34a" opacity="0.9" />
                    <text x="120" y="40" textAnchor="middle" fill="white" fontSize="10" fontFamily="sans-serif" fontWeight="600">Applikationskarte</text>
                    {/* Lines of text */}
                    {[72, 86, 100, 114, 128, 142].map((y) => (
                      <rect key={y} x="76" y={y} width={y % 24 === 0 ? 80 : 95} height="6" rx="2" fill="#e2e8f0" />
                    ))}
                    {/* Disclaimer stripe */}
                    <rect x="60" y="150" width="120" height="20" rx="0" fill="#fef9c3" opacity="0.9" />
                    <text x="120" y="163" textAnchor="middle" fill="#854d0e" fontSize="7" fontFamily="sans-serif">Agronomendisclaimer</text>
                    {/* File type chips */}
                    <rect x="200" y="25" width="70" height="28" rx="6" fill="#dcfce7" stroke="#bbf7d0" strokeWidth="1" />
                    <text x="235" y="43" textAnchor="middle" fill="#166534" fontSize="10" fontFamily="monospace" fontWeight="600">.SHP</text>
                    <rect x="280" y="25" width="90" height="28" rx="6" fill="#dcfce7" stroke="#bbf7d0" strokeWidth="1" />
                    <text x="325" y="43" textAnchor="middle" fill="#166534" fontSize="10" fontFamily="monospace" fontWeight="600">TASKDATA</text>
                    <rect x="200" y="63" width="70" height="28" rx="6" fill="#fef9c3" stroke="#fef08a" strokeWidth="1" />
                    <text x="235" y="81" textAnchor="middle" fill="#854d0e" fontSize="10" fontFamily="monospace" fontWeight="600">.PDF</text>
                    <rect x="280" y="63" width="90" height="28" rx="6" fill="#f0fdf4" stroke="#bbf7d0" strokeWidth="1" />
                    <text x="325" y="81" textAnchor="middle" fill="#166534" fontSize="10" fontFamily="monospace" fontWeight="600">REST API</text>
                    {/* Zone map mini */}
                    <rect x="200" y="110" width="170" height="95" rx="8" fill="#0a1f0f" />
                    <polygon points="210,120 290,115 300,175 205,180" fill="#16a34a" opacity="0.7" />
                    <polygon points="295,115 360,120 358,178 300,175" fill="#f59e0b" opacity="0.6" />
                    <text x="285" y="205" textAnchor="middle" fill="#94a3b8" fontSize="8" fontFamily="monospace">Vorschau Ausbringungszonen</text>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ==================================================================
            PRICING
            ================================================================== */}
        <section id="preise" className="bg-gray-50 py-24 lg:py-32">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {/* Header */}
            <div className="mx-auto max-w-2xl text-center mb-12">
              <p className="text-sm font-semibold uppercase tracking-widest text-agrolens-600 mb-3">
                Preise
              </p>
              <h2
                className="text-4xl font-extrabold text-gray-900 sm:text-5xl"
                style={{ letterSpacing: "-0.03em" }}
              >
                Transparent. Skalierbar.
                <br />
                <span className="text-agrolens-600">Sofort rentabel.</span>
              </h2>
              <p className="mt-5 text-lg text-gray-600">
                Alle Pläne beinhalten eine 14-tägige kostenlose Testphase.
              </p>

              {/* Free tier callout */}
              <div className="mt-6 inline-flex items-center gap-3 rounded-xl border border-agrolens-200 bg-agrolens-50 px-5 py-3">
                <svg className="h-5 w-5 flex-shrink-0 text-agrolens-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-sm text-agrolens-800">
                  <strong className="font-semibold">Basis-Plan kostenlos:</strong> 1 Feld · bis zu 15 ha · NDVI-Analyse · kein Export · dauerhaft gratis
                </span>
                <Link href="/signup" className="flex-shrink-0 text-sm font-semibold text-agrolens-600 hover:text-agrolens-700 transition-colors">
                  Jetzt starten &rarr;
                </Link>
              </div>

              {/* Toggle */}
              <div className="mt-8 inline-flex items-center rounded-xl border border-gray-200 bg-white p-1 shadow-sm">
                <button
                  type="button"
                  onClick={() => setAnnual(false)}
                  className={`rounded-lg px-5 py-2 text-sm font-semibold transition-all duration-150 ${
                    !annual
                      ? "bg-agrolens-600 text-white shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  Monatlich
                </button>
                <button
                  type="button"
                  onClick={() => setAnnual(true)}
                  className={`rounded-lg px-5 py-2 text-sm font-semibold transition-all duration-150 ${
                    annual
                      ? "bg-agrolens-600 text-white shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  Jährlich
                  <span className="ml-1.5 rounded-full bg-earth-100 px-2 py-0.5 text-xs font-bold text-earth-700">
                    –20 %
                  </span>
                </button>
              </div>
            </div>

            {/* Plan cards */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
              {plans.map((plan) => (
                <div
                  key={plan.name}
                  className={`relative flex flex-col rounded-2xl bg-white p-8 shadow-card transition-shadow duration-200 hover:shadow-card-hover ${
                    plan.highlighted
                      ? "ring-2 ring-agrolens-600"
                      : "ring-1 ring-gray-200"
                  }`}
                >
                  {/* Recommended badge */}
                  {plan.badge && (
                    <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                      <span className="inline-flex items-center rounded-full bg-agrolens-600 px-4 py-1 text-xs font-bold text-white shadow-sm">
                        {plan.badge}
                      </span>
                    </div>
                  )}

                  {/* Plan header */}
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">{plan.name}</h3>
                    <p className="mt-1 text-sm text-gray-500">{plan.description}</p>
                    <p className="mt-1 text-xs font-medium text-agrolens-600 bg-agrolens-50 rounded-md px-2 py-0.5 inline-block">
                      {plan.limits}
                    </p>
                  </div>

                  {/* Price */}
                  <div className="mt-6 pb-6 border-b border-gray-100">
                    {annual ? (
                      <>
                        <p className="flex items-baseline gap-1">
                          <span
                            className="text-4xl font-extrabold text-gray-900"
                            style={{ letterSpacing: "-0.02em" }}
                          >
                            € {Math.round(plan.annualPrice / 12)}
                          </span>
                          <span className="text-base text-gray-500 font-normal">/ Monat</span>
                        </p>
                        <p className="mt-1 text-sm text-gray-500">
                          € {plan.annualPrice} / Jahr — 2 Monate gratis
                        </p>
                      </>
                    ) : (
                      <>
                        <p className="flex items-baseline gap-1">
                          <span
                            className="text-4xl font-extrabold text-gray-900"
                            style={{ letterSpacing: "-0.02em" }}
                          >
                            € {plan.monthlyPrice}
                          </span>
                          <span className="text-base text-gray-500 font-normal">/ Monat</span>
                        </p>
                        <p className="mt-1 text-sm text-gray-500">
                          Jährlich € {plan.annualPrice} (20 % Rabatt)
                        </p>
                      </>
                    )}
                  </div>

                  {/* Feature list */}
                  <ul className="mt-6 flex-1 space-y-3">
                    {plan.features.map((feature) => (
                      <li key={feature.text} className="flex items-start gap-3">
                        {feature.included ? <CheckIcon /> : <XIcon />}
                        <span
                          className={`text-sm ${
                            feature.included ? "text-gray-700" : "text-gray-400"
                          }`}
                        >
                          {feature.text}
                        </span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA */}
                  <Link
                    href={plan.href}
                    className={`mt-8 block rounded-xl px-6 py-3 text-center text-sm font-semibold transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-agrolens-500 focus:ring-offset-2 ${
                      plan.highlighted
                        ? "bg-agrolens-600 text-white shadow-sm hover:bg-agrolens-700"
                        : "bg-gray-50 text-gray-900 ring-1 ring-gray-200 hover:bg-gray-100"
                    }`}
                  >
                    {plan.cta}
                  </Link>
                </div>
              ))}
            </div>

            {/* Footnote */}
            <p className="mt-10 text-center text-sm text-gray-400">
              Alle Preise zzgl. MwSt. · Keine Mindestvertragslaufzeit bei Monatsplänen ·{" "}
              <Link href="/agb" className="underline hover:text-gray-600 transition-colors">
                AGB
              </Link>
            </p>
          </div>
        </section>

        {/* ==================================================================
            DARK CTA
            ================================================================== */}
        <section className="bg-agrolens-950 py-24 lg:py-32">
          <div className="mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8">
            {/* Decorative background text */}
            <p
              className="mb-6 text-sm font-semibold uppercase tracking-widest text-agrolens-600"
            >
              Jetzt starten
            </p>
            <h2
              className="text-4xl font-extrabold text-white sm:text-6xl"
              style={{ letterSpacing: "-0.03em" }}
            >
              Bereit, Pestizidkosten
              <br />
              zu senken?
            </h2>
            <p className="mx-auto mt-6 max-w-xl text-lg text-agrolens-300">
              Starten Sie kostenlos. Keine Kreditkarte erforderlich.
              Ihre erste Ausbringungskarte in unter 24 Stunden.
            </p>

            <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
              <Link
                href="/signup"
                className="inline-flex items-center rounded-xl bg-white px-8 py-4 text-base font-semibold text-agrolens-700 shadow-lg hover:bg-agrolens-50 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-agrolens-950 transition-all duration-150"
              >
                Kostenlos starten
              </Link>
              <Link
                href="/contact"
                className="inline-flex items-center rounded-xl border border-agrolens-700 px-8 py-4 text-base font-semibold text-agrolens-300 hover:border-agrolens-500 hover:text-white focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-agrolens-950 transition-all duration-150"
              >
                Demo buchen
              </Link>
            </div>

            {/* Trust signals in dark */}
            <div className="mt-12 flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
              {[
                "14 Tage kostenlos testen",
                "DSGVO-konform",
                "Deutscher Support",
                "Ende-zu-Ende verschlüsselt",
              ].map((item) => (
                <div key={item} className="flex items-center gap-2 text-sm text-agrolens-400">
                  <svg className="h-4 w-4 text-agrolens-600" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clipRule="evenodd" />
                  </svg>
                  {item}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ==================================================================
            FOOTER
            ================================================================== */}
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
                  Satellitengestützte Präzisionslandwirtschaft für
                  europäische Betriebe.
                </p>
              </div>

              {/* Nav links */}
              <nav className="flex flex-wrap gap-x-6 gap-y-2" aria-label="Footer-Navigation">
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
                © {new Date().getFullYear()} AgroLens. Alle Rechte vorbehalten.
              </p>
              <p className="text-xs text-agrolens-700">
                Contains modified Copernicus Sentinel data {new Date().getFullYear()}. · ISOBUS® ist ein eingetragenes Warenzeichen der AEF.
              </p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
