"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/lib/api/client";
import { getFields, type Field } from "@/lib/api/fields";
import FieldList from "@/components/fields/FieldList";

interface Farm {
  id: string;
  name: string;
}

export default function FieldsPage() {
  const [fields, setFields] = useState<Field[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const farms = await apiClient.get<Farm[]>("/api/v1/farms/");
        const allFields = await Promise.all(farms.map((f) => getFields(f.id)));
        setFields(allFields.flat());
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Fehler beim Laden der Felder");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Meine Felder</h1>
        <Link
          href="/dashboard/fields/new"
          className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
        >
          + Neues Feld
        </Link>
      </div>

      {loading && (
        <div className="text-center py-16 text-gray-400 text-sm">Felder werden geladen…</div>
      )}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}
      {!loading && !error && <FieldList fields={fields} />}
    </div>
  );
}
