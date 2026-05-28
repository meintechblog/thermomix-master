import { chatList } from "@/lib/chat-db";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Long-poll SSE: every 1.5s check the DB for messages newer than the cursor.
export async function GET(req: Request) {
  const url = new URL(req.url);
  const sinceParam = url.searchParams.get("since");
  let cursor = sinceParam ? parseInt(sinceParam) : 0;
  if (!Number.isFinite(cursor) || cursor < 0) cursor = 0;

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const writeEvent = (event: string, data: unknown) => {
        controller.enqueue(encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`));
      };

      writeEvent("hello", { cursor });
      const backlog = chatList(cursor);
      for (const m of backlog) {
        writeEvent("message", m);
        cursor = m.id;
      }

      const abortSignal = req.signal;
      let closed = false;
      abortSignal.addEventListener("abort", () => { closed = true; });

      while (!closed) {
        await new Promise(r => setTimeout(r, 1500));
        if (closed) break;
        try {
          const msgs = chatList(cursor);
          for (const m of msgs) {
            writeEvent("message", m);
            cursor = m.id;
          }
          controller.enqueue(encoder.encode(`: hb ${Date.now()}\n\n`));
        } catch (e) {
          writeEvent("error", { message: String(e) });
          break;
        }
      }
      try { controller.close(); } catch {}
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  });
}
