"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient } from "@/lib/api/client";
import { createField } from "@/lib/api/fields";
import FieldUploadForm from "@/components/fields/FieldUploadForm";
import FieldDrawMap from "@/components/fields/FieldDrawMap";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

interface Farm {
  id: string;
  name: string;
}

type Tab = "upload" | "draw";

const drawSchema = z.object({
  name: z.string().min(1, "Name erforderlich").max(120),
  crop_type: z.string().optional(),
  flik: z.string().max(18).optional(),
  planting_date: z.string().optional(),
});

type DrawValues = z.infer<typeof drawSchema>;

export default function NewFieldPage() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("upload");
  const [farms, setFarms] = useState<Farm[]>([]);
  const [farmId, setFarmId] = useState<string>("");
  const [drawnGeometry, setDrawnGeometry] = useState<GeoJSON.Geometry | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<DrawValues>({ resolver: zodResolver(drawSchema) });

  useEffect(() => {
    apiClient
      .get<Farm[]>("/api/v1/farms")
      .then((data) => {
        setFarms(data);
        if (data.length > 0) setFarmId(data[0].id);
      })
      .catch(() => setLoadError("Betriebe konnten nicht geladen werden."));
  }, []);

  async function onDrawSubmit(values: DrawValues) {
    if (!drawnGeometry) {
      setApiError("Bitte zeichnen Sie zuerst einen Feldumriss auf der Karte.");
      return;
    }
    if (!farmId) return;
    setSubmitting(true);
    setApiError(null);
    try {
      await createField({
        farm_id: farmId,
        name: values.name,
        crop_type: values.crop_type || undefined,
        flik: values.flik || undefined,
        planting_date: values.planting_date || undefined,
        geometry: drawnGeometry,
      });
      router.push("/dashboard/fields");
      router.refresh();
    } catch (err: unknown) {
      setApiError(err instanceof Error ? err.message : "Unbekannter Fehler");
    } finally {
      setSubmitting(false);
    }
  }

  if (loadError) {
    return (
      <div className="max-w-2xl mx-auto py-8 px-4">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {loadError}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Neues Feld anlegen</h1>

      {farms.length > 1 && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-1">Betrieb</label>
          <select
            value={farmId}
            onChange={(e) => setFarmId(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          >
            {farms.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Tab switcher */}
      <div className="flex border-b border-gray-200 mb-6">
        {(["upload", "draw"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-5 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              tab === t
                ? "border-green-600 text-green-700"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {t === "upload" ? "Datei hochladen" : "Auf Karte zeichnen"}
          </button>
        ))}
      </div>

      {tab === "upload" && farmId && <FieldUploadForm farmId={farmId} />}

      {tab === "draw" && (
        <form onSubmit={handleSubmit(onDrawSubmit)} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Feldname *</label>
            <input
              {...register("name")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="z.B. Nordfeld Müller"
            />
            {errors.name && (
              <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Fruchtart</label>
            <input
              {...register("crop_type")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="z.B. Winterweizen"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Feldumriss zeichnen *
            </label>
            <FieldDrawMap onPolygon={setDrawnGeometry} />
            {!drawnGeometry && (
              <p className="text-xs text-gray-500 mt-1">
                Klicken Sie auf das Polygon-Werkzeug und zeichnen Sie Ihr Feld.
              </p>
            )}
            {drawnGeometry && (
              <p className="text-green-600 text-xs mt-1">Polygon gezeichnet</p>
            )}
          </div>

          {apiError && (
            <p className="text-red-500 text-sm bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {apiError}
            </p>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full bg-green-600 text-white py-2.5 rounded-lg font-medium text-sm hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {submitting ? "Wird gespeichert…" : "Feld anlegen"}
          </button>
        </form>
      )}
    </div>
  );
}
