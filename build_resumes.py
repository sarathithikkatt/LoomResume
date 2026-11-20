import re
import os
from playwright.sync_api import sync_playwright

output_dir = r"D:\Dev\LoomResume"

common_css = """
@page {
  size: letter;
  margin: 0.35in 0.45in 0.35in 0.45in;
}
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
body {
  font-family: Arial, "Helvetica Neue", Helvetica, sans-serif;
  color: #1a1a1a;
  background: #ffffff;
  font-size: 8.5pt;
  line-height: 1.25;
}
a {
  color: #1a1a1a;
  text-decoration: none;
}
.header {
  text-align: center;
  margin-bottom: 5px;
}
.name {
  font-size: 16pt;
  font-weight: 700;
  letter-spacing: 0.6px;
  color: #0f172a;
  text-transform: uppercase;
  margin-bottom: 2px;
}
.contact {
  font-size: 8.2pt;
  color: #334155;
}
.contact span {
  margin: 0 4px;
  color: #94a3b8;
}
.section-title {
  font-size: 9.2pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #0f172a;
  border-bottom: 1px solid #0f172a;
  padding-bottom: 1px;
  margin-top: 5px;
  margin-bottom: 3px;
}
.summary-text {
  font-size: 8.3pt;
  color: #1e293b;
  text-align: justify;
  line-height: 1.24;
}
.skill-group {
  margin-bottom: 1.5px;
  font-size: 8.2pt;
  line-height: 1.22;
}
.skill-group strong {
  color: #0f172a;
  font-weight: 700;
}
.role-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-top: 3px;
  margin-bottom: 1px;
}
.role-title {
  font-size: 8.6pt;
  font-weight: 700;
  color: #0f172a;
}
.role-company {
  font-weight: 400;
  color: #334155;
}
.role-meta {
  font-size: 8.2pt;
  font-weight: 600;
  color: #475569;
  white-space: nowrap;
}
.project-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-top: 3px;
  margin-bottom: 1px;
}
.project-title {
  font-size: 8.6pt;
  font-weight: 700;
  color: #0f172a;
}
.project-tech {
  font-weight: 400;
  font-style: italic;
  color: #475569;
  font-size: 8pt;
}
.project-link {
  font-size: 8pt;
  color: #0369a1;
}
ul {
  padding-left: 14px;
  margin-top: 1px;
  margin-bottom: 2px;
}
li {
  font-size: 8.2pt;
  color: #1e293b;
  margin-bottom: 1.5px;
  line-height: 1.22;
}
.edu-row {
  display: flex;
  justify-content: space-between;
  font-size: 8.3pt;
  margin-top: 1.5px;
}
.edu-row strong {
  color: #0f172a;
}
.achieve-row {
  font-size: 8.2pt;
  margin-top: 1.5px;
  color: #1e293b;
  line-height: 1.22;
}
"""

# 1. FRONTEND RESUME HTML
html_frontend = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Anoop Sidhan - Frontend Engineer Resume</title>
<style>{common_css}</style>
</head>
<body>
  <div class="header">
    <div class="name">Anoop Sidhan</div>
    <div class="contact">
      Kerala, India <span>|</span> +91 7593023443 <span>|</span> anoopsidhan777@gmail.com <span>|</span> www.anoop.pro <span>|</span> linkedin.com/in/anoopdev <span>|</span> github.com/Anoop072001
    </div>
  </div>

  <div class="section-title">Professional Summary</div>
  <div class="summary-text">
    Frontend Engineer with 2+ years of experience engineering high-performance, responsive web applications and design systems serving 30,000+ users. Expert in TypeScript, React 19, Next.js (App Router), Tailwind CSS, TanStack Query, and Zustand. Proven track record of architecting 50+ route enterprise web platforms, complex client/server state workflows, interactive analytics dashboards, and Web3 wallet interfaces. Grounded in enterprise test automation and cross-browser reliability.
  </div>

  <div class="section-title">Technical Skills</div>
  <div class="skill-group"><strong>Frontend Core:</strong> React, Next.js (App Router, SSR, SSG), TypeScript, JavaScript (ES6+), HTML5, CSS3, Vite</div>
  <div class="skill-group"><strong>State & Data Fetching:</strong> TanStack Query (React Query), Zustand, Context API, Axios, WebSockets</div>
  <div class="skill-group"><strong>UI & Design Systems:</strong> Tailwind CSS v4, shadcn/ui, Radix UI, Framer Motion, TipTap Rich Text, Recharts</div>
  <div class="skill-group"><strong>Forms & Validation:</strong> React Hook Form, Zod</div>
  <div class="skill-group"><strong>Web3 & Integrations:</strong> RainbowKit, Wagmi, viem, ethers.js, Razorpay Checkout.js, OpenAI API</div>
  <div class="skill-group"><strong>Cloud, DevOps & Testing:</strong> Docker, GCP Cloud Run, Azure VM, GitHub Actions (CI/CD), Vercel, Selenium, Postman, Git</div>

  <div class="section-title">Professional Experience</div>
  <div class="role-header">
    <div><span class="role-title">Levantate Labs</span> <span class="role-company">— Frontend / Full Stack Developer</span></div>
    <div class="role-meta">Kerala, India | Feb 2026 – Present</div>
  </div>
  <ul>
    <li>Architected the frontend for <strong>Maestro</strong>, an online LMS spanning <strong>50+ Next.js App Router routes</strong> with TypeScript, serving student, instructor, and admin experiences with optimized Core Web Vitals.</li>
    <li>Engineered interactive course learning flows—video player, curriculum sidebar, and learning paths—using <strong>TanStack Query</strong> for server state synchronization and <strong>Zustand</strong> for client UI state.</li>
    <li>Built GitHub assignment workflows: GitHub App OAuth connect flow, repository selection, submission/review steps, and responsive OpenGraph link preview cards using container-query layouts.</li>
    <li>Developed instructor authoring tools with <strong>TipTap rich text editors</strong> and administrative analytics dashboards featuring <strong>Recharts</strong>, role-based access control, and audit logs.</li>
    <li>Designed a responsive UI component library with <strong>Tailwind CSS v4, shadcn/ui, and Radix UI</strong>; integrated Razorpay checkout and implemented type-safe form validation using <strong>React Hook Form + Zod</strong>.</li>
    <li>Built and deployed high-converting web interfaces for client platforms <strong>exploitless.com</strong> and <strong>veretin.com</strong> using Next.js and Prisma.</li>
  </ul>

  <div class="role-header">
    <div><span class="role-title">Planck Network</span> <span class="role-company">— Web3 Frontend Developer</span></div>
    <div class="role-meta">Remote | Jun 2025 – May 2026</div>
  </div>
  <ul>
    <li>Architected and launched the full UI for <strong>Planck Hub</strong> and <strong>Planck Explorer</strong> from scratch, onboarding <strong>30,000+ users</strong> and scaling to <strong>80M+ tokens</strong> staked at peak.</li>
    <li>Integrated Blockscout APIs for real-time L1 blockchain metrics; implemented Web3 wallet onboarding via <strong>RainbowKit and Wagmi</strong> with robust error handling boundaries.</li>
    <li>Containerized frontend builds with <strong>Docker</strong> and deployed to <strong>GCP Cloud Run</strong>; automated release pipelines using GitHub Actions CI/CD to eliminate deployment downtime.</li>
    <li>Engineered responsive client application <strong>AirBubble.ai</strong> using React and Vite; deployed on an Azure VM with Nginx reverse proxy (port 443/SSL) and automated CI/CD deployments.</li>
  </ul>

  <div class="role-header">
    <div><span class="role-title">IBM (Client: JP Morgan Chase & Co.)</span> <span class="role-company">— Quality Engineer</span></div>
    <div class="role-meta">India | Feb 2024 – Feb 2025</div>
  </div>
  <ul>
    <li>Automated enterprise UI and API regression suites using <strong>Java, Selenium WebDriver, and Cucumber (BDD)</strong>, reducing manual testing effort by <strong>80%</strong>.</li>
    <li>Validated UI workflows for the Trade Processing System (TPS) including document ingestion, versioning panels, dynamic forms, and RBAC permissions across multi-environment test beds.</li>
    <li>Collaborated with developers in Agile/Scrum ceremonies to review UI acceptance criteria and resolve defects early in sprint cycles.</li>
  </ul>

  <div class="section-title">Key Projects</div>
  <div class="project-header">
    <div><span class="project-title">Levantate Bridge — AI-to-Human Task Marketplace (ETHOnline 2026)</span></div>
    <div><span class="project-link">ethglobal.com/showcase/levantate-bridge-urkyw</span></div>
  </div>
  <div class="project-tech">Next.js 16, React 19, TypeScript, Tailwind CSS 4, RainbowKit, Wagmi, TanStack Query, World ID (IDKit)</div>
  <ul>
    <li>Engineered a full-stack Web3 marketplace connecting autonomous AI agents with human workers, with USDC escrow on Arc testnet.</li>
    <li>Integrated World ID biometric Selfie Check verification on bidding forms and live event indexing from The Graph.</li>
    <li>Built fluid layouts with side drawers, modal dialogs, and real-time bid status updates using TanStack Query.</li>
  </ul>

  <div class="project-header">
    <div><span class="project-title">BidaDate — Real-Time Social Ranking Platform</span></div>
    <div><span class="project-link">bidadate.lol</span></div>
  </div>
  <div class="project-tech">Next.js, TypeScript, Tailwind CSS, Supabase, Razorpay Checkout.js, Drizzle ORM</div>
  <ul>
    <li>Developed a full-stack platform featuring dynamic real-time leaderboards sorted by bid volume across regional and national boards.</li>
    <li>Integrated Razorpay Checkout.js modal with instant client feedback states, error boundary fallbacks, and optimistic UI updates.</li>
  </ul>

  <div class="section-title">Education & Achievements</div>
  <div class="edu-row">
    <div><strong>B.Tech in Computer Science & Engineering</strong> — Christ College of Engineering, Kerala</div>
    <div class="role-meta">2019 – 2023 | CGPA: 8.81 / 10.0</div>
  </div>
  <div class="achieve-row">
    • <strong>Winner – Hac'KP Hackathon (2021):</strong> 1st place out of 500+ teams. &nbsp;|&nbsp; • <strong>Cybersecurity:</strong> Designed and deployed Grapnel 1.0 dark web monitoring tool for Kerala Police Cyberdome.
  </div>
</body>
</html>
"""

# 2. FULL STACK RESUME HTML
html_fullstack = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Anoop Sidhan - Full Stack Developer Resume</title>
<style>{common_css}</style>
</head>
<body>
  <div class="header">
    <div class="name">Anoop Sidhan</div>
    <div class="contact">
      Kerala, India <span>|</span> +91 7593023443 <span>|</span> anoopsidhan777@gmail.com <span>|</span> www.anoop.pro <span>|</span> linkedin.com/in/anoopdev <span>|</span> github.com/Anoop072001
    </div>
  </div>

  <div class="section-title">Professional Summary</div>
  <div class="summary-text">
    Full Stack Software Engineer with 2+ years of experience designing and scaling production web services, distributed systems, and cloud infrastructure serving 30,000+ users. Proficient in TypeScript, Node.js, Next.js, Spring Boot (Java), and PostgreSQL. Experienced in architecting RESTful APIs, relational database schemas with complex indexing and triggers, event-driven payment flows, and automated CI/CD pipelines. Strong enterprise background in API verification and data validation from IBM.
  </div>

  <div class="section-title">Technical Skills</div>
  <div class="skill-group"><strong>Languages:</strong> TypeScript, JavaScript, Java, SQL, C++, Solidity</div>
  <div class="skill-group"><strong>Backend Frameworks & APIs:</strong> Node.js, Next.js Server Actions & API Routes, Express.js, Spring Boot, RESTful APIs</div>
  <div class="skill-group"><strong>Databases & ORMs:</strong> PostgreSQL (RLS, Triggers, Indexes), Supabase, MySQL, MongoDB, Prisma ORM, Drizzle ORM</div>
  <div class="skill-group"><strong>Frontend:</strong> React, Next.js (App Router), Tailwind CSS, TanStack Query, Zustand, shadcn/ui, React Hook Form, Zod</div>
  <div class="skill-group"><strong>Cloud & DevOps:</strong> Docker, Google Cloud Platform (Cloud Run, Artifact Registry), Microsoft Azure (VM, Nginx), CI/CD (GitHub Actions)</div>
  <div class="skill-group"><strong>Auth, Testing & Tools:</strong> NextAuth v5, Razorpay API (HMAC SHA-256), Selenium, Postman, TestNG, Git/GitHub, Jira, Linux</div>

  <div class="section-title">Professional Experience</div>
  <div class="role-header">
    <div><span class="role-title">Levantate Labs</span> <span class="role-company">— Full Stack Developer</span></div>
    <div class="role-meta">Kerala, India | Feb 2026 – Present</div>
  </div>
  <ul>
    <li>Architected full-stack backend services and UI for <strong>Maestro LMS</strong> across 50+ routes using Next.js App Router, TypeScript, and TanStack Query for seamless server-client state caching.</li>
    <li>Designed database models and relational queries for <strong>exploitless.com</strong> and <strong>veretin.com</strong> using <strong>PostgreSQL, Prisma 7 (@prisma/adapter-pg), and MongoDB</strong>.</li>
    <li>Implemented secure authentication for administrative dashboards using <strong>NextAuth v5 (Auth.js)</strong> with @auth/prisma-adapter and bcryptjs password hashing.</li>
    <li>Integrated <strong>Razorpay Orders API</strong> with server-side order generation, webhook callback handlers, and HMAC signature validation to handle paid enrollments securely.</li>
    <li>Developed and scheduled background Node.js cron workers to fetch, sanitize, and cache external social feeds into PostgreSQL databases.</li>
    <li>Engineered marketing platform <strong>levantate.in</strong> with Next.js and MongoDB, enhancing digital presence and client lead acquisition.</li>
  </ul>

  <div class="role-header">
    <div><span class="role-title">Planck Network</span> <span class="role-company">— Web3 Full Stack Developer</span></div>
    <div class="role-meta">Remote | Jun 2025 – May 2026</div>
  </div>
  <ul>
    <li>Built core web infrastructure for <strong>Planck Hub</strong> and <strong>Planck Explorer</strong>, supporting <strong>30,000+ onboarded users</strong> and <strong>80M+ tokens</strong> staked at peak.</li>
    <li>Containerized web services and applications using <strong>Docker</strong>; deployed images to <strong>GCP Artifact Registry</strong> and managed serverless hosting on <strong>GCP Cloud Run</strong>.</li>
    <li>Architected automated <strong>GitHub Actions CI/CD pipelines</strong> for automated testing, container builds, and zero-downtime production deployments.</li>
    <li>Provisioned an <strong>Azure VM</strong> with Linux, SSH hardening, and configured <strong>Nginx as a reverse proxy</strong> on port 443 with automated SSL certificates for AirBubble.ai.</li>
  </ul>

  <div class="role-header">
    <div><span class="role-title">IBM (Client: JP Morgan Chase & Co.)</span> <span class="role-company">— Quality Engineer</span></div>
    <div class="role-meta">India | Feb 2024 – Feb 2025</div>
  </div>
  <ul>
    <li>Developed automated API and integration test suites in <strong>Java, Selenium, and Cucumber</strong>, cutting manual regression testing effort by <strong>80%</strong>.</li>
    <li>Validated high-volume modules within the Trade Processing System (TPS), verifying document ingestion pipelines, metadata accuracy, and transaction consistency.</li>
    <li>Executed comprehensive database validations across <strong>PostgreSQL, Oracle, and MySQL Server</strong> using complex SQL scripts to ensure absolute financial data integrity.</li>
    <li>Debugged REST API payloads via <strong>Postman</strong> and tracked issues in Jira, actively participating in Agile/Scrum sprint delivery.</li>
  </ul>

  <div class="section-title">Key Projects</div>
  <div class="project-header">
    <div><span class="project-title">Job Finder — Automated Referral & Outreach Platform</span></div>
    <div><span class="project-link">github.com/Anoop072001/ReferralAutomation</span></div>
  </div>
  <div class="project-tech">Spring Boot, Next.js, Java, TypeScript, OpenAI API, RapidAPI, PostgreSQL, Tailwind CSS</div>
  <ul>
    <li>Engineered a full-stack tool matching candidate resumes and location data to live listings via LinkedIn RapidAPI with a <strong>Spring Boot</strong> backend.</li>
    <li>Integrated <strong>OpenAI API</strong> to programmatically generate personalized cold emails and referral pitches, reducing manual outreach time by 75%.</li>
    <li>Crafted responsive Next.js frontend with Tailwind CSS and connected to Spring Boot REST endpoints for profile and application tracking.</li>
  </ul>

  <div class="project-header">
    <div><span class="project-title">BidaDate — Real-Time Pay-to-Rank Social Platform</span></div>
    <div><span class="project-link">bidadate.lol</span></div>
  </div>
  <div class="project-tech">Next.js, TypeScript, PostgreSQL, Drizzle ORM, Supabase, Razorpay API, Resend</div>
  <ul>
    <li>Architected PostgreSQL schema with composite/partial indexes on hot query paths and <strong>PL/pgSQL triggers</strong> for append-only bid logs and discoverability sync.</li>
    <li>Implemented Supabase Auth with Resend email OTP, Row-Level Security (RLS) policies, and Drizzle ORM over direct Postgres connection.</li>
    <li>Built Razorpay checkout with HMAC SHA-256 signature verification and webhook backup safety nets for dropped sessions.</li>
  </ul>

  <div class="section-title">Education & Achievements</div>
  <div class="edu-row">
    <div><strong>B.Tech in Computer Science & Engineering</strong> — Christ College of Engineering, Kerala</div>
    <div class="role-meta">2019 – 2023 | CGPA: 8.81 / 10.0</div>
  </div>
  <div class="achieve-row">
    • <strong>Winner – Hac'KP Hackathon (2021):</strong> 1st place out of 500+ teams. &nbsp;|&nbsp; • <strong>Cybersecurity:</strong> Designed and deployed Grapnel 1.0 dark web monitoring tool for Kerala Police Cyberdome.
  </div>
</body>
</html>
"""

# 3. FINTECH & ENTERPRISE RESUME HTML
html_fintech = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Anoop Sidhan - Fintech & Enterprise Software Engineer Resume</title>
<style>{common_css}</style>
</head>
<body>
  <div class="header">
    <div class="name">Anoop Sidhan</div>
    <div class="contact">
      Kerala, India <span>|</span> +91 7593023443 <span>|</span> anoopsidhan777@gmail.com <span>|</span> www.anoop.pro <span>|</span> linkedin.com/in/anoopdev <span>|</span> github.com/Anoop072001
    </div>
  </div>

  <div class="section-title">Professional Summary</div>
  <div class="summary-text">
    Software Engineer with 2+ years of experience engineering secure, mission-critical systems, transactional payment integrations, and automated enterprise verification pipelines. Former Quality Engineer at IBM delivering test automation for JP Morgan Chase & Co.'s Trade Processing System. Proficient in TypeScript, Java, PostgreSQL, Node.js, and Docker. Deep expertise in HMAC payment verification, Row-Level Security (RLS), ACID data integrity, and CI/CD reliability.
  </div>

  <div class="section-title">Technical Skills</div>
  <div class="skill-group"><strong>Languages:</strong> TypeScript, JavaScript, Java, SQL, Solidity, C++</div>
  <div class="skill-group"><strong>Enterprise & Backend:</strong> Node.js, Next.js Server Actions/APIs, Spring Boot, REST APIs, Microservices, NextAuth v5</div>
  <div class="skill-group"><strong>Databases & Data Integrity:</strong> PostgreSQL (RLS, Partial Indexes, Triggers), Oracle DB, MySQL, Drizzle ORM, Prisma ORM</div>
  <div class="skill-group"><strong>Payments & Security:</strong> Razorpay (HMAC SHA-256 Signatures, Webhooks), Circle Wallets, Escrow Smart Contracts, bcryptjs, SSL/TLS, RBAC</div>
  <div class="skill-group"><strong>Cloud & Infrastructure:</strong> Docker, GCP (Cloud Run, Artifact Registry), Azure VM, Nginx Reverse Proxy, GitHub Actions (CI/CD)</div>
  <div class="skill-group"><strong>Testing & Compliance:</strong> Selenium WebDriver, BDD/Cucumber, TestNG, Postman API Testing, Enterprise Audit Logs, Agile/Scrum</div>

  <div class="section-title">Professional Experience</div>
  <div class="role-header">
    <div><span class="role-title">IBM</span> <span class="role-company">— Software Quality Engineer (Client: JP Morgan Chase & Co.)</span></div>
    <div class="role-meta">India | Feb 2024 – Feb 2025</div>
  </div>
  <ul>
    <li>Automated end-to-end regression test suites for the <strong>Trade Processing System (TPS)</strong> using <strong>Java, Selenium, and BDD (Cucumber)</strong>, reducing manual verification effort by <strong>80%</strong>.</li>
    <li>Validated enterprise document upload pipelines, metadata schemas, version control integrity, and Role-Based Access Control (RBAC) across multi-tenant environments.</li>
    <li>Executed automated REST API verification with <strong>Postman</strong> and complex SQL validation scripts across <strong>Oracle, PostgreSQL, and MySQL Server</strong> to enforce zero financial data discrepancy.</li>
    <li>Spearheaded defect triaging in Agile sprints alongside product owners and development leads, achieving rapid defect turnaround and preventing critical production escapes.</li>
    <li>Authored technical test specifications and trained incoming engineers on automated testing frameworks and enterprise verification standards.</li>
  </ul>

  <div class="role-header">
    <div><span class="role-title">Levantate Labs</span> <span class="role-company">— Full Stack Software Engineer</span></div>
    <div class="role-meta">Kerala, India | Feb 2026 – Present</div>
  </div>
  <ul>
    <li>Engineered transaction pipelines with <strong>Razorpay</strong>: implemented server-side order generation, client Checkout.js handling, HMAC signature verification, and asynchronous webhook listeners for transactional safety.</li>
    <li>Built administrative audit logging, role permissions, and financial order reporting for <strong>Maestro LMS</strong> using Next.js App Router, TypeScript, and Recharts.</li>
    <li>Shipped <strong>exploitless.com</strong>, a security-focused client product, implementing <strong>NextAuth v5</strong> via @auth/prisma-adapter, PostgreSQL via Prisma 7, and bcryptjs cryptographic password hashing.</li>
    <li>Programmed scheduled background workers and cron jobs for database synchronization and secure API caching with PostgreSQL.</li>
  </ul>

  <div class="role-header">
    <div><span class="role-title">Planck Network</span> <span class="role-company">— Web3 Systems & Frontend Developer</span></div>
    <div class="role-meta">Remote | Jun 2025 – May 2026</div>
  </div>
  <ul>
    <li>Developed infrastructure and web interfaces for high-value blockchain platforms managing <strong>80M+ tokens staked</strong> at peak and <strong>30,000+ active users</strong>.</li>
    <li>Containerized services with <strong>Docker</strong> and deployed production workloads to <strong>GCP Cloud Run</strong> and Artifact Registry via GitHub Actions CI/CD pipelines.</li>
    <li>Hardened and maintained an <strong>Azure Linux VM</strong> production instance: configured <strong>Nginx reverse proxy on port 443 with SSL/TLS termination</strong>, SSH key-only access, and automated deployment scripts.</li>
  </ul>

  <div class="section-title">Key Projects</div>
  <div class="project-header">
    <div><span class="project-title">BidaDate — Secure Transactional Ranking Platform</span></div>
    <div><span class="project-link">bidadate.lol</span></div>
  </div>
  <div class="project-tech">Next.js, PostgreSQL, Drizzle ORM, Supabase, Razorpay API, Resend, Tailwind CSS</div>
  <ul>
    <li>Built a secure ranking platform with transactional bidding leaderboards sorted dynamically by bid amount and timestamp.</li>
    <li>Implemented <strong>HMAC SHA-256 signature verification</strong> on checkout callbacks paired with a serverless webhook reconciliation worker to prevent payment tampering and dropped transactions.</li>
    <li>Designed PostgreSQL schema with partial indexing on hot query paths and <strong>PL/pgSQL triggers</strong> for immutable, append-only bid audit logs and strict Row-Level Security (RLS).</li>
  </ul>

  <div class="project-header">
    <div><span class="project-title">Levantate Bridge — Smart Contract Escrow & Verification Marketplace (ETHOnline 2026)</span></div>
    <div><span class="project-link">ethglobal.com/showcase/levantate-bridge-urkyw</span></div>
  </div>
  <div class="project-tech">Solidity, Foundry, Next.js 16, Circle Wallets SDK, World ID, The Graph, GPT-4o</div>
  <ul>
    <li>Engineered an autonomous task marketplace with programmatic <strong>USDC escrow contracts</strong> on Arc testnet using Circle Developer-Controlled Wallets.</li>
    <li>Enforced Sybil-resistant identity gating via <strong>World ID biometric verification</strong> and indexed on-chain financial settlement events via The Graph.</li>
  </ul>

  <div class="section-title">Education & Achievements</div>
  <div class="edu-row">
    <div><strong>B.Tech in Computer Science & Engineering</strong> — Christ College of Engineering, Kerala</div>
    <div class="role-meta">2019 – 2023 | CGPA: 8.81 / 10.0</div>
  </div>
  <div class="achieve-row">
    • <strong>Winner – Hac'KP Hackathon (2021):</strong> 1st place out of 500+ teams. &nbsp;|&nbsp; • <strong>Cybersecurity:</strong> Designed and deployed <strong>Grapnel 1.0</strong>, an automated dark web monitoring tool for the Kerala Police Cyberdome.
  </div>
</body>
</html>
"""

files_to_render = [
    ("Anoop_Sidhan_Resume_Frontend.html", "Anoop_Sidhan_Resume_Frontend.pdf", html_frontend),
    ("Anoop_Sidhan_Resume_FullStack.html", "Anoop_Sidhan_Resume_FullStack.pdf", html_fullstack),
    ("Anoop_Sidhan_Resume_Fintech.html", "Anoop_Sidhan_Resume_Fintech.pdf", html_fintech)
]

for html_name, pdf_name, content in files_to_render:
    html_path = os.path.join(output_dir, html_name)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    for html_name, pdf_name, content in files_to_render:
        html_path = os.path.join(output_dir, html_name)
        pdf_path = os.path.join(output_dir, pdf_name)
        page = browser.new_page()
        page.goto(f"file:///{html_path.replace(os.sep, '/')}")
        page.pdf(path=pdf_path, format="Letter", print_background=True, margin={"top": "0.35in", "right": "0.45in", "bottom": "0.35in", "left": "0.45in"})
        page.close()
    browser.close()

print("All PDFs generated. Checking page counts...")
for _, pdf_name, _ in files_to_render:
    pdf_path = os.path.join(output_dir, pdf_name)
    with open(pdf_path, "rb") as f:
        data = f.read()
    page_count = len(re.findall(rb'/Type\s*/Page\b', data))
    size_kb = len(data) / 1024
    print(f"{pdf_name}: {page_count} page(s) | {size_kb:.1f} KB")
