"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import type { Field } from "@/lib/api/fields";

const HEALTH_FILL: Record<string, string> = {
  normal: "#22c55e",
  mild_stress: "#f59e0b",
  significant_stress: "#ef4444",
  unknown: "#94a3b8",
};

interface Props {
  fields: Field[];
}

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN ?? "";

export default function FieldOverviewMap({ fields }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const router = useRouter();

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
      if (!fields.length) return;

      const geojson: GeoJSON.FeatureCollection = {
        type: "FeatureCollection",
        features: fields.map((f) => ({
          type: "Feature",
          properties: { id: f.id, name: f.name, health: "unknown" },
          geometry: f.geometry,
        })),
      };

      map.addSource("fields", { type: "geojson", data: geojson });

      map.addLayer({
        id: "fields-fill",
        type: "fill",
        source: "fields",
        paint: {
          "fill-color": [
            "match",
            ["get", "health"],
            "normal", HEALTH_FILL.normal,
            "mild_stress", HEALTH_FILL.mild_stress,
            "significant_stress", HEALTH_FILL.significant_stress,
            HEALTH_FILL.unknown,
          ],
          "fill-opacity": 0.6,
        },
      });

      map.addLayer({
        id: "fields-outline",
        type: "line",
        source: "fields",
        paint: { "line-color": "#ffffff", "line-width": 1.5 },
      });

      // Fit map to all fields
      const coords = fields
        .flatMap((f) => {
          if (f.geometry.type === "Polygon") return f.geometry.coordinates.flat();
          if (f.geometry.type === "MultiPolygon") return f.geometry.coordinates.flat(2);
          return [];
        })
        .filter((c): c is [number, number] => Array.isArray(c) && c.length >= 2);

      if (coords.length) {
        const bounds = coords.reduce(
          (b, c) => b.extend(c as [number, number]),
          new mapboxgl.LngLatBounds(coords[0], coords[0])
        );
        map.fitBounds(bounds, { padding: 40, maxZoom: 14 });
      }

      map.on("click", "fields-fill", (e) => {
        const id = e.features?.[0]?.properties?.id;
        if (id) router.push(`/dashboard/fields/${id}`);
      });

      map.on("mouseenter", "fields-fill", () => {
        map.getCanvas().style.cursor = "pointer";
      });
      map.on("mouseleave", "fields-fill", () => {
        map.getCanvas().style.cursor = "";
      });
    });

    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [fields, router]);

  return (
    <div ref={containerRef} className="w-full h-[360px] rounded-xl overflow-hidden border border-gray-200" />
  );
}
