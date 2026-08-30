<![CDATA[<div align="center">

# 🚀 JeevanYaan — An AI-Powered Career & Wellness Companion

**A full-stack Generative AI web application built with Django, LangChain, LangGraph, and CatBoost that empowers users with intelligent career planning, academic assistance, and mental health insights — all in one platform.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](https://djangoproject.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?logo=chainlink&logoColor=white)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.5-FF6F00?logo=graphql&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq_LPU-Cloud-F55036?logo=groq&logoColor=white)](https://groq.com)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Technology Stack](#-technology-stack)
- [AI Modules Deep Dive](#-ai-modules-deep-dive)
- [Database Design](#-database-design)
- [Authentication & Authorization](#-authentication--authorization)
- [Deployment Modes](#-deployment-modes)
- [API & External Services](#-api--external-services)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Future Scope](#-future-scope)
- [License](#-license)

---

## 🌟 Overview

**JeevanYaan** (जीवनयान — *"Vehicle of Life"*) is a comprehensive AI-powered companion designed to address two critical aspects of a user's life: **career development** and **mental wellness**. The platform bundles eight distinct AI-powered modules — each backed by LLMs, agentic graphs, machine learning models, and real-time web search — into a unified Django web application.

The application follows a modular, agent-based architecture where each tool is implemented as an independent utility module that can leverage:
- **LangGraph state machines** for multi-step agentic workflows
- **RAG (Retrieval-Augmented Generation)** with FAISS vector stores
- **CatBoost ML classifiers** for predictive health analytics
- **Tavily & GitHub APIs** for real-time web intelligence
- **Branded PDF report generation** with template overlays

---

## ✨ Key Features

| Module | Description | AI Technique |
|--------|-------------|--------------|
| 🎯 **Career Planner** | Generates personalized career plans with role recommendations, skill gap analysis, and learning roadmaps | LangGraph Agent + Tavily Web Search |
| 🧠 **Mental Health Analyzer** | Predicts mental health risk using lifestyle data and generates AI-powered wellness reviews | CatBoost ML + LLM Expert Review |
| 📝 **Quiz Maker** | Creates custom MCQ quizzes with auto-grading and AI-generated explanations for incorrect answers | LLM (JSON Output Parsing) |
| 🔬 **Research Agent** | Searches, scrapes, and synthesizes web articles into cohesive research summaries | LangGraph (Search → Scrape → Summarize) |
| 📄 **Resume Scanner** | Analyzes uploaded resumes using RAG to generate scores, strengths, and job role recommendations | RAG (FAISS + HuggingFace Embeddings) |
| 🗺️ **Roadmap Creator** | Builds skill-based learning roadmaps by discovering top GitHub repositories in any domain | GitHub API + LLM Synthesis |
| 📚 **Notes Assistant** | Processes uploaded documents (PDF/DOCX/TXT) into summaries, revision notes, or practice Q&A | LangGraph Map-Reduce + Multi-Model Pipeline |
| 📰 **News Portal** | Fetches and presents categorized trending news with time-based filtering | Tavily News Search API |

### Cross-Cutting Features

- **📥 PDF Export** — Every tool's output can be downloaded as a branded PDF report with custom background templates
- **🔒 Role-Based Rate Limiting** — Admin-configurable daily usage quotas per tool, per user group
- **👤 Smart User Profiles** — Profile data auto-fills into AI tools for personalized context
- **💭 Thought of the Day** — Session-cached AI-generated daily motivational thoughts
- **📊 Usage Analytics** — CSV-based token usage and response metadata logging
- **🖥️ Desktop App Mode** — Launch as a native desktop application via PyWebView + Waitress

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser / Desktop)                │
│              HTML Templates + CSS + JavaScript                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTP
┌────────────────────────────▼─────────────────────────────────────┐
│                     DJANGO APPLICATION LAYER                     │
│                                                                  │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐               │
│  │  URLs    │──│    Views     │──│    Forms      │               │
│  │ (Router) │  │ (Controllers)│  │ (Validation)  │               │
│  └──────────┘  └──────┬───────┘  └───────────────┘               │
│                       │                                          │
│  ┌────────────────────▼──────────────────────────────────────┐   │
│  │                UTILITY MODULES (main/utils/)              │   │
│  │                                                           │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌──────────────────┐     │   │
│  │  │  LangGraph  │ │    RAG      │ │   ML Inference   │     │   │
│  │  │  Agents     │ │  Pipelines  │ │   (CatBoost)     │     │   │
│  │  └──────┬──────┘ └──────┬──────┘ └────────┬─────────┘     │   │
│  │         │               │                  │              │   │
│  │  ┌──────▼──────────────▼──────────────────▼────────────┐  │   │
│  │  │           SHARED INFRASTRUCTURE                     │  │   │
│  │  │  • PDF Generator  • Rate Limiter  • Usage Logger    │  │   │
│  │  └──────────────────────────────────────────────────── ┘  │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────────┐    │
│  │   Models    │  │  Admin Panel     │  │  Template Tags    │    │
│  │  (ORM)      │  │  (Django Admin)  │  │  (Custom Filters) │    │
│  └──────┬──────┘  └──────────────────┘  └───────────────────┘    │
└─────────┼────────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────────┐
│                       DATA LAYER                                 │
│                                                                  │
│   MySQL (Production/Dev)  │  SQLite (Desktop)  │  Cloud DB URL   │
│                                                                  │
│   ml_models/catboost_model_v4.cbm   (Pre-trained ML Model)       │
└──────────────────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                              │
│                                                                  │
│   Groq LPU Cloud (LLM API)  │  Tavily (Web Search & News)        │
│   GitHub API (Repositories)  │  HuggingFace (Embeddings)         │
└──────────────────────────────────────────────────────────────────┘
```

### Request Flow (Example: Career Planner)

```
User submits form
  → views.career_planner_view()
    → rate_limiter.check_and_get_limit()   # Check daily quota
    → career_planner.get_career_plan()     # Enter LangGraph
      → StateGraph compiles & invokes
        → Tavily web search for career insights
        → LLM generates personalized plan (with web context)
        → Fallback to LLM-only if web search fails
      → logger.log_response_metadata()    # Log token usage to CSV
    → Render result to template (Markdown → HTML)
    → User clicks "Download PDF"
      → pdf_generator.create_pdf_bytes()  # Markdown → HTML → PDF + Background overlay
```

---

## 📁 Project Structure

```
jeevanyaan/                          # Django Project Root
├── jeevanyaan/                      # Project Configuration Package
│   ├── settings.py                  # Multi-mode DB config (MySQL/SQLite/Cloud)
│   ├── urls.py                      # Root URL router
│   ├── wsgi.py                      # WSGI entry point (Gunicorn/Waitress)
│   └── asgi.py                      # ASGI entry point
│
├── main/                            # Primary Django Application
│   ├── views.py                     # All view controllers (~700 lines)
│   ├── profile_views.py             # User profile management view
│   ├── models.py                    # UserProfile, ModulesControl, UserModuleUsage
│   ├── forms.py                     # RegistrationForm, UserProfileForm
│   ├── admin.py                     # Django Admin registrations & fieldsets
│   ├── urls.py                      # App-level URL patterns (tools, auth, API)
│   ├── apps.py                      # App configuration
│   │
│   ├── utils/                       # 🧠 AI & Utility Modules
│   │   ├── career_planner.py        # LangGraph agent + Tavily web search
│   │   ├── mental_health_analyzer.py# CatBoost ML + LLM expert review
│   │   ├── quiz_maker.py            # LLM quiz generation + explanation engine
│   │   ├── research_agent.py        # LangGraph (Search → Scrape → Summarize)
│   │   ├── resume_scanner.py        # RAG pipeline (FAISS + HuggingFace)
│   │   ├── roadmap_creator.py       # GitHub API + LLM synthesis
│   │   ├── notes_assistant.py       # LangGraph Map-Reduce multi-file pipeline
│   │   ├── news_portal.py           # Tavily news API integration (Pydantic models)
│   │   ├── pdf_generator.py         # Markdown → HTML → PDF with background overlay
│   │   ├── rate_limiter.py          # Role-based daily usage quota system
│   │   └── logger.py                # Token usage & response metadata CSV logger
│   │
│   ├── templates/                   # Django HTML Templates
│   │   ├── home.html                # Main dashboard with tool cards & limits
│   │   ├── login.html               # User login page
│   │   ├── register.html            # User registration page
│   │   ├── my_profile.html          # Editable user profile page
│   │   └── tools/                   # Individual tool templates
│   │       ├── career_planner.html
│   │       ├── mental_health_analyzer.html
│   │       ├── quiz_maker.html
│   │       ├── research_agent.html
│   │       ├── resume_scanner.html
│   │       ├── roadmap_creator.html
│   │       ├── notes_assistant.html
│   │       └── news_portal.html
│   │
│   └── templatetags/
│       └── custom_filters.py        # get_item filter for dict key access in templates
│
├── ml_models/                       # Pre-trained Machine Learning Models
│   ├── catboost_model.cbm           # CatBoost classifier v1
│   └── catboost_model_v4.cbm        # CatBoost classifier v4 (active)
│
├── static/                          # Static Assets
│   ├── css/
│   │   ├── styles.css               # Auth pages styling
│   │   └── main_styles.css          # Dashboard & tools styling
│   ├── images/                      # Logos, backgrounds, tool GIFs, PDF templates
│   └── videos/                      # Video assets
│
├── launcher.py                      # Desktop app launcher (PyWebView + Waitress)
├── manage.py                        # Django management script
├── requirements.txt                 # Python dependencies (~240 packages)
├── Procfile                         # Heroku/Railway deployment config
├── runtime.txt                      # Python runtime version (3.12.0)
├── .env                             # Environment variables (API keys)
└── .gitignore                       # Git exclusion rules
```

---

## 🛠 Technology Stack

### Backend & Framework

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.12 | Core programming language |
| **Django** | 5.2.4 | Web framework (MVT architecture) |
| **Gunicorn** | 25.1.0 | Production WSGI server |
| **Waitress** | 3.0.2 | Windows-compatible WSGI server (desktop mode) |
| **WhiteNoise** | 6.12.0 | Static file serving in production |

### AI / LLM Framework

| Technology | Version | Purpose |
|-----------|---------|---------|
| **LangChain** | 0.3.26 | LLM orchestration, prompt templates, output parsers, RAG chains |
| **LangGraph** | 0.5.3 | Stateful agentic workflows (state machines for multi-step AI pipelines) |
| **LangChain-Groq** | 0.3.6 | Groq LPU Cloud integration for ultra-fast LLM inference |
| **LangChain-HuggingFace** | 0.3.1 | HuggingFace embedding models for RAG |
| **LangChain-Community** | 0.3.27 | Tavily search tools, document loaders |

### Machine Learning

| Technology | Version | Purpose |
|-----------|---------|---------|
| **CatBoost** | 1.2.8 | Gradient boosting classifier for mental health prediction |
| **scikit-learn** | 1.7.2 | ML utilities |
| **FAISS (CPU)** | 1.11.0 | Vector similarity search for RAG-based resume analysis |
| **Sentence-Transformers** | 5.1.1 | `all-MiniLM-L6-v2` embedding model |
| **PyTorch** | 2.8.0 | Deep learning framework (transformers backend) |
| **Transformers** | 4.57.0 | HuggingFace model infrastructure |

### LLM Models Used (via Groq API)

| Model | Tool(s) | Use Case |
|-------|---------|----------|
| `openai/gpt-oss-120b` | Career Planner, Mental Health AI Review, Resume Scanner, Notes Assistant (Final) | High-quality generation (primary model) |
| `openai/gpt-oss-20b` | Quiz Maker, Notes Assistant (Chunks) | Faster generation for structured output |
| `llama-3.3-70b-versatile` | Quiz Explanations, Roadmap Creator | Balanced quality and speed |
| `llama-3.1-8b-instant` | Thought of the Day, Notes Assistant (Chunks) | Ultra-fast lightweight tasks |
| `meta-llama/llama-4-scout-17b-16e-instruct` | Notes Assistant (Chunks) | Round-robin multi-model processing |
| `moonshotai/kimi-k2-instruct` | Notes Assistant (Chunks) | Round-robin multi-model processing |

### Data & Databases

| Technology | Purpose |
|-----------|---------|
| **MySQL** | Primary development/production database |
| **SQLite** | Desktop mode local database |
| **dj-database-url** | Cloud database URL parsing (Railway/Heroku) |
| **Pandas** | Data manipulation & CSV logging |

### External APIs

| Service | Purpose |
|---------|---------|
| **Groq Cloud** | LLM inference (LPU-accelerated) |
| **Tavily** | Web search (Career Planner, Research Agent) & News API |
| **GitHub API** | Repository search for roadmap generation |
| **HuggingFace** | Embedding model downloads |

### PDF & Document Processing

| Technology | Purpose |
|-----------|---------|
| **xhtml2pdf (pisa)** | HTML → PDF conversion |
| **pypdf** | PDF reading, merging, and background overlay |
| **Markdown** | Markdown → HTML conversion |
| **python-docx** | DOCX file reading |
| **newspaper3k** | Web article scraping & parsing |

### Frontend

| Technology | Purpose |
|-----------|---------|
| **HTML5** | Template structure |
| **CSS3** | Custom styling (dark/light themes) |
| **JavaScript** | Client-side interactivity |
| **Django Templates** | Server-side rendering with template inheritance |

### Desktop Application

| Technology | Purpose |
|-----------|---------|
| **PyWebView** | Native desktop window wrapping the web app |
| **PyInstaller** | Packaging into standalone `.exe` |

---

## 🧠 AI Modules Deep Dive

### 1. Career Planner (`career_planner.py`)

**Architecture:** LangGraph StateGraph with web-augmented generation.

```
START → [generate_career_advise_node] → END
             │
             ├── Tavily Web Search (career topic)
             ├── Clean & truncate web content (3000 chars max)
             ├── LLM Prompt (web-enriched or fallback)
             └── Returns: Markdown career plan
```

- **Web Augmentation:** Uses Tavily to fetch the latest industry trends and integrates them into the LLM prompt for up-to-date career advice.
- **Graceful Fallback:** If web search fails, falls back to pure LLM generation.
- **Profile Auto-fill:** Pre-populates form fields from the user's stored profile data (career goals, education, skills, experience).

---

### 2. Mental Health Analyzer (`mental_health_analyzer.py`)

**Architecture:** Hybrid ML Prediction + LLM Expert Review.

```
User Input (12 features)
  → CatBoost Classifier (catboost_model_v4.cbm)
    → Prediction: High/Low Likelihood
    → Probability Score
  → LLM Expert Prompt (system: compassionate mental health expert)
    → Contextual AI Review with actionable advice
    → Medical disclaimer included
```

- **12 Input Features:** Age, Gender, Occupation, Country, Stress Level, Sleep Hours, Work Hours, Physical Activity, Social Media Usage, Diet Quality, Smoking Habit, Alcohol Consumption.
- **CatBoost Model:** Pre-trained classifier loaded once (singleton pattern) for efficient inference.
- **Categorical Feature Handling:** Explicit `category` dtype conversion to match training data format.

---

### 3. Research Agent (`research_agent.py`)

**Architecture:** Three-node LangGraph pipeline.

```
START → [search_node] → [scrape_node] → [summarize_node] → END
            │                  │                │
            │                  │                └── LLM: Synthesize into
            │                  │                    cohesive bullet points
            │                  │
            │                  └── newspaper3k: Download & parse articles
            │                      (truncated to 4000 chars each)
            │
            └── TavilySearchResults: Find 4 relevant URLs
```

- **Full Pipeline:** Searches → Scrapes actual article content → Synthesizes into a unified summary.
- **Error Resilience:** Each scrape failure is handled individually; the pipeline continues with available articles.

---

### 4. Notes Assistant (`notes_assistant.py`)

**Architecture:** LangGraph Map-Reduce with multi-model round-robin processing.

```
                    ┌── [process_file] (File 1) ──┐
START ──(fanout)──> ├── [process_file] (File 2) ──┼──> [generate_final_output] ──> END
                    └── [process_file] (File N) ──┘
```

- **Parallel File Processing:** Uses LangGraph's `Send` API for fan-out parallel processing of multiple uploaded files.
- **Token-Aware Chunking:** Splits large files into 3500-token chunks using `tiktoken` (cl100k_base encoding).
- **Multi-Model Round-Robin:** Distributes chunks across 6 different LLM models for load balancing and variety.
- **4 Output Modes:** Summary, Quick Revision Notes, Practice Q&A, or Custom Instructions.
- **Multi-Format Input:** Supports `.txt`, `.pdf`, and `.docx` file uploads (up to 5 files).

---

### 5. Resume Scanner (`resume_scanner.py`)

**Architecture:** Full RAG (Retrieval-Augmented Generation) pipeline.

```
Upload PDF → PyPDFLoader → RecursiveCharacterTextSplitter (1000/200)
  → HuggingFaceEmbeddings (all-MiniLM-L6-v2)
    → FAISS VectorStore → Retriever
      → RAG Chain: {context: retriever, edu_qual: input} | prompt | LLM
        → Resume analysis with scoring, strengths, job roles
```

- **Embedding Model:** `all-MiniLM-L6-v2` via HuggingFace for semantic document embeddings.
- **Vector Store:** FAISS (CPU) for fast similarity search on resume chunks.
- **File Validation:** The LLM first verifies whether the uploaded file is actually a resume.
- **Temporary Storage:** Files are saved temporarily, processed, then deleted immediately.

---

### 6. Quiz Maker (`quiz_maker.py`)

**Architecture:** Two-stage LLM pipeline with structured JSON output.

```
Stage 1: Generate Quiz
  → LLM (gpt-oss-20b) with JsonOutputParser
  → Returns: List of {question, options: {A,B,C,D}, answer}

Stage 2: Generate Explanations (on submit)
  → For each incorrect answer:
    → LLM (llama-3.3-70b) generates personalized explanation
  → Returns: Dict of {question: explanation}
```

- **Session-Based State Machine:** Manages quiz lifecycle (config → taking → results) via Django sessions.
- **Structured Output:** Uses LangChain's `JsonOutputParser` to ensure valid JSON responses from the LLM.
- **Adaptive Explanations:** Explanations are tailored to the user's selected difficulty level.

---

### 7. Roadmap Creator (`roadmap_creator.py`)

**Architecture:** GitHub API search + LLM synthesis.

```
Domain Input → GitHub API (search repositories, sort by stars, top 5)
  → Format repo data (name, description, URL)
    → LLM: Generate skill-based learning roadmap
      → Key modules, topics, repo references, certifications
```

- **Authenticated GitHub API:** Uses a personal access token for higher rate limits.
- **Star-Sorted Results:** Fetches the top 5 most-starred repositories in the given domain.

---

### 8. News Portal (`news_portal.py`)

**Architecture:** Tavily News API with Pydantic data models.

```
NewsRequest (category, time_filter, limit)
  → Tavily Search API (topic: "news", days: 1/7/30)
    → Map to Pydantic models (NewsItem, NewsResponse)
      → Generate Markdown for PDF export
```

- **7 Categories:** Technology, Business, Science, Health, Sports, Politics, General.
- **3 Time Filters:** Daily (1 day), Weekly (7 days), Monthly (30 days).
- **Structured Data:** Uses Pydantic `BaseModel` for type-safe request/response handling.

---

## 🗄 Database Design

### Models

```
┌──────────────────────────────────────────────────────────────┐
│                        UserProfile                           │
├──────────────────────────────────────────────────────────────┤
│ user (OneToOne → User)                                       │
│ education_level (choices: High School → PhD)                 │
│ degree_name                                                  │
│ current_status (choices: Student/Professional/Job Seeker/    │
│                 Freelancer)                                   │
│ primary_domain                                               │
│ years_of_experience                                          │
│ skills (TextField, comma-separated)                          │
│ career_goals (TextField)                                     │
│ github_profile, linkedin_profile, portfolio_website (URLs)   │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                      ModulesControl                          │
├──────────────────────────────────────────────────────────────┤
│ name_of_module (choices: auto-discovered from utils/ folder) │
│ daily_limit (PositiveIntegerField)                           │
│ role (ForeignKey → Group)                                    │
│ unique_together: (name_of_module, role)                      │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                     UserModuleUsage                          │
├──────────────────────────────────────────────────────────────┤
│ user (ForeignKey → User)                                     │
│ module_name (CharField)                                      │
│ date (DateField, default: today)                             │
│ usage_count (PositiveIntegerField)                           │
│ unique_together: (user, module_name, date)                   │
└──────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

- **Dynamic Module Discovery:** `ModulesControl` auto-discovers available tools by scanning Python files in `main/utils/`, excluding infrastructure files (`__init__.py`, `logger.py`, `pdf_generator.py`).
- **Auto Profile Creation:** Django signals (`post_save`) automatically create a `UserProfile` when a new `User` is registered.
- **Multi-Group Rate Limiting:** Users belonging to multiple groups receive the highest daily limit available across all their groups.

---

## 🔐 Authentication & Authorization

### Authentication Flow

```
Register (username, full name, password with confirmation)
  → Login (username + password via Django's authenticate())
    → Session-based authentication
      → All tool views check request.user.is_authenticated
        → Logout clears session
```

### Authorization (Role-Based Access Control)

| Component | Mechanism |
|-----------|-----------|
| **User Groups** | Django's built-in `Group` model (e.g., `External Users`, `Premium Users`) |
| **Auto-Assignment** | Users without any group are auto-assigned to `External Users` |
| **Rate Limits** | `ModulesControl` entries define daily limits per module per group |
| **Enforcement** | `check_and_get_limit()` is called at the start of every tool view |
| **Usage Tracking** | `UserModuleUsage` records per-user, per-module, per-day counts |

### Admin Panel

The Django Admin interface provides:
- **ModulesControl Admin:** Set daily limits for any tool for any user group
- **UserModuleUsage Admin:** Monitor per-user tool usage with date and count filters
- **UserProfile Admin:** View and edit user profiles with logically grouped fieldsets

---

## 🖥 Deployment Modes

### 1. Web Mode (Default)

```bash
# Development
python manage.py runserver

# Production (Gunicorn)
gunicorn jeevanyaan.wsgi:application
```

Uses MySQL database and is deployable to platforms like Railway, Heroku, or any WSGI-compatible host.

### 2. Desktop Mode

```bash
python launcher.py
```

- Sets `APP_MODE=desktop` environment variable
- Uses SQLite stored in `~/JeevanYaanData/desktop_db.sqlite3`
- Launches a **Waitress** WSGI server on `127.0.0.1:8000`
- Opens a native **PyWebView** desktop window (1400×900, resizable)
- Packagable as a standalone `.exe` using **PyInstaller** (supports `sys.frozen` / `sys._MEIPASS`)

### 3. Cloud Database Mode

When the `DATABASE_URL` environment variable is set, the app automatically uses `dj-database-url` to parse and connect to a cloud-hosted database (PostgreSQL, MySQL, etc.).

### Database Selection Logic

```python
if APP_MODE == "desktop":
    → SQLite (~/JeevanYaanData/desktop_db.sqlite3)
elif DATABASE_URL is set:
    → Cloud DB (parsed via dj-database-url)
else:
    → Local MySQL (jeevanyaan_db)
```

---

## 🔌 API & External Services

### Internal API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/get-thought/` | GET | Returns an AI-generated thought of the day (cached in session) |

### External Services Required

| Service | API Key Env Var | Required By |
|---------|----------------|-------------|
| **Groq** | `GROQ_API_KEY` | All AI tools (LLM inference) |
| **Tavily** | `TAVILY_API_KEY` | Career Planner, Research Agent, News Portal |
| **GitHub** | `GITHUB_TOKEN` | Roadmap Creator |
| **HuggingFace** | `HF_TOKEN` | Resume Scanner (embeddings) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- MySQL Server (for web mode) or SQLite (for desktop mode)
- API keys for Groq, Tavily, GitHub, and HuggingFace

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/SohamMistry01/JeevanYaan.git
cd JeevanYaan/django_app/jeevanyaan

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
# Create a .env file with the required API keys (see below)

# 5. Run database migrations
python manage.py migrate

# 6. Create a superuser (for admin access)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

### Launch as Desktop App

```bash
python launcher.py
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root with the following keys:

```env
# LLM Inference
GROQ_API_KEY=your_groq_api_key

# Web Search & News
TAVILY_API_KEY=your_tavily_api_key

# GitHub Repository Search
GITHUB_TOKEN=your_github_personal_access_token

# HuggingFace Embeddings
HF_TOKEN=your_huggingface_token

# Database (Cloud deployment only)
DATABASE_URL=your_database_url

# App Mode (set by launcher.py for desktop mode)
APP_MODE=web
```

---

## 🔮 Future Scope

- **🤖 Conversational AI Chat Interface** — Add a real-time chatbot companion using WebSocket and streaming LLM responses
- **📈 Analytics Dashboard** — Visualize tool usage patterns, token consumption trends, and user engagement metrics from the CSV logs
- **🌐 Multi-Language Support** — Extend AI tools to support regional languages for wider accessibility
- **🔗 LLM Provider Abstraction** — Add support for multiple LLM providers (OpenAI, Anthropic, local models) with a unified interface
- **📱 Progressive Web App (PWA)** — Enable offline-capable mobile experience with service workers
- **🧪 A/B Testing Framework** — Compare different LLM models and prompts for quality benchmarking across tools
- **📊 Built-in Consistency Scoring** — Surface the existing consistency metrics in the UI for transparency on AI output quality
- **🔄 Real-Time Collaboration** — Allow mentors and mentees to share career plans and review progress together
- **🏥 Mental Health Journaling** — Add a daily journaling feature that tracks wellness trends over time with longitudinal ML analysis
- **🎓 Certification Tracker** — Integrate with certification platforms to track and verify learning progress recommended by the Career Planner

---

## 📄 License

This project is developed for academic and personal use. All rights reserved by the author.

---

<div align="center">

**Built with ❤️ using Django, LangChain, LangGraph & CatBoost**

*JeevanYaan — Your AI companion for a better career and a healthier life.*

</div>
]]>
