import AnimatedBackground from "@/components/AnimatedBackground";
import Navigation from "@/components/Navigation";
import Hero from "@/components/Hero";
import { useState } from "react";
import About from "@/components/About";
import Resume from "@/components/Resume";
import Footer from "@/components/Footer";
import Contact from "@/components/Contact";
import Skills from "@/components/Skills";
import Certifications from "@/components/Certifications";
import Projects from "@/components/Projects";
import ResumeModal from "@/components/ResumeModal";

const Index = () => {
  const [isResumeModalOpen, setIsResumeModalOpen] = useState(false);
  return (
    <div className="min-h-screen bg-background text-foreground relative">
      <AnimatedBackground />
      <Navigation />
      <Hero onViewResume={() => setIsResumeModalOpen(true)} />
      <About />
      <Resume onViewResume={() => setIsResumeModalOpen(true)} />
      <Projects />
      <Certifications />
      <Skills />
      <Contact />
      <Footer />
      <ResumeModal
        isOpen={isResumeModalOpen}
        onClose={() => setIsResumeModalOpen(false)}
      />
    </div>
  );
};

export default Index;
