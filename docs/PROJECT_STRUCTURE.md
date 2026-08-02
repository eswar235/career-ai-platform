# Project Structure Documentation

Complete breakdown of the Career Assistant SaaS platform project structure.

## Root Level

```
career-ai-platform/
├── frontend/                 # Next.js frontend application
├── backend/                  # FastAPI backend application
├── docs/                     # Project documentation
├── .github/                  # GitHub workflows (CI/CD)
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── docker-compose.yml        # Multi-container Docker setup
├── Makefile                  # Development commands
└── README.md                 # Project overview
```

## Backend Structure

```
backend/
├── app/                      # Main application code
│   ├── core/                 # Core application configuration
│   │   ├── __init__.py
│   │   ├── config.py         # Settings management
│   │   └── logging.py        # Logging configuration
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py           # Base model class
│   │   ├── user.py           # User model (will be created)
│   │   ├── resume.py         # Resume model (will be created)
│   │   └── ...
│   ├── routes/               # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication routes (will be created)
│   │   ├── users.py          # User management routes (will be created)
│   │   ├── resumes.py        # Resume routes (will be created)
│   │   └── ...
│   ├── services/             # Business logic services
│   │   ├── __init__.py
│   │   ├── auth_service.py   # Authentication logic (will be created)
│   │   ├── user_service.py   # User management (will be created)
│   │   ├── resume_service.py # Resume parsing & handling (will be created)
│   │   └── ...
│   ├── schemas/              # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py           # User schemas (will be created)
│   │   ├── resume.py         # Resume schemas (will be created)
│   │   └── ...
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   ├── validation.py     # Validation utilities
│   │   ├── parsing.py        # Parsing utilities
│   │   └── formatting.py     # Formatting utilities
│   ├── main.py               # FastAPI app initialization
│   └── __init__.py
├── tests/                    # Test files
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures (will be created)
│   ├── test_models/          # Model tests (will be created)
│   ├── test_routes/          # Route tests (will be created)
│   ├── test_services/        # Service tests (will be created)
│   └── test_utils/           # Utility tests (will be created)
├── migrations/               # Alembic database migrations
│   ├── versions/             # Migration files
│   ├── env.py                # Alembic environment config
│   ├── script.py.mako        # Alembic script template
│   └── init.sql              # Database initialization script
├── scripts/                  # Utility scripts (to be created)
│   ├── seed_data.py          # Load sample data
│   ├── create_admin.py       # Create admin user
│   └── cleanup.py            # Data cleanup
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── pytest.ini                # Pytest configuration
├── alembic.ini               # Alembic configuration
├── Dockerfile                # Docker image for backend
└── .dockerignore             # Files to ignore in Docker
```

### Backend Key Files

#### `app/main.py`
- FastAPI application initialization
- Middleware configuration (CORS, trusted hosts)
- Health check endpoints
- Error handlers
- Root route documentation

#### `app/core/config.py`
- Environment variable management
- Settings validation
- Default values
- Database and service configuration

#### `app/core/logging.py`
- Logging configuration
- JSON formatter for structured logging
- File and console handlers
- Third-party logger configuration

#### `requirements.txt`
- FastAPI and dependencies
- SQLAlchemy ORM
- Database drivers
- Authentication libraries
- External API clients
- Testing and development tools

## Frontend Structure

```
frontend/
├── src/                      # Source code
│   ├── app/                  # Next.js app router (14+)
│   │   ├── layout.tsx        # Root layout component
│   │   ├── page.tsx          # Home page
│   │   ├── (auth)/           # Auth routes group (layout)
│   │   │   ├── layout.tsx
│   │   │   ├── login/page.tsx       # Login page (will be created)
│   │   │   └── register/page.tsx    # Registration page (will be created)
│   │   ├── (app)/            # App routes group (protected)
│   │   │   ├── layout.tsx
│   │   │   ├── dashboard/page.tsx   # Dashboard (will be created)
│   │   │   ├── resume/page.tsx      # Resume management (will be created)
│   │   │   ├── jobs/page.tsx        # Job search (will be created)
│   │   │   └── applications/page.tsx # Applications tracker (will be created)
│   │   └── api/              # API routes (optional)
│   │       └── ...
│   ├── components/           # Reusable React components
│   │   ├── __tests__/        # Component tests
│   │   ├── common/           # Common components
│   │   │   ├── Header.tsx
│   │   │   ├── Navigation.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Button.tsx
│   │   ├── forms/            # Form components (will be created)
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── ...
│   │   ├── cards/            # Card components (will be created)
│   │   │   ├── JobCard.tsx
│   │   │   ├── ResumeCard.tsx
│   │   │   └── ...
│   │   └── modals/           # Modal components (will be created)
│   ├── lib/                  # Utility functions & hooks
│   │   ├── api.ts            # API client / fetch wrapper
│   │   ├── utils.ts          # Utility functions
│   │   ├── hooks/            # Custom React hooks
│   │   │   ├── useAuth.ts    # Authentication hook
│   │   │   ├── useFetch.ts   # Data fetching hook
│   │   │   └── ...
│   │   └── store/            # State management (Zustand)
│   │       ├── authStore.ts  # Auth state
│   │       ├── userStore.ts  # User state
│   │       └── ...
│   └── styles/               # Styles
│       ├── globals.css       # Global styles
│       ├── variables.css     # CSS variables
│       └── themes.css        # Theme styles
├── public/                   # Static assets
│   ├── images/
│   ├── icons/
│   └── fonts/
├── __tests__/                # Test files
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # E2E tests (Playwright)
├── .next/                    # Next.js build output (gitignored)
├── node_modules/             # Dependencies (gitignored)
├── package.json              # Dependencies and scripts
├── tsconfig.json             # TypeScript configuration
├── next.config.js            # Next.js configuration
├── tailwind.config.ts        # Tailwind CSS configuration
├── postcss.config.js         # PostCSS configuration
├── .eslintrc.json            # ESLint configuration
├── .prettierrc.json          # Prettier configuration
├── .env.example              # Environment variables template
├── Dockerfile                # Docker image for frontend
├── jest.config.js            # Jest testing configuration
└── .dockerignore             # Files to ignore in Docker
```

### Frontend Key Files

#### `src/app/layout.tsx`
- Root layout for all pages
- Global providers (auth, theme)
- Metadata configuration
- HTML/body setup

#### `src/app/page.tsx`
- Landing/home page
- Onboarding flows
- Feature showcase

#### `src/lib/api.ts`
- Axios/fetch configuration
- API base URL
- Request/response interceptors
- Error handling

#### `src/store/authStore.ts` (Zustand)
- User authentication state
- Token management
- Login/logout actions

#### `package.json`
- Next.js and React
- TypeScript
- Tailwind CSS and utilities
- Testing libraries (Jest, React Testing Library)
- Linting and formatting tools

## GitHub Actions Configuration

```
.github/workflows/
├── backend-ci.yml            # Backend CI/CD pipeline
├── frontend-ci.yml           # Frontend CI/CD pipeline
└── deploy.yml                # Deployment pipeline (will be created)
```

### Workflow Details

#### `backend-ci.yml`
- Python version matrix
- Dependency caching
- Linting (Black, Flake8)
- Type checking (Mypy)
- Unit & integration tests
- Coverage reporting

#### `frontend-ci.yml`
- Node.js version matrix
- Dependency caching
- ESLint and Prettier checks
- Type checking (TypeScript)
- Build verification
- Test coverage

## Documentation

```
docs/
├── SETUP.md                  # Setup instructions
├── PROJECT_STRUCTURE.md      # This file
├── ARCHITECTURE.md           # System architecture (will be created)
├── DATABASE.md               # Database schema guide (will be created)
├── API.md                    # API documentation (will be created)
├── DEPLOYMENT.md             # Deployment guide (will be created)
├── CONTRIBUTING.md           # Contributing guidelines (will be created)
└── TROUBLESHOOTING.md        # Troubleshooting guide (will be created)
```

## Configuration Files

### Root Level
- `.env.example` - Environment variables template
- `.gitignore` - Git ignore rules
- `docker-compose.yml` - Multi-container setup
- `Makefile` - Development commands

### Backend
- `.env.example` - Backend-specific env vars
- `requirements.txt` - Python dependencies
- `pytest.ini` - Pytest configuration
- `alembic.ini` - Database migrations config
- `Dockerfile` - Docker image build

### Frontend
- `.env.example` - Frontend-specific env vars
- `package.json` - Node dependencies
- `tsconfig.json` - TypeScript configuration
- `next.config.js` - Next.js configuration
- `tailwind.config.ts` - Tailwind CSS configuration
- `.eslintrc.json` - ESLint configuration
- `.prettierrc.json` - Prettier configuration
- `Dockerfile` - Docker image build

## File Naming Conventions

### Backend
- Models: `snake_case.py` (e.g., `user.py`, `resume.py`)
- Routes: `snake_case.py` (e.g., `auth.py`, `users.py`)
- Services: `snake_case_service.py` (e.g., `auth_service.py`)
- Schemas: `snake_case.py` (e.g., `user.py`, `resume.py`)
- Tests: `test_*.py` (e.g., `test_models.py`, `test_auth.py`)
- Classes: `PascalCase` (e.g., `User`, `Resume`)

### Frontend
- Components: `PascalCase.tsx` (e.g., `Button.tsx`, `LoginForm.tsx`)
- Hooks: `usePascalCase.ts` (e.g., `useAuth.ts`, `useFetch.ts`)
- Utilities: `camelCase.ts` (e.g., `formatting.ts`, `validation.ts`)
- Types: `*.ts` or `*.d.ts` (e.g., `types.ts`)
- Tests: `*.test.tsx` or `*.spec.tsx`
- Stores: `*Store.ts` (e.g., `authStore.ts`, `userStore.ts`)

## Module Organization

### Backend Models Organization
```
models/
├── __init__.py
├── base.py                   # Base model with common fields
├── user.py                   # User & authentication models
├── resume.py                 # Resume & parsed data models
├── job.py                    # Job & matching models
├── application.py            # Application & history models
└── alert.py                  # Job alert & notification models
```

### Frontend Components Organization
```
components/
├── common/                   # Reusable across app
│   ├── Header.tsx
│   ├── Navigation.tsx
│   └── Footer.tsx
├── auth/                     # Authentication components
│   ├── LoginForm.tsx
│   └── RegisterForm.tsx
├── resume/                   # Resume related
│   ├── ResumeUpload.tsx
│   └── ResumeViewer.tsx
├── jobs/                     # Job search related
│   ├── JobSearch.tsx
│   └── JobCard.tsx
├── application/              # Application tracking
│   ├── ApplicationList.tsx
│   └── ApplicationDetail.tsx
└── layout/                   # Layout components
    ├── MainLayout.tsx
    └── AuthLayout.tsx
```

## Data Flow

### User Registration Flow (Left to Right)
1. **Frontend**: User submits registration form
2. **API**: POST /api/auth/register
3. **Backend**: Validate, hash password, create user
4. **Database**: Insert user record
5. **Email Service**: Send verification email
6. **Frontend**: Redirect to email verification page

### Job Search Flow
1. **Frontend**: User enters search parameters
2. **API**: GET /api/jobs/search?keyword=...
3. **Backend**: Query job APIs, cache results
4. **LLM Service**: Generate embeddings
5. **Database**: Store jobs and embeddings
6. **Frontend**: Display results with match scores

## Git Branches

```
main                         # Production-ready code
├── develop                  # Development branch
│   ├── feature/feature-name # Feature branches
│   ├── bugfix/bug-name      # Bug fix branches
│   ├── hotfix/hotfix-name   # Production hotfixes
│   └── docs/doc-name        # Documentation branches
```

## Development Phases

Each phase adds new modules to the structure:

- **Phase 0**: Foundation (current)
  - Core configuration
  - Database setup
  - Docker setup

- **Phase 1**: Authentication
  - Auth models & routes
  - User management
  - Security middleware

- **Phase 2**: Resume Management
  - Resume upload
  - PDF parsing
  - Data extraction

- **Phase 3**: Job Integration
  - Job search
  - API integration
  - Caching

... and so on

