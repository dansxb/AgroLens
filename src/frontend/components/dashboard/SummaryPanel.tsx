import type { Field } from "@/lib/api/fields";

interface Props {
  fields: Field[];
}

interface Stat {
  label: string;
  value: string;
  sub?: string;
}

/** Top-border accent color for each stat card, in order. */
const CARD_ACCENTS = [
  "border-t-agrolens-500",
  "border-t-earth-500",
  "border-t-agrolens-400",
  "border-t-amber-500",
] as const;

/**
 * SummaryPanel — four premium stat cards displayed in a responsive grid.
 *
 * Each card shows a KPI (fields count, total hectares, top crop, active
 * alerts) with a colored top-border accent so the eye can orient instantly.
 * All business logic (aggregations, labels) is kept intact; only the visual
 * layer is upgraded.
 */
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
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      {stats.map((s, i) => (
        <div
          key={s.label}
          className={`bg-white rounded-2xl shadow-sm ring-1 ring-black/5 px-5 py-5 border-t-2 ${CARD_ACCENTS[i]}`}
        >
          <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-3">
            {s.label}
          </p>
          <p className="text-3xl font-extrabold text-gray-900 tabular-nums leading-none">
            {s.value}
          </p>
          {s.sub && (
            <p className="text-xs text-gray-400 mt-2">{s.sub}</p>
          )}
        </div>
      ))}
    </div>
  );
}
