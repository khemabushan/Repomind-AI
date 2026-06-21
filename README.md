# 🚀 RepoMind AI

**AI-Powered GitHub Repository Intelligence Platform**

RepoMind AI helps developers understand any GitHub repository within seconds by automatically generating architecture insights, documentation, onboarding guides, complexity analysis, diagrams, recruiter summaries, and interview preparation content.

---

## 📌 Overview

Understanding large codebases is time-consuming and challenging, especially when joining new projects or reviewing open-source repositories.

RepoMind AI solves this problem by automatically analyzing a GitHub repository and generating:

* 📄 Executive summaries
* 🏗 Architecture analysis
* 📂 Folder structure explanations
* 📘 API documentation
* 🎯 Onboarding guides
* 📊 Complexity metrics
* 🔷 Mermaid architecture diagrams
* 💼 Recruiter-friendly project summaries
* 🎤 Interview preparation content
* 🤖 AI-powered repository insights

Simply paste a GitHub repository URL and RepoMind AI performs the analysis automatically.

---

## ✨ Features

### 📄 Executive Summary

Generates a high-level overview of the repository, including:

* Project purpose
* Target audience
* Technology stack
* Production readiness
* Key technical highlights

### 🏗 Architecture Detection

Automatically identifies:

* Monolithic Architecture
* MVC Architecture
* MERN Stack
* FastAPI Projects
* React Applications
* Microservice Structures

### 📂 Repository Explorer

Analyzes:

* Folder organization
* Important files
* Project structure
* Source code layout

### 📘 Documentation Generator

Creates:

* Project documentation
* Technical summaries
* Developer-friendly explanations

### 🎯 Onboarding Guide

Generates onboarding instructions for new developers.

### 📊 Complexity Analysis

Measures:

* Lines of code
* Repository size
* Language distribution
* Project complexity

### 🔷 Mermaid Diagram Generator

Automatically creates architecture diagrams using Mermaid syntax.

### 💼 Recruiter View

Generates recruiter-friendly descriptions highlighting:

* Business value
* Technical skills
* Resume-ready summaries

### 🎤 Interview Preparation

Produces likely interview questions based on repository content.

### 🤖 AI-Powered Insights

Uses LLM-powered analysis to understand project structure and functionality.

---

## 🏗 System Architecture

Frontend → FastAPI Backend → Repository Analyzer → AI Engine → Documentation Generator

Workflow:

1. User submits GitHub repository URL
2. Repository is cloned locally
3. Source files are analyzed
4. Architecture is detected
5. Documentation is generated
6. Complexity metrics are calculated
7. Diagrams are generated
8. Results are displayed in the dashboard

---

## 🛠 Tech Stack

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* Axios

### Backend

* FastAPI
* Python
* SQLAlchemy
* AsyncIO
* GitPython

### Database

* SQLite (Development)

### AI & Analysis

* OpenAI API
* Custom Repository Analysis Engine
* Mermaid Diagram Generation

### DevOps

* Docker
* Docker Compose
* Nginx

---

## 📁 Project Structure

```text
repomind/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── workers/
│   │   └── core/
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── services/
│
└── docker-compose.yml
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/khemabushan/Repomind-AI.git
cd Repomind-AI
```

### Backend Setup

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

Create `.env`

```env
OPENAI_API_KEY=your_api_key
```

Run backend:

```bash
python -m uvicorn app.main:app --reload --port 8001
```

---

### Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

Backend API:

```text
http://localhost:8001
```

Swagger Docs:

```text
http://localhost:8001/docs
```

---

## 🚀 Usage

1. Open the application
2. Paste a GitHub repository URL
3. Click **Analyze Repository**
4. Wait for analysis to complete
5. Explore generated insights

Available sections:

* Summary
* Architecture
* Folders
* Setup Guide
* API Docs
* README
* Recruiter View
* Interview Questions
* Onboarding Guide
* Diagrams
* Complexity Metrics

---

## 📈 Future Enhancements

* Multi-repository comparison
* GitHub authentication
* Vector database integration
* Advanced RAG pipeline
* Repository chat assistant
* CI/CD analysis
* Security scanning
* Cloud deployment support

---

## 🎯 Learning Outcomes

This project demonstrates:

* Full-Stack Development
* FastAPI Backend Design
* React + TypeScript Development
* REST API Development
* AI Integration
* Repository Analysis
* System Architecture Understanding
* Docker Deployment

---

## 👨‍💻 Author

**Hemabushan K**

B.Tech Computer Science & Engineering (AI & ML)

GitHub:
https://github.com/khemabushan

---

## ⭐ Support

If you found this project useful, consider giving it a star on GitHub.
