/**
 * ProfileForm — User profile update form.
 *
 * Pre-fills with the current user values fetched from the parent page.
 * On submit, calls {@code PUT /api/v1/users/me} via the typed API client
 * and shows a success toast on save.
 *
 * Fields:
 *   - Full name
 *   - Farm name
 *   - Country (ISO 3166-1 alpha-2, free-text validated)
 *   - Phone number
 */

"use client";

import React, { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { apiClient } from "@/lib/api/client";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Shape of the user profile returned by GET /api/v1/users/me */
export interface UserProfile {
  id: string;
  email: string;
  full_name: string | null;
  farm_name: string | null;
  country: string | null;
  phone: string | null;
  created_at: string;
}

/** Props for the {@link ProfileForm} component. */
export interface ProfileFormProps {
  /** Initial profile values to pre-fill the form. */
  initialValues: UserProfile;
  /** Callback invoked after a successful save. */
  onSaved?: () => void;
}

// ---------------------------------------------------------------------------
// Validation schema
// ---------------------------------------------------------------------------

const profileSchema = z.object({
  full_name: z
    .string()
    .max(255, "Name must be 255 characters or fewer.")
    .optional()
    .or(z.literal("")),
  farm_name: z
    .string()
    .max(255, "Farm name must be 255 characters or fewer.")
    .optional()
    .or(z.literal("")),
  country: z
    .string()
    .regex(/^[A-Za-z]{2}$/, "Please enter a valid 2-letter country code (e.g. DE, GB).")
    .optional()
    .or(z.literal("")),
  phone: z.string().max(30, "Phone number too long.").optional().or(z.literal("")),
});

type ProfileFormValues = z.infer<typeof profileSchema>;

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Form for updating the current user's profile fields.
 *
 * @param props - {@link ProfileFormProps}
 * @returns The profile form React element.
 */
export function ProfileForm({
  initialValues,
  onSaved,
}: ProfileFormProps): React.ReactElement {
  const [serverError, setServerError] = useState<string | null>(null);
  const [successToast, setSuccessToast] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: initialValues.full_name ?? "",
      farm_name: initialValues.farm_name ?? "",
      country: initialValues.country ?? "",
      phone: initialValues.phone ?? "",
    },
  });

  // Re-populate form if parent re-fetches initial values.
  useEffect(() => {
    reset({
      full_name: initialValues.full_name ?? "",
      farm_name: initialValues.farm_name ?? "",
      country: initialValues.country ?? "",
      phone: initialValues.phone ?? "",
    });
  }, [initialValues, reset]);

  const onSubmit = async (values: ProfileFormValues): Promise<void> => {
    setServerError(null);
    setSubmitting(true);

    try {
      // Build partial update — only send non-empty fields.
      const body: Record<string, string> = {};
      if (values.full_name) body.full_name = values.full_name;
      if (values.farm_name) body.farm_name = values.farm_name;
      if (values.country) body.country = values.country.toUpperCase();
      if (values.phone) body.phone = values.phone;

      await apiClient.put<UserProfile>("/api/v1/users/me", body);

      setSuccessToast(true);
      setTimeout(() => setSuccessToast(false), 4000);
      onSaved?.();
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to save profile.";
      setServerError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate aria-label="Profile form">
      {/* Server error */}
      {serverError && (
        <div
          role="alert"
          className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {serverError}
        </div>
      )}

      {/* Success toast */}
      {successToast && (
        <div
          role="status"
          aria-live="polite"
          className="mb-4 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700"
        >
          Profile saved successfully.
        </div>
      )}

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        {/* Full name */}
        <div>
          <label
            htmlFor="full_name"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Full name
          </label>
          <input
            id="full_name"
            type="text"
            autoComplete="name"
            aria-invalid={errors.full_name ? "true" : "false"}
            aria-describedby={errors.full_name ? "full_name-error" : undefined}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm text-gray-900 focus:border-agrolens-600 focus:outline-none focus:ring-1 focus:ring-agrolens-600"
            {...register("full_name")}
          />
          {errors.full_name && (
            <p id="full_name-error" role="alert" className="mt-1 text-xs text-red-600">
              {errors.full_name.message}
            </p>
          )}
        </div>

        {/* Farm name */}
        <div>
          <label
            htmlFor="farm_name"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Farm name
          </label>
          <input
            id="farm_name"
            type="text"
            autoComplete="organization"
            aria-invalid={errors.farm_name ? "true" : "false"}
            aria-describedby={errors.farm_name ? "farm_name-error" : undefined}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm text-gray-900 focus:border-agrolens-600 focus:outline-none focus:ring-1 focus:ring-agrolens-600"
            {...register("farm_name")}
          />
          {errors.farm_name && (
            <p id="farm_name-error" role="alert" className="mt-1 text-xs text-red-600">
              {errors.farm_name.message}
            </p>
          )}
        </div>

        {/* Country code */}
        <div>
          <label
            htmlFor="country"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Country code{" "}
            <span className="font-normal text-gray-400">(ISO 2-letter, e.g. DE)</span>
          </label>
          <input
            id="country"
            type="text"
            maxLength={2}
            autoComplete="country"
            aria-invalid={errors.country ? "true" : "false"}
            aria-describedby={errors.country ? "country-error" : undefined}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm uppercase text-gray-900 focus:border-agrolens-600 focus:outline-none focus:ring-1 focus:ring-agrolens-600"
            {...register("country")}
          />
          {errors.country && (
            <p id="country-error" role="alert" className="mt-1 text-xs text-red-600">
              {errors.country.message}
            </p>
          )}
        </div>

        {/* Phone */}
        <div>
          <label
            htmlFor="phone"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Phone number{" "}
            <span className="font-normal text-gray-400">(optional)</span>
          </label>
          <input
            id="phone"
            type="tel"
            autoComplete="tel"
            aria-invalid={errors.phone ? "true" : "false"}
            aria-describedby={errors.phone ? "phone-error" : undefined}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm text-gray-900 focus:border-agrolens-600 focus:outline-none focus:ring-1 focus:ring-agrolens-600"
            {...register("phone")}
          />
          {errors.phone && (
            <p id="phone-error" role="alert" className="mt-1 text-xs text-red-600">
              {errors.phone.message}
            </p>
          )}
        </div>
      </div>

      {/* Read-only email */}
      <div className="mt-5">
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Email address
        </label>
        <p className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2.5 text-sm text-gray-500">
          {initialValues.email}
          <span className="ml-2 text-xs text-gray-400">(managed by authentication provider)</span>
        </p>
      </div>

      {/* Save button */}
      <div className="mt-6 flex justify-end">
        <button
          type="submit"
          disabled={submitting || !isDirty}
          className="rounded-lg bg-agrolens-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-agrolens-700 focus:outline-none focus:ring-2 focus:ring-agrolens-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {submitting ? "Saving…" : "Save changes"}
        </button>
      </div>
    </form>
  );
}
