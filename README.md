# Career Assistant SaaS Platform

An AI-powered platform that helps students and job seekers find relevant jobs, optimize their resumes, and simplify the application process using advanced AI capabilities.

## Project Overview

The Career Assistant platform streamlines the entire job application workflow:
- **Resume Management**: Upload and parse resumes automatically with AI
- **Job Matching**: Find relevant jobs with AI-powered semantic matching
- **Resume Optimization**: Generate ATS-friendly, tailored resumes for specific jobs
- **Cover Letter Generation**: Create personalized cover letters with AI
- **Application Tracking**: Track all applications and their statuses
- **Analytics**: Analyze job search patterns and success rates

## Tech Stack

### Frontend
- **Framework**: Next.js 14+ with React 18+
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Shadcn/ui
- **State Management**: React Context API / Zustand
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Vector DB**: ChromaDB for embeddings
- **Async**: Uvicorn + Async workers
- **Deployment**: Railway or Render

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **File Storage**: Supabase Storage
- **LLM Service**: OpenAI API
- **Job APIs**: LinkedIn Jobs, Indeed, GitHub Jobs
- **Email**: SendGrid
- **Error Tracking**: Sentry
- **CI/CD**: GitHub Actions

## Project Structure

```
career-ai-platform/
├── frontend/                    # Next.js frontend application
│   ├── src/
│   │   ├── app/                 # Next.js app router
│   │   ├── components/          # React components
│   │   ├── lib/                 # Utility functions & API client
│   │   └── styles/              # Global styles & tailwind config
│   ├── public/                  # Static assets
│   ├── __tests__/               # Test files
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   └── Dockerfile
│
├── backend/                     # FastAPI backend application
│   ├── app/
│   │   ├── models/              # SQLAlchemy models
│   │   ├── routes/              # API route handlers
│   │   ├── services/            # Business logic services
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── utils/               # Utility functions
│   │   ├── __init__.py
│   │   └── main.py              # FastAPI app initialization
│   ├── tests/                   # Test files
│   ├── migrations/              # Alembic database migrations
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment variables template
│   ├── Dockerfile
│   ├── docker-compose.yml       # Docker Compose configuration
│   ├── pytest.ini
│   └── alembic.ini
│
├── docs/                        # Project documentation
│   ├── API.md                   # API documentation
│   ├── ARCHITECTURE.md          # System architecture guide
│   ├── DATABASE.md              # Database schema guide
│   ├── SETUP.md                 # Setup instructions
│   └── DEPLOYMENT.md            # Deployment guide
│
├── .github/
│   └── workflows/               # GitHub Actions CI/CD
│       ├── frontend-ci.yml
│       ├── backend-ci.yml
│       └── deploy.yml
│
├── .env.example                 # Root environment variables template
├── docker-compose.yml           # Root Docker Compose for full stack
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
└── LICENSE                      # MIT License

```

## Prerequisites

- **Node.js**: 18+ (for frontend)
- **Python**: 3.9+ (for backend)
- **PostgreSQL**: 14+ (for database)
- **Docker & Docker Compose**: For containerized development
- **Git**: For version control

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd career-ai-platform

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend python -m alembic upgrade head

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
alembic upgrade head

# Run development server
uvicorn app.main:app --reload
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Run development server
npm run dev
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/career_ai
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-...
LINKEDIN_API_KEY=...
INDEED_API_KEY=...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=...
JWT_SECRET=your-secret-key
ENVIRONMENT=development
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Career Assistant
```

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### 3. Frontend Development
```bash
cd frontend
npm run dev
```

### 4. Running Tests

**Backend:**
```bash
cd backend
pytest
pytest --cov=app  # With coverage
```

**Frontend:**
```bash
cd frontend
npm test
npm run test:watch
```

### 5. Linting & Formatting

**Backend:**
```bash
cd backend
black app/  # Format code
flake8 app/  # Lint code
```

**Frontend:**
```bash
cd frontend
npm run lint
npm run format
```

### 6. Commit & Push
```bash
git add .
git commit -m "feat: description of changes"
git push origin feature/your-feature-name
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

For detailed API documentation, see [docs/API.md](docs/API.md).

## Database Schema

For database schema documentation, see [docs/DATABASE.md](docs/DATABASE.md).

## Architecture

For system architecture details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Deployment

For deployment instructions, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Testing

- Backend: 80%+ code coverage target with pytest
- Frontend: Unit and integration tests with Jest/Vitest
- E2E tests with Playwright (future phase)

## CI/CD Pipeline

GitHub Actions workflow runs:
- Linting (ESLint, Black, Flake8)
- Unit tests
- Integration tests
- Security scanning
- Build and deploy to staging on PR merge
- Production deployment on release

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Ensure linting passes
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and feature requests, please use GitHub Issues.

## Timeline & Roadmap

### MVP (Phase 1 - Current)
- User authentication
- Resume upload and parsing
- Profile management
- Job search integration
- AI-powered job matching
- Resume optimization
- Cover letter generation
- Application tracking
- Basic analytics

### Phase 2 (Future)
- Browser automation for form filling
- Interview preparation
- Salary negotiation guidance

### Phase 3 (Future)
- AI-powered career recommendations
- Skill development paths
- Recruiter marketplace

### Phase 4 (Future)
- Corporate team features
- Multi-language support
- International job markets

## References

- [Requirements Document](../.kiro/specs/career-assistant-saas/requirements.md)
- [Design Document](../.kiro/specs/career-assistant-saas/design.md)
- [Tasks List](../.kiro/specs/career-assistant-saas/tasks.md)

