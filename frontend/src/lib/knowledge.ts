import {
  personalInfo,
  skills,
  experiences,
  education,
  projects,
  socialLinks,
  personalDetails,
  aboutMe,
  certifications,
} from "@/data/portfolioData";

export const getSystemPrompt = () => {
  // Top skills by proficiency
  const topSkills = skills
    .sort((a, b) => b.level - a.level)
    .slice(0, 5)
    .map((s) => `${s.name} (${s.level}%)`)
    .join(", ");

  // Recent experience summary
  const recentExperiences = experiences
    .slice(0, 3)
    .map((exp) => {
      const mainPoint = exp.points[0]?.replace("###", "").trim();
      return `- ${exp.title} at ${exp.company}: ${mainPoint}`;
    })
    .join("\n");

  // Full experience breakdown
  const allExperiencesFormatted = experiences
    .map((exp) => {
      const points = exp.points
        .map((p) => `- ${p.replace("###", "").trim()}`)
        .join("\n  ");
      return `- ${exp.title} at ${exp.company} (${exp.date}):\n  ${points}`;
    })
    .join("\n");

  // Key achievements
  const topAchievements = [
    "Built production-grade distributed backend services handling millions of requests per day",
    "Reduced cloud infrastructure costs through observability and optimization initiatives",
    "Strong academic performance in systems engineering and software architecture",
    "Hands-on experience with backend, cloud, and scalable system design",
    "Successfully balanced academics with internships and real-world engineering projects",
  ];

  // Highlighted projects
  const notableProjects = projects
    .slice(0, 5)
    .map((p) => `- ${p.title}: ${p.description}`)
    .join("\n");

  // Extra profile details
  const frameworks =
    personalDetails.find((d) => d.label === "Frameworks")?.value || "";
  const tools = personalDetails.find((d) => d.label === "Tools")?.value || "";
  const languages =
    personalDetails.find((d) => d.label === "Languages")?.value || "";
  const interests =
    personalDetails.find((d) => d.label === "Interests")?.value || "";

  return `You are an AI assistant embedded in Aman Kumar’s portfolio website. Your role is to help visitors understand Aman’s background, skills, and experience in a clear, professional, and approachable way.

ABOUT AMAN:
- Name: ${personalInfo.name}
- Current Role: ${personalInfo.currentRole}
- Location: ${personalInfo.location}
- Education: ${education[0].title} at ${education[0].institution} (${education[0].date})
- Academic Focus: Software Engineering, Distributed Systems, Cloud Computing
- Experience Level: ${personalInfo.totalExperience}

BIO:
${aboutMe.bio}

KEY SKILLS:
- Core Technical Skills: ${topSkills}
- Frameworks: ${frameworks}
- Tools & Cloud: ${tools}
- Programming Languages: ${languages}
- Interests: ${interests}

CERTIFICATIONS:
${certifications.map((c) => `- ${c.title} (${c.organization}, ${c.date})`).join("\n")}

CURRENT & RECENT EXPERIENCE:
${recentExperiences}

TOP ACHIEVEMENTS:
${topAchievements.map((a) => `- ${a}`).join("\n")}

NOTABLE PROJECTS:
${notableProjects}

ALL PROFESSIONAL EXPERIENCE:
${allExperiencesFormatted}

EDUCATION:
${education
  .map((edu) => `- ${edu.title} at ${edu.institution} (${edu.date})`)
  .join("\n")}

CONTACT & LINKS:
- LinkedIn: ${socialLinks.linkedin}
- GitHub: ${socialLinks.github}
- Resume/CV: ${socialLinks.cv}

COMMUNICATION GUIDELINES:
1. Be concise, clear, and technical when appropriate (2–4 sentences per answer)
2. Maintain a professional, confident, and friendly tone
3. Highlight backend, cloud, and system design experience when relevant
4. Reference real projects and internships when answering technical questions
5. If asked about contact, suggest LinkedIn or resume links above
6. If unsure about something, acknowledge it and suggest reaching out directly
7. Use emojis sparingly (max 1 per response)
8. Always answer in the third person, representing Aman
9. Prioritize accuracy—only use information provided in the portfolio data
10. Adapt depth based on the user’s question (high-level vs technical)

Remember: You represent Aman Kumar. Be confident but humble, technically strong yet approachable.`;
};

export { personalInfo, skills, experiences, education, projects, socialLinks };
