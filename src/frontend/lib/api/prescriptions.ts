"use client";

import { apiClient } from "@/lib/api/client";

export type ApplicationType = "fungicide" | "herbicide" | "insecticide";

export interface PrescriptionZone {
  zone_label: string;
  rate_l_ha: number;
  area_ha: number;
  geometry: GeoJSON.Geometry;
}

export interface Prescription {
  id: string;
  field_id: string;
  application_type: ApplicationType;
  base_rate_l_ha: number;
  n_zones: number;
  disclaimer: string;
  created_at: string;
  zones: PrescriptionZone[];
}

export interface PrescriptionCreate {
  application_type: ApplicationType;
  base_rate_l_ha: number;
  n_zones?: number;
}

export function getPrescriptions(fieldId: string): Promise<Prescription[]> {
  return apiClient.get<Prescription[]>(`/api/v1/fields/${fieldId}/prescriptions`);
}

export function createPrescription(
  fieldId: string,
  data: PrescriptionCreate
): Promise<Prescription> {
  return apiClient.post<Prescription>(`/api/v1/fields/${fieldId}/prescriptions`, data);
}

export function getExportUrl(
  fieldId: string,
  applicationType: ApplicationType,
  format: "shapefile" | "taskdata" | "pdf"
): string {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  return `${base}/api/v1/fields/${fieldId}/prescriptions/${applicationType}/export/${format}`;
}
