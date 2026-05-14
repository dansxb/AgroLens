"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from "recharts";
import type { NdviPoint } from "@/lib/api/analytics";

interface Props {
  data: NdviPoint[];
}

function fmt(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("de-DE", { month: "short", day: "numeric" });
}

export default function NdviChart({ data }: Props) {
  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-40 bg-gray-50 rounded-xl border border-gray-100 text-sm text-gray-400">
        Analyse wird durchgeführt…
      </div>
    );
  }

  const chartData = data.map((p) => ({
    date: fmt(p.date),
    ndvi: parseFloat(p.mean_ndvi.toFixed(3)),
    upper: parseFloat((p.mean_ndvi + p.std_ndvi).toFixed(3)),
    lower: parseFloat(Math.max(0, p.mean_ndvi - p.std_ndvi).toFixed(3)),
  }));

  return (
    <div className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm">
      <p className="text-sm font-medium text-gray-700 mb-3">NDVI-Verlauf</p>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData} margin={{ top: 4, right: 8, bottom: 4, left: -10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} />
          <Tooltip
            formatter={(v: number) => v.toFixed(3)}
            labelFormatter={(l) => `Datum: ${l}`}
          />
          <ReferenceLine y={0.3} stroke="#ef4444" strokeDasharray="4 2" label={{ value: "Stress", position: "right", fontSize: 10 }} />
          <Line
            type="monotone"
            dataKey="upper"
            stroke="#bbf7d0"
            dot={false}
            strokeWidth={1}
            name="NDVI + σ"
          />
          <Line
            type="monotone"
            dataKey="lower"
            stroke="#bbf7d0"
            dot={false}
            strokeWidth={1}
            name="NDVI − σ"
          />
          <Line
            type="monotone"
            dataKey="ndvi"
            stroke="#16a34a"
            strokeWidth={2}
            dot={false}
            name="NDVI"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
