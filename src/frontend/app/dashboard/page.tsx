"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api/client";
import { getFields, type Field } from "@/lib/api/fields";
import FieldOverviewMap from "@/components/dashboard/FieldOverviewMap";
import SummaryPanel from "@/components/dashboard/SummaryPanel";
import PlanUsageBar from "@/components/dashboard/PlanUsageBar";

interface Farm {
  id: string;
  name: string;
}

interface UsageData {
  hectares_used: number;
  plan_limit: number | null;
  usage_pct: number;
}

export default function DashboardPage() {
  const [fields, setFields] = useState<Field[]>([]);
  const [usage, setUsage] = useState<UsageData>({ hectares_used: 0, plan_limit: null, usage_pct: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [farms, usageData] = await Promise.all([
          apiClient.get<Farm[]>("/api/v1/farms/"),
          apiClient.get<UsageData>("/api/v1/account/usage"),
        ]);
        const allFields = await Promise.all(farms.map((f) => getFields(f.id)));
        setFields(allFields.flat());
        setUsage(usageData);
      } catch {
        // Silently degrade — map shows empty state
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 md:px-6 space-y-5">
      <h1 className="text-xl font-bold text-gray-900">Übersicht</h1>

      {loading ? (
        <div className="text-sm text-gray-400 py-8 text-center">Daten werden geladen…</div>
      ) : (
        <>
          <FieldOverviewMap fields={fields} />
          <SummaryPanel fields={fields} />
          <PlanUsageBar
            hectaresUsed={usage.hectares_used}
            planLimit={usage.plan_limit}
            usagePct={usage.usage_pct}
          />
        </>
      )}
    </div>
  );
}
