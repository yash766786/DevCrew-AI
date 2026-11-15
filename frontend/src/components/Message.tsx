"use client";
import { motion } from "framer-motion";
import { Bot, User } from "lucide-react";

type Props = {
  role: "user" | "assistant";
  content: string;
};

export default function Message({ role, content }: Props) {
  const isUser = role === "user";

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 8,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        duration: 0.25,
      }}
      className={`flex gap-2 mb-4 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser && (
        <div
          className="
            w-7
            h-7
            rounded-full
            bg-gradient-to-br
            from-blue-500
            to-purple-600
            flex
            items-center
            justify-center
            shrink-0
            shadow-lg
          "
        >
          <Bot size={14} />
        </div>
      )}

      <div
        className={`
          max-w-[88%]
          px-3
          py-2.5
          text-[13px]
          leading-relaxed
          rounded-2xl
          backdrop-blur-md
          border

          ${
            isUser
              ? `
                bg-gradient-to-r
                from-blue-600
                to-violet-600
                border-blue-500/20
                text-white
                rounded-br-md
              `
              : `
                bg-[#111827]
                border-white/10
                text-gray-200
                rounded-bl-md
              `
          }
        `}
      >
        {content}
      </div>

      {isUser && (
        <div
          className="
            w-7
            h-7
            rounded-full
            bg-[#1F2937]
            border
            border-white/10
            flex
            items-center
            justify-center
            shrink-0
          "
        >
          <User size={14} />
        </div>
      )}
    </motion.div>
  );
}
