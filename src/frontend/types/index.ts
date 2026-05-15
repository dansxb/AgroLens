/**
 * Central type re-exports for AgroLens frontend.
 *
 * Import shared types from here rather than from individual API modules.
 * The source modules remain authoritative; this file provides a single
 * stable import path so callers don't need to know which module owns a type.
 *
 * Usage:
 * ```ts
 * import type { Field, Prescription, HealthSummary } from "@/types";
 * ```
 */

// Field types
export type { Field, FieldCreate, FieldUpdate } from "@/lib/api/fields";

// Prescription types
export type {
  ApplicationType,
  Prescription,
  PrescriptionCreate,
  PrescriptionZone,
} from "@/lib/api/prescriptions";

// Analytics types
export type { NdviPoint, HealthSummary } from "@/lib/api/analytics";

// Auth types (re-exported from Supabase for convenience)
export type { User, Session } from "@supabase/supabase-js";
