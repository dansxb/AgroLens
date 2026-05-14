"use client";

import { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { initDraw, extractPolygon, clearDraw } from "@/lib/mapbox/drawing";
import type MapboxDraw from "@mapbox/mapbox-gl-draw";

interface Props {
  onPolygon: (geometry: GeoJSON.Geometry | null) => void;
}

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN ?? "";

export default function FieldDrawMap({ onPolygon }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const drawRef = useRef<MapboxDraw | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    mapboxgl.accessToken = MAPBOX_TOKEN;
    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: "mapbox://styles/mapbox/satellite-streets-v12",
      center: [10.4515, 51.1657], // Germany center
      zoom: 6,
    });

    map.addControl(new mapboxgl.NavigationControl(), "top-right");

    map.on("load", () => {
      drawRef.current = initDraw(map);
      setReady(true);

      map.on("draw.create", () => onPolygon(extractPolygon(drawRef.current!)));
      map.on("draw.update", () => onPolygon(extractPolygon(drawRef.current!)));
      map.on("draw.delete", () => onPolygon(null));
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
      drawRef.current = null;
    };
  }, [onPolygon]);

  function handleClear() {
    if (drawRef.current) {
      clearDraw(drawRef.current);
      onPolygon(null);
    }
  }

  return (
    <div className="relative">
      <div ref={containerRef} className="w-full h-[400px] rounded-lg overflow-hidden border border-gray-200" />
      {ready && (
        <div className="absolute bottom-3 left-3 flex gap-2">
          <button
            type="button"
            onClick={handleClear}
            className="bg-white text-gray-700 border border-gray-300 text-xs px-3 py-1.5 rounded-lg shadow hover:bg-gray-50 transition-colors"
          >
            Zeichnung löschen
          </button>
        </div>
      )}
      {!ready && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 rounded-lg">
          <p className="text-sm text-gray-500">Karte wird geladen…</p>
        </div>
      )}
    </div>
  );
}
