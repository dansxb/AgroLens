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
        "w-full max-w-md rounded-2xl bg-white px-8 py-10 shadow-xl ring-1 ring-gray-100",
        className
      )}
      role="main"
    >
      {/* Title */}
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-bold tracking-tight text-gray-900">
          {title}
        </h1>
        {subtitle && (
          <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div
          role="alert"
          aria-live="assertive"
          className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          <span className="font-medium">Error: </span>
          {error}
        </div>
      )}

      {/* Success banner */}
      {success && (
        <div
          role="status"
          aria-live="polite"
          className="mb-4 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700"
        >
          {success}
        </div>
      )}

      {/* Form content */}
      {children}
    </div>
  );
}
