"use client";

import { useState } from "react";
import { Download, Copy, Check } from "lucide-react";
import { getExportUrl, type ApplicationType, type Prescription } from "@/lib/api/prescriptions";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";

interface Props {
  fieldId: string;
  prescription: Prescription;
}

async function downloadExport(
  fieldId: string,
  applicationType: ApplicationType,
  format: "shapefile" | "taskdata" | "pdf",
  filename: string
) {
  const supabase = createSupabaseBrowserClient();
  const { data: { session } } = await supabase.auth.getSession();
  const url = getExportUrl(fieldId, applicationType, format);

  const response = await fetch(url, {
    headers: session?.access_token
      ? { Authorization: `Bearer ${session.access_token}` }
      : {},
  });

  if (!response.ok) throw new Error(`Export fehlgeschlagen: ${response.status}`);

  const blob = await response.blob();
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

export default function ExportButtons({ fieldId, prescription }: Props) {
  const [copying, setCopying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const appType = prescription.application_type;

  async function handleCopyGeoJSON() {
    setCopying(true);
    setError(null);
    try {
      const fc: GeoJSON.FeatureCollection = {
        type: "FeatureCollection",
        features: prescription.zones.map((z) => ({
          type: "Feature",
          properties: { zone_label: z.zone_label, rate_l_ha: z.rate_l_ha },
          geometry: z.geometry,
        })),
      };
      await navigator.clipboard.writeText(JSON.stringify(fc, null, 2));
      setTimeout(() => setCopying(false), 1800);
    } catch {
      setError("Kopieren fehlgeschlagen");
      setCopying(false);
    }
  }

  async function handleDownload(
    format: "shapefile" | "taskdata" | "pdf",
    filename: string
  ) {
    setError(null);
    try {
      await downloadExport(fieldId, appType, format, filename);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Download fehlgeschlagen");
    }
  }

  return (
    <div className="space-y-3">
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Export</p>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => handleDownload("shapefile", `prescription_${appType}.zip`)}
          className="flex items-center gap-1.5 text-sm px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
        >
          <Download size={15} /> Shapefile
        </button>
        <button
          onClick={() => handleDownload("taskdata", `TASKDATA_${appType}.XML`)}
          className="flex items-center gap-1.5 text-sm px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
        >
          <Download size={15} /> TASKDATA.XML
        </button>
        <button
          onClick={() => handleDownload("pdf", `prescription_${appType}.pdf`)}
          className="flex items-center gap-1.5 text-sm px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
        >
          <Download size={15} /> PDF-Bericht
        </button>
        <button
          onClick={handleCopyGeoJSON}
          className="flex items-center gap-1.5 text-sm px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
        >
          {copying ? <Check size={15} className="text-green-600" /> : <Copy size={15} />}
          {copying ? "Kopiert!" : "GeoJSON kopieren"}
        </button>
      </div>
      {error && <p className="text-red-500 text-xs">{error}</p>}
    </div>
  );
}
