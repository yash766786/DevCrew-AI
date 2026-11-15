"use client";
import { Send } from "lucide-react";
import { motion } from "framer-motion";

type Props = {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
};

export default function PromptInput({ value, onChange, onSend }: Props) {
  return (
    <div
      className="
        border-t
        border-white/10
        bg-[#0F172A]/80
        backdrop-blur-xl
        p-3
      "
    >
      <div
        className="
          bg-[#111827]
          border
          border-white/10
          rounded-3xl
          p-3
        "
      >
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
          placeholder="Build a landing page, dashboard, portfolio..."
          className="
            w-full
            resize-none
            outline-none
            bg-transparent
            text-sm
            text-white
            placeholder:text-gray-500
            min-h-[70px]
          "
        />

        <div
          className="
            flex
            justify-between
            items-center
            mt-3
          "
        >
          <div
            className="
              text-[11px]
              text-gray-500
            "
          >
            Press Enter ↵ to send
          </div>

          <motion.button
            whileHover={{
              scale: 1.05,
            }}
            whileTap={{
              scale: 0.95,
            }}
            onClick={onSend}
            className="
              h-10
              w-10
              rounded-full
              bg-gradient-to-r
              from-blue-600
              to-violet-600
              text-white
              flex
              items-center
              justify-center
              shadow-lg
              shadow-blue-500/20
            "
          >
            <Send size={16} />
          </motion.button>
        </div>
      </div>
    </div>
  );
}
