import { ChatRoom } from "@/components/ChatRoom";
import { PeerStatusIndicator } from "@/components/PeerStatusIndicator";
import { chatRecent } from "@/lib/chat-db";

export const dynamic = "force-dynamic";

export default function ChatPage() {
  const backlog = chatRecent(200);
  return (
    <div className="-mx-4 sm:-mx-6 -my-6 sm:-my-8 h-[calc(100%+3rem)] sm:h-[calc(100%+4rem)]">
      <div className="bg-white lg:rounded-2xl overflow-hidden shadow lg:m-0 flex flex-col h-full">
        <header className="bg-gray-900 text-gray-50 px-5 py-3 flex items-center gap-3 shrink-0">
          <div className="text-sm font-mono">thermomix · chat-bridge</div>
          <div className="ml-auto">
            <PeerStatusIndicator />
          </div>
        </header>
        <ChatRoom initialBacklog={backlog} />
      </div>
    </div>
  );
}
