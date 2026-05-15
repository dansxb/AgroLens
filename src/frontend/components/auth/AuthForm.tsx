/**
 * AuthForm — Reusable authentication form wrapper component.
 *
 * Renders a titled card containing the provided form children, plus an
 * optional error message banner.  All auth pages (login, signup,
 * reset-password) use this component for consistent layout and error
 * display.
 *
 * @example
 * ```tsx
 * <AuthForm title="Sign In" error={error}>
 *   <input ... />
 *   <button type="submit">Sign in</button>
 * </AuthForm>
 * ```
 */

"use client";

import React from "react";
import clsx from "clsx";

/** Props for the {@link AuthForm} component. */
export interface AuthFormProps {
  /** Form heading displayed at the top of the card. */
  title: string;
  /** Optional subtitle or description shown below the title. */
  subtitle?: string;
  /** Error message to display (null/undefined hides the error banner). */
  error?: string | null;
  /** Success message to display (e.g. "Check your email"). */
  success?: string | null;
  /** Form children: inputs, buttons, links. */
  children: React.ReactNode;
  /** Additional CSS classes applied to the card container. */
  className?: string;
}

/**
 * Wraps authentication form content in a styled card with a title and
 * optional error/success message banners.
 *
 * @param props - {@link AuthFormProps}
 * @returns A React element containing the styled form card.
 */
export function AuthForm({
  title,
  subtitle,
  error,
  success,
  children,
  className,
}: AuthFormProps): React.ReactElement {
  return (
    <div
      className={clsx(
        "w-full max-w-md rounded-2xl bg-white px-8 py-10 shadow-xl ring-1 ring-black/5",
        className
      )}
      role="main"
    >
      {/* Brand mark + title */}
      <div className="mb-8 text-center">
        <div className="mx-auto mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-agrolens-600">
          <svg
            className="h-5 w-5 text-white"
            viewBox="0 0 24 24"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M17 8C8 10 5.9 16.17 3.82 19.07a10 10 0 0 0 15.44-1.83A16 16 0 0 0 17 8Z" />
            <path
              d="M12 3c-1 3.5 1 6 2 8l-4.5 6"
              stroke="currentColor"
              strokeWidth="1.5"
              fill="none"
              strokeLinecap="round"
            />
          </svg>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">
          {title}
        </h1>
        {subtitle && (
          <p className="mt-1.5 text-sm text-gray-500">{subtitle}</p>
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div
          role="alert"
          aria-live="assertive"
          className="mb-4 flex gap-3 rounded-xl border border-red-100 bg-red-50 px-4 py-3"
        >
          <svg
            className="mt-0.5 h-4 w-4 flex-shrink-0 text-red-500"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.75}
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
            />
          </svg>
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Success banner */}
      {success && (
        <div
          role="status"
          aria-live="polite"
          className="mb-4 flex gap-3 rounded-xl border border-agrolens-100 bg-agrolens-50 px-4 py-3"
        >
          <svg
            className="mt-0.5 h-4 w-4 flex-shrink-0 text-agrolens-600"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.75}
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-sm text-agrolens-700">{success}</p>
        </div>
      )}

      {/* Form content */}
      {children}
    </div>
  );
}
