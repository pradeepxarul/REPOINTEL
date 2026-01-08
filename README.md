# 🚀 GitHub User Data Analyzer - Production API

> **AI-Powered GitHub Profile Analysis & Candidate Assessment System**

A high-performance FastAPI service that extracts comprehensive developer data from GitHub profiles and generates AI-powered candidate reports for hiring decisions.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ Features

### 📊 Complete GitHub Analysis
- **User Profiles** - Full developer information
- **Repository Data** - All public repos with detailed metrics
- **Language Statistics** - Percentage breakdown of tech stack
- **README Extraction** - Main README content
- **📄 ALL Markdown Files** - Complete `.md` file extraction (CONTRIBUTING, docs, etc.)
- **Smart Caching** - 24-hour TTL for instant repeat queries

### 🤖 AI-Powered Candidate Reports
- **GROQ Llama 3.3 70B** - Primary (Fast & Cost-effective)
- **OpenAI GPT-4o** - Alternative
- **Google Gemini** - Alternative
- **Comprehensive Analysis** - Skills, projects, code quality, hiring recommendations
- **Domain Detection** - Web, Mobile, ML, DevOps, etc.
- **Framework Identification** - React, FastAPI, Django, etc.
- **Quantitative Scores** - Technical assessment, code quality, hiring score (/10)

### 💾 Data Persistence
- **JSON Storage** - Auto-save all analyzed profiles to `db/`
- **Fast Retrieval** - Use stored data for instant reports
- **Human-Readable** - Easy to inspect and backup

---

## 🏗️ Architecture

```
src/
├── core/           # Configuration & exceptions
├── models/         # Pydantic schemas
├── services/       # Business logic (GitHub, LLM, Storage, Cache)
├── api/            # FastAPI routes
├── utils/          # Validators, logging
└── main.py         # Application entry
```

**Professional layered architecture** with clean separation of concerns.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- GitHub App credentials
- GROQ API key (or OpenAI/Gemini)

### 2. Installation

```bash
# Clone repository
git clone <your-repo-url>
cd Git-user_data-analyser

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Copy `.env.example` to `.env` and configure:

```env
# GitHub App (Required)
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----..."
GITHUB_INSTALLATION_ID=your_installation_id

# LLM for AI Reports (Required for reports)
GROQ_API_KEY=gsk_your_groq_key_here
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=2048
```

### 4. Run Server

```bash
cd src
python main.py
```

Server starts at `http://localhost:8000`

📖 **Swagger Docs**: `http://localhost:8000/docs`

---

## 📡 API Endpoints

### POST /api/v1/analyze
**Analyze GitHub Profile + Extract All Data**

**Request:**
```json
{
  "github_input": "torvalds"
}
```

**Response:**
```json
{
  "user": {
    "login": "torvalds",
    "name": "Linus Torvalds",
    "bio": "...",
    // ... full profile
  },
  "repositories": [
    {
      "name": "linux",
      "full_name": "torvalds/linux",
      
      // ✅ Popularity Metrics
      "stargazers_count": 250,
      "forks_count": 45,
      "watchers_count": 180,
      "open_issues_count": 12,
      
      // ✅ Activity metrics
      "pushed_at": "2025-12-30T13:31:35Z",
      "last_commit_date": "2025-12-30T13:31:35Z",
      "days_since_last_commit": 1,
      
      // ✅ Repository Features
      "language": "C",
      "topics": ["kernel", "os"],
      "has_wiki": true,
      "has_projects": false,
      
      // ✅ Language Breakdown
      "languages": {
        "raw_bytes": {"C": 98300, "Assembly": 1200},
        "percentages": {"C": 98.3, "Assembly": 1.7}
      },
      
      "readme": {
        "content": "... full README ...",
        "has_readme": true,
        "length_chars": 5020
      },
      
      // ✅ ALL Markdown Files
      "markdown_files": [
        {
          "filename": "CONTRIBUTING.md",
          "path": "docs/CONTRIBUTING.md",
          "content": "... COMPLETE CONTENT ...",
          "length_chars": 2500
        }
      ]
    }
  ]
}
```

**Auto-saves to:** `db/{username}.json`

---

### POST /api/v1/reports/generate
**Generate AI-Powered Candidate Report**

**Request:**
```json
{
  "username": "torvalds",
  "report_type": "full",
  "use_stored": true
}
```

**Response:**
```json
{
  "report": {
    "candidate": {
      "name": "Linus Torvalds",
      "username": "torvalds"
    },
    "executive_summary": "...",
    "technical_assessment": {
      "overall_score": 9.5,
      "primary_languages": ["C", "Assembly"],
      "frameworks_detected": ["Linux Kernel"],
      "specializations": ["Systems Programming", "OS Development"]
    },
    "code_quality": {
      "overall_score": 9.8,
      "documentation_score": 9.5
    },
    "hiring_recommendation": {
      "overall_score": 9.5,
      "suitable_roles": ["Principal Engineer", "CTO"],
      "seniority_fit": "Staff/Principal",
      "recommendation_summary": "..."
    }
  }
}
```

---

## 🤖 Switching LLM Models

### Change Provider

**Option 1: GROQ (Recommended)**
```env
GROQ_API_KEY=gsk_your_key
LLM_MODEL=llama-3.3-70b-versatile
```

**Option 2: OpenAI**
```env
GROQ_API_KEY=  # Leave empty
OPENAI_API_KEY=sk-proj-your_key
LLM_MODEL=gpt-4o
```

**Option 3: Google Gemini**
```env
GROQ_API_KEY=  # Leave empty
GOOGLE_API_KEY=your_gemini_key
LLM_MODEL=gemini-pro
```

### Change Model Parameters

```env
# Model name
LLM_MODEL=llama-3.3-70b-versatile

# Temperature (creativity: 0.0 = focused, 1.0 = creative)
LLM_TEMPERATURE=0.1

# Max tokens in response
LLM_MAX_TOKENS=2048
```

### Available GROQ Models
- `llama-3.3-70b-versatile` (Recommended - Best balance)
- `llama-3.1-8b-instant` (Fastest)
- `mixtral-8x7b-32768` (Large context)

**Just update `.env` and restart!** No code changes needed.

---

## 📁 Data Storage

### JSON Storage
All analyzed profiles auto-save to `db/` folder:

```
db/
├── torvalds.json
├── gvanrossum.json
└── ...
```

Each file contains:
- Complete user profile
- All repositories
- **ALL markdown files** with full content
- Metadata (timestamp, API calls)

---

## 🎯 Use Cases

### For Recruiters
- **Skill Assessment** - Language proficiency, framework expertise
- **Code Quality** - Documentation, best practices
- **Activity Tracking** - Recent commits, consistency
- **Hiring Scores** - AI-powered recommendations (/10)

### For  AI Matching
- **Complete Data Export** - All repos, languages, READMEs, markdown
- **JSON Format** - Easy integration with AI systems
- **Structured Reports** - Parse scores, skills, recommendations

### For Developers
- **Portfolio Analysis** - See how your profile looks to recruiters
- **Skill Mapping** - Identify technology gaps
- **Project Insights** - Understand your strengths

---

## ⚙️ Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_APP_ID` | ✅ Yes | - | GitHub App ID |
| `GITHUB_PRIVATE_KEY` | ✅ Yes | - | GitHub App private key |
| `GITHUB_INSTALLATION_ID` | ✅ Yes | - | Installation ID |
| `GROQ_API_KEY` | For AI | - | GROQ API key (primary) |
| `OPENAI_API_KEY` | For AI | - | OpenAI API key |
| `GOOGLE_API_KEY` | For AI | - | Gemini API key |
| `LLM_MODEL` | No | llama-3.3-70b-versatile | Model name |
| `LLM_TEMPERATURE` | No | 0.1 | Response creativity |
| `LLM_MAX_TOKENS` | No | 2048 | Max response length |
| `PORT` | No | 8000 | Server port |
| `MAX_REPOS_PER_USER` | No | 15 | Repos to analyze |
| `CACHE_TTL_SECONDS` | No | 86400 | Cache duration |

---

## 📊 Performance

- **Analysis Speed**: ~1.5-2 seconds (uncached)
- **Cached Response**: <20ms
- **Capacity**: 112K users/month per server
- **AI Report**: 2-5 seconds (GROQ)
- **Rate Limit**: 5,000 req/hour (GitHub App)

---

## 🛡️ Production Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
ENV PORT=8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### PM2 (Node Process Manager)

```bash
# Install PM2
npm install -g pm2

# Start server
pm2 start "python src/main.py" --name github-analyzer

# Auto-restart on reboot
pm2 startup
pm2 save
```

### Environment Variables in Production
- Use secrets management (AWS Secrets Manager, Azure Key Vault)
- Never commit `.env` to git
- Rotate API keys regularly

---

## 🔧 Development

### Project Structure
```
Git-user_data-analyser/
├── src/
│   ├── core/              # Config, exceptions
│   ├── models/            # Pydantic schemas
│   ├── services/          # Business logic
│   ├── api/               # Routes
│   ├── utils/             # Helpers
│   └── main.py            # Entry point
├── db/                    # JSON storage
├── cache/                 # API cache
├── requirements.txt       # Dependencies
├── .env                   # Config (gitignored)
├── .env.example           # Config template
└── README.md              # This file
```

### Adding New Features
1. **Models**: Add to `models/schemas.py`
2. **Services**: Create in `services/`
3. **Routes**: Add to `api/routes.py`
4. **Config**: Update `core/config.py`

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🆘 Support

### Common Issues

**Q: "Field required" error on startup**
- A: Check `.env` file exists and has all required fields

**Q: AI reports return template mode**
- A: Add `GROQ_API_KEY` (or OPENAI/GOOGLE key) to `.env`

**Q: No markdown files in response**
- A: Repos might not have additional `.md` files (only README)

**Q: How to change LLM provider?**
- A: Update `GROQ_API_KEY`, `OPENAI_API_KEY`, or `GOOGLE_API_KEY` in `.env`

### Docs
- **API Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🎉 Credits

Built with:
- [Fast API](https://fastapi.tiangolo.com/) - Modern Python web framework
- [GROQ](https://groq.com/) - Fast AI inference
- [Pydantic](https://pydantic.dev/) - Data validation
- [GitHub API](https://docs.github.com/en/rest) - Data source

---

**Made with ❤️ for modern hiring teams**
#   R e p o I n t e l -  
 