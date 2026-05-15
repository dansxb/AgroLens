"use client";

import { useEffect } from "react";
import { captureException } from "@/lib/sentry";

interface Props {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: Props) {
  useEffect(() => {
    captureException(error, { digest: error.digest ?? "" });
  }, [error]);

  return (
    <html lang="de">
      <body>
        <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-4">
          <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-sm">
            <h1 className="text-xl font-semibold text-gray-900">
              Etwas ist schiefgelaufen
            </h1>
            <p className="mt-2 text-sm text-gray-600">
              Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es erneut.
            </p>
            {error.digest && (
              <p className="mt-1 font-mono text-xs text-gray-400">
                Fehler-ID: {error.digest}
              </p>
            )}
            <button
              onClick={reset}
              className="mt-6 rounded-md bg-agrolens-600 px-4 py-2 text-sm font-semibold text-white hover:bg-agrolens-700"
            >
              Erneut versuchen
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
