import type { Prescription } from "@/lib/api/prescriptions";

interface Props {
  prescription: Prescription;
}

export default function ZoneBreakdownTable({ prescription }: Props) {
  const total = prescription.zones.reduce((s, z) => s + z.area_ha, 0);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-100 text-left text-xs text-gray-500 uppercase tracking-wide">
            <th className="pb-2 pr-4 font-medium">Zone</th>
            <th className="pb-2 pr-4 font-medium text-right">Fläche (ha)</th>
            <th className="pb-2 pr-4 font-medium text-right">Anteil</th>
            <th className="pb-2 font-medium text-right">Rate (L/ha)</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-50">
          {prescription.zones.map((z) => (
            <tr key={z.zone_label}>
              <td className="py-2.5 pr-4 font-medium text-gray-800">{z.zone_label}</td>
              <td className="py-2.5 pr-4 text-right text-gray-600">{z.area_ha.toFixed(2)}</td>
              <td className="py-2.5 pr-4 text-right text-gray-500">
                {total > 0 ? ((z.area_ha / total) * 100).toFixed(0) : "—"}%
              </td>
              <td className="py-2.5 text-right font-semibold text-gray-800">
                {z.rate_l_ha.toFixed(1)}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="border-t border-gray-200">
            <td className="pt-2.5 pr-4 font-medium text-gray-900">Gesamt</td>
            <td className="pt-2.5 pr-4 text-right font-medium text-gray-900">
              {total.toFixed(2)}
            </td>
            <td className="pt-2.5 pr-4 text-right text-gray-500">100%</td>
            <td className="pt-2.5 text-right font-medium text-gray-900">
              {(
                prescription.zones.reduce((s, z) => s + z.rate_l_ha * z.area_ha, 0) / (total || 1)
              ).toFixed(1)}{" "}
              ⌀
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
