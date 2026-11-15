"use client";

import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Palette,
  Layers,
  Check,
  Sparkles,
} from "lucide-react";

type Plan = {
  project_name: string;
  project_type: string;
  theme: string;
  sections: string[];
  summary: string;
};

type Props = {
  plan: Plan;
  onApprove: () => void;
};

export default function PlanCard({ plan, onApprove }: Props) {
  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 15,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="
        bg-[#111827]
        border
        border-white/10
        rounded-3xl
        p-4
        mt-3
        mb-5
        shadow-xl
      "
    >
      {/* Header */}

      <div className="mb-4">
        <div
          className="
            flex
            items-center
            gap-2
            text-blue-400
            text-xs
            uppercase
            tracking-wider
          "
        >
          <Sparkles size={12} />
          Generated Plan
        </div>

        <h2
          className="
            text-lg
            font-semibold
            mt-2
            text-white
          "
        >
          {plan.project_name}
        </h2>
      </div>

      {/* Metadata */}

      <div className="space-y-3 text-sm">
        <div
          className="
            flex
            items-center
            gap-2
            text-gray-300
          "
        >
          <LayoutDashboard size={14} />
          {plan.project_type}
        </div>

        <div
          className="
            flex
            items-center
            gap-2
            text-gray-300
          "
        >
          <Palette size={14} />
          {plan.theme}
        </div>

        <div>
          <div
            className="
              flex
              items-center
              gap-2
              text-gray-300
              mb-2
            "
          >
            <Layers size={14} />
            Sections
          </div>

          <div className="flex flex-wrap gap-2">
            {plan.sections.map((section) => (
              <span
                key={section}
                className="
                    px-2.5
                    py-1
                    rounded-full
                    bg-white/5
                    border
                    border-white/10
                    text-xs
                    text-gray-300
                  "
              >
                {section}
              </span>
            ))}
          </div>
        </div>

        <div>
          <div
            className="
              text-xs
              text-gray-500
              mb-1
            "
          >
            Summary
          </div>

          <p
            className="
              text-sm
              text-gray-400
              leading-relaxed
            "
          >
            {plan.summary}
          </p>
        </div>
      </div>

      {/* Actions */}

      <motion.button
        whileHover={{
          scale: 1.02,
        }}
        whileTap={{
          scale: 0.98,
        }}
        onClick={onApprove}
        className="
          mt-5
          w-full
          py-3
          rounded-2xl
          bg-gradient-to-r
          from-blue-600
          to-violet-600
          text-white
          flex
          items-center
          justify-center
          gap-2
          font-medium
          shadow-lg
          shadow-blue-500/20
        "
      >
        <Check size={16} />
        Approve & Build
      </motion.button>

      <div
        className="
          mt-3
          text-[11px]
          text-gray-500
          text-center
        "
      >
        You can approve or ask for modifications in chat
      </div>
    </motion.div>
  );
}
