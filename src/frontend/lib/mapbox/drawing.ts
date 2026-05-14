import type { Map } from "mapbox-gl";
import MapboxDraw from "@mapbox/mapbox-gl-draw";

export function initDraw(map: Map): MapboxDraw {
  const draw = new MapboxDraw({
    displayControlsDefault: false,
    controls: { polygon: true, trash: true },
    defaultMode: "draw_polygon",
  });
  map.addControl(draw as unknown as mapboxgl.IControl);
  return draw;
}

export function extractPolygon(draw: MapboxDraw): GeoJSON.Geometry | null {
  const data = draw.getAll();
  if (!data.features.length) return null;
  const feature = data.features[0];
  if (
    feature.geometry.type !== "Polygon" &&
    feature.geometry.type !== "MultiPolygon"
  ) {
    return null;
  }
  return feature.geometry as GeoJSON.Geometry;
}

export function clearDraw(draw: MapboxDraw): void {
  draw.deleteAll();
}
