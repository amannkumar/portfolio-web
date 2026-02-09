import { motion } from "framer-motion";
import { useScrollReveal, scrollVariants } from "@/hooks/use-scroll-reveal";
import InteractiveElement from "@/components/InteractiveElement";
import {
  SiReact,
  SiJavascript,
  SiHtml5,
  SiCss3,
  SiTailwindcss,
  SiTypescript,
  SiFlutter,
  SiSpringboot,
  SiPostgresql,
  SiPython,
  SiGithub,
  SiJira,
  SiPostman,
  SiIntellijidea,
  SiAmazonwebservices,
  SiDocker,
  SiRedis,
  SiApachekafka,
} from "react-icons/si";
import { FaJava } from "react-icons/fa6";

type Skill = {
  name: string;
  Icon: React.ComponentType<{ className?: string }>;
};

type SkillGroup = {
  title: string;
  skills: Skill[];
};

const frontend: SkillGroup = {
  title: "Frontend",
  skills: [
    { name: "React", Icon: SiReact },
    { name: "JavaScript", Icon: SiJavascript },
    { name: "TypeScript", Icon: SiTypescript },
    { name: "HTML", Icon: SiHtml5 },
    { name: "CSS", Icon: SiCss3 },
    { name: "Tailwind", Icon: SiTailwindcss },
    { name: "Flutter", Icon: SiFlutter },
  ],
};

const backend: SkillGroup = {
  title: "Backend",
  skills: [
    { name: "Java", Icon: FaJava },
    { name: "Spring Boot", Icon: SiSpringboot },
    { name: "PostgreSQL", Icon: SiPostgresql },
    { name: "Python", Icon: SiPython },
  ],
};

const tools: SkillGroup = {
  title: "Tools",
  skills: [
    { name: "GitHub", Icon: SiGithub },
    { name: "Jira", Icon: SiJira },
    { name: "Postman", Icon: SiPostman },
    // { name: "VS Code", Icon: SiVisualstudiocode },
    { name: "IntelliJ IDEA", Icon: SiIntellijidea },
  ],
};

const cloud: SkillGroup = {
  title: "Cloud & DevOps",
  skills: [
    { name: "AWS", Icon: SiAmazonwebservices },
    // added based on your SWE stack (and resume mentions)
    { name: "Docker", Icon: SiDocker },
    { name: "Redis", Icon: SiRedis },
    { name: "Kafka", Icon: SiApachekafka },
  ],
};

const Skills = () => {
  const { ref, isInView } = useScrollReveal();

  return (
    <section id="skills" className="py-20 relative overflow-hidden">
      {/* ✅ same theme background as Contact */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-card/20 to-background" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,hsla(173_80%_40%/0.1),transparent_70%)]" />

      <div className="container mx-auto px-4 relative z-10" ref={ref}>
        {/* Title */}
        <motion.div
          initial={scrollVariants.floatUp.initial}
          animate={isInView ? scrollVariants.floatUp.animate : {}}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
          className="text-center mb-14"
        >
          <h2 className="text-5xl md:text-6xl font-bold mb-4">Skills</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Technologies I use to build scalable backend systems and modern user
            experiences.
          </p>
        </motion.div>

        <div className="max-w-5xl mx-auto">
          <div className="grid gap-8">
            {/* Row 1: Frontend + Backend */}
            <div className="grid lg:grid-cols-2 gap-8">
              <GroupCard group={frontend} isInView={isInView} delay={0.2} />
              <GroupCard group={backend} isInView={isInView} delay={0.2} />
            </div>

            <div className="grid lg:grid-cols-2 gap-8">
              <GroupCard group={tools} isInView={isInView} delay={0.5} />
              <GroupCard group={cloud} isInView={isInView} delay={0.65} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

function GroupCard({
  group,
  isInView,
  delay,
  wide,
}: {
  group: SkillGroup;
  isInView: boolean;
  delay: number;
  wide?: boolean;
}) {
  return (
    <motion.div
      initial={scrollVariants.assemble.initial}
      animate={isInView ? scrollVariants.assemble.animate : {}}
      transition={{ duration: 0.9, delay, ease: [0.22, 1, 0.36, 1] }}
      className="
    glass
    p-4
    rounded-2xl
    border border-white/10
    hover:border-primary/40
    transition-all
  "
    >
      <div className="flex items-center justify-center gap-3 mb-6">
        <h3 className="text-2xl font-bold text-center">
          <span className="text-primary">{group.title}</span>
        </h3>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 justify-items-center">
        {group.skills.map((s, idx) => (
          <InteractiveElement key={s.name}>
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{
                duration: 0.5,
                delay: delay + 0.1 + idx * 0.06,
                ease: [0.22, 1, 0.36, 1],
              }}
              className="flex flex-col items-center group"
            >
              <div className="w-[88px] h-[88px] rounded-2xl glass flex items-center justify-center">
                <s.Icon className="w-9 h-9 text-primary group-hover:text-primary-foreground transition-colors" />
              </div>
              <p className="mt-3 text-sm font-semibold text-foreground/90">
                {s.name}
              </p>
            </motion.div>
          </InteractiveElement>
        ))}
      </div>
    </motion.div>
  );
}

export default Skills;
