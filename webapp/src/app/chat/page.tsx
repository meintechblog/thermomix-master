import { ChatRoom } from "@/components/ChatRoom";
import { PeerStatusIndicator } from "@/components/PeerStatusIndicator";
import { chatRecent } from "@/lib/chat-db";

export const dynamic = "force-dynamic";

export default function ChatPage() {
  const backlog = chatRecent(200);
  return (
    <div className="-mx-6 -my-8 lg:mx-0 lg:my-0">
      <div className="bg-white lg:rounded-2xl overflow-hidden shadow lg:m-0 flex flex-col h-[100dvh] lg:h-[85vh]">
        <header className="bg-gray-900 text-gray-50 px-5 py-3 flex items-center gap-3">
          <div className="text-sm font-mono">cookidoo · chat-bridge</div>
          <div className="ml-auto">
            <PeerStatusIndicator />
          </div>
        </header>
        <ChatRoom initialBacklog={backlog} />
      </div>
    </div>
  );
}
