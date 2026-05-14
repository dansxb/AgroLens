import type { Field } from "@/lib/api/fields";

interface Props {
  fields: Field[];
}

interface Stat {
  label: string;
  value: string;
  sub?: string;
}

export default function SummaryPanel({ fields }: Props) {
  const totalHa = fields
    .reduce((sum, f) => sum + (f.area_ha ?? 0), 0)
    .toFixed(1);

  const cropCounts: Record<string, number> = {};
  for (const f of fields) {
    const crop = f.crop_type ?? "Unbekannt";
    cropCounts[crop] = (cropCounts[crop] ?? 0) + 1;
  }
  const topCrop =
    Object.entries(cropCounts).sort((a, b) => b[1] - a[1])[0]?.[0] ?? "—";

  const stats: Stat[] = [
    { label: "Felder", value: String(fields.length) },
    { label: "Gesamtfläche", value: `${totalHa} ha` },
    { label: "Häufigste Frucht", value: topCrop },
    { label: "Aktive Warnungen", value: "0", sub: "Keine Stresswarnungen" },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {stats.map((s) => (
        <div
          key={s.label}
          className="bg-white rounded-xl border border-gray-100 px-4 py-4 shadow-sm"
        >
          <p className="text-xs text-gray-500 mb-1">{s.label}</p>
          <p className="text-2xl font-bold text-gray-900">{s.value}</p>
          {s.sub && <p className="text-xs text-gray-400 mt-0.5">{s.sub}</p>}
        </div>
      ))}
    </div>
  );
}
