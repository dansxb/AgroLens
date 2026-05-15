/**
 * Account Settings page — /dashboard/settings
 *
 * Fetches the current user profile from GET /api/v1/users/me, renders
 * the {@link ProfileForm} for editing, and provides a "Delete account"
 * button that opens the {@link DeleteAccountDialog}.
 *
 * This is a Client Component because it calls the backend API using
 * the client-side Supabase session.
 */

"use client";

import React, { useEffect, useState } from "react";
import { apiClient } from "@/lib/api/client";
import { ProfileForm, type UserProfile } from "@/components/settings/ProfileForm";
import { DeleteAccountDialog } from "@/components/settings/DeleteAccountDialog";

/**
 * Account settings page component.
 *
 * @returns The settings page React element.
 */
export default function SettingsPage(): React.ReactElement {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState<boolean>(false);

  const fetchProfile = async (): Promise<void> => {
    setLoading(true);
    setFetchError(null);
    try {
      const data = await apiClient.get<UserProfile>("/api/v1/users/me");
      setProfile(data);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to load profile.";
      setFetchError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchProfile();
  }, []);

  return (
    <>
      <div className="mx-auto max-w-2xl px-4 py-8">
        {/* Page header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Account Settings</h1>
          <p className="mt-1 text-sm text-gray-500">
            Manage your profile and account preferences.
          </p>
        </div>

        {/* Profile section */}
        <section
          aria-labelledby="profile-heading"
          className="mb-8 rounded-xl border border-gray-200 bg-white px-6 py-6 shadow-sm"
        >
          <h2
            id="profile-heading"
            className="mb-5 text-base font-semibold text-gray-900"
          >
            Profile
          </h2>

          {loading && (
            <div className="flex items-center gap-3 text-sm text-gray-500">
              <svg
                className="h-4 w-4 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
                aria-hidden="true"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                />
              </svg>
              Loading profile…
            </div>
          )}

          {fetchError && !loading && (
            <div
              role="alert"
              className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
            >
              {fetchError}{" "}
              <button
                type="button"
                onClick={() => void fetchProfile()}
                className="font-medium underline hover:no-underline"
              >
                Try again
              </button>
            </div>
          )}

          {profile && !loading && (
            <ProfileForm
              initialValues={profile}
              onSaved={() => void fetchProfile()}
            />
          )}
        </section>

        {/* Danger zone section */}
        <section
          aria-labelledby="danger-heading"
          className="rounded-xl border border-red-200 bg-white px-6 py-6 shadow-sm"
        >
          <h2
            id="danger-heading"
            className="mb-2 text-base font-semibold text-red-700"
          >
            Danger Zone
          </h2>
          <p className="mb-4 text-sm text-gray-600">
            Permanently delete your AgroLens account and all associated data.
            This action cannot be undone.
          </p>
          <button
            type="button"
            onClick={() => setDeleteDialogOpen(true)}
            className="rounded-lg border border-red-300 bg-white px-4 py-2.5 text-sm font-medium text-red-600 shadow-sm hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          >
            Delete my account
          </button>
        </section>
      </div>

      {/* Account deletion confirmation dialog */}
      <DeleteAccountDialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        userEmail={profile?.email ?? ""}
      />
    </>
  );
}
