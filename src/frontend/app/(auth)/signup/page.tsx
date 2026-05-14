/**
 * Sign-up page — email + password registration with email verification.
 *
 * After successful submission, Supabase sends a verification email and
 * the user sees a "Check your email" confirmation message.
 *
 * Password requirements:
 *   - Minimum 8 characters
 *   - At least 1 uppercase letter
 *   - At least 1 number
 */

"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { createSupabaseBrowserClient } from "@/lib/supabase/client";
import { AuthForm } from "@/components/auth/AuthForm";
import { GoogleSignInButton } from "@/components/auth/GoogleSignInButton";

// ---------------------------------------------------------------------------
// Validation schema
// ---------------------------------------------------------------------------

const signupSchema = z
  .object({
    email: z
      .string()
      .min(1, "Email is required.")
      .email("Please enter a valid email address."),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters.")
      .regex(/[A-Z]/, "Password must contain at least one uppercase letter.")
      .regex(/[0-9]/, "Password must contain at least one number."),
    confirmPassword: z.string().min(1, "Please confirm your password."),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match.",
    path: ["confirmPassword"],
  });

type SignupFormValues = z.infer<typeof signupSchema>;

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Email + password sign-up page.
 *
 * @returns The sign-up page React element.
 */
export default function SignupPage(): React.ReactElement {
  const [serverError, setServerError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupFormValues>({
    resolver: zodResolver(signupSchema),
    mode: "onBlur",
  });

  const onSubmit = async (values: SignupFormValues): Promise<void> => {
    setServerError(null);
    setSubmitting(true);

    try {
      const supabase = createSupabaseBrowserClient();
      const { error } = await supabase.auth.signUp({
        email: values.email,
        password: values.password,
        options: {
          // Redirect the user back to /dashboard after clicking the
          // email verification link.
          emailRedirectTo: `${window.location.origin}/dashboard`,
        },
      });

      if (error) {
        setServerError(error.message);
        return;
      }

      setSuccess(true);
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <AuthForm
        title="Check your email"
        success="We've sent a verification link to your email address. Click the link to activate your account and get started."
      >
        <p className="text-center text-sm text-gray-500">
          Already verified?{" "}
          <Link
            href="/login"
            className="font-medium text-agrolens-600 hover:underline"
          >
            Sign in
          </Link>
        </p>
      </AuthForm>
    );
  }

  return (
    <AuthForm
      title="Create your account"
      subtitle="Start your free AgroLens trial — no credit card required"
      error={serverError}
    >
      <form
        onSubmit={handleSubmit(onSubmit)}
        noValidate
        aria-label="Sign up form"
      >
        {/* Email */}
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
            placeholder="you@farm.com"
            {...register("email")}
          />
          {errors.email && (
            <p id="email-error" role="alert" className="mt-1 text-xs text-red-600">
              {errors.email.message}
            </p>
          )}
        </div>

        {/* Password */}
        <div className="mb-4">
          <label
            htmlFor="password"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Password
          </label>
          <input
            id="password"
            type="password"
            autoComplete="new-password"
            aria-invalid={errors.password ? "true" : "false"}
            aria-describedby="password-hint password-error"
            className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:border-agrolens-600 focus:outline-none focus:ring-1 focus:ring-agrolens-600 aria-[invalid=true]:border-red-500"
            placeholder="••••••••"
            {...register("password")}
          />
          <p id="password-hint" className="mt-1 text-xs text-gray-400">
            8+ characters, 1 uppercase letter, 1 number.
          </p>
          {errors.password && (
            <p id="password-error" role="alert" className="mt-1 text-xs text-red-600">
              {errors.password.message}
            </p>
          )}
        </div>

        {/* Confirm password */}
        <div className="mb-6">
          <label
            htmlFor="confirmPassword"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            Confirm password
          </label>
          <input
            id="confirmPassword"
            type="password"
            autoComplete="new-password"
            aria-invalid={errors.confirmPassword ? "true" : "false"}
            aria-describedby={errors.confirmPassword ? "confirm-error" : undefined}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:border-agrolens-600 focus:outline-none focus:ring-1 focus:ring-agrolens-600 aria-[invalid=true]:border-red-500"
            placeholder="••••••••"
            {...register("confirmPassword")}
          />
          {errors.confirmPassword && (
            <p id="confirm-error" role="alert" className="mt-1 text-xs text-red-600">
              {errors.confirmPassword.message}
            </p>
          )}
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-agrolens-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-agrolens-700 focus:outline-none focus:ring-2 focus:ring-agrolens-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? "Creating account…" : "Create account"}
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

      <GoogleSignInButton disabled={submitting} />

      <p className="mt-6 text-center text-sm text-gray-500">
        Already have an account?{" "}
        <Link
          href="/login"
          className="font-medium text-agrolens-600 hover:text-agrolens-700 hover:underline"
        >
          Sign in
        </Link>
      </p>
    </AuthForm>
  );
}
