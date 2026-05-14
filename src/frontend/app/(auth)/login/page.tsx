/**
 * Login page — email + password sign-in with Google OAuth option.
 *
 * Validates inputs with react-hook-form + zod.  On success, redirects
 * the user to /dashboard (or to the ?next= URL if set by middleware).
 *
 * Keyboard navigation: fully accessible — all inputs and buttons are
 * reachable via Tab key; errors are announced via aria-live regions.
 */

"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { createSupabaseBrowserClient } from "@/lib/supabase/client";
import { AuthForm } from "@/components/auth/AuthForm";
import { GoogleSignInButton } from "@/components/auth/GoogleSignInButton";

// ---------------------------------------------------------------------------
// Validation schema
// ---------------------------------------------------------------------------

const loginSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required.")
    .email("Please enter a valid email address."),
  password: z.string().min(1, "Password is required."),
});

type LoginFormValues = z.infer<typeof loginSchema>;

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Email + password login page with Google OAuth button.
 *
 * @returns The login page React element.
 */
export default function LoginPage(): React.ReactElement {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("next") ?? "/dashboard";

  const [serverError, setServerError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    mode: "onBlur",
  });

  const onSubmit = async (values: LoginFormValues): Promise<void> => {
    setServerError(null);
    setSubmitting(true);

    try {
      const supabase = createSupabaseBrowserClient();
      const { error } = await supabase.auth.signInWithPassword({
        email: values.email,
        password: values.password,
      });

      if (error) {
        setServerError(error.message);
        return;
      }

      // Successful login — navigate to intended destination.
      router.push(redirectTo);
      router.refresh();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthForm
      title="Welcome back"
      subtitle="Sign in to your AgroLens account"
      error={serverError}
    >
      <form
        onSubmit={handleSubmit(onSubmit)}
        noValidate
        aria-label="Sign in form"
      >
        {/* Email field */}
        <div className="mb-4">
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

        {/* Password field */}
        <div className="mb-6">
          <div className="mb-1 flex items-center justify-between">
            <label
              htmlFor="password"
              className="text-sm font-medium text-gray-700"
            >
              Password
            </label>
            <Link
              href="/reset-password"
              className="text-sm text-agrolens-600 hover:text-agrolens-700 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-agrolens-600"
            >
              Forgot password?
            </Link>
          </div>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            aria-invalid={errors.password ? "true" : "false"}
            aria-describedby={errors.password ? "password-error" : undefined}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:border-agrolens-600 focus:outline-none focus:ring-1 focus:ring-agrolens-600 aria-[invalid=true]:border-red-500"
            placeholder="••••••••"
            {...register("password")}
          />
          {errors.password && (
            <p
              id="password-error"
              role="alert"
              className="mt-1 text-xs text-red-600"
            >
              {errors.password.message}
            </p>
          )}
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-agrolens-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-agrolens-700 focus:outline-none focus:ring-2 focus:ring-agrolens-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? "Signing in…" : "Sign in"}
        </button>
      </form>

      {/* Divider */}
      <div className="relative my-5">
        <div className="absolute inset-0 flex items-center" aria-hidden="true">
          <div className="w-full border-t border-gray-200" />
        </div>
        <div className="relative flex justify-center text-xs">
          <span className="bg-white px-3 text-gray-400">or</span>
        </div>
      </div>

      {/* Google OAuth */}
      <GoogleSignInButton redirectTo={redirectTo} disabled={submitting} />

      {/* Sign up link */}
      <p className="mt-6 text-center text-sm text-gray-500">
        Don&apos;t have an account?{" "}
        <Link
          href="/signup"
          className="font-medium text-agrolens-600 hover:text-agrolens-700 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-agrolens-600"
        >
          Sign up free
        </Link>
      </p>
    </AuthForm>
  );
}
