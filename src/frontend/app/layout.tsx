import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import OfflineBanner from "@/components/OfflineBanner";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: {
    default: "AgroLens — Precision Pesticide Intelligence",
    template: "%s | AgroLens",
  },
  description:
    "Satellite-powered Variable Rate Application maps for arable farming. " +
    "Reduce pesticide use by 20–40% with AI-driven precision recommendations.",
  keywords: [
    "precision agriculture",
    "VRA maps",
    "variable rate application",
    "pesticide reduction",
    "NDVI",
    "Sentinel-2",
    "farm management",
    "agritech",
  ],
  authors: [{ name: "AgroLens" }],
  creator: "AgroLens",
  publisher: "AgroLens",
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://agrolens.io",
    siteName: "AgroLens",
    title: "AgroLens — Precision Pesticide Intelligence",
    description:
      "Reduce pesticide use by 20–40% with AI-driven satellite prescription maps.",
    images: [
      {
        url: "https://agrolens.io/og-image.png",
        width: 1200,
        height: 630,
        alt: "AgroLens — Precision Pesticide Intelligence",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "AgroLens — Precision Pesticide Intelligence",
    description:
      "Reduce pesticide use by 20–40% with AI-driven satellite prescription maps.",
    images: ["https://agrolens.io/og-image.png"],
  },
  // PWA manifest
  manifest: "/manifest.json",
  icons: {
    icon: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
};

export const viewport: Viewport = {
  themeColor: "#16a34a",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

interface RootLayoutProps {
  children: React.ReactNode;
}

/**
 * Root layout — wraps every page with the global HTML shell.
 *
 * Applies Tailwind CSS globals and sets the document metadata.
 * The Inter font is loaded via a CSS @import in globals.css to avoid
 * the next/font bundle size impact during Phase 0 scaffolding.
 */
export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="de" className={`h-full ${inter.variable}`}>
      <body className="h-full bg-white font-sans">
        <OfflineBanner />
        {children}
      </body>
    </html>
  );
}
