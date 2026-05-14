import Link from "next/link";

/**
 * AgroLens public landing page.
 *
 * Hero section explaining the product value proposition with a clear
 * CTA button directing visitors to sign up or log in.
 */
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* ----------------------------------------------------------------
          Navigation bar
          ---------------------------------------------------------------- */}
      <nav className="border-b border-gray-100 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-2">
              {/* Logo mark */}
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-agrolens-600">
                <svg
                  className="h-5 w-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3.75 3v11.25A2.25 2.25 0 006 16.5h12a2.25 2.25 0 002.25-2.25V3m-18 0h18m-9 12.75v3.75M12 19.5H9.75M12 19.5h2.25"
                  />
                </svg>
              </div>
              <span className="text-xl font-bold text-gray-900">AgroLens</span>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/login"
                className="text-sm font-medium text-gray-600 hover:text-gray-900"
              >
                Sign in
              </Link>
              <Link href="/signup" className="btn-primary text-sm">
                Start free trial
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* ----------------------------------------------------------------
          Hero section
          ---------------------------------------------------------------- */}
      <main>
        <section className="relative overflow-hidden bg-gradient-to-b from-agrolens-50 to-white">
          <div className="mx-auto max-w-7xl px-4 pb-24 pt-20 sm:px-6 sm:pb-32 lg:px-8 lg:pt-28">
            <div className="mx-auto max-w-3xl text-center">
              {/* Badge */}
              <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-agrolens-200 bg-agrolens-50 px-4 py-1.5">
                <span className="h-2 w-2 rounded-full bg-agrolens-500" />
                <span className="text-sm font-medium text-agrolens-700">
                  Satellite AI · Pesticide Reduction · EU CAP Compliant
                </span>
              </div>

              {/* Headline */}
              <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl">
                Precision Pesticide Intelligence
                <span className="block text-agrolens-600">
                  Powered by Satellite AI
                </span>
              </h1>

              {/* Sub-headline */}
              <p className="mt-6 text-lg leading-8 text-gray-600 sm:text-xl">
                AgroLens analyses Sentinel-2 satellite imagery for every field you
                manage and generates Variable Rate Application maps that tell you
                exactly where to apply more — or less — pesticide.
              </p>

              {/* Key stats */}
              <p className="mt-4 text-base text-gray-500">
                Typical results:{" "}
                <strong className="text-gray-900">20–40% pesticide reduction</strong>{" "}
                · Saves{" "}
                <strong className="text-gray-900">€20–50 / ha / season</strong> ·
                Updated every 10 days
              </p>

              {/* CTA buttons */}
              <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
                <Link href="/signup" className="btn-primary px-8 py-3 text-base">
                  Start your free trial
                </Link>
                <Link
                  href="/login"
                  className="btn-secondary px-8 py-3 text-base"
                >
                  Sign in to dashboard
                </Link>
              </div>

              {/* Trust signal */}
              <p className="mt-6 text-sm text-gray-400">
                No credit card required · Free up to 50 ha · Cancel anytime
              </p>
            </div>
          </div>
        </section>

        {/* ----------------------------------------------------------------
            Feature pillars section
            ---------------------------------------------------------------- */}
        <section className="bg-white py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
                How AgroLens works
              </h2>
              <p className="mt-4 text-lg text-gray-600">
                From satellite pass to prescription map in under 24 hours.
              </p>
            </div>

            <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              {[
                {
                  step: "01",
                  title: "Upload field boundaries",
                  description:
                    "Draw your fields directly on the map or upload a GeoJSON / KML file. " +
                    "AgroLens immediately begins monitoring your fields.",
                  icon: (
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497z"
                    />
                  ),
                },
                {
                  step: "02",
                  title: "Satellite AI analysis",
                  description:
                    "Our pipeline automatically retrieves Sentinel-2 multispectral imagery, " +
                    "computes NDVI and NDRE vegetation indices, and delineates three management " +
                    "zones per field using k-means clustering.",
                  icon: (
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5"
                    />
                  ),
                },
                {
                  step: "03",
                  title: "Download prescription maps",
                  description:
                    "Export ISOBUS-compatible shapefiles for your variable rate sprayer, " +
                    "download a PDF report for your agronomist, or access the data via our " +
                    "REST API.",
                  icon: (
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"
                    />
                  ),
                },
              ].map((feature) => (
                <div key={feature.step} className="card hover:shadow-md transition-shadow">
                  <div className="flex items-start gap-4">
                    <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-agrolens-100">
                      <svg
                        className="h-6 w-6 text-agrolens-600"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        strokeWidth={1.5}
                        aria-hidden="true"
                      >
                        {feature.icon}
                      </svg>
                    </div>
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-widest text-agrolens-500">
                        Step {feature.step}
                      </p>
                      <h3 className="mt-1 text-base font-semibold text-gray-900">
                        {feature.title}
                      </h3>
                      <p className="mt-2 text-sm leading-6 text-gray-600">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ----------------------------------------------------------------
            Pricing teaser
            ---------------------------------------------------------------- */}
        <section className="bg-agrolens-50 py-20">
          <div className="mx-auto max-w-4xl px-4 text-center sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900">
              Simple, per-hectare pricing
            </h2>
            <p className="mt-4 text-lg text-gray-600">
              Start free. Upgrade when you need more.
            </p>

            <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-3">
              {[
                {
                  name: "Starter",
                  ha: "Up to 100 ha",
                  monthly: "€49",
                  annual: "€470/yr",
                  cta: "Start free trial",
                },
                {
                  name: "Farmer",
                  ha: "Up to 500 ha",
                  monthly: "€199",
                  annual: "€1,910/yr",
                  cta: "Start free trial",
                  highlighted: true,
                },
                {
                  name: "Pro",
                  ha: "Up to 2,000 ha",
                  monthly: "€599",
                  annual: "€5,750/yr",
                  cta: "Start free trial",
                },
              ].map((plan) => (
                <div
                  key={plan.name}
                  className={`rounded-xl p-6 shadow-sm ${
                    plan.highlighted
                      ? "bg-agrolens-600 text-white ring-2 ring-agrolens-600"
                      : "bg-white text-gray-900"
                  }`}
                >
                  <h3
                    className={`text-lg font-semibold ${
                      plan.highlighted ? "text-white" : "text-gray-900"
                    }`}
                  >
                    {plan.name}
                  </h3>
                  <p
                    className={`mt-1 text-sm ${
                      plan.highlighted ? "text-agrolens-200" : "text-gray-500"
                    }`}
                  >
                    {plan.ha}
                  </p>
                  <p className="mt-4 text-3xl font-bold">
                    {plan.monthly}
                    <span
                      className={`text-base font-normal ${
                        plan.highlighted ? "text-agrolens-200" : "text-gray-500"
                      }`}
                    >
                      /mo
                    </span>
                  </p>
                  <p
                    className={`mt-1 text-sm ${
                      plan.highlighted ? "text-agrolens-200" : "text-gray-500"
                    }`}
                  >
                    or {plan.annual} (save 20%)
                  </p>
                  <Link
                    href="/signup"
                    className={`mt-6 block rounded-md px-4 py-2 text-center text-sm font-semibold ${
                      plan.highlighted
                        ? "bg-white text-agrolens-700 hover:bg-agrolens-50"
                        : "bg-agrolens-600 text-white hover:bg-agrolens-700"
                    } transition-colors`}
                  >
                    {plan.cta}
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ----------------------------------------------------------------
            Footer
            ---------------------------------------------------------------- */}
        <footer className="bg-white border-t border-gray-100">
          <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
            <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
              <p className="text-sm text-gray-500">
                © {new Date().getFullYear()} AgroLens. All rights reserved.
              </p>
              <p className="text-sm text-gray-400">
                Powered by free Sentinel-2 satellite data from ESA Copernicus.
              </p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
