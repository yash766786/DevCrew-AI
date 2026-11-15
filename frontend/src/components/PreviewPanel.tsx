"use client";
import { useEffect, useMemo, useRef, useState } from "react";

import {
  Activity,
  Eye,
  Download,
  ExternalLink,
  Loader2,
  CheckCircle2,
  XCircle,
} from "lucide-react";

import { motion, AnimatePresence } from "framer-motion";
import { downloadProject } from "@/lib/api";

type ActivityItem = {
  event: string;
  status?: string;
  message: string;
};

type Props = {
  previewUrl: string;
  projectId: string | null;
  activities: ActivityItem[];
};

export default function PreviewPanel({
  previewUrl,
  projectId,
  activities,
}: Props) {
  const [tab, setTab] = useState<"preview" | "activity">("activity");
  const [iframeKey, setIframeKey] = useState(0);
  const activityRef = useRef<HTMLDivElement>(null);

  // Auto switch to preview
  useEffect(() => {
    if (previewUrl) {
      setIframeKey((prev) => prev + 1);
      setTab("preview");
    }
  }, [previewUrl]);

  // Auto scroll timeline
  useEffect(() => {
    if (!activityRef.current) return;

    activityRef.current.scrollTop = activityRef.current.scrollHeight;
  }, [activities]);

  const handleDownload = async () => {
    if (!projectId) return;

    try {
      await downloadProject(projectId);
    } catch (error) {
      console.error(error);
    }
  };

  // Keep only latest status per agent
  const timelineActivities = useMemo(() => {
    return Object.values(
      activities.reduce(
        (acc, item) => {
          acc[item.event] = item;
          return acc;
        },
        {} as Record<string, ActivityItem>,
      ),
    );
  }, [activities]);

  // Current running agent
  const currentAgent = [...timelineActivities]
    .reverse()
    .find((a) => a.status === "running");

  // Active count
  const activeCount = timelineActivities.filter(
    (a) => a.status === "running",
  ).length;

  const renderTimelineDot = (status?: string) => {
    switch (status) {
      case "running":
        return (
          <div
            className="
              h-5
              w-5
              rounded-full
              bg-blue-500
              ring-4
              ring-blue-500
              flex
              items-center
              justify-center
            "
          >
            <Loader2
              size={10}
              className="
                text-white
                animate-spin
                bg-black
              "
            />
          </div>
        );

      case "completed":
        return (
          <div
            className="
              h-5
              w-5
              rounded-full
              bg-green-500
              ring-4
              ring-black
              flex
              items-center
              justify-center
            "
          >
            <CheckCircle2 size={10} className="text-white" />
          </div>
        );

      case "failed":
        return (
          <div
            className="
              h-5
              w-5
              rounded-full
              bg-red-500
              ring-4
              ring-red-100
              flex
              items-center
              justify-center
            "
          >
            <XCircle size={10} className="text-white" />
          </div>
        );

      default:
        return (
          <div
            className="
              h-4
              w-4
              rounded-full
              bg-gray-400
            "
          />
        );
    }
  };

  // return (
  //   <div className="flex-1 flex flex-col">
  //     {/* HEADER */}

  //     <div
  //       className="
  //         h-16
  //         border-b
  //         bg-white/80
  //         backdrop-blur-md
  //         px-5
  //         flex
  //         items-center
  //         justify-between
  //       "
  //     >
  //       {/* Tabs */}
  //       <div className="flex gap-2">
  //         <button
  //           onClick={() => setTab("activity")}
  //           className={`
  //             flex
  //             items-center
  //             gap-2
  //             px-4
  //             py-2
  //             rounded-xl
  //             text-sm
  //             font-medium
  //             transition-all

  //             ${tab === "activity" ? "bg-black text-white" : "bg-white border"}
  //           `}
  //         >
  //           <Activity size={16} />
  //           Activity
  //         </button>

  //         <button
  //           onClick={() => setTab("preview")}
  //           className={`
  //             flex
  //             items-center
  //             gap-2
  //             px-4
  //             py-2
  //             rounded-xl
  //             text-sm
  //             font-medium
  //             transition-all

  //             ${tab === "preview" ? "bg-black text-white" : "bg-white border"}
  //           `}
  //         >
  //           <Eye size={16} />
  //           Preview
  //         </button>
  //       </div>

  //       {/* Actions */}
  //       <div className="flex gap-2">
  //         {previewUrl && (
  //           <button
  //             onClick={() => window.open(previewUrl, "_blank")}
  //             className="
  //               flex
  //               items-center
  //               gap-2
  //               px-4
  //               py-2
  //               rounded-xl
  //               border
  //               bg-white
  //               hover:shadow-md
  //               transition-all
  //             "
  //           >
  //             <ExternalLink size={16} />
  //             Open
  //           </button>
  //         )}

  //         <button
  //           onClick={handleDownload}
  //           disabled={!projectId}
  //           className="
  //             flex
  //             items-center
  //             gap-2
  //             px-4
  //             py-2
  //             rounded-xl
  //             bg-black
  //             text-white
  //             hover:opacity-90
  //             disabled:opacity-50
  //             transition-all
  //           "
  //         >
  //           <Download size={16} />
  //           ZIP
  //         </button>
  //       </div>
  //     </div>

  //     {/* CONTENT */}
  //     <AnimatePresence mode="wait">
  //       {tab === "activity" ? (
  //         <motion.div
  //           key="activity"
  //           initial={{
  //             opacity: 0,
  //             y: 10,
  //           }}
  //           animate={{
  //             opacity: 1,
  //             y: 0,
  //           }}
  //           exit={{
  //             opacity: 0,
  //           }}
  //           ref={activityRef}
  //           className="
  //             flex-1
  //             overflow-y-auto
  //             p-6
  //             bg-gray-50
  //           "
  //         >
  //           {activities.length === 0 ? (
  //             <div
  //               className="
  //                 h-full
  //                 flex
  //                 items-center
  //                 justify-center
  //                 text-gray-500
  //               "
  //             >
  //               Waiting for agents...
  //             </div>
  //           ) : (
  //             <>
  //               {/* Current Agent */}

  //               {currentAgent && (
  //                 <div
  //                   className="
  //                     mb-5
  //                     rounded-3xl
  //                     bg-black
  //                     text-white
  //                     p-5
  //                   "
  //                 >
  //                   <div
  //                     className="
  //                       text-xs
  //                       uppercase
  //                       opacity-70
  //                     "
  //                   >
  //                     Currently Working
  //                   </div>

  //                   <div
  //                     className="
  //                       mt-2
  //                       text-lg
  //                       font-semibold
  //                     "
  //                   >
  //                     {currentAgent.event}
  //                   </div>
  //                 </div>
  //               )}

  //               {/* Active Count */}

  //               <div
  //                 className="
  //                   mb-6
  //                   bg-white
  //                   border
  //                   rounded-3xl
  //                   p-5
  //                 "
  //               >
  //                 <div
  //                   className="
  //                     text-sm
  //                     text-gray-500
  //                   "
  //                 >
  //                   Active Agents
  //                 </div>

  //                 <div
  //                   className="
  //                     mt-2
  //                     text-4xl
  //                     font-bold
  //                   "
  //                 >
  //                   {activeCount}
  //                 </div>
  //               </div>

  //               {/* Timeline */}
  //               <div
  //                 className="
  //                   relative
  //                   pl-8
  //                 "
  //               >
  //                 <div
  //                   className="
  //                     absolute
  //                     left-[9px]
  //                     top-0
  //                     bottom-0
  //                     w-[2px]
  //                     bg-gray-200
  //                   "
  //                 />

  //                 {timelineActivities.map((activity, index) => (
  //                   <motion.div
  //                     key={index}
  //                     initial={{
  //                       opacity: 0,
  //                       x: -10,
  //                     }}
  //                     animate={{
  //                       opacity: 1,
  //                       x: 0,
  //                     }}
  //                     className="
  //                         relative
  //                         mb-8
  //                       "
  //                   >
  //                     {/* Dot */}

  //                     <div
  //                       className="
  //                           absolute
  //                           -left-8
  //                           top-1
  //                         "
  //                     >
  //                       {renderTimelineDot(activity.status)}
  //                     </div>

  //                     {/* Content */}

  //                     <div
  //                       className="
  //                           bg-white
  //                           border
  //                           rounded-2xl
  //                           p-4
  //                           shadow-sm
  //                         "
  //                     >
  //                       <div
  //                         className="
  //                             flex
  //                             items-center
  //                             justify-between
  //                           "
  //                       >
  //                         <h3
  //                           className="
  //                               font-semibold
  //                             "
  //                         >
  //                           {activity.event}
  //                         </h3>

  //                         <span
  //                           className="
  //                               text-xs
  //                               uppercase
  //                               text-gray-400
  //                             "
  //                         >
  //                           {activity.status}
  //                         </span>
  //                       </div>

  //                       <p
  //                         className="
  //                             mt-2
  //                             text-sm
  //                             text-gray-600
  //                             leading-relaxed
  //                           "
  //                       >
  //                         {activity.message}
  //                       </p>
  //                     </div>
  //                   </motion.div>
  //                 ))}
  //               </div>
  //             </>
  //           )}
  //         </motion.div>
  //       ) : (
  //         <motion.div
  //           key="preview"
  //           initial={{
  //             opacity: 0,
  //           }}
  //           animate={{
  //             opacity: 1,
  //           }}
  //           exit={{
  //             opacity: 0,
  //           }}
  //           className="
  //             flex-1
  //             p-4
  //             bg-gray-100
  //           "
  //         >
  //           {!previewUrl ? (
  //             <div
  //               className="
  //                 h-full
  //                 flex
  //                 items-center
  //                 justify-center
  //                 text-gray-500
  //               "
  //             >
  //               No preview available
  //             </div>
  //           ) : (
  //             <div
  //               className="
  //                 h-full
  //                 overflow-hidden
  //                 rounded-3xl
  //                 border
  //                 bg-white
  //                 shadow-xl
  //               "
  //             >
  //               <iframe
  //                 key={iframeKey}
  //                 src={`${previewUrl}?t=${Date.now()}`}
  //                 className="
  //                   w-full
  //                   h-full
  //                   border-0
  //                 "
  //               />
  //             </div>
  //           )}
  //         </motion.div>
  //       )}
  //     </AnimatePresence>
  //   </div>
  // );

  return (
    <div className="flex-1 flex flex-col bg-[#0a0a0a]">
      {/* HEADER */}

      <div
        className="
        h-14
        border-b
        border-slate-800
        bg-[#0f0f0f]/90
        backdrop-blur-xl
        px-4
        flex
        items-center
        justify-between
      "
      >
        {/* Tabs */}

        <div className="flex gap-2">
          <button
            onClick={() => setTab("activity")}
            className={`
            flex
            items-center
            gap-2
            px-3
            py-1.5
            rounded-xl
            text-xs
            font-medium
            transition-all

            ${
              tab === "activity"
                ? "bg-cyan-500 text-black"
                : "bg-slate-900 border border-slate-800 text-slate-400"
            }
          `}
          >
            <Activity size={14} />
            Activity
          </button>

          <button
            onClick={() => setTab("preview")}
            className={`
            flex
            items-center
            gap-2
            px-3
            py-1.5
            rounded-xl
            text-xs
            font-medium
            transition-all

            ${
              tab === "preview"
                ? "bg-cyan-500 text-black"
                : "bg-slate-900 border border-slate-800 text-slate-400"
            }
          `}
          >
            <Eye size={14} />
            Preview
          </button>
        </div>

        {/* Actions */}

        <div className="flex gap-2">
          {previewUrl && (
            <button
              onClick={() => window.open(previewUrl, "_blank")}
              className="
              flex
              items-center
              gap-2
              px-3
              py-1.5
              rounded-xl
              border
              border-slate-800
              bg-slate-900
              text-slate-300
              text-xs
              hover:border-slate-700
              transition-all
            "
            >
              <ExternalLink size={14} />
              Open
            </button>
          )}

          <button
            onClick={handleDownload}
            disabled={!projectId}
            className="
            flex
            items-center
            gap-2
            px-3
            py-1.5
            rounded-xl
            bg-cyan-500
            text-black
            text-xs
            font-medium
            hover:bg-cyan-400
            disabled:opacity-50
            transition-all
          "
          >
            <Download size={14} />
            ZIP
          </button>
        </div>
      </div>

      {/* CONTENT */}

      <AnimatePresence mode="wait">
        {tab === "activity" ? (
          <motion.div
            key="activity"
            initial={{
              opacity: 0,
              y: 10,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            exit={{
              opacity: 0,
            }}
            ref={activityRef}
            className="
            flex-1
            overflow-y-auto
            p-4
            bg-[#0a0a0a]
          "
          >
            {activities.length === 0 ? (
              <div
                className="
                h-full
                flex
                items-center
                justify-center
                text-slate-500
                text-sm
              "
              >
                Waiting for agents...
              </div>
            ) : (
              <>
                {/* Current Agent */}

                {currentAgent && (
                  <div
                    className="
                    mb-4
                    rounded-2xl
                    bg-gradient-to-r
                    from-cyan-500/20
                    to-blue-500/20
                    border
                    border-cyan-500/20
                    p-4
                  "
                  >
                    <div
                      className="
                      text-[10px]
                      uppercase
                      tracking-wider
                      text-cyan-400
                    "
                    >
                      Currently Working
                    </div>

                    <div
                      className="
                      mt-1
                      text-sm
                      font-semibold
                      text-white
                    "
                    >
                      {currentAgent.event}
                    </div>
                  </div>
                )}

                {/* Active Count */}

                <div
                  className="
                  mb-5
                  bg-slate-900
                  border
                  border-slate-800
                  rounded-2xl
                  p-4
                "
                >
                  <div
                    className="
                    text-xs
                    text-slate-500
                  "
                  >
                    Active Agents
                  </div>

                  <div
                    className="
                    mt-1
                    text-2xl
                    font-bold
                    text-white
                  "
                  >
                    {activeCount}
                  </div>
                </div>

                {/* Timeline */}

                <div
                  className="
                  relative
                  pl-8
                "
                >
                  <div
                    className="
                    absolute
                    left-[9px]
                    top-0
                    bottom-0
                    w-[2px]
                    bg-slate-800
                  "
                  />

                  {timelineActivities.map((activity, index) => (
                    <motion.div
                      key={index}
                      initial={{
                        opacity: 0,
                        x: -10,
                      }}
                      animate={{
                        opacity: 1,
                        x: 0,
                      }}
                      className="
                        relative
                        mb-5
                      "
                    >
                      {/* Dot */}

                      <div
                        className="
                          absolute
                          -left-8
                          top-1
                        "
                      >
                        {renderTimelineDot(activity.status)}
                      </div>

                      {/* Content */}

                      <div
                        className="
                          bg-slate-900
                          border
                          border-slate-800
                          rounded-xl
                          px-3
                          py-2.5
                          hover:border-slate-700
                          transition-all
                        "
                      >
                        <div
                          className="
                            flex
                            items-center
                            justify-between
                          "
                        >
                          <h3
                            className="
                              text-xs
                              font-semibold
                              text-white
                            "
                          >
                            {activity.event}
                          </h3>

                          <span
                            className="
                              text-[10px]
                              uppercase
                              tracking-wide
                              text-slate-500
                            "
                          >
                            {activity.status}
                          </span>
                        </div>

                        <p
                          className="
                            mt-1
                            text-[11px]
                            text-slate-400
                            leading-relaxed
                          "
                        >
                          {activity.message}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </>
            )}
          </motion.div>
        ) : (
          <motion.div
            key="preview"
            initial={{
              opacity: 0,
            }}
            animate={{
              opacity: 1,
            }}
            exit={{
              opacity: 0,
            }}
            className="
            flex-1
            p-3
            bg-[#050505]
          "
          >
            {!previewUrl ? (
              <div
                className="
                h-full
                flex
                items-center
                justify-center
                text-slate-500
                text-sm
              "
              >
                No preview available
              </div>
            ) : (
              <div
                className="
                h-full
                overflow-hidden
                rounded-2xl
                border
                border-slate-800
                bg-black
                shadow-2xl
              "
              >
                <iframe
                  key={iframeKey}
                  src={`${previewUrl}?t=${Date.now()}`}
                  className="
                  w-full
                  h-full
                  border-0
                "
                />
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
