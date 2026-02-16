import { motion } from "framer-motion";
import { useMemo } from "react";
import { useScrollReveal, scrollVariants } from "@/hooks/use-scroll-reveal";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@/components/ui/tooltip";
import RecentActivityCards from "@/components/utils/RecentActivityCard";
import { useActivity } from "@/hooks/use-activity";
import type { ActivityDay } from "@/types/activity";

type HeatCell = {
  date: string; // YYYY-MM-DD
  count: number;
};

type Props = {
  data?: HeatCell[];
};

const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];
function formatDate(d: Date) {
  return d.toLocaleDateString("en-US", {
    month: "short", // Sep
    day: "numeric", // 28
    year: "numeric", // 2026
  });
}

/* ---------------- Utilities ---------------- */
function pad2(n: number) {
  return String(n).padStart(2, "0");
}

function toISO(d: Date) {
  return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`;
}

function startOfDay(d: Date) {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  return x;
}

function addDays(d: Date, days: number) {
  const x = new Date(d);
  x.setDate(x.getDate() + days);
  return x;
}

function daysDiff(a: Date, b: Date) {
  const ms = startOfDay(b).getTime() - startOfDay(a).getTime();
  return Math.floor(ms / (1000 * 60 * 60 * 24));
}

function startOfMonth(d: Date) {
  return startOfDay(new Date(d.getFullYear(), d.getMonth(), 1));
}

function endOfMonth(d: Date) {
  return startOfDay(new Date(d.getFullYear(), d.getMonth() + 1, 0));
}

function alignToSunday(d: Date) {
  return addDays(d, -d.getDay()); // Sunday = 0
}

function alignToSaturday(d: Date) {
  return addDays(d, 6 - d.getDay());
}

/* -------- Demo Data -------- */
function generateDemoData(today: Date): HeatCell[] {
  const out: HeatCell[] = [];
  const t = startOfDay(today);

  for (let i = 0; i < 365; i++) {
    const d = addDays(t, -i);
    if (Math.random() < 0.35) {
      out.push({
        date: toISO(d),
        count: 1 + Math.floor(Math.random() * 6),
      });
    }
  }
  return out;
}

/* -------- Color Levels -------- */
function level(count: number) {
  if (count === 0) return "bg-background/50";
  if (count <= 2) return "bg-primary/25";
  if (count <= 4) return "bg-primary/45";
  if (count <= 7) return "bg-primary/65";
  return "bg-primary";
}

/**
 * Build 12 months (including current month) where each month
 * is its own grid of week columns. Cells that fall outside the month become null.
 * This guarantees: July dates are in July block, never inside August block.
 */
function buildMonthBlocks(today: Date) {
  const t = startOfDay(today);

  // last 12 months (oldest -> newest)
  const months: { year: number; month: number }[] = [];
  for (let i = 11; i >= 0; i--) {
    const d = new Date(t.getFullYear(), t.getMonth() - i, 1);
    months.push({ year: d.getFullYear(), month: d.getMonth() });
  }

  return months.map(({ year, month }) => {
    const monthStart = startOfDay(new Date(year, month, 1));
    const monthEnd = endOfMonth(monthStart);

    // build a calendar grid aligned to weeks, but we will null out non-month dates
    const gridStart = alignToSunday(monthStart);
    const gridEnd = alignToSaturday(monthEnd);

    const totalDays = daysDiff(gridStart, gridEnd) + 1;
    const weeks = Math.ceil(totalDays / 7);

    // week columns: Date | null
    const weekColumns: Array<Array<Date | null>> = [];
    for (let col = 0; col < weeks; col++) {
      const week: Array<Date | null> = [];
      for (let row = 0; row < 7; row++) {
        const d = addDays(gridStart, col * 7 + row);
        const inMonth = d >= monthStart && d <= monthEnd;
        const isFuture = d > today;

        week.push(inMonth && !isFuture ? d : null);
      }
      weekColumns.push(week);
    }

    return {
      year,
      month,
      label: MONTHS[month],
      weekColumns,
      weeks,
    };
  });
}

const Journal = ({ data }: Props) => {
  const { ref, isInView } = useScrollReveal();
  const today = useMemo(() => startOfDay(new Date()), []);

  const heatData = useMemo(
    () => data ?? generateDemoData(today),
    [data, today],
  );

  const map = useMemo(() => {
    const m = new Map<string, number>();
    heatData.forEach((d) => m.set(d.date, d.count));
    return m;
  }, [heatData]);

  const monthBlocks = useMemo(() => buildMonthBlocks(today), [today]);

  // sizing
  const cellSize = 10;
  const gap = 4;
  const monthGap = 15; // space between months

  return (
    <section id="journal" className="py-20 relative overflow-hidden w-full">
      <div className="absolute inset-0 bg-gradient-to-b from-background via-card/20 to-background" />

      <div className="container mx-auto px-4 relative z-10" ref={ref}>
        {/* Section title */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <h2 className="text-5xl md:text-6xl font-bold mb-4">
            Daily <span className="gradient-text">Activity Log</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            A real-time log of my daily engineering work — tracking problem
            solving, project development, and technical execution across
            platforms.
          </p>
        </motion.div>

        {/* Outer card */}
        <motion.div
          initial={scrollVariants.assemble.initial}
          animate={isInView ? scrollVariants.assemble.animate : {}}
          transition={{ duration: 0.9, delay: 0.25, ease: [0.22, 1, 0.36, 1] }}
          className="glass rounded-2xl border border-white/10 hover:border-primary/40 transition-all max-w-6xl mx-auto"
        >
          <div className="p-6 md:p-8">
            <h3 className="text-2xl font-bold mb-6 text-center">
              <span className="text-primary">Journal Entry</span>
            </h3>

            {/* Scroll container */}
            <div
              className="overflow-x-auto glass rounded-2xl border border-white/10 p-5 md:p-6 w-full"
              style={{ WebkitOverflowScrolling: "touch" }}
            >
              <div className="w-max mx-auto">
                {/* Month labels */}
                <div
                  className="flex items-end"
                  style={{ gap: `${monthGap}px`, marginBottom: 10 }}
                >
                  {monthBlocks.map((mb) => {
                    const width = mb.weeks * (cellSize + gap) - gap;
                    return (
                      <div
                        key={`${mb.year}-${mb.month}`}
                        className="text-xs text-muted-foreground font-medium text-center"
                        style={{ width }}
                      >
                        {mb.label}
                      </div>
                    );
                  })}
                </div>

                {/* Month blocks */}
                <div className="flex" style={{ gap: `${monthGap}px` }}>
                  {monthBlocks.map((mb) => (
                    <div
                      key={`${mb.year}-${mb.month}`}
                      className="flex"
                      style={{ gap: `${gap}px` }}
                    >
                      {mb.weekColumns.map((week, colIdx) => (
                        <div
                          key={colIdx}
                          className="flex flex-col"
                          style={{ gap: `${gap}px` }}
                        >
                          {week.map((d, rowIdx) => {
                            if (!d) {
                              return (
                                <div
                                  key={rowIdx}
                                  style={{ width: cellSize, height: cellSize }}
                                  className="rounded-[3px] bg-transparent"
                                />
                              );
                            }

                            const iso = toISO(d);
                            const count = map.get(iso) ?? 0;

                            return (
                              <Tooltip key={iso}>
                                <TooltipTrigger asChild>
                                  <div
                                    className={`rounded-[3px] border border-black/15 dark:border-white/15 ${level(count)} transition-all hover:scale-125 hover:border-primary/50 cursor-pointer`}
                                    style={{
                                      width: cellSize,
                                      height: cellSize,
                                    }}
                                  />
                                </TooltipTrigger>

                                <TooltipContent
                                  side="top"
                                  sideOffset={8}
                                  className="bg-background/90 backdrop-blur-md border border-white/10 text-foreground"
                                >
                                  <div className="text-xs font-semibold">
                                    {formatDate(d)}
                                  </div>
                                  <div className="text-xs text-muted-foreground">
                                    {count} activities
                                  </div>
                                </TooltipContent>
                              </Tooltip>
                            );
                          })}
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <p className="text-xs text-muted-foreground text-center mt-4">
              Hover a square to see the date and activity count.
            </p>
            <div className="w-full h-px bg-gradient-to-r from-transparent via-primary/60 to-transparent my-6" />

            <RecentActivityCards />
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Journal;
