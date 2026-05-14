"use client";

import { useEffect, useState } from "react";

export default function OfflineBanner() {
  const [offline, setOffline] = useState(false);
  const [lastOnline, setLastOnline] = useState<string | null>(null);

  useEffect(() => {
    function handleOnline() {
      setOffline(false);
    }
    function handleOffline() {
      setOffline(true);
      setLastOnline(new Date().toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" }));
    }

    setOffline(!navigator.onLine);
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  if (!offline) return null;

  return (
    <div className="w-full bg-amber-400 text-amber-900 text-xs font-medium text-center py-1.5 px-4 z-50">
      Offline-Modus — Letzte Verbindung: {lastOnline ?? "—"}
    </div>
  );
}
