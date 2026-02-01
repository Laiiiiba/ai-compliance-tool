# AI Compliance & Risk Self-Assessment Tool

A production-grade web application that helps startups and small teams assess AI regulatory risk and compliance readiness, with a primary focus on the EU AI Act.

## 🎯 Project Overview

This tool provides deterministic, rule-based compliance assessments without AI-based decision making. It serves as a **decision-support tool**, not legal advice.

### Key Features

- **Deterministic Risk Classification**: 100% rule-based, fully explainable
- **EU AI Act Focus**: Tailored risk categories and compliance requirements
- **Audit-Ready**: Complete decision trails for all assessments
- **Production-Grade**: Built with enterprise patterns and security in mind

## 🛠️ Tech Stack

**Backend:**
- Python 3.11
- FastAPI
- SQLAlchemy 2.0 (typed ORM)
- PostgreSQL
- Alembic (migrations)

**Infrastructure:**
- Docker & docker-compose
- Uvicorn (ASGI server)

**Frontend (MVP):**
- Jinja2 server-rendered HTML

## 📋 Prerequisites

- Python 3.11+
- Docker Desktop
- Git
- PostgreSQL (via Docker)

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ai-compliance-tool
```

### 2. Set Up Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Start Services
```bash
docker-compose up -d
```

### 6. Run Migrations
```bash
alembic upgrade head
```

### 7. Start Application
```bash
uvicorn app.main:app --reload
```

Visit: `http://localhost:8000`

## 📁 Project Structure
```
ai-compliance-tool/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Configuration & database
│   ├── db/models/        # SQLAlchemy models
│   ├── services/         # Business logic (risk engine)
│   └── schemas/          # Pydantic schemas
├── alembic/              # Database migrations
├── tests/                # Test suite
└── docs/                 # Documentation
```

## 🏗️ Architecture Principles

- **No AI-Based Decisions**: All risk classification is deterministic
- **Single Source of Truth**: One SQLAlchemy Base, one metadata registry
- **Explainability First**: Every decision has a clear reasoning trail
- **Security by Design**: Data minimization, secure defaults

## 🧪 Testing
```bash
pytest
```

## 📖 Documentation

See `/docs` for:
- Architecture decisions
- Risk classification rules
- API documentation
- Deployment guide

## ⚠️ Important Disclaimers

This tool is a **decision-support system** and does NOT provide:
- Legal advice
- Automated compliance certification
- Guarantees of regulatory compliance

All AI-generated content (explanations, drafts) is clearly labeled and requires human review.

## 👥 Contributing

This is a learning/portfolio project. See `CONTRIBUTING.md` for guidelines.

## 📄 License

MIT License - See LICENSE file for details

## 🙋 Author

Built as a production-grade learning project to demonstrate:
- Backend engineering best practices
- System architecture design
- Regulatory technology (RegTech) understanding
- Production-ready code standards

---

**Status**: 🚧 In Active Development