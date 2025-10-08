# How to: Create a README

**Purpose**: Step-by-step guide for creating comprehensive, effective README documentation

**Scope**: README.md files for projects, libraries, APIs, and major components

**Overview**: This practical guide walks through creating a professional README file that serves as the primary
    entry point for understanding and using a project. Covers essential sections, optional enhancements, content
    organization, tech stack documentation, installation instructions, usage examples, and project structure.
    Provides templates for different project types, writing guidelines, and a verification checklist. Suitable
    for anyone creating new project documentation or improving existing README files.

**Dependencies**: README standards (.ai/docs/readme-standards.md), README template (.ai/templates/README.template)

**Exports**: Practical README creation process, section-by-section guidance, examples, and checklists

**Related**: readme-standards.md, README.template, file-headers.md

**Implementation**: Step-by-step process with templates and examples for different project types

---

## Prerequisites

Before starting, ensure you have:
- [ ] Clear understanding of your project's purpose and audience
- [ ] List of technologies used in the project
- [ ] Installation requirements and steps (tested)
- [ ] Basic usage examples
- [ ] Access to README template (`.ai/templates/README.template`)

**Estimated Time**: 30-45 minutes

**Difficulty**: Intermediate

## Step 1: Choose Your README Type

Select the appropriate README structure based on project type:

### Application README
**Focus**: Installation, usage, configuration, deployment
**Audience**: Developers running/deploying the application
**Examples**: Web apps, mobile apps, desktop applications

### Library README
**Focus**: Installation, API documentation, usage examples
**Audience**: Developers integrating the library
**Examples**: npm packages, Python libraries, SDKs

### API README
**Focus**: Endpoint documentation, authentication, examples
**Audience**: API consumers, integration developers
**Examples**: REST APIs, GraphQL APIs, microservices

### Infrastructure README
**Focus**: Prerequisites, deployment, configuration
**Audience**: DevOps engineers, infrastructure teams
**Examples**: Terraform modules, Kubernetes configs, CI/CD pipelines

## Step 2: Start with Project Title and Description

Create a compelling introduction:

### Project Title
```markdown
# Project Name

Brief, compelling description (1-3 sentences) that explains what the project does and why it's useful.

**Status**: ✅ Stable | 🚧 In Development | ⚠️ Experimental | 📦 Archived
```

### Guidelines
- Title should match repository name
- Description explains **what**, not **how**
- Highlight unique value proposition
- Include status badge if helpful

### Examples

**Good**:
```markdown
# TaskFlow API

A high-performance task management API built with FastAPI, providing real-time task tracking, team collaboration, and automated workflow orchestration.

**Status**: ✅ Stable
```

**Bad**:
```markdown
# My Project

This is a project I made using Python.
```

## Step 3: Document Tech Stack

List all major technologies clearly:

### Format
```markdown
## Tech Stack

**Backend**:
- Python 3.11+
- FastAPI 0.104+
- SQLAlchemy 2.0+
- PostgreSQL 15+
- Redis 7+

**Frontend** (if applicable):
- React 18+
- TypeScript 5+
- Vite 5+
- TailwindCSS 3+

**Infrastructure**:
- Docker & Docker Compose
- AWS (ECS, RDS, ElastiCache)
- Terraform for IaC

**Development Tools**:
- Poetry for dependency management
- Ruff for linting and formatting
- Pytest for testing
- MyPy for type checking
```

### Guidelines
- Group by category (Backend, Frontend, Infrastructure, Development)
- Include version requirements when important
- List major dependencies only
- Keep it scannable - developers skim this

## Step 4: List Prerequisites

Document everything users need before installation:

### Format
```markdown
## Prerequisites

Before you begin, ensure you have:

**Required**:
- **Docker**: 20.10 or higher ([Install](https://docs.docker.com/get-docker/))
- **Docker Compose**: 2.0 or higher
- **Python**: 3.11 or higher (for local development)
- **Poetry**: 1.5+ ([Install](https://python-poetry.org/docs/#installation))
- **Git**: For version control

**Optional**:
- **AWS CLI**: For deployment ([Install](https://aws.amazon.com/cli/))
- **Terraform**: 1.5+ for infrastructure management
- **Make**: For convenient task automation (included on Linux/Mac)
```

### Guidelines
- Separate required from optional
- Include version requirements
- Provide installation links for less common tools
- Explain why each prerequisite is needed if not obvious

## Step 5: Write Installation Instructions

Provide clear, tested step-by-step installation:

### Format
```markdown
## Installation

### Using Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/username/project.git
   cd project
   ```

2. **Copy environment configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and start services**:
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**:
   ```bash
   docker-compose exec backend poetry run alembic upgrade head
   ```

5. **Verify installation**:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "healthy"}
   ```

### Local Development (Without Docker)

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **Set up database**:
   ```bash
   createdb taskflow
   poetry run alembic upgrade head
   ```

3. **Start development server**:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

### Troubleshooting Installation

**Port already in use**:
```bash
# Change port in docker-compose.yml or .env
PORT=8001 docker-compose up -d
```

**Database connection fails**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres
# Restart if needed
docker-compose restart postgres
```
```

### Guidelines
- Number each step clearly
- Include expected output when helpful
- Provide multiple installation methods if applicable
- Test instructions on fresh machine/environment
- Include verification step
- Add common troubleshooting issues

## Step 6: Provide Usage Examples

Show users how to use your project:

### Format
```markdown
## Usage

### Quick Start

Start the development server:
```bash
make dev
```

Access the application:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

### Basic Examples

**Create a task**:
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete README",
    "priority": "high",
    "due_date": "2025-10-15"
  }'
```

**Response**:
```json
{
  "id": 1,
  "title": "Complete README",
  "priority": "high",
  "status": "pending",
  "created_at": "2025-10-02T10:30:00Z"
}
```

**List tasks**:
```bash
curl http://localhost:8000/api/v1/tasks
```

**Update task**:
```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

### Common Commands

```bash
make dev              # Start development environment
make test             # Run all tests
make lint             # Run linting
make format           # Format code
make migrate          # Run database migrations
```

### Advanced Usage

For advanced usage scenarios, see [User Guide](docs/USER_GUIDE.md).
```

### Guidelines
- Start with simplest use case
- Include working, tested examples
- Show expected output
- Provide both CLI and UI examples if applicable
- Link to detailed documentation for advanced features

## Step 7: Document Project Structure

Help users navigate the codebase:

### Format
```markdown
## Project Structure

```
taskflow-api/
├── app/                      # Application source code
│   ├── api/                  # API layer
│   │   ├── v1/              # API version 1
│   │   │   ├── endpoints/   # Endpoint handlers
│   │   │   └── dependencies.py
│   │   └── deps.py          # Global dependencies
│   ├── core/                 # Core functionality
│   │   ├── config.py        # Configuration management
│   │   ├── security.py      # Security utilities
│   │   └── database.py      # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── task.py
│   │   └── user.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── task.py
│   │   └── user.py
│   ├── services/            # Business logic layer
│   │   ├── task_service.py
│   │   └── user_service.py
│   └── main.py              # Application entry point
├── tests/                   # Test files
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── conftest.py         # Pytest configuration
├── alembic/                # Database migrations
│   ├── versions/           # Migration files
│   └── env.py
├── .docker/                # Docker configurations
│   ├── dockerfiles/        # Dockerfiles
│   │   ├── Dockerfile.backend
│   │   └── Dockerfile.frontend
│   └── compose/            # Docker Compose files
│       └── app.yml
├── docs/                   # Additional documentation
│   ├── API.md             # API documentation
│   ├── ARCHITECTURE.md    # Architecture guide
│   └── DEPLOYMENT.md      # Deployment guide
├── scripts/                # Utility scripts
│   ├── seed.sh            # Database seeding
│   └── deploy.sh          # Deployment script
├── .env.example            # Environment template
├── .gitignore             # Git ignore patterns
├── pyproject.toml         # Project dependencies
├── Makefile              # Development commands
├── docker-compose.yml    # Docker Compose config
└── README.md             # This file
```

**Key Directories**:
- `app/` - Application source code organized by layer
- `tests/` - All test files (unit, integration, e2e)
- `alembic/` - Database migration management
- `.docker/` - Docker and container configurations
- `docs/` - Detailed documentation
```

### Guidelines
- Show directory tree with comments
- Explain purpose of each major directory
- Don't document every file - focus on structure
- Keep it current as structure changes
- Add key directories section for quick reference

## Step 8: Add Development Guidelines

Help contributors work on the project:

### Format
```markdown
## Development

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
poetry run pytest tests/unit/test_tasks.py

# Run tests matching pattern
poetry run pytest -k "test_create"
```

### Code Quality

This project follows strict code quality standards:

**Python**:
- PEP 8 style guide (120 character line length)
- Type hints required for all functions
- Google-style docstrings
- Maximum complexity of 10 (McCabe)

**Tools**:
```bash
make lint              # Run Ruff linting
make lint-fix          # Auto-fix issues
make typecheck         # MyPy type checking
make security-scan     # Bandit security scan
```

### Git Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/task-filtering
   ```

2. **Make changes and commit**:
   ```bash
   git add .
   git commit -m "feat: Add task filtering by status"
   ```

3. **Push and create PR**:
   ```bash
   git push origin feature/task-filtering
   ```

4. **Ensure CI passes** before requesting review

### Database Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "Add priority field"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1
```

See [Contributing Guide](CONTRIBUTING.md) for detailed guidelines.
```

### Guidelines
- Document testing procedures
- Include code quality standards
- Explain Git workflow
- Cover database migrations if applicable
- Link to detailed contributing guide

## Step 9: Add Optional Sections (As Needed)

Include these sections based on project requirements:

### Configuration
```markdown
## Configuration

Create a `.env` file based on `.env.example`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis
REDIS_URL=redis://localhost:6379/0

# Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS (for production)
AWS_REGION=us-east-1
```

See [Configuration Guide](docs/CONFIGURATION.md) for all options.
```

### Deployment
```markdown
## Deployment

### Production Deployment

**Using AWS ECS**:
```bash
# Deploy infrastructure
cd terraform
terraform init
terraform apply

# Deploy application
./scripts/deploy.sh production
```

See [Deployment Guide](docs/DEPLOYMENT.md) for details.
```

### API Documentation
```markdown
## API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

See [API Documentation](docs/API.md) for detailed endpoint specifications.
```

### Contributing
```markdown
## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.
```

### License
```markdown
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

## Step 10: Verify Your README

Use this checklist to ensure completeness:

### Essential Content
- [ ] Project title and clear description
- [ ] Status badge (if applicable)
- [ ] Tech stack documented
- [ ] Prerequisites listed with versions
- [ ] Installation instructions (tested and working)
- [ ] Usage examples included
- [ ] Project structure documented
- [ ] Development guidelines provided

### Content Quality
- [ ] All code examples tested
- [ ] Installation works on fresh environment
- [ ] Links are working and current
- [ ] No broken references
- [ ] No typos or errors
- [ ] Consistent formatting
- [ ] Clear and concise writing

### Maintenance
- [ ] README matches current code
- [ ] Version numbers current
- [ ] No outdated information
- [ ] Contact/support information current

## Common Mistakes and Solutions

### Mistake 1: Installation Instructions Don't Work

**Problem**: Commands fail on fresh install

**Solution**:
1. Test on clean environment
2. Include all prerequisites
3. Provide expected output
4. Add troubleshooting section

### Mistake 2: Missing Prerequisites

**Problem**: Users can't install because tools missing

**Solution**:
1. List all required tools
2. Include version requirements
3. Provide installation links
4. Explain platform differences

### Mistake 3: No Usage Examples

**Problem**: Users don't know how to use project after installing

**Solution**:
1. Show simplest use case first
2. Include working examples
3. Show expected output
4. Link to detailed docs

### Mistake 4: Outdated Information

**Problem**: README doesn't match current code

**Solution**:
1. Update README with code changes
2. Test examples regularly
3. Review in pull requests
4. Keep structure diagram current

### Mistake 5: Too Much Information

**Problem**: README is overwhelming and hard to navigate

**Solution**:
1. Keep README focused on essentials
2. Move detailed docs to separate files
3. Use clear sections with headers
4. Link to detailed documentation

## Examples by Project Type

### Application README (Minimal)

```markdown
# TaskFlow

A simple task management application.

## Quick Start

```bash
docker-compose up -d
open http://localhost:3000
```

## Tech Stack

- React 18
- Node.js 20
- PostgreSQL 15

## License

MIT
```

### Application README (Comprehensive)

```markdown
# TaskFlow API

High-performance task management API with real-time updates and team collaboration features.

**Status**: ✅ Stable

## Tech Stack

**Backend**: Python 3.11+, FastAPI, PostgreSQL, Redis
**Infrastructure**: Docker, AWS ECS, Terraform

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (local dev)

## Quick Start

```bash
git clone https://github.com/user/taskflow.git
cd taskflow
cp .env.example .env
docker-compose up -d
curl http://localhost:8000/health
```

## Project Structure

```
taskflow-api/
├── app/          # Application code
├── tests/        # Tests
├── .docker/      # Docker configs
└── docs/         # Documentation
```

## Development

```bash
make dev          # Start dev environment
make test         # Run tests
make lint         # Lint code
```

See [Development Guide](docs/DEVELOPMENT.md).

## Deployment

See [Deployment Guide](docs/DEPLOYMENT.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
```

## Quick Reference

### Essential Sections (All READMEs)
1. Title and description
2. Tech stack
3. Prerequisites
4. Installation
5. Usage
6. Project structure
7. Development guidelines

### Optional Sections (As Needed)
8. Configuration
9. API documentation
10. Deployment
11. Architecture
12. Troubleshooting
13. Contributing
14. License

## Next Steps

After creating your README:
1. **Test all commands** in the README
2. **Have someone else** follow the instructions
3. **Commit README** with descriptive message
4. **Keep it updated** as project changes
5. **Review in PRs** for accuracy
6. **Link from other docs** to README sections

## Additional Resources

- **README standards**: `.ai/docs/readme-standards.md`
- **README template**: `.ai/templates/README.template`
- **File headers**: `.ai/howtos/how-to-write-file-headers.md`
- **API documentation**: `.ai/howtos/how-to-document-api.md`
