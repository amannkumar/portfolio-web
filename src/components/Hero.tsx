import { motion } from "framer-motion";
import { Button } from "@/components/utils/button";
import { Download } from "lucide-react";
import { FaGithub, FaLinkedin } from "react-icons/fa6";
import { SiLeetcode } from "react-icons/si";
import { useState, useEffect } from "react";
import MagneticButton from "@/components/MagneticButton";
import { roles, personalInfo, tagline } from "@/data/portfolioData";

interface HeroProps {
  onViewResume: () => void;
}

const Hero = ({ onViewResume }: HeroProps) => {
  const [displayedText, setDisplayedText] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const role = roles[currentIndex % roles.length];
    let charIndex = 0;

    const typingInterval = setInterval(() => {
      if (charIndex <= role.length) {
        setDisplayedText(role.substring(0, charIndex));
        charIndex++;
      } else {
        clearInterval(typingInterval);
        setTimeout(() => {
          setCurrentIndex((prev) => prev + 1);
        }, 2000);
      }
    }, 150);

    return () => clearInterval(typingInterval);
  }, [currentIndex]);

  return (
    <section
      id="home"
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
    >
      {/* Animated Background */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,hsla(173_80%_40%/0.1),transparent_50%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,hsla(217_91%_60%/0.15),transparent_50%)]" />

      {/* Floating particles */}
      <div className="absolute inset-0">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-primary/30 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.2, 0.5, 0.2],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      <div className="container mx-auto px-4 z-10">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <span className="text-primary text-lg font-medium mb-4 block">
              {personalInfo.greeting}
            </span>
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              I'm{" "}
              <span className="gradient-text">{personalInfo.displayName}</span>
            </h1>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="h-16 mb-8"
          >
            <h2 className="text-2xl md:text-4xl font-semibold text-primary">
              {displayedText}
              <span className="animate-pulse">|</span>
            </h2>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="space-y-2 mb-8"
          >
            <p className="text-xl md:text-2xl text-foreground/90">
              {tagline.primary}
            </p>
            <p className="text-lg md:text-xl text-muted-foreground">
              {tagline.secondary}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9, duration: 0.8 }}
            className="flex flex-wrap gap-4 justify-center"
          >
            <MagneticButton strength={0.4}>
              <Button
                size="lg"
                variant="outline"
                className="border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white dark:border-blue-400 dark:text-blue-400 dark:hover:bg-blue-400 dark:hover:text-black"
                asChild
              >
                <a
                  href="https://www.linkedin.com/in/aamankumar/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center"
                >
                  <FaLinkedin className="mr-2 h-5 w-5" />
                  LinkedIn
                </a>
              </Button>
            </MagneticButton>

            <MagneticButton strength={0.4}>
              <Button
                size="lg"
                variant="outline"
                className="border-gray-900 text-gray-900 hover:bg-gray-900 hover:text-white dark:border-gray-200 dark:text-gray-200 dark:hover:bg-gray-200 dark:hover:text-black"
                asChild
              >
                <a
                  href="https://github.com/amannkumar"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center"
                >
                  <FaGithub className="mr-2 h-5 w-5" />
                  Github
                </a>
              </Button>
            </MagneticButton>

            <MagneticButton strength={0.4}>
              <Button
                size="lg"
                variant="outline"
                className="border-orange-500 text-orange-500 hover:bg-orange-500 hover:text-white dark:border-orange-400 dark:text-orange-400 dark:hover:bg-orange-400 dark:hover:text-black"
                asChild
              >
                <a
                  href="https://leetcode.com/u/amannkumar/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center"
                >
                  <SiLeetcode className="mr-2 h-5 w-5" />
                  Leetcode
                </a>
              </Button>
            </MagneticButton>

            <Button
              size="lg"
              variant="outline"
              className="border-secondary text-secondary hover:bg-secondary hover:text-secondary-foreground dark:border-secondary-dark dark:text-secondary-dark dark:hover:bg-secondary-dark/80 dark:hover:text-secondary-foreground"
              onClick={onViewResume}
            >
              <Download className="mr-2 h-5 w-5" />
              View CV
            </Button>
          </motion.div>

          {/* Scroll Indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2, duration: 0.8 }}
            className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
          >
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="w-6 h-10 border-2 border-primary rounded-full flex justify-center"
            >
              <motion.div
                animate={{ y: [0, 12, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="w-1 h-3 bg-primary rounded-full mt-2"
              />
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
