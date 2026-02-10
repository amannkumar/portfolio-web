import { motion } from "framer-motion";
import { useInView } from "framer-motion";
import { useRef, useState, useMemo } from "react";
import { useScrollReveal, scrollVariants } from "@/hooks/use-scroll-reveal";
import { recentActivityDetails } from "@/data/portfolioData";

const Journal = () => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });
  return (
    <section id="journal" className="py-20 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-background via-card/20 to-background" />

      <div className="container mx-auto px-4 relative z-10" ref={ref}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          {" "}
          <h2 className="text-5xl md:text-6xl font-bold mb-4">
            Daily <span className="gradient-text">Activity Log</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            A real-time log of my daily engineering work — tracking problem
            solving, project development, and technical execution across
            platforms.
          </p>
        </motion.div>

        <motion.div
          initial={scrollVariants.assemble.initial}
          animate={isInView ? scrollVariants.assemble.animate : {}}
          transition={{ duration: 0.9, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className=" glass p-4
    rounded-2xl border border-white/10 hover:border-primary/40 transition-all"
        >
          <div className="flex items-center justify-center gap-3 mb-6">
            <h3 className="text-2xl font-bold text-center">
              <span className="text-primary">JournalEntry</span>
            </h3>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Journal;
