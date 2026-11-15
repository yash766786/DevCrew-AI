"use client";
import { useState, useRef, useEffect } from "react";
import { PanelLeftClose, PanelLeftOpen, Bot } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Message from "./Message";
import PlanCard from "./PlanCard";
import PromptInput from "./PromptInput";
import { createProject, respondToProject, modifyProject } from "@/lib/api";
import { useSessionSocket } from "@/hooks/useSessionSocket";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  plan?: any;
};

type Props = {
  sessionId: string | null;
  setSessionId: (id: string) => void;

  projectId: string | null;
  setProjectId: (id: string) => void;

  status: string;
  setStatus: (status: "idle" | "awaiting_approval" | "preview_ready") => void;

  setPreviewUrl: (url: string) => void;
  setActivities: React.Dispatch<React.SetStateAction<any[]>>;
};

export default function ChatPanel({
  sessionId,
  setSessionId,
  projectId,
  setProjectId,
  status,
  setStatus,
  setPreviewUrl,
  setActivities,
}: Props) {
  const [input, setInput] = useState("");
  const [collapsed, setCollapsed] = useState(false);
  const [agentThinking, setAgentThinking] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "What would you like to build today?",
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  // APPROVE PLAN
  const handleApprove = async () => {
    if (!projectId) return;

    setMessages((prev) =>
      prev.map((msg) => ({
        ...msg,
        plan: undefined,
      })),
    );

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: "Building application...",
      },
    ]);

    setAgentThinking(true);

    await respondToProject(projectId, "approve");
  };

  // SEND MESSAGE
  const handleSend = async () => {
    if (!input.trim()) return;

    const message = input;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: message,
      },
    ]);

    setInput("");

    if (!sessionId) {
      alert("Waiting for websocket connection...");
      return;
    }

    try {
      setAgentThinking(true);

      // CREATE PROJECT

      if (status === "idle") {
        const result = await createProject(message, sessionId);

        if (result.error) {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: result.error,
            },
          ]);
        } else if (result.status === "rejected") {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: result.reason,
            },
          ]);
        } else {
          setProjectId(result.project_id);

          setStatus("awaiting_approval");

          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: result.summary,
              plan: result.plan,
            },
          ]);
        }

        setAgentThinking(false);
        return;
      }

      // PLAN CHANGES

      if (status === "awaiting_approval" && projectId) {
        const result = await respondToProject(projectId, message);

        if (result.error) {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: result.error,
            },
          ]);
        } else if (result.status === "awaiting_approval") {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: result.summary,
              plan: result.plan,
            },
          ]);
        } else if (result.status === "rejected") {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: result.reason,
            },
          ]);
        }

        setAgentThinking(false);
        return;
      }
      // WEBSITE MODIFICATION
      if (status === "preview_ready" && projectId) {
        const result = await modifyProject(projectId, message);

        if (result.error) {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: result.error,
            },
          ]);
        } else if (result.status === "rejected") {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: result.reason,
            },
          ]);
        } else if (result.assistant_response) {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: result.assistant_response,
            },
          ]);
        }

        setAgentThinking(false);
      }
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong.",
        },
      ]);

      setAgentThinking(false);
    }
  };

  // SOCKET EVENTS
  useSessionSocket((event) => {
    console.log("CHAT PANEL RECEIVED:", event);

    if (event.event === "session_created") {
      setSessionId(event.session_id);

      return;
    }

    setActivities((prev) => [...prev, event]);

    if (event.status === "completed") {
      setAgentThinking(false);
    }

    if (event.event === "preview_ready") {
      setStatus("preview_ready");

      setPreviewUrl("");

      setTimeout(() => {
        setPreviewUrl(event.message);
      }, 1000);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Preview is ready.",
        },
      ]);
    }
  });

  return (
    <motion.div
      animate={{
        width: collapsed ? 72 : 460,
      }}
      transition={{
        duration: 0.25,
      }}
      className="
      border-r
      border-slate-800
      bg-slate-950
      flex
      flex-col
      shrink-0
    "
    >
      {/* HEADER */}

      <div
        className="
        h-16
        border-b
        border-slate-800
        px-4
        flex
        items-center
        justify-between
        bg-slate-950/90
        backdrop-blur-xl
      "
      >
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{
                opacity: 0,
              }}
              animate={{
                opacity: 1,
              }}
              exit={{
                opacity: 0,
              }}
            >
              <div className="font-semibold text-sm text-white">DevCrew AI</div>

              <div className="text-[11px] text-slate-400">
                Software Engineer
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="
          p-2
          rounded-lg
          text-slate-400
          hover:text-white
          hover:bg-slate-900
          transition-all
        "
        >
          {collapsed ? (
            <PanelLeftOpen size={18} />
          ) : (
            <PanelLeftClose size={18} />
          )}
        </button>
      </div>

      {collapsed ? null : (
        <>
          {/* MESSAGES */}

          <div
            className="
            flex-1
            overflow-y-auto
            p-4
            bg-slate-950
          "
          >
            {messages.map((msg, index) => (
              <div key={index}>
                <Message role={msg.role} content={msg.content} />

                {msg.plan && (
                  <PlanCard plan={msg.plan} onApprove={handleApprove} />
                )}
              </div>
            ))}

            {/* AGENT THINKING */}

            {agentThinking && (
              <div className="flex gap-3 mt-4">
                <div
                  className="
                  w-8
                  h-8
                  rounded-full
                  bg-gradient-to-br
                  from-cyan-500
                  to-blue-600
                  text-white
                  flex
                  items-center
                  justify-center
                  shadow-lg
                "
                >
                  <Bot size={14} />
                </div>

                <div
                  className="
                  bg-slate-900
                  border
                  border-slate-800
                  rounded-2xl
                  px-4
                  py-3
                "
                >
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" />

                    <div className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:150ms]" />

                    <div className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:300ms]" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* INPUT */}

          <PromptInput value={input} onChange={setInput} onSend={handleSend} />
        </>
      )}
    </motion.div>
  );
}
