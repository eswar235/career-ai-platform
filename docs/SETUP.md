# Setup Guide

Complete setup instructions for the Career Assistant SaaS platform.

## Prerequisites

### System Requirements
- OS: Linux, macOS, or Windows (with WSL2)
- RAM: 8GB minimum (16GB recommended)
- Disk Space: 10GB minimum
- Internet connection for API integrations

### Software Requirements
- **Git**: Latest version
- **Docker**: 20.10+ and Docker Compose 2.0+
- **Node.js**: 18.0+ LTS
- **Python**: 3.11+
- **PostgreSQL**: 14+ (if running locally without Docker)

## Quick Start with Docker Compose

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/career-ai-platform.git
cd career-ai-platform
```

### 2. Configure Environment Variables
```bash
# Copy the example env file
cp .env.example .env

# Edit with your configuration
nano .env
```

### 3. Start All Services
```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 4. Initialize Database
```bash
# Run migrations
docker-compose exec backend python -m alembic upgrade head

# (Optional) Load sample data
docker-compose exec backend python scripts/seed_data.py
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Redis Commander**: http://localhost:8081

## Manual Setup (Development)

### Backend Setup

#### 1. Python Environment
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### 3. Environment Configuration
```bash
# Copy env template
cp .env.example .env

# Edit configuration
nano .env
```

#### 4. Database Setup
```bash
# Install PostgreSQL (if not already installed)
# On macOS:
brew install postgresql
brew services start postgresql

# On Ubuntu:
sudo apt-get install postgresql postgresql-contrib

# Create database
createdb career_ai_db
createuser career_ai_user
psql -U postgres -d career_ai_db -c "ALTER USER career_ai_user WITH PASSWORD 'password';"

# Run migrations
alembic upgrade head
```

#### 5. Start Backend Server
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Or using make (if available)
make run-backend
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

#### 1. Install Node Dependencies
```bash
cd frontend

npm install
# or
yarn install
```

#### 2. Environment Configuration
```bash
# Copy env template
cp .env.example .env.local

# Edit configuration (ensure API URL matches backend)
nano .env.local
```

#### 3. Start Development Server
```bash
npm run dev
# or
yarn dev
```

Frontend will be available at `http://localhost:3000`

## Development Workflow

### Running Services Individually

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Running Tests

**Backend Tests:**
```bash
cd backend
pytest                          # Run all tests
pytest --cov=app               # With coverage
pytest -v                       # Verbose output
pytest tests/test_models.py    # Specific test file
```

**Frontend Tests:**
```bash
cd frontend
npm test                        # Run tests
npm run test:watch            # Watch mode
npm run test:coverage         # With coverage
```

### Code Quality

**Backend:**
```bash
cd backend

# Format code
black app/

# Check linting
flake8 app/

# Type checking
mypy app/
```

**Frontend:**
```bash
cd frontend

# Lint
npm run lint

# Format
npm run format

# Type check
npm run type-check
```

## Database Management

### Alembic Migrations

#### Create a New Migration
```bash
cd backend

# Generate migration for model changes
alembic revision --autogenerate -m "Add user table"

# Edit the generated file in migrations/versions/

# Apply migration
alembic upgrade head
```

#### Migration Commands
```bash
alembic current          # Show current revision
alembic history          # Show migration history
alembic downgrade -1     # Rollback one migration
alembic upgrade head     # Apply all pending migrations
```

### Database Connection

#### Connect with psql
```bash
psql -U career_ai_user -d career_ai_db -h localhost
```

#### Using pgAdmin (Optional)
```bash
docker run -p 5050:80 dpage/pgadmin4
# Access at http://localhost:5050
# Default: admin@pgadmin.org / admin
```

## Docker Troubleshooting

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### Clean Up
```bash
# Stop services
docker-compose down

# Remove volumes (CAUTION: deletes database)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache
```

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :3000
# Kill process
kill -9 <PID>
```

#### Database Connection Refused
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Recreate database
docker-compose down -v
docker-compose up -d postgres
```

#### Node Modules Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/db
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
JWT_SECRET=your-secret-key
OPENAI_API_KEY=sk-...
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Career Assistant
```

## Initial Data

### Create Admin User (Future)
```bash
cd backend
python scripts/create_admin.py --email admin@example.com --password password
```

### Load Sample Data (Future)
```bash
cd backend
python scripts/seed_data.py
```

## IDE Setup

### VS Code

#### Recommended Extensions
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black (ms-python.black-formatter)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)
- Thunder Client (rangav.vscode-thunder-client)

#### Settings (.vscode/settings.json)
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=100"],
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.python"
  },
  "[typescript]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### PyCharm

#### Configuration
1. Set Python interpreter to virtual environment
2. Mark `backend` folder as Sources Root
3. Enable Django support (if needed)
4. Configure code style to PEP 8

## Next Steps

1. **Read the Documentation**: See `docs/ARCHITECTURE.md` for system overview
2. **Explore the API**: Visit `http://localhost:8000/docs` for interactive API docs
3. **Start Development**: Begin with Phase 1 tasks in `tasks.md`
4. **Review Code**: Check existing code patterns and conventions

## Support

- **Issues**: Create an issue on GitHub
- **Documentation**: See `docs/` folder
- **Specs**: Check `.kiro/specs/career-assistant-saas/`

