"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import * as toGeoJSON from "@mapbox/togeojson";
import { createField } from "@/lib/api/fields";

const schema = z.object({
  name: z.string().min(1, "Name erforderlich").max(120),
  crop_type: z.string().optional(),
  flik: z.string().max(18).optional(),
  planting_date: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface Props {
  farmId: string;
}

function extractGeometry(geojson: GeoJSON.GeoJSON): GeoJSON.Geometry | null {
  if (geojson.type === "FeatureCollection" && geojson.features.length > 0) {
    return geojson.features[0].geometry;
  }
  if (geojson.type === "Feature") return geojson.geometry;
  if (geojson.type === "Polygon" || geojson.type === "MultiPolygon") {
    return geojson as GeoJSON.Geometry;
  }
  return null;
}

export default function FieldUploadForm({ farmId }: Props) {
  const router = useRouter();
  const fileRef = useRef<HTMLInputElement>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [geometry, setGeometry] = useState<GeoJSON.Geometry | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    setFileError(null);
    setGeometry(null);
    const file = e.target.files?.[0];
    if (!file) return;

    const text = await file.text();
    try {
      let geojson: GeoJSON.GeoJSON;
      if (file.name.endsWith(".kml")) {
        const dom = new DOMParser().parseFromString(text, "text/xml");
        geojson = toGeoJSON.kml(dom) as GeoJSON.GeoJSON;
      } else {
        geojson = JSON.parse(text) as GeoJSON.GeoJSON;
      }
      const geom = extractGeometry(geojson);
      if (!geom) {
        setFileError("Keine gültige Polygon-Geometrie gefunden.");
        return;
      }
      setGeometry(geom);
    } catch {
      setFileError("Datei konnte nicht gelesen werden. Bitte GeoJSON oder KML hochladen.");
    }
  }

  async function onSubmit(values: FormValues) {
    if (!geometry) {
      setFileError("Bitte eine GeoJSON- oder KML-Datei hochladen.");
      return;
    }
    setSubmitting(true);
    setApiError(null);
    try {
      await createField({
        farm_id: farmId,
        name: values.name,
        crop_type: values.crop_type || undefined,
        flik: values.flik || undefined,
        planting_date: values.planting_date || undefined,
        geometry,
      });
      router.push("/dashboard/fields");
      router.refresh();
    } catch (err: unknown) {
      setApiError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Feldname *</label>
        <input
          {...register("name")}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-agrolens-500 focus:border-transparent"
          placeholder="z.B. Nordfeld Müller"
        />
        {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Fruchtart</label>
        <input
          {...register("crop_type")}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-agrolens-500 focus:border-transparent"
          placeholder="z.B. Winterweizen"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">FLIK-Nummer</label>
        <input
          {...register("flik")}
          maxLength={18}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-agrolens-500 focus:border-transparent"
          placeholder="Optional — 18-stellige FLIK-Nummer"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Aussaatdatum</label>
        <input
          {...register("planting_date")}
          type="date"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-agrolens-500 focus:border-transparent"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Geometrie (GeoJSON oder KML) *</label>
        <input
          ref={fileRef}
          type="file"
          accept=".geojson,.kml,application/geo+json,application/vnd.google-earth.kml+xml"
          onChange={handleFile}
          className="block w-full text-sm text-gray-500 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-agrolens-50 file:text-agrolens-700 hover:file:bg-agrolens-100"
        />
        {fileError && <p className="text-red-500 text-xs mt-1">{fileError}</p>}
        {geometry && <p className="text-agrolens-600 text-xs mt-1">Geometrie geladen ({geometry.type})</p>}
      </div>

      {apiError && (
        <p className="text-red-500 text-sm bg-red-50 border border-red-200 rounded-lg px-3 py-2">
          {apiError}
        </p>
      )}

      <button
        type="submit"
        disabled={submitting}
        className="w-full bg-agrolens-600 text-white py-2.5 rounded-lg font-medium text-sm hover:bg-agrolens-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {submitting ? "Wird gespeichert…" : "Feld anlegen"}
      </button>
    </form>
  );
}
