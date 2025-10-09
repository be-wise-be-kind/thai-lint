# How to: Install Pre-commit Hooks

**Purpose**: Step-by-step guide to install and configure pre-commit hooks framework with Docker integration

**Scope**: Local development environment setup for automated code quality enforcement

**Overview**: This guide walks through installing the pre-commit framework, configuring hooks for your project,
    and integrating with Docker-based linting containers. Covers prerequisites verification, framework
    installation, configuration copying, git hooks installation, container setup, and testing. Includes
    troubleshooting common installation issues and validation steps. Applicable to Python, TypeScript, and
    multi-language projects using Docker-first development patterns.

**Dependencies**: Git repository, Docker, Docker Compose, Python or Node.js, project Makefile with linting targets

**Exports**: Installed pre-commit framework, configured git hooks, working pre-commit setup

**Related**: how-to-add-custom-hook.md, how-to-debug-failing-hooks.md, PRE_COMMIT_STANDARDS.md

**Implementation**: Template-based configuration with manual installation and testing steps

---

## Prerequisites

Before installing pre-commit hooks, verify:

### 1. Git Repository Initialized

```bash
# Check if git repository exists
git rev-parse --git-dir

# Expected output: .git
```

If not initialized:
```bash
git init
```

### 2. Docker and Docker Compose Running

```bash
# Check Docker is running
docker ps

# Check Docker Compose is available
docker compose version

# Expected: Docker Compose version v2.x.x
```

If Docker is not running, start Docker Desktop or Docker daemon.

### 3. Project Has Makefile with Linting Targets

```bash
# Check Makefile exists
ls -la Makefile

# Check for required targets
grep -E "lint-fix:|lint-all:|lint-ensure-containers:" Makefile
```

Required Makefile targets:
- `lint-fix`: Auto-fix linting issues
- `lint-all`: Run all linters
- `lint-ensure-containers`: Ensure linting containers are running
- `test-all`: Run all tests (for pre-push hooks)

### 4. Python or Node.js Installed (for pre-commit framework)

```bash
# Check Python
python --version
# or
python3 --version

# Check pip
pip --version
# or
pip3 --version
```

---

## Installation Steps

### Step 1: Copy Pre-commit Configuration Template

Copy the pre-commit configuration template to your project root:

```bash
# From the ai-projen repository root
cp plugins/standards/pre-commit-hooks/ai-content/templates/.pre-commit-config.yaml.template .pre-commit-config.yaml

# Verify the file was copied
ls -la .pre-commit-config.yaml
```

**Expected result**: `.pre-commit-config.yaml` file in your project root.

### Step 2: Review and Customize Configuration

Open `.pre-commit-config.yaml` and review the hooks:

```bash
# View the configuration
cat .pre-commit-config.yaml
```

**Key sections to review**:
1. **Branch protection**: Adjust protected branches if needed
2. **Python hooks**: Enabled if you have Python files
3. **TypeScript hooks**: Enabled if you have TypeScript files
4. **Docker container names**: Update if your container names differ

**Common customizations**:

Add more protected branches:
```yaml
- id: no-commit-to-main
  entry: bash -c 'branch=$(git rev-parse --abbrev-ref HEAD); if [ "$branch" = "main" ] || [ "$branch" = "develop" ]; then ...'
```

Adjust file paths for your project:
```yaml
# If your Python code is in a different directory
files: ^src/.*\.py$
```

### Step 3: Install Pre-commit Framework

Install pre-commit using pip:

```bash
# Using pip
pip install pre-commit

# Or using pip3
pip3 install pre-commit

# Verify installation
pre-commit --version

# Expected output: pre-commit 3.x.x
```

**Alternative installation methods**:

Using Homebrew (macOS):
```bash
brew install pre-commit
```

Using conda:
```bash
conda install -c conda-forge pre-commit
```

### Step 4: Install Git Hooks

Install the pre-commit and pre-push hooks into your git repository:

```bash
# Install pre-commit hooks (runs on 'git commit')
pre-commit install

# Expected output: pre-commit installed at .git/hooks/pre-commit

# Install pre-push hooks (runs on 'git push')
pre-commit install --hook-type pre-push

# Expected output: pre-commit installed at .git/hooks/pre-push
```

**Verify installation**:
```bash
# Check that hooks were installed
ls -la .git/hooks/pre-commit .git/hooks/pre-push

# Check hook contents
cat .git/hooks/pre-commit
# Should contain reference to pre-commit framework
```

### Step 5: Ensure Docker Linting Containers Are Running

Pre-commit hooks execute in Docker containers. Ensure containers are running:

```bash
# Start linting containers using Makefile
just lint-ensure-containers

# Or start all containers
docker compose up -d

# Verify containers are running
docker ps | grep linter

# Expected: Python linting container and/or JS linting container
```

**Container naming**: The template uses dynamic container names based on branch:
```bash
durable-code-python-linter-<branch-name>
durable-code-js-linter-<branch-name>
```

If your containers have different names, update the `.pre-commit-config.yaml` file.

### Step 6: Test Pre-commit Hooks

Test the hooks on your existing codebase:

```bash
# Run all hooks on all files (first run downloads tools and may take time)
pre-commit run --all-files

# Expected: Hooks run on all files, may show warnings or errors
```

**First run notes**:
- First run is slower (tools are downloaded and cached)
- May show many errors on existing code
- Subsequent runs are much faster

**Address failures**:
```bash
# Auto-fix issues first
just lint-fix

# Add fixed files
git add -u

# Try again
pre-commit run --all-files
```

### Step 7: Test Commit Workflow

Test the complete commit workflow on a feature branch:

```bash
# Create a test feature branch
git checkout -b test-pre-commit-install

# Create a test file
echo "# Test Pre-commit Hooks" > test-precommit.md

# Stage the file
git add test-precommit.md

# Commit (hooks run automatically)
git commit -m "Test pre-commit hooks installation"

# Expected: Hooks run successfully, commit completes
```

**If commit succeeds**:
```
✅ Pre-commit hooks are working correctly!
```

**If commit fails**:
- Review the hook output
- Fix any issues
- Try committing again

**Clean up test**:
```bash
# Go back to main branch
git checkout main

# Delete test branch
git branch -D test-pre-commit-install

# Remove test file if it exists
rm -f test-precommit.md
```

### Step 8: Test Branch Protection

Verify that branch protection is working:

```bash
# Switch to main branch
git checkout main

# Try to commit directly to main (should fail)
echo "# Test" > test-branch-protection.md
git add test-branch-protection.md
git commit -m "Test direct commit to main"

# Expected output:
# ❌ Direct commits to main/master branch are not allowed! Create a feature branch instead.

# Clean up
rm -f test-branch-protection.md
```

If branch protection works, you'll see the error message and commit will be blocked.

---

## Post-Installation Configuration

### Copy Documentation to .ai Folder

Copy pre-commit documentation to your project's .ai folder:

```bash
# Create directories if needed
mkdir -p .ai/docs
mkdir -p .ai/howtos

# Copy standards documentation
cp plugins/standards/pre-commit-hooks/ai-content/standards/PRE_COMMIT_STANDARDS.md .ai/docs/

# Copy how-to guides
cp plugins/standards/pre-commit-hooks/ai-content/howtos/how-to-install-pre-commit.md .ai/howtos/
cp plugins/standards/pre-commit-hooks/ai-content/howtos/how-to-add-custom-hook.md .ai/howtos/
cp plugins/standards/pre-commit-hooks/ai-content/howtos/how-to-debug-failing-hooks.md .ai/howtos/

echo "✅ Documentation copied to .ai folder"
```

### Update .ai/index.yaml

Add pre-commit hooks reference to `.ai/index.yaml`:

```yaml
standards:
  pre-commit-hooks:
    description: "Pre-commit hooks for automated code quality enforcement"
    documentation:
      - path: "docs/PRE_COMMIT_STANDARDS.md"
        description: "Pre-commit hooks standards and configuration"
    howtos:
      - path: "howto/how-to-install-pre-commit.md"
        description: "Install and configure pre-commit hooks"
      - path: "howto/how-to-add-custom-hook.md"
        description: "Create custom pre-commit hooks"
      - path: "howto/how-to-debug-failing-hooks.md"
        description: "Debug failing pre-commit hooks"
    configuration:
      - path: ".pre-commit-config.yaml"
        description: "Pre-commit hooks configuration"
```

---

## Validation

After installation, validate that everything is working:

### Check Installation

```bash
# 1. Pre-commit framework installed
pre-commit --version

# 2. Git hooks installed
ls -la .git/hooks/pre-commit .git/hooks/pre-push

# 3. Configuration file exists
ls -la .pre-commit-config.yaml

# 4. Docker containers running
docker ps | grep linter

# 5. Makefile targets available
grep -E "lint-fix:|lint-all:" Makefile
```

### Run Full Test

```bash
# Run all hooks on all files
pre-commit run --all-files

# Should complete without errors (or with expected errors to fix)
```

### Test Complete Workflow

```bash
# 1. Create feature branch
git checkout -b feature/test-workflow

# 2. Make a change
echo "print('Hello, World!')" > app/test.py
git add app/test.py

# 3. Commit (hooks run)
git commit -m "Add test file"

# 4. Push (pre-push hooks run)
git push origin feature/test-workflow

# 5. Clean up
git checkout main
git branch -D feature/test-workflow
rm -f app/test.py
```

---

## Troubleshooting

### Issue: Pre-commit not found

**Symptoms**: `pre-commit: command not found`

**Solution**: Install pre-commit framework
```bash
pip install pre-commit
# or
pip3 install pre-commit
```

### Issue: Hooks not running on commit

**Symptoms**: Commit succeeds without running hooks

**Solution**: Install git hooks
```bash
pre-commit install
pre-commit install --hook-type pre-push
```

### Issue: Docker container not found

**Symptoms**: `Error: No such container: durable-code-python-linter-...`

**Solution**: Start Docker containers
```bash
just lint-ensure-containers
# or
docker compose up -d
```

### Issue: Hooks fail with "make: command not found"

**Symptoms**: `make: lint-fix: command not found`

**Solution**: Ensure Makefile has required targets
```bash
# Check Makefile exists
ls -la Makefile

# Add missing targets (example):
cat >> Makefile << 'EOF'
lint-fix:
	docker exec <container> ruff format .
	docker exec <container> ruff check --fix .

lint-all:
	docker exec <container> ruff check .
	docker exec <container> flake8 .

lint-ensure-containers:
	docker compose up -d
EOF
```

### Issue: Hooks are too slow

**Symptoms**: Hooks take > 30 seconds on small changes

**Solution**:
1. First run is slower (tools downloaded and cached)
2. Subsequent runs should be faster (3-10s)
3. Ensure Docker containers are already running:
   ```bash
   just lint-ensure-containers
   ```

### Issue: Want to skip hooks temporarily

**Symptoms**: Need to commit urgently without running hooks

**Solution**: Use `--no-verify` (emergency only)
```bash
git commit --no-verify -m "Emergency fix"
```

**Warning**: Only use for genuine emergencies. Skipped commits should be fixed immediately.

---

## Best Practices

### Development Workflow

1. **Always work on feature branches**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Run lint-fix before committing**
   ```bash
   just lint-fix
   git add -u
   git commit -m "Your message"
   ```

3. **Commit frequently with small changes**
   - Smaller commits = faster hooks
   - Easier to fix issues

4. **Review hook output**
   - Understand why hooks failed
   - Don't skip without good reason

### Container Management

1. **Keep containers running during development**
   ```bash
   docker compose up -d
   ```

2. **Restart containers if hooks fail mysteriously**
   ```bash
   docker compose restart
   ```

3. **Check container logs if issues persist**
   ```bash
   docker logs <container-name>
   ```

### Hook Maintenance

1. **Update hooks regularly**
   ```bash
   pre-commit autoupdate
   ```

2. **Test after updates**
   ```bash
   pre-commit run --all-files
   ```

3. **Commit hook configuration changes**
   ```bash
   git add .pre-commit-config.yaml
   git commit -m "Update pre-commit hooks"
   ```

---

## Next Steps

After successful installation:

1. **Read the standards document**: `.ai/docs/PRE_COMMIT_STANDARDS.md`
2. **Learn to add custom hooks**: `.ai/howtos/how-to-add-custom-hook.md`
3. **Learn to debug hooks**: `.ai/howtos/how-to-debug-failing-hooks.md`
4. **Share with team**: Send this guide to other developers
5. **Integrate with CI/CD**: Run same hooks in GitHub Actions

---

## Summary

✅ **Installation Complete Checklist**:

- [ ] Git repository initialized
- [ ] Docker and Docker Compose running
- [ ] Makefile with linting targets present
- [ ] Pre-commit framework installed (`pre-commit --version`)
- [ ] `.pre-commit-config.yaml` copied and reviewed
- [ ] Git hooks installed (`pre-commit install`)
- [ ] Pre-push hooks installed (`pre-commit install --hook-type pre-push`)
- [ ] Docker linting containers running
- [ ] Hooks tested on all files (`pre-commit run --all-files`)
- [ ] Commit workflow tested on feature branch
- [ ] Branch protection tested (cannot commit to main)
- [ ] Documentation copied to `.ai/` folder
- [ ] `.ai/index.yaml` updated

**You're ready to use pre-commit hooks!** 🎉

Every commit will now automatically:
- Prevent commits to main/master
- Auto-fix formatting and style issues
- Run language-specific linters
- Check for security vulnerabilities
- Enforce code quality standards

Every push will:
- Run comprehensive linting on all code
- Run all tests
- Ensure code quality before sharing
