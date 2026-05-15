"use client";

import { apiClient } from "@/lib/api/client";

export interface Field {
  id: string;
  farm_id: string;
  name: string;
  crop_type: string | null;
  area_ha: number | null;
  flik: string | null;
  geometry: GeoJSON.Geometry;
  planting_date: string | null;
  created_at: string;
}

export interface FieldCreate {
  farm_id: string;
  name: string;
  crop_type?: string;
  flik?: string;
  planting_date?: string;
  geometry: GeoJSON.Geometry;
}

export interface FieldUpdate {
  name?: string;
  crop_type?: string;
  flik?: string;
  planting_date?: string;
}

export function getFields(farmId?: string): Promise<Field[]> {
  const url = farmId
    ? `/api/v1/fields/?farm_id=${farmId}`
    : `/api/v1/fields/`;
  return apiClient.get<Field[]>(url);
}

export function getField(fieldId: string): Promise<Field> {
  return apiClient.get<Field>(`/api/v1/fields/${fieldId}`);
}

export function createField(data: FieldCreate): Promise<Field> {
  return apiClient.post<Field>(`/api/v1/fields/`, data);
}

export function updateField(fieldId: string, data: FieldUpdate): Promise<Field> {
  return apiClient.put<Field>(`/api/v1/fields/${fieldId}`, data);
}

export function deleteField(fieldId: string): Promise<void> {
  return apiClient.delete(`/api/v1/fields/${fieldId}`);
}
