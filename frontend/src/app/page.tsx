"use client";
import { useState } from "react";
import Header from "@/components/Header";
import ChatPanel from "@/components/ChatPanel";
import PreviewPanel from "@/components/PreviewPanel";

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [projectId, setProjectId] = useState<string | null>(null);

  const [status, setStatus] = useState<
    "idle" | "awaiting_approval" | "preview_ready"
  >("idle");

  const [previewUrl, setPreviewUrl] = useState("");
  const [activities, setActivities] = useState<any[]>([]);

  return (
    <main
      className="
        h-screen
        flex
        flex-col
        bg-[#0B0F19]
        text-white
        overflow-hidden
        relative
      "
    >
      <div
        className="
          absolute
          top-0
          right-0
          h-[500px]
          w-[500px]
          rounded-full
          bg-purple-500/10
          blur-[140px]
          pointer-events-none
        "
      />

      <div
        className="
          absolute
          bottom-0
          left-0
          h-[500px]
          w-[500px]
          rounded-full
          bg-blue-500/10
          blur-[140px]
          pointer-events-none
        "
      />

      <Header />

      <div className="flex flex-1 overflow-hidden">
        <ChatPanel
          sessionId={sessionId}
          setSessionId={setSessionId}
          projectId={projectId}
          setProjectId={setProjectId}
          status={status}
          setStatus={setStatus}
          setPreviewUrl={setPreviewUrl}
          setActivities={setActivities}
        />

        <PreviewPanel
          previewUrl={previewUrl}
          projectId={projectId}
          activities={activities}
        />
      </div>
    </main>
  );
}
