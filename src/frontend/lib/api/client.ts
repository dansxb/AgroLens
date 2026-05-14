/**
 * Typed fetch wrapper for AgroLens backend API calls.
 *
 * Attaches the Supabase JWT from the current session to every request
 * as a ``Authorization: Bearer <token>`` header.  Throws a typed
 * {@link ApiError} on non-2xx responses so callers can distinguish
 * between network errors and API errors.
 *
 * Usage:
 * ```ts
 * import { apiClient } from "@/lib/api/client";
 *
 * const farms = await apiClient.get<Farm[]>("/api/v1/farms");
 * const newFarm = await apiClient.post<Farm>("/api/v1/farms", { name: "My Farm" });
 * ```
 */

"use client";

import { createSupabaseBrowserClient } from "@/lib/supabase/client";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Shape returned by API error responses from the FastAPI backend. */
export interface ApiErrorResponse {
  detail: string | { msg: string; type: string }[];
}

/** Error class thrown by {@link apiClient} on non-2xx responses. */
export class ApiError extends Error {
  /** HTTP status code (e.g. 404, 422, 500). */
  public readonly status: number;
  /** Parsed error detail from the response body. */
  public readonly detail: string;

  constructor(status: number, detail: string) {
    super(`API error ${status}: ${detail}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

// ---------------------------------------------------------------------------
// Request helpers
// ---------------------------------------------------------------------------

/**
 * Retrieve the current Supabase session access token.
 *
 * Returns ``null`` if no session is active (unauthenticated).
 */
async function getAccessToken(): Promise<string | null> {
  try {
    const supabase = createSupabaseBrowserClient();
    const {
      data: { session },
    } = await supabase.auth.getSession();
    return session?.access_token ?? null;
  } catch {
    return null;
  }
}

/**
 * Parse a non-2xx response body into a human-readable error message.
 */
async function parseErrorDetail(response: Response): Promise<string> {
  try {
    const body: ApiErrorResponse = await response.json();
    if (typeof body.detail === "string") {
      return body.detail;
    }
    if (Array.isArray(body.detail)) {
      return body.detail.map((e) => e.msg).join(", ");
    }
    return `HTTP ${response.status} ${response.statusText}`;
  } catch {
    return `HTTP ${response.status} ${response.statusText}`;
  }
}

/** Base URL of the FastAPI backend, injected at build time. */
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Core fetch function
// ---------------------------------------------------------------------------

/**
 * Perform an authenticated HTTP request to the AgroLens backend.
 *
 * @param method - HTTP method string.
 * @param path - API path (e.g. ``/api/v1/farms``).  Must start with ``/``.
 * @param body - Optional request body (serialised as JSON).
 * @param extraHeaders - Additional HTTP headers to merge.
 * @returns Parsed JSON response body typed as ``T``.
 * @throws {@link ApiError} on non-2xx responses.
 * @throws {@link Error} on network failures.
 */
async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  extraHeaders?: Record<string, string>
): Promise<T> {
  const token = await getAccessToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...extraHeaders,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${path}`;

  const response = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    // Include cookies for browser-based session continuity
    credentials: "include",
  });

  if (!response.ok) {
    const detail = await parseErrorDetail(response);
    throw new ApiError(response.status, detail);
  }

  // Handle 204 No Content (e.g. DELETE responses)
  if (response.status === 204) {
    return undefined as unknown as T;
  }

  return response.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Public API client object
// ---------------------------------------------------------------------------

/**
 * Typed HTTP client for the AgroLens backend API.
 *
 * All methods automatically attach the Supabase JWT Bearer token.
 */
export const apiClient = {
  /**
   * Perform a GET request.
   *
   * @param path - API path.
   * @returns Parsed response body typed as ``T``.
   */
  get<T>(path: string): Promise<T> {
    return request<T>("GET", path);
  },

  /**
   * Perform a POST request with a JSON body.
   *
   * @param path - API path.
   * @param body - Request body (serialised as JSON).
   * @returns Parsed response body typed as ``T``.
   */
  post<T>(path: string, body?: unknown): Promise<T> {
    return request<T>("POST", path, body);
  },

  /**
   * Perform a PUT request with a JSON body.
   *
   * @param path - API path.
   * @param body - Request body (serialised as JSON).
   * @returns Parsed response body typed as ``T``.
   */
  put<T>(path: string, body?: unknown): Promise<T> {
    return request<T>("PUT", path, body);
  },

  /**
   * Perform a PATCH request with a partial JSON body.
   *
   * @param path - API path.
   * @param body - Partial update body.
   * @returns Parsed response body typed as ``T``.
   */
  patch<T>(path: string, body?: unknown): Promise<T> {
    return request<T>("PATCH", path, body);
  },

  /**
   * Perform a DELETE request.
   *
   * @param path - API path.
   * @returns ``undefined`` on 204 No Content, or parsed body on 200.
   */
  delete<T = void>(path: string): Promise<T> {
    return request<T>("DELETE", path);
  },
} as const;
