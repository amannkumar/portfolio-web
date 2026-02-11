import { motion } from "framer-motion";
import { useMemo } from "react";
import { useScrollReveal, scrollVariants } from "@/hooks/use-scroll-reveal";
import InteractiveElement from "@/components/InteractiveElement";
import { recentActivityDetails } from "@/data/portfolioData";

type RecentActivity = {
  label: string;
  value: string;
};

/* ---------------- Parse Sections ---------------- */
function parseActivity(value: string) {
  const parts = value
    .split("•")
    .map((s) => s.trim())
    .filter(Boolean);
  const bySection: Record<string, string[]> = {};

  for (const part of parts) {
    const idx = part.indexOf(":");
    if (idx === -1) continue;

    const section = part.slice(0, idx).trim();
    const items = part
      .slice(idx + 1)
      .split(",")
      .map((x) => x.trim())
      .filter(Boolean);

    bySection[section] = items;
  }

  return bySection;
}

/* ---------------- Styling Helpers ---------------- */
function sectionAccent(section: string) {
  if (section.toLowerCase().includes("dsa")) return "text-primary";
  if (section.toLowerCase().includes("github")) return "text-emerald-400";
  if (section.toLowerCase().includes("task")) return "text-amber-400";
  return "text-muted-foreground";
}

function badgeBg(section: string) {
  if (section.toLowerCase().includes("dsa"))
    return "bg-primary/15 text-primary";
  if (section.toLowerCase().includes("github"))
    return "bg-emerald-500/15 text-emerald-300";
  if (section.toLowerCase().includes("task"))
    return "bg-amber-500/15 text-amber-300";
  return "bg-muted/20 text-muted-foreground";
}

function countTotal(parsed: Record<string, string[]>) {
  return Object.values(parsed).reduce((s, arr) => s + arr.length, 0);
}

/* ---------------- Component ---------------- */
const RecentActivityCards = ({
  items = recentActivityDetails as RecentActivity[],
}: {
  items?: RecentActivity[];
}) => {
  const { ref, isInView } = useScrollReveal();

  const normalized = useMemo(() => {
    return (items ?? []).slice(0, 7).map((d) => ({
      ...d,
      parsed: parseActivity(d.value),
    }));
  }, [items]);

  return (
    <section className="relative overflow-hidden" ref={ref}>
      {/* Title */}
      <motion.div
        initial={scrollVariants.floatUp.initial}
        animate={isInView ? scrollVariants.floatUp.animate : {}}
        transition={{ duration: 0.9 }}
        className="flex items-center justify-between mb-4"
      >
        <h3 className="text-lg font-bold">Recent Activity (Last 7 Days)</h3>
      </motion.div>

      {/* Cards */}
      <div className="flex gap-4 overflow-x-auto pb-2">
        {normalized.map((day, index) => {
          const parsed = day.parsed;
          const total = countTotal(parsed);

          return (
            //<InteractiveElement key={day.label}>
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{
                duration: 0.6,
                delay: 0.1 + index * 0.06,
              }}
              className="
                  glass
                  rounded-xl
                  border border-primary/25
                  hover:border-primary/45
                  transition-all
                  min-w-[210px]
                  w-[240px]
                  p-3
                "
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="text-base font-semibold">
                    {day.label.split("—")[0].trim()}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {day.label.split("—")[1]?.trim()}
                  </div>
                </div>

                <div
                  className="
                      w-7 h-7
                      rounded-full
                      bg-primary/15
                      border border-primary/25
                      text-primary
                      flex items-center justify-center
                      text-xs font-bold
                    "
                >
                  {total}
                </div>
              </div>

              {/* Sections */}
              <div className="space-y-3">
                {Object.entries(parsed).map(([section, items]) => (
                  <div key={section}>
                    <div className="flex items-center justify-between mb-1">
                      <div
                        className={`text-xs font-semibold ${sectionAccent(section)} flex items-center gap-1`}
                      >
                        <span className="w-1 h-1 rounded-full bg-current" />
                        {section}
                      </div>

                      <div
                        className={`text-[10px] px-1.5 py-0.5 rounded-full ${badgeBg(section)}`}
                      >
                        {items.length}
                      </div>
                    </div>

                    <ul className="space-y-0.5">
                      {items.slice(0, 4).map((it, i) => (
                        <li
                          key={i}
                          className="text-xs text-muted-foreground flex gap-1"
                        >
                          <span className="text-primary/70">•</span>
                          <span className="line-clamp-1">{it}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </motion.div>
            //</InteractiveElement>
          );
        })}
      </div>
    </section>
  );
};

export default RecentActivityCards;
