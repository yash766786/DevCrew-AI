"use client";
import { motion } from "framer-motion";
import { Cpu, Sparkles, Activity } from "lucide-react";

export default function Header() {
  return (
    <motion.header
      initial={{
        y: -20,
        opacity: 0,
      }}
      animate={{
        y: 0,
        opacity: 1,
      }}
      className="
        h-16
        border-b
        border-slate-800
        bg-[#0b0b0b]/95
        backdrop-blur-xl
        px-6
        flex
        items-center
        justify-between
        shrink-0
      "
    >
      {/* LEFT */}

      <div className="flex items-center gap-4">
        {/* Logo */}

        <div
          className="
            relative
            h-10
            w-10
            rounded-xl

            bg-gradient-to-br
            from-cyan-500
            via-blue-500
            to-purple-600

            text-white
            flex
            items-center
            justify-center

            shadow-lg
            shadow-cyan-500/20
          "
        >
          <Cpu size={18} />

          <div
            className="
              absolute
              inset-0
              rounded-xl
              bg-cyan-400/20
              blur-lg
            "
          />
        </div>

        {/* Title */}

        <div>
          <h1
            className="
              text-white
              font-semibold
              tracking-tight
            "
          >
            DevCrew AI
          </h1>

          <p
            className="
              text-[11px]
              text-slate-400
            "
          >
            Autonomous Software Engineer
          </p>
        </div>
      </div>

      {/* CENTER STATUS */}

      <div
        className="
          hidden
          md:flex
          items-center
          gap-2

          px-3
          py-1.5

          rounded-full

          border
          border-cyan-500/20

          bg-cyan-500/5

          text-cyan-400
          text-xs
          font-medium
        "
      >
        <Activity size={12} className="animate-pulse" />
        Live Agent Execution
      </div>

      {/* RIGHT */}

      <div
        className="
          flex
          items-center
          gap-2

          text-xs
          text-slate-400
        "
      >
        <Sparkles size={14} className="text-cyan-400" />
        Agentic Development
      </div>
    </motion.header>
  );
}
