# README Documentation Standards

**Purpose**: Standards and best practices for creating comprehensive, effective README documentation

**Scope**: README.md files for all projects, libraries, and major components

**Overview**: This document establishes standards for creating high-quality README files that serve as the
    primary entry point for understanding and using a project. Covers essential sections, optional enhancements,
    content organization, tech stack documentation, installation instructions, usage examples, and project structure
    documentation. Provides templates and examples for different project types including applications, libraries,
    APIs, and infrastructure projects. Ensures README files are comprehensive, maintainable, and valuable for both
    new developers and experienced contributors.

**Dependencies**: Markdown knowledge, project understanding, file header standards

**Exports**: README structure standards, section templates, content guidelines, and examples

**Related**: .ai/templates/README.template, file-headers.md, how-to-create-readme.md

**Implementation**: Template-based README creation with project-type specific sections

---

## Overview

The README.md file is the first thing developers see when encountering a project. It serves as:
- **Project introduction**: What the project does and why it exists
- **Quick start guide**: How to get up and running quickly
- **Reference documentation**: Where to find more detailed information
- **Contribution guide**: How to contribute to the project

A well-written README can make the difference between a project being adopted or ignored.

## Essential Sections

Every README must include these core sections:

### 1. Project Title and Description

**Format**:
```markdown
# Project Name

Brief, compelling description of what the project does (1-3 sentences).

**Status**: ✅ Stable | 🚧 In Development | ⚠️ Experimental | 📦 Archived
```

**Guidelines**:
- Title should match the project name exactly
- Description should explain what, not how
- Include status badge if applicable
- Keep it concise - details go in later sections

**Example**:
```markdown
# TaskFlow API

A high-performance task management API built with FastAPI, providing real-time task tracking, team collaboration, and automated workflow orchestration.

**Status**: ✅ Stable
```

### 2. Tech Stack

**Format**:
```markdown
## Tech Stack

**Backend**:
- Python 3.11+
- FastAPI 0.104+
- SQLAlchemy 2.0+
- PostgreSQL 15+
- Redis 7+

**Infrastructure**:
- Docker & Docker Compose
- AWS (ECS, RDS, ElastiCache)
- Terraform for IaC

**Development**:
- Poetry for dependency management
- Ruff for linting and formatting
- Pytest for testing
- MyPy for type checking
```

**Guidelines**:
- Group by category (Backend, Frontend, Infrastructure, Development, etc.)
- Include version requirements when important
- List major dependencies only (not every library)
- Keep it scannable - developers skim this section

### 3. Prerequisites

**Format**:
```markdown
## Prerequisites

Before you begin, ensure you have:
- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher
- **Python**: 3.11 or higher (for local development)
- **Poetry**: 1.5+ (for dependency management)
- **Git**: For version control

Optional:
- **AWS CLI**: For deployment
- **Terraform**: 1.5+ for infrastructure management
```

**Guidelines**:
- List all required tools and versions
- Separate required from optional
- Include download links for less common tools
- Explain why each prerequisite is needed if not obvious

### 4. Installation

**Format**:
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
   poetry run alembic upgrade head
   ```

3. **Start development server**:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```
```

**Guidelines**:
- Provide step-by-step instructions
- Include expected output when helpful
- Offer multiple installation methods if applicable
- Test instructions on a fresh machine
- Include troubleshooting for common issues

### 5. Usage

**Format**:
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
  -d '{"title": "Complete README", "priority": "high"}'
```

**List tasks**:
```bash
curl http://localhost:8000/api/v1/tasks
```

**Update task status**:
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
make seed             # Seed database with sample data
```


**Guidelines**:
- Show the most common use cases first
- Include working, tested examples
- Provide both UI and API examples if applicable
- Reference detailed documentation for advanced usage
- Use actual commands users can copy-paste

### 6. Project Structure

**Format**:
```markdown
## Project Structure


project/
├── app/                      # Application source code
│   ├── api/                  # API endpoints
│   │   ├── v1/              # API version 1
│   │   │   ├── endpoints/   # Endpoint handlers
│   │   │   └── dependencies.py
│   │   └── deps.py
│   ├── core/                 # Core functionality
│   │   ├── config.py        # Configuration
│   │   ├── security.py      # Security utilities
│   │   └── database.py      # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── main.py              # Application entry point
├── tests/                   # Test files
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── conftest.py         # Pytest configuration
├── alembic/                # Database migrations
├── .docker/                # Docker configurations
│   ├── dockerfiles/        # Dockerfiles
│   └── compose/            # Docker Compose files
├── docs/                   # Additional documentation
├── scripts/                # Utility scripts
├── .env.example            # Environment template
├── pyproject.toml          # Project dependencies
├── Makefile               # Development commands
└── README.md              # This file

```

**Guidelines**:
- Show only important directories and files
- Add comments explaining each section's purpose
- Keep it current as structure changes
- Group related items together
- Don't document every file - focus on structure

### 7. Development Guidelines

**Format**:
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

This project follows:
- **PEP 8** style guide with 120 character line length
- **Type hints** required for all functions
- **Google-style docstrings** for documentation
- **Maximum complexity** of 10 (McCabe)

```bash
# Linting
make lint

# Auto-fix issues
make lint-fix

# Type checking
make typecheck

# Security scanning
make security-scan
```

### Git Workflow

1. Create feature branch from `main`:
   ```bash
   git checkout -b feature/task-filtering
   ```

2. Make changes and commit:
   ```bash
   git add .
   git commit -m "feat: Add task filtering by status"
   ```

3. Push and create pull request:
   ```bash
   git push origin feature/task-filtering
   ```

4. Ensure CI passes before merging

### Database Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "Add task priority field"

# Apply migrations
poetry run alembic upgrade head

# Rollback
poetry run alembic downgrade -1
```
```

**Guidelines**:
- Document development workflow
- Include code quality standards
- Explain testing procedures
- Describe branching strategy
- Link to detailed contribution guide if exists

## Optional Sections

Include these sections based on project needs:

### API Documentation

```markdown
## API Documentation

### Endpoints

**Tasks**:
- `GET /api/v1/tasks` - List all tasks
- `POST /api/v1/tasks` - Create new task
- `GET /api/v1/tasks/{id}` - Get task by ID
- `PATCH /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

**Authentication**:
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Register
- `POST /api/v1/auth/refresh` - Refresh token

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

See [API Documentation](docs/API.md) for detailed endpoint specifications.
```

### Configuration

```markdown
## Configuration

### Environment Variables

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
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

See [Configuration Guide](docs/CONFIGURATION.md) for all options.
```

### Deployment

```markdown
## Deployment

### Production Deployment

**Using Docker Compose**:
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

**Using AWS ECS**:
```bash
# Deploy infrastructure
cd terraform
terraform init
terraform apply

# Deploy application
./scripts/deploy.sh production
```

See [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions.

### Architecture

```markdown
## Architecture

### System Overview

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   API       │────▶│  Database   │
│ (React App) │     │  (FastAPI)  │     │ (PostgreSQL)│
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    Redis    │
                    │  (Cache)    │
                    └─────────────┘
```

### Key Components

- **API Layer**: FastAPI application handling HTTP requests
- **Service Layer**: Business logic and data processing
- **Data Layer**: SQLAlchemy models and database access
- **Cache Layer**: Redis for session storage and caching

See [Architecture Documentation](docs/ARCHITECTURE.md) for details.
```

### Troubleshooting

```markdown
## Troubleshooting

### Common Issues

**Database connection errors**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection string in .env
cat .env | grep DATABASE_URL

# Restart database
docker-compose restart postgres
```

**Port already in use**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

**Migration conflicts**:
```bash
# Reset database (WARNING: destroys data)
docker-compose down -v
docker-compose up -d
poetry run alembic upgrade head
```

See [FAQ](docs/FAQ.md) for more solutions.
```

### Contributing

```markdown
## Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'feat: Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Build process or tooling changes

### Code Review Process

- All PRs require one approval
- CI must pass (tests, linting, type checking)
- Coverage must not decrease

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.
```

### License

```markdown
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

### Acknowledgments

```markdown
## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for database ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- Contributors and maintainers
```

## README Templates by Project Type

### Application README

Focus on:
- Installation and setup
- Usage examples
- Configuration
- Deployment

### Library README

Focus on:
- Installation (pip install, npm install)
- API documentation
- Usage examples
- Contributing guidelines

### API README

Focus on:
- Endpoint documentation
- Authentication
- Request/response examples
- Rate limiting and quotas

### Infrastructure README

Focus on:
- Prerequisites (cloud accounts, tools)
- Deployment procedures
- Configuration management
- Disaster recovery

## Content Guidelines

### Writing Style

1. **Be concise**: Get to the point quickly
2. **Be specific**: Provide exact commands and values
3. **Be complete**: Include all necessary information
4. **Be current**: Keep README updated with code changes
5. **Be helpful**: Anticipate questions and answer them

### Code Examples

1. **Use real examples**: Test all code snippets
2. **Include output**: Show expected results
3. **Be copy-pastable**: Users should be able to copy and run
4. **Handle errors**: Show how to handle common errors
5. **Explain context**: Add comments when necessary

### Formatting

1. **Use headings**: Organize with clear hierarchy
2. **Use code blocks**: Syntax highlighting for readability
3. **Use lists**: Break down steps and options
4. **Use tables**: For comparing options or features
5. **Use badges**: For status, version, build, coverage (optional)

### Links

1. **Link to detailed docs**: README is entry point, not complete documentation
2. **Use relative links**: For files in same repository
3. **Keep links current**: Update when moving files
4. **External links**: Use for dependencies, tools, references

## README Anti-Patterns

### What to Avoid

1. **Too long**: Don't try to document everything in README
2. **Too short**: Missing critical information
3. **Outdated**: Instructions that don't work
4. **Untested**: Commands that haven't been verified
5. **Overly complex**: Assuming too much knowledge
6. **Missing context**: Not explaining why, only how
7. **Broken links**: Links to moved or deleted content
8. **No examples**: Pure text without demonstrations

### Common Mistakes

1. **Installation that doesn't work**: Always test on fresh environment
2. **Missing prerequisites**: Assuming tools are installed
3. **No quickstart**: Making users read entire README
4. **Technical jargon**: Unexplained terminology
5. **No project structure**: Hard to navigate codebase
6. **Inconsistent formatting**: Poor readability
7. **Platform-specific**: Only works on one OS without mention

## Maintenance

### Keeping README Current

1. **Update with major changes**: New features, breaking changes
2. **Test periodically**: Verify instructions still work
3. **Review on releases**: Ensure version info is correct
4. **Accept contributions**: Let users improve documentation
5. **Use automation**: Generate parts from code when possible

### Version Control

1. **Commit README changes**: With related code changes
2. **Review in PRs**: Check for documentation updates
3. **Track major updates**: Note significant README changes in releases

## Examples

### Minimal README

```markdown
# Project Name

Brief description of what this project does.

## Installation

```bash
npm install project-name
```

## Usage

```javascript
import { feature } from 'project-name';

feature.doSomething();
```

## License

MIT
```

### Comprehensive README

```markdown
# TaskFlow API

A high-performance task management API built with FastAPI, providing real-time task tracking, team collaboration, and automated workflow orchestration.

**Status**: ✅ Stable

## Tech Stack

**Backend**: Python 3.11+, FastAPI 0.104+, SQLAlchemy 2.0+, PostgreSQL 15+
**Infrastructure**: Docker, AWS ECS, Terraform
**Development**: Poetry, Ruff, Pytest, MyPy

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (for local development)

## Quick Start

```bash
# Clone and start
git clone https://github.com/username/taskflow.git
cd taskflow
cp .env.example .env
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

## Usage

**API Documentation**: http://localhost:8000/docs

**Create task**:
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Complete README"}'
```

## Project Structure

```
taskflow/
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

See [Development Guide](docs/DEVELOPMENT.md) for details.

## Deployment

```bash
terraform apply   # Deploy infrastructure
./scripts/deploy.sh  # Deploy application
```

See [Deployment Guide](docs/DEPLOYMENT.md).

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT - see [LICENSE](LICENSE) file.
```

## Validation Checklist

Use this checklist to verify README completeness:

- [ ] Project title and clear description
- [ ] Tech stack documented
- [ ] Prerequisites listed with versions
- [ ] Installation instructions tested
- [ ] Usage examples included
- [ ] Project structure documented
- [ ] Development guidelines provided
- [ ] All code examples tested
- [ ] Links working and current
- [ ] Formatting consistent
- [ ] Free of temporal language
- [ ] Free of typos and errors

## Next Steps

- **Use template**: Start with .ai/templates/README.template
- **Follow structure**: Include all essential sections
- **Test instructions**: Verify all commands work
- **Review examples**: Study examples in this document
- **Maintain regularly**: Keep README current with code changes
- **Link to details**: Use README as entry point to detailed docs
