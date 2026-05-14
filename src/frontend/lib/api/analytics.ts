"use client";

import { apiClient } from "@/lib/api/client";

export interface NdviPoint {
  date: string;
  mean_ndvi: number;
  std_ndvi: number;
}

export interface HealthSummary {
  status: "normal" | "mild_stress" | "significant_stress" | "unknown";
  latest_ndvi: number | null;
  latest_date: string | null;
  composite_age_days: number | null;
}

export function getNdviSeries(fieldId: string): Promise<NdviPoint[]> {
  return apiClient.get<NdviPoint[]>(`/api/v1/fields/${fieldId}/ndvi-series`);
}

export function getHealthSummary(fieldId: string): Promise<HealthSummary> {
  return apiClient.get<HealthSummary>(`/api/v1/fields/${fieldId}/health-summary`);
}
