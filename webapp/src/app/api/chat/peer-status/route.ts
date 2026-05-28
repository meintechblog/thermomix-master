import { getPeerStatus, setPeerStatus } from "@/lib/chat-db";
import { z } from "zod";

export const runtime = "nodejs";

const AUTH_TOKEN = process.env.CHAT_BRIDGE_TOKEN || "";

function authOk(req: Request): boolean {
  if (!AUTH_TOKEN) return true;
  const got = req.headers.get("authorization") || "";
  return got === `Bearer ${AUTH_TOKEN}`;
}

// GET — Browser polls for current peer status.
export async function GET() {
  const status = getPeerStatus();
  const now = Math.floor(Date.now() / 1000);
  const daemonAgeS = status?.daemon_last_seen ? now - status.daemon_last_seen : null;
  const peerAgeS = status?.peer_last_seen ? now - status.peer_last_seen : null;
  return Response.json({
    daemon_alive: daemonAgeS !== null && daemonAgeS < 30,
    daemon_age_s: daemonAgeS,
    peer_id: status?.peer_id || null,
    peer_alive: status?.peer_id != null && peerAgeS !== null && peerAgeS < 30,
    peer_age_s: peerAgeS,
  });
}

// POST — Daemon heartbeats here every 5s.
const Body = z.object({
  peer_id: z.string().nullable(),
});

export async function POST(req: Request) {
  if (!authOk(req)) return Response.json({ error: "unauthorized" }, { status: 401 });
  let parsed;
  try {
    parsed = Body.parse(await req.json());
  } catch {
    return Response.json({ error: "invalid_body" }, { status: 400 });
  }
  setPeerStatus(parsed.peer_id);
  return Response.json({ ok: true });
}
