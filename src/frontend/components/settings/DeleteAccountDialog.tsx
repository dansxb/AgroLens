/**
 * DeleteAccountDialog — Confirmation dialog for account deletion.
 *
 * The user must type "DELETE" to enable the confirm button.  On
 * confirmation, calls {@code DELETE /api/v1/users/me}, signs the user
 * out, and redirects to the homepage.
 *
 * This component is a controlled dialog — the parent controls whether
 * it is open via the {@code open} prop.
 */

"use client";

import React, { useRef, useState, useEffect } from "react";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";
import { apiClient, ApiError } from "@/lib/api/client";

/** Required confirmation string to enable account deletion. */
const CONFIRM_WORD = "DELETE";

/** Props for the {@link DeleteAccountDialog} component. */
export interface DeleteAccountDialogProps {
  /** Whether the dialog is currently open. */
  open: boolean;
  /** Callback to close the dialog without deleting. */
  onClose: () => void;
  /** Authenticated user's email address, used for password re-authentication. */
  userEmail: string;
}

/**
 * Modal confirmation dialog for permanent account deletion.
 *
 * The user must type {@code "DELETE"} before the confirm button becomes
 * active.  On confirmation:
 * 1. Calls {@code DELETE /api/v1/users/me} to delete the backend record
 *    and Supabase Auth user.
 * 2. Signs the user out of Supabase client-side.
 * 3. Redirects to {@code /} (homepage).
 *
 * @param props - {@link DeleteAccountDialogProps}
 * @returns The dialog React element (renders nothing when closed).
 */
export function DeleteAccountDialog({
  open,
  onClose,
  userEmail,
}: DeleteAccountDialogProps): React.ReactElement | null {
  const [confirmText, setConfirmText] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [deleting, setDeleting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus the input when the dialog opens.
  useEffect(() => {
    if (open) {
      setConfirmText("");
      setPassword("");
      setError(null);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  if (!open) return null;

  const isConfirmed = confirmText === CONFIRM_WORD;
  const canSubmit = isConfirmed && password.length > 0;

  const handleDelete = async (): Promise<void> => {
    if (!canSubmit) return;

    setError(null);
    setDeleting(true);

    try {
      // Re-authenticate before deleting — prevents accidental deletion from
      // an unattended session.
      const supabase = createSupabaseBrowserClient();
      const { error: authError } = await supabase.auth.signInWithPassword({
        email: userEmail,
        password,
      });
      if (authError) {
        setError("Incorrect password. Please try again.");
        setDeleting(false);
        return;
      }

      await apiClient.delete("/api/v1/users/me");

      // Sign out client-side (session cookie is now invalid).
      await supabase.auth.signOut();

      // Hard redirect to homepage — clears all React state.
      window.location.href = "/";
    } catch (err: unknown) {
      const message =
        err instanceof ApiError
          ? err.detail
          : err instanceof Error
          ? err.message
          : "Failed to delete account. Please try again.";
      setError(message);
      setDeleting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>): void => {
    if (e.key === "Escape") {
      onClose();
    }
  };

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-dialog-title"
      aria-describedby="delete-dialog-description"
      onKeyDown={handleKeyDown}
    >
      <div className="w-full max-w-md rounded-2xl bg-white px-8 py-8 shadow-2xl">
        {/* Icon + title */}
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-red-100">
            <svg
              className="h-5 w-5 text-red-600"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <h2
            id="delete-dialog-title"
            className="text-lg font-semibold text-gray-900"
          >
            Delete your account
          </h2>
        </div>

        <p
          id="delete-dialog-description"
          className="mb-5 text-sm text-gray-600"
        >
          This action is{" "}
          <span className="font-semibold text-red-600">permanent and irreversible</span>
          . All your farms, fields, and prescription data will be deleted.
          You will lose access immediately.
        </p>

        {/* Confirmation input */}
        <div className="mb-5">
          <label
            htmlFor="confirm-delete"
            className="mb-1.5 block text-sm font-medium text-gray-700"
          >
            Type{" "}
            <span
              className="rounded bg-gray-100 px-1.5 py-0.5 font-mono text-xs font-semibold text-gray-800"
              aria-label="DELETE"
            >
              DELETE
            </span>{" "}
            to confirm account deletion
          </label>
          <input
            ref={inputRef}
            id="confirm-delete"
            type="text"
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            aria-invalid={!isConfirmed && confirmText.length > 0 ? "true" : "false"}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm font-mono text-gray-900 focus:border-red-500 focus:outline-none focus:ring-1 focus:ring-red-500"
            placeholder="DELETE"
            autoComplete="off"
            spellCheck={false}
          />
        </div>

        {/* Password re-authentication */}
        <div className="mb-5">
          <label
            htmlFor="confirm-password"
            className="mb-1.5 block text-sm font-medium text-gray-700"
          >
            Enter your password to confirm
          </label>
          <input
            id="confirm-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm text-gray-900 focus:border-red-500 focus:outline-none focus:ring-1 focus:ring-red-500"
            placeholder="Your account password"
            autoComplete="current-password"
          />
        </div>

        {/* Error */}
        {error && (
          <div
            role="alert"
            className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {error}
          </div>
        )}

        {/* Buttons */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={deleting}
            className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleDelete}
            disabled={!canSubmit || deleting}
            aria-disabled={!canSubmit || deleting}
            className="flex-1 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {deleting ? "Deleting…" : "Delete my account"}
          </button>
        </div>
      </div>
    </div>
  );
}
