#!/bin/bash

# Dynamic Skills System - Complete Installation Script
# For OpenClaw Beginners
# Version: 1.0.0

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SKILLS_DB="skillsdb"
DB_USER="${USER:-postgres}"
LOOKUP_PORT=8845
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Dynamic Skills System - Installation Wizard         ║${NC}"
echo -e "${BLUE}║   Version 1.0.0 - 49 Pre-configured Skills            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Step 1: Check prerequisites
echo ""
print_status "Step 1/7: Checking prerequisites..."
echo ""

# Check PostgreSQL
if command -v psql &> /dev/null; then
    PG_VERSION=$(psql --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
    print_success "PostgreSQL installed (version $PG_VERSION)"
else
    print_error "PostgreSQL not found!"
    echo ""
    echo "Please install PostgreSQL:"
    echo "  macOS: brew install postgresql@16"
    echo "  Linux: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
    print_success "Python 3 installed (version $PY_VERSION)"
else
    print_error "Python 3 not found!"
    echo ""
    echo "Please install Python 3.9+:"
    echo "  macOS: brew install python@3.9"
    echo "  Linux: sudo apt-get install python3 python3-pip"
    exit 1
fi

# Check Redis (optional)
if command -v redis-cli &> /dev/null && redis-cli ping &> /dev/null; then
    print_success "Redis installed and running (caching enabled)"
    REDIS_AVAILABLE=true
else
    print_warning "Redis not found (optional - caching will be disabled)"
    REDIS_AVAILABLE=false
fi

echo ""

# Step 2: Check pgvector extension
print_status "Step 2/7: Checking pgvector extension..."
echo ""

if psql -U "$DB_USER" -d postgres -c "\dx" 2>/dev/null | grep -q vector; then
    print_success "pgvector extension already installed"
else
    print_warning "pgvector extension not found, attempting to install..."
    
    # Try to create extension
    if psql -U "$DB_USER" -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null; then
        print_success "pgvector extension installed"
    else
        print_error "Could not install pgvector extension"
        echo ""
        echo "Please install pgvector:"
        echo "  macOS: brew install pgvector"
        echo "  Linux: sudo apt-get install postgresql-16-pgvector"
        echo ""
        echo "Then run: psql -U postgres -c \"CREATE EXTENSION IF NOT EXISTS vector;\""
        exit 1
    fi
fi

echo ""

# Step 3: Create database
print_status "Step 3/7: Creating database..."
echo ""

if psql -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$SKILLS_DB"; then
    print_warning "Database '$SKILLS_DB' already exists"
    read -p "Do you want to drop and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        dropdb -U "$DB_USER" "$SKILLS_DB"
        createdb -U "$DB_USER" "$SKILLS_DB"
        print_success "Database recreated"
    else
        print_status "Using existing database"
    fi
else
    createdb -U "$DB_USER" "$SKILLS_DB"
    print_success "Database '$SKILLS_DB' created"
fi

# Enable pgvector in the new database
psql -U "$DB_USER" -d "$SKILLS_DB" -c "CREATE EXTENSION IF NOT EXISTS vector;" > /dev/null 2>&1
print_success "pgvector enabled in database"

echo ""

# Step 4: Import schema and skills
print_status "Step 4/7: Importing skills database..."
echo ""

if [ -f "$SCRIPT_DIR/sql/import.sql" ]; then
    psql -U "$DB_USER" -d "$SKILLS_DB" -f "$SCRIPT_DIR/sql/import.sql" > /dev/null 2>&1
    print_success "Database schema and skills imported"
    
    # Verify skill count
    SKILL_COUNT=$(psql -U "$DB_USER" -d "$SKILLS_DB" -t -c "SELECT COUNT(*) FROM skills WHERE status='active';" | tr -d ' ')
    if [ "$SKILL_COUNT" -eq 49 ]; then
        print_success "Verified: $SKILL_COUNT skills imported"
    else
        print_warning "Expected 49 skills, found $SKILL_COUNT"
    fi
else
    print_error "import.sql not found!"
    exit 1
fi

echo ""

# Step 5: Install Python dependencies
print_status "Step 5/7: Installing Python dependencies..."
echo ""

if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip3 install -q -r "$SCRIPT_DIR/requirements.txt"
    print_success "Dependencies installed"
else
    print_warning "requirements.txt not found, skipping"
fi

echo ""

# Step 6: Generate embeddings
print_status "Step 6/7: Generating embeddings..."
echo ""

export SKILLS_DB_DSN="postgresql://$DB_USER@localhost/$SKILLS_DB"

if [ -f "$SCRIPT_DIR/scripts/generate_embeddings.py" ]; then
    cd "$SCRIPT_DIR"
    python3 scripts/generate_embeddings.py > /dev/null 2>&1
    print_success "Embeddings generated"
else
    print_warning "Embedding script not found, skipping"
fi

echo ""

# Step 7: Start lookup service
print_status "Step 7/7: Starting lookup service..."
echo ""

# Check if service is already running
if lsof -i :$LOOKUP_PORT > /dev/null 2>&1; then
    print_warning "Lookup service already running on port $LOOKUP_PORT"
    read -p "Do you want to restart it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill $(lsof -t -i :$LOOKUP_PORT) 2>/dev/null || true
        sleep 2
    fi
fi

if [ -f "$SCRIPT_DIR/services/lookup_service_v2.py" ]; then
    cd "$SCRIPT_DIR"
    nohup python3 services/lookup_service_v2.py > /tmp/lookup_service.log 2>&1 &
    sleep 3
    
    if lsof -i :$LOOKUP_PORT > /dev/null 2>&1; then
        print_success "Lookup service started on port $LOOKUP_PORT"
    else
        print_error "Failed to start lookup service"
        echo "Check logs: /tmp/lookup_service.log"
    fi
else
    print_warning "Lookup service not found, skipping"
fi

echo ""

# Final verification
print_status "Verifying installation..."
echo ""

# Health check
if curl -s http://localhost:$LOOKUP_PORT/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:$LOOKUP_PORT/health)
    print_success "Health check passed: $HEALTH"
else
    print_warning "Health check failed (service may still be starting)"
fi

# Test semantic search
echo ""
print_status "Testing semantic search..."
TEST_RESULT=$(curl -s -X POST http://localhost:$LOOKUP_PORT/skills/lookup \
  -H "Content-Type: application/json" \
  -d '{"query": "test website", "max_skills": 1}' 2>/dev/null)

if echo "$TEST_RESULT" | grep -q "testing-webapps"; then
    print_success "Semantic search working correctly"
else
    print_warning "Semantic search test inconclusive"
fi

echo ""

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Installation Complete! 🎉                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Summary:"
echo "  • Database: $SKILLS_DB"
echo "  • Skills: 49"
echo "  • Lookup Service: http://localhost:$LOOKUP_PORT"
echo "  • Health Check: http://localhost:$LOOKUP_PORT/health"
echo ""

# Set environment variable
echo "To use the skills system, add to your ~/.zshrc or ~/.bashrc:"
echo ""
echo "  export SKILLS_DB_DSN=\"postgresql://$DB_USER@localhost/$SKILLS_DB\""
echo ""

if ! grep -q "SKILLS_DB_DSN" ~/.zshrc 2>/dev/null; then
    read -p "Add this to ~/.zshrc automatically? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "" >> ~/.zshrc
        echo "# Dynamic Skills System" >> ~/.zshrc
        echo "export SKILLS_DB_DSN=\"postgresql://$DB_USER@localhost/$SKILLS_DB\"" >> ~/.zshrc
        print_success "Environment variable added to ~/.zshrc"
        echo "Run 'source ~/.zshrc' to apply"
    fi
fi

echo ""
echo "Next steps:"
echo "  1. Test: curl http://localhost:$LOOKUP_PORT/health"
echo "  2. Try: curl -X POST http://localhost:$LOOKUP_PORT/skills/lookup -H 'Content-Type: application/json' -d '{\"query\": \"test website\"}'"
echo "  3. Integrate with OpenClaw: openclaw gateway restart"
echo ""
echo "Documentation: $SCRIPT_DIR/INSTALL.md"
echo ""
