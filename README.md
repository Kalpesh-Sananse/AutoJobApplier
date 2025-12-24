🚀 AI-Assisted Auto Job Applier
Production-Ready Job Automation using n8n, RAG & LLMs
📌 Overview

AI-Assisted Auto Job Applier automates job discovery, intelligent matching, and controlled job applications using n8n workflows, RAG, and LLMs.
It is built with a production mindset—ethical automation, transparency, and scalability.

🎯 Scope

This project will:

Fetch real-time job listings from job APIs / aggregators

Match jobs with user profiles using RAG + LLMs

Apply automatically to relevant jobs with safety checks

Provide a web dashboard for job feed, tracking, and profile management

Track applied, skipped, and failed applications

This project will not:

Bypass CAPTCHA or platform restrictions

Mass-apply blindly

Guarantee job offers

🧠 Architecture (High Level)
Dashboard → Backend API → n8n → RAG + LLM → Playwright Worker → Job Platforms

🛠️ Tech Stack

Frontend: React / Next.js

Backend: Node.js / FastAPI

Automation: n8n

AI: LLM (OpenAI / Gemini / Local)

RAG: Chroma / Pinecone

Browser Automation: Playwright

Database: PostgreSQL / Firebase

📦 Get Started
git clone https://github.com/Kalpesh-Sananse/AutoJobApplier.git
cd AutoJobApplier

🚧 Status

🟡 Architecture & workflow design phase
🔜 Backend, RAG pipeline & dashboard development

👨‍💻 Author

Kalpesh Sanasne
Android • Full-Stack • GenAI Developer

⭐ Built as a real-world, production-ready AI automation system — not a demo.
