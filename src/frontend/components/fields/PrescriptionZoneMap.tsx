"use client";

import { useEffect, useRef } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import type { Prescription } from "@/lib/api/prescriptions";

const ZONE_COLORS = ["#22c55e", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"];
const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN ?? "";

interface Props {
  prescription: Prescription;
}

export default function PrescriptionZoneMap({ prescription }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);

  const compositeAgeDays =
    (prescription as unknown as { composite_age_days?: number }).composite_age_days ?? null;
  const stale = compositeAgeDays !== null && compositeAgeDays > 21;

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;
    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/satellite-streets-v12",
      center: [10.4515, 51.1657],
      zoom: 5,
    });

    map.addControl(new mapboxgl.NavigationControl(), "top-right");

    map.on("load", () => {
      const features: GeoJSON.Feature[] = prescription.zones.map((z, i) => ({
        type: "Feature",
        properties: {
          zone_label: z.zone_label,
          rate: z.rate_l_ha,
          color: ZONE_COLORS[i % ZONE_COLORS.length],
        },
        geometry: z.geometry,
      }));

      const geojson: GeoJSON.FeatureCollection = { type: "FeatureCollection", features };

      map.addSource("zones", { type: "geojson", data: geojson });
      map.addLayer({
        id: "zones-fill",
        type: "fill",
        source: "zones",
        paint: {
          "fill-color": ["get", "color"],
          "fill-opacity": 0.65,
        },
      });
      map.addLayer({
        id: "zones-outline",
        type: "line",
        source: "zones",
        paint: { "line-color": "#ffffff", "line-width": 1.5 },
      });

      // Fit bounds
      const coords = prescription.zones
        .flatMap((z) => {
          if (z.geometry.type === "Polygon") return z.geometry.coordinates.flat();
          if (z.geometry.type === "MultiPolygon") return z.geometry.coordinates.flat(2);
          return [];
        })
        .filter((c): c is [number, number] => Array.isArray(c) && c.length >= 2);

      if (coords.length) {
        const bounds = coords.reduce(
          (b, c) => b.extend(c as [number, number]),
          new mapboxgl.LngLatBounds(coords[0], coords[0])
        );
        map.fitBounds(bounds, { padding: 32, maxZoom: 16 });
      }

      // Tooltip
      const popup = new mapboxgl.Popup({ closeButton: false, closeOnClick: false });
      map.on("mouseenter", "zones-fill", (e) => {
        map.getCanvas().style.cursor = "pointer";
        const props = e.features?.[0]?.properties;
        if (props) {
          popup
            .setLngLat(e.lngLat)
            .setHTML(`<strong>${props.zone_label}</strong><br/>${props.rate} L/ha`)
            .addTo(map);
        }
      });
      map.on("mouseleave", "zones-fill", () => {
        map.getCanvas().style.cursor = "";
        popup.remove();
      });
    });

    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [prescription]);

  return (
    <div>
      {stale && (
        <div className="mb-2 bg-amber-50 border border-amber-200 text-amber-700 text-xs px-3 py-2 rounded-lg">
          Hinweis: Das zugrunde liegende Satellitenbild ist {compositeAgeDays} Tage alt.
        </div>
      )}
      <div className="relative">
        <div ref={containerRef} className="w-full h-[320px] rounded-xl overflow-hidden border border-gray-200" />
        {/* Legend */}
        <div className="absolute bottom-3 left-3 bg-white bg-opacity-90 rounded-lg px-3 py-2 shadow text-xs space-y-1">
          {prescription.zones.map((z, i) => (
            <div key={z.zone_label} className="flex items-center gap-2">
              <span
                className="inline-block w-3 h-3 rounded-sm"
                style={{ backgroundColor: ZONE_COLORS[i % ZONE_COLORS.length] }}
              />
              {z.zone_label} — {z.rate_l_ha} L/ha
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
