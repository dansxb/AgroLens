/**
 * Password reset page — sends a Supabase password-reset email.
 *
 * The user enters their email address and Supabase sends a magic link.
 * After submission the page shows a confirmation message regardless of
 * whether the email exists (to prevent user enumeration).
 */

"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { createSupabaseBrowserClient } from "@/lib/supabase/client";
import { AuthForm } from "@/components/auth/AuthForm";

// ---------------------------------------------------------------------------
// Validation schema
// ---------------------------------------------------------------------------

const resetSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required.")
    .email("Please enter a valid email address."),
});

type ResetFormValues = z.infer<typeof resetSchema>;

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Password reset request page.
 *
 * @returns The reset-password page React element.
 */
export default function ResetPasswordPage(): React.ReactElement {
  const [serverError, setServerError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetFormValues>({
    resolver: zodResolver(resetSchema),
    mode: "onBlur",
  });

  const onSubmit = async (values: ResetFormValues): Promise<void> => {
    setServerError(null);
    setSubmitting(true);

    try {
      const supabase = createSupabaseBrowserClient();
      const { error } = await supabase.auth.resetPasswordForEmail(
        values.email,
        {
          // Redirect the user to the update-password page after clicking
          // the link in the email.
          redirectTo: `${window.location.origin}/auth/update-password`,
        }
      );

      if (error) {
        setServerError(error.message);
        return;
      }

      setSubmitted(true);
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <AuthForm
        title="Check your email"
        success="If an account exists for that email address, we've sent a password-reset link. The link expires in 1 hour."
      >
        <p className="text-center text-sm text-gray-500">
          Remember your password?{" "}
          <Link
            href="/login"
            className="font-medium text-agrolens-600 hover:underline"
          >
            Back to sign in
          </Link>
        </p>
      </AuthForm>
    );
  }

  return (
    <AuthForm
      title="Reset your password"
      subtitle="Enter your email and we'll send you a reset link."
      error={serverError}
    >
      <form
        onSubmit={handleSubmit(onSubmit)}
        noValidate
        aria-label="Password reset form"
      >
        <div className="mb-6">
          <label
            htmlFor="email"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Email address
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            aria-invalid={errors.email ? "true" : "false"}
            aria-describedby={errors.email ? "email-error" : undefined}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:border-agrolens-600 focus:outline-none focus:ring-1 focus:ring-agrolens-600 aria-[invalid=true]:border-red-500"
            placeholder="you@example.com"
            {...register("email")}
          />
          {errors.email && (
            <p
              id="email-error"
              role="alert"
              className="mt-1 text-xs text-red-600"
            >
              {errors.email.message}
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-agrolens-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-agrolens-700 focus:outline-none focus:ring-2 focus:ring-agrolens-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? "Sending…" : "Send reset link"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-gray-500">
        <Link
          href="/login"
          className="font-medium text-agrolens-600 hover:text-agrolens-700 hover:underline"
        >
          ← Back to sign in
        </Link>
      </p>
    </AuthForm>
  );
}
