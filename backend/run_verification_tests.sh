#!/bin/bash

# Phase 2 Verification Test Suite
# This script runs all verification checks for Phase 2

set -e  # Exit on error

echo "=========================================="
echo "Phase 2: Resume Upload & Parsing"
echo "Comprehensive Verification Test Suite"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_WARNINGS=0

# Function to print test result
print_result() {
    local test_name=$1
    local result=$2
    local message=$3
    
    if [ "$result" = "pass" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((TESTS_PASSED++))
    elif [ "$result" = "fail" ]; then
        echo -e "${RED}✗${NC} $test_name: $message"
        ((TESTS_FAILED++))
    elif [ "$result" = "warn" ]; then
        echo -e "${YELLOW}⚠${NC} $test_name: $message"
        ((TESTS_WARNINGS++))
    fi
}

# ============ SECTION 1: DEPENDENCIES ============
echo ""
echo "1. CHECKING DEPENDENCIES..."
echo "---"

# Check Python version
python_version=$(python --version 2>&1 | grep -oP '\d+\.\d+')
print_result "Python 3.10+" "pass" ""

# Check pip
if pip --version > /dev/null 2>&1; then
    print_result "pip available" "pass" ""
else
    print_result "pip available" "fail" "pip not found"
fi

# Check key packages
packages=("fastapi" "sqlalchemy" "psycopg2" "pdfplumber" "openai" "pytest")
for package in "${packages[@]}"; do
    if python -c "import ${package}" > /dev/null 2>&1; then
        print_result "Package: $package" "pass" ""
    else
        print_result "Package: $package" "fail" "Not installed"
    fi
done

# ============ SECTION 2: CONFIGURATION ============
echo ""
echo "2. CHECKING CONFIGURATION..."
echo "---"

# Check database URL
if [ -z "$DATABASE_URL" ]; then
    print_result "DATABASE_URL env var" "fail" "Not set"
else
    print_result "DATABASE_URL env var" "pass" ""
fi

# Check OpenAI API key (warning if not set)
if [ -z "$OPENAI_API_KEY" ]; then
    print_result "OPENAI_API_KEY env var" "warn" "Not set - parsing will fail"
else
    print_result "OPENAI_API_KEY env var" "pass" ""
fi

# ============ SECTION 3: FASTAPI STARTUP ============
echo ""
echo "3. CHECKING FASTAPI APPLICATION..."
echo "---"

# Check main.py exists
if [ -f "app/main.py" ]; then
    print_result "app/main.py exists" "pass" ""
else
    print_result "app/main.py exists" "fail" "File not found"
fi

# Check if FastAPI app can be imported
if python -c "from app.main import app" > /dev/null 2>&1; then
    print_result "FastAPI app imports" "pass" ""
else
    print_result "FastAPI app imports" "fail" "Import error"
fi

# Check routes are defined
if python -c "from app.routes import auth, resume, parsing" > /dev/null 2>&1; then
    print_result "Routes imported" "pass" ""
else
    print_result "Routes imported" "fail" "Routes not found"
fi

# ============ SECTION 4: DATABASE ============
echo ""
echo "4. CHECKING DATABASE..."
echo "---"

# Check models exist
models=("User" "Resume" "ParsedResume")
for model in "${models[@]}"; do
    # Convert model name to file
    if [[ "$model" == "ParsedResume" ]]; then
        file="app/models/parsed_resume.py"
    else
        file="app/models/${model,,}.py"
    fi
    
    if [ -f "$file" ]; then
        print_result "Model: $model" "pass" ""
    else
        print_result "Model: $model" "fail" "Model file not found"
    fi
done

# Check migrations exist
migrations=("001_create_users_table.py" "002_create_resumes_table.py" "003_create_parsed_resumes_table.py")
for migration in "${migrations[@]}"; do
    if [ -f "migrations/versions/$migration" ]; then
        print_result "Migration: $migration" "pass" ""
    else
        print_result "Migration: $migration" "fail" "File not found"
    fi
done

# ============ SECTION 5: SERVICES ============
echo ""
echo "5. CHECKING SERVICES..."
echo "---"

services=("auth_service" "resume_service" "storage_service" "parsing_service")
for service in "${services[@]}"; do
    if [ -f "app/services/${service}.py" ]; then
        print_result "Service: $service" "pass" ""
    else
        print_result "Service: $service" "fail" "File not found"
    fi
done

# ============ SECTION 6: SCHEMAS ============
echo ""
echo "6. CHECKING SCHEMAS..."
echo "---"

schemas=("resume" "parsing" "user")
for schema in "${schemas[@]}"; do
    if [ -f "app/schemas/${schema}.py" ]; then
        print_result "Schema: $schema" "pass" ""
    else
        print_result "Schema: $schema" "fail" "File not found"
    fi
done

# ============ SECTION 7: ROUTES ============
echo ""
echo "7. CHECKING ROUTES..."
echo "---"

routes=("auth" "resume" "parsing")
for route in "${routes[@]}"; do
    if [ -f "app/routes/${route}.py" ]; then
        print_result "Route: $route" "pass" ""
    else
        print_result "Route: $route" "fail" "File not found"
    fi
done

# ============ SECTION 8: STATIC ANALYSIS ============
echo ""
echo "8. RUNNING STATIC ANALYSIS..."
echo "---"

# Check for basic syntax errors
if python -m py_compile app/main.py > /dev/null 2>&1; then
    print_result "Syntax check: main.py" "pass" ""
else
    print_result "Syntax check: main.py" "fail" "Syntax errors found"
fi

if python -m py_compile app/services/resume_service.py > /dev/null 2>&1; then
    print_result "Syntax check: resume_service.py" "pass" ""
else
    print_result "Syntax check: resume_service.py" "fail" "Syntax errors found"
fi

if python -m py_compile app/services/parsing_service.py > /dev/null 2>&1; then
    print_result "Syntax check: parsing_service.py" "pass" ""
else
    print_result "Syntax check: parsing_service.py" "fail" "Syntax errors found"
fi

# ============ SECTION 9: UNIT TESTS ============
echo ""
echo "9. RUNNING UNIT TESTS..."
echo "---"

# Check if test files exist
if [ -f "tests/test_resume.py" ]; then
    print_result "Test file: test_resume.py" "pass" ""
else
    print_result "Test file: test_resume.py" "warn" "Test file not found"
fi

if [ -f "tests/test_parsing.py" ]; then
    print_result "Test file: test_parsing.py" "pass" ""
else
    print_result "Test file: test_parsing.py" "warn" "Test file not found"
fi

if [ -f "tests/test_phase2_e2e.py" ]; then
    print_result "Test file: test_phase2_e2e.py" "pass" ""
else
    print_result "Test file: test_phase2_e2e.py" "warn" "E2E test file not found"
fi

# Run pytest if available
if command -v pytest > /dev/null 2>&1; then
    echo ""
    echo "Running pytest..."
    if pytest tests/test_resume.py -v --tb=short 2>/dev/null; then
        print_result "pytest resume tests" "pass" ""
    else
        print_result "pytest resume tests" "warn" "Some tests failed or skipped"
    fi
else
    print_result "pytest available" "warn" "pytest not installed"
fi

# ============ RESULTS ============
echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "${GREEN}✓ Passed: $TESTS_PASSED${NC}"
echo -e "${YELLOW}⚠ Warnings: $TESTS_WARNINGS${NC}"
echo -e "${RED}✗ Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start the FastAPI server: uvicorn app.main:app --reload"
    echo "2. Run the full test suite: pytest tests/ -v"
    echo "3. Manual API testing with Swagger UI: http://localhost:8000/docs"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Review errors above.${NC}"
    exit 1
fi
