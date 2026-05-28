"use client";

import { useEffect, useState } from "react";

type Status = {
  daemon_alive: boolean;
  daemon_age_s: number | null;
  peer_id: string | null;
  peer_alive: boolean;
  peer_age_s: number | null;
};

function fmtAge(s: number | null): string {
  if (s == null) return "?";
  if (s < 60) return `${s}s`;
  if (s < 3600) return `${Math.floor(s / 60)}m`;
  return `${Math.floor(s / 3600)}h`;
}

export function PeerStatusIndicator() {
  const [status, setStatus] = useState<Status | null>(null);
  const [fetchFailed, setFetchFailed] = useState(false);

  useEffect(() => {
    let stopped = false;

    const poll = async () => {
      try {
        const res = await fetch("/api/chat/peer-status", { cache: "no-store" });
        if (!res.ok) throw new Error(`status ${res.status}`);
        const data = (await res.json()) as Status;
        if (!stopped) {
          setStatus(data);
          setFetchFailed(false);
        }
      } catch {
        if (!stopped) setFetchFailed(true);
      }
    };

    poll();
    const interval = setInterval(poll, 5000);
    return () => {
      stopped = true;
      clearInterval(interval);
    };
  }, []);

  if (fetchFailed || !status) {
    return (
      <div className="flex items-center gap-1.5 text-xs text-gray-400" title="Webapp-Status unbekannt">
        <span className="w-1.5 h-1.5 rounded-full bg-gray-400" />
        <span>checking…</span>
      </div>
    );
  }

  if (!status.daemon_alive) {
    return (
      <div
        className="flex items-center gap-1.5 text-xs text-red-300"
        title={`Mac-Daemon nicht erreichbar (last heartbeat ${fmtAge(status.daemon_age_s)} ago)`}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
        <span>Daemon offline</span>
      </div>
    );
  }

  if (status.peer_alive) {
    return (
      <div
        className="flex items-center gap-1.5 text-xs text-green-300"
        title={`Claude-Session ${status.peer_id} läuft (heartbeat ${fmtAge(status.daemon_age_s)} ago)`}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
        <span>Session online</span>
      </div>
    );
  }

  return (
    <div
      className="flex items-center gap-1.5 text-xs text-yellow-300"
      title={`Daemon läuft, aber keine Session in dem Repo aktiv (queued bis Session wieder läuft)`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-yellow-400" />
      <span>Session offline (queued)</span>
    </div>
  );
}
