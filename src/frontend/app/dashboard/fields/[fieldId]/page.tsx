"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getField, type Field } from "@/lib/api/fields";
import { getPrescriptions, createPrescription, type Prescription, type ApplicationType } from "@/lib/api/prescriptions";
import { getNdviSeries, getHealthSummary, type NdviPoint, type HealthSummary } from "@/lib/api/analytics";
import NdviChart from "@/components/fields/NdviChart";
import PrescriptionZoneMap from "@/components/fields/PrescriptionZoneMap";
import ZoneBreakdownTable from "@/components/fields/ZoneBreakdownTable";
import ExportButtons from "@/components/fields/ExportButtons";
import { ChevronLeft, Plus, X } from "lucide-react";

export default function FieldDetailPage() {
  const { fieldId } = useParams<{ fieldId: string }>();

  const [field, setField] = useState<Field | null>(null);
  const [ndviData, setNdviData] = useState<NdviPoint[]>([]);
  const [health, setHealth] = useState<HealthSummary | null>(null);
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [selectedPx, setSelectedPx] = useState<Prescription | null>(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  // Modal form state
  const [modalAppType, setModalAppType] = useState<ApplicationType>("fungicide");
  const [modalBaseRate, setModalBaseRate] = useState<string>("200");
  const [modalNZones, setModalNZones] = useState<string>("3");
  const [modalSubmitting, setModalSubmitting] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [f, ndvi, h, px] = await Promise.all([
          getField(fieldId),
          getNdviSeries(fieldId),
          getHealthSummary(fieldId),
          getPrescriptions(fieldId),
        ]);
        setField(f);
        setNdviData(ndvi);
        setHealth(h);
        setPrescriptions(px);
        if (px.length) setSelectedPx(px[0]);
      } catch {
        // partial load — individual sections handle empty state
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [fieldId]);

  async function handleGeneratePrescription() {
    setModalSubmitting(true);
    setModalError(null);
    try {
      const px = await createPrescription(fieldId, {
        application_type: modalAppType,
        base_rate_l_ha: parseFloat(modalBaseRate),
        n_zones: parseInt(modalNZones, 10),
      });
      setPrescriptions((prev) => [px, ...prev]);
      setSelectedPx(px);
      setShowModal(false);
    } catch (err: unknown) {
      setModalError(err instanceof Error ? err.message : "Fehler");
    } finally {
      setModalSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-8 px-4 text-center text-sm text-gray-400">
        Felddaten werden geladen…
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-6 px-4 md:px-6 space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/dashboard/fields" className="text-gray-400 hover:text-gray-600">
          <ChevronLeft size={20} />
        </Link>
        <h1 className="text-xl font-bold text-gray-900">{field?.name ?? fieldId}</h1>
        {health && (
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
            health.status === "normal" ? "bg-green-100 text-green-700"
            : health.status === "mild_stress" ? "bg-amber-100 text-amber-700"
            : health.status === "significant_stress" ? "bg-red-100 text-red-700"
            : "bg-gray-100 text-gray-500"
          }`}>
            {health.status === "normal" ? "Normal"
              : health.status === "mild_stress" ? "Leichter Stress"
              : health.status === "significant_stress" ? "Signifikanter Stress"
              : "Berechnung…"}
          </span>
        )}
      </div>

      {/* NDVI Chart */}
      <NdviChart data={ndviData} />

      {/* Prescription section */}
      <div className="bg-white rounded-xl border border-gray-100 p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-900">Applikationsplan</h2>
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-1.5 text-sm bg-green-600 text-white px-3 py-1.5 rounded-lg hover:bg-green-700 transition-colors"
          >
            <Plus size={15} /> Plan erstellen
          </button>
        </div>

        {prescriptions.length > 1 && (
          <div className="flex gap-2 flex-wrap">
            {prescriptions.map((px) => (
              <button
                key={px.id}
                onClick={() => setSelectedPx(px)}
                className={`text-xs px-3 py-1 rounded-full border transition-colors ${
                  selectedPx?.id === px.id
                    ? "border-green-600 bg-green-50 text-green-700"
                    : "border-gray-200 text-gray-500 hover:bg-gray-50"
                }`}
              >
                {px.application_type} · {new Date(px.created_at).toLocaleDateString("de-DE")}
              </button>
            ))}
          </div>
        )}

        {selectedPx ? (
          <>
            <PrescriptionZoneMap prescription={selectedPx} />
            <ZoneBreakdownTable prescription={selectedPx} />
            <ExportButtons fieldId={fieldId} prescription={selectedPx} />
            {selectedPx.disclaimer && (
              <p className="text-xs text-gray-400 italic border-t border-gray-50 pt-3">
                {selectedPx.disclaimer}
              </p>
            )}
          </>
        ) : (
          <p className="text-sm text-gray-400 py-4 text-center">
            Noch kein Applikationsplan vorhanden. Klicken Sie auf „Plan erstellen".
          </p>
        )}
      </div>

      {/* Generation modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-sm p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">Plan erstellen</h3>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                <X size={18} />
              </button>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Applikationstyp</label>
              <select
                value={modalAppType}
                onChange={(e) => setModalAppType(e.target.value as ApplicationType)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
              >
                <option value="fungicide">Fungizid</option>
                <option value="herbicide">Herbizid</option>
                <option value="insecticide">Insektizid</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Basisrate (L/ha)</label>
              <input
                type="number"
                min="1"
                max="1000"
                step="10"
                value={modalBaseRate}
                onChange={(e) => setModalBaseRate(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Anzahl Zonen</label>
              <select
                value={modalNZones}
                onChange={(e) => setModalNZones(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
              >
                {[2, 3, 4, 5].map((n) => (
                  <option key={n} value={n}>{n} Zonen</option>
                ))}
              </select>
            </div>

            {modalError && (
              <p className="text-red-500 text-xs">{modalError}</p>
            )}

            <button
              onClick={handleGeneratePrescription}
              disabled={modalSubmitting}
              className="w-full bg-green-600 text-white py-2.5 rounded-lg font-medium text-sm hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              {modalSubmitting ? "Wird berechnet…" : "Plan berechnen"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
