<!-- webapp-chat-bridge:start -->
## Chat-Bridge (webapp `/chat` ↔ this session)

When you receive a channel message starting with `💬 [chat from=webapp …]`,
the browser-chat is asking you something. Reply with:

```bash
./scripts/chat_bridge/cookidoo-chat reply "your answer"
```

The browser sees the reply within ≤1.5s via SSE. Details: `scripts/chat_bridge/README.md`.
<!-- webapp-chat-bridge:end -->
