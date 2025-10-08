# How to: Debug Failing Hooks

**Purpose**: Troubleshooting guide for diagnosing and fixing pre-commit hook failures in Docker environments

**Scope**: Common hook failures, Docker container issues, configuration problems, and systematic debugging approaches

**Overview**: This guide provides systematic approaches to debugging pre-commit hook failures. Covers understanding
    hook output, testing hooks in isolation, Docker container troubleshooting, configuration validation, common
    failure patterns (container not found, command not found, permission errors, timeout issues), and resolution
    strategies. Includes debugging workflows, verbose output interpretation, and when to skip hooks. Applicable
    to Docker-first development with Python, TypeScript, and custom validation hooks.

**Dependencies**: Pre-commit framework, Docker, Docker Compose, .pre-commit-config.yaml, linting containers

**Exports**: Debugging strategies, problem resolution procedures, validated working hooks

**Related**: how-to-install-pre-commit.md, how-to-add-custom-hook.md, PRE_COMMIT_STANDARDS.md

**Implementation**: Step-by-step debugging procedures with examples and resolution strategies

---

## Quick Diagnosis

Start with these quick checks:

```bash
# 1. Check if pre-commit is installed
pre-commit --version

# 2. Check if hooks are installed
ls -la .git/hooks/pre-commit .git/hooks/pre-push

# 3. Check if Docker containers are running
docker ps | grep linter

# 4. Run specific failing hook
pre-commit run <hook-id> --all-files --verbose
```

---

## Understanding Hook Output

### Successful Hook Output

```
Prevent commits to main branch...............................Passed
Auto-fix linting issues......................................Passed
Ruff (Python format + lint)..................................Passed
MyPy (Python type checking)..................................Passed
```

**Indicators**:
- `Passed` status
- No error messages
- Exit code 0

### Failed Hook Output

```
Prevent commits to main branch...............................Failed
- hook id: no-commit-to-main
- exit code: 1

❌ Direct commits to main/master branch are not allowed! Create a feature branch instead.
```

**Indicators**:
- `Failed` status
- Hook ID shown
- Exit code (non-zero)
- Error message(s)

### Skipped Hook Output

```
Ruff (Python format + lint)..................................Skipped
```

**Indicators**:
- `Skipped` status
- Hook didn't run (no matching files)

---

## Debugging Workflow

### Step 1: Identify the Failing Hook

Run all hooks to see which ones fail:

```bash
pre-commit run --all-files

# Output shows failed hooks:
# Ruff (Python format + lint)..................................Failed
```

### Step 2: Run Hook in Isolation

Run only the failing hook with verbose output:

```bash
pre-commit run <hook-id> --all-files --verbose

# Example:
pre-commit run python-ruff --all-files --verbose

# Verbose output shows:
# - Full command executed
# - All output from command
# - Exit code
```

### Step 3: Test Hook Command Directly

Extract the command from `.pre-commit-config.yaml` and run it directly:

```bash
# Find the hook in .pre-commit-config.yaml
grep -A 10 "id: python-ruff" .pre-commit-config.yaml

# Copy the entry command and run it
bash -c 'files=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.py$" | grep -E "^(app|tools)/" || true); if [ -n "$files" ]; then make lint-ensure-containers >/dev/null 2>&1; docker exec <container> ruff check $files; fi'
```

### Step 4: Break Down the Command

Test each part of the command separately:

```bash
# 1. Check file detection
files=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.py$" | grep -E "^(app|tools)/" || true)
echo "Files: $files"

# 2. Check container is running
docker ps | grep linter

# 3. Check command works in container
docker exec <container> ruff --version

# 4. Run command on specific file
docker exec <container> ruff check app/main.py
```

### Step 5: Review and Fix

Based on findings, fix the issue:
- Missing container → Start containers
- Command not found → Install tool in container
- Permission error → Check file permissions
- Configuration error → Fix `.pre-commit-config.yaml`

---

## Common Issues and Solutions

### Issue 1: Docker Container Not Found

**Symptoms**:
```
Error: No such container: durable-code-python-linter-main
```

**Diagnosis**:
```bash
# Check running containers
docker ps

# Check if container name matches
docker ps | grep linter
```

**Solutions**:

**Solution A: Start containers**
```bash
# Start linting containers
make lint-ensure-containers

# Or start all containers
docker compose up -d

# Verify containers are running
docker ps | grep linter
```

**Solution B: Fix container name in configuration**

Check your container naming pattern:
```bash
# Get actual container name
docker ps --format '{{.Names}}' | grep linter

# Example output:
# myproject-python-linter-main
```

Update `.pre-commit-config.yaml` with correct name:
```yaml
entry: bash -c '... docker exec myproject-python-linter-main ruff check $files'
```

**Solution C: Use docker-compose service name**
```yaml
entry: bash -c '... docker compose exec python-linter ruff check $files'
```

### Issue 2: Command Not Found

**Symptoms**:
```
bash: ruff: command not found
```

**Diagnosis**:
```bash
# Check if tool exists in container
docker exec <container> which ruff

# Check tool version
docker exec <container> ruff --version
```

**Solutions**:

**Solution A: Install tool in container**

Add tool to container's requirements:
```dockerfile
# In Dockerfile
RUN pip install ruff
```

Rebuild container:
```bash
docker compose build python-linter
docker compose up -d python-linter
```

**Solution B: Use correct tool name**

Check available tools:
```bash
docker exec <container> ls /usr/local/bin/
```

Update hook to use correct name.

### Issue 3: Makefile Target Not Found

**Symptoms**:
```
make: *** No rule to make target 'lint-fix'. Stop.
```

**Diagnosis**:
```bash
# Check Makefile exists
ls -la Makefile

# Check for target
grep "lint-fix:" Makefile
```

**Solutions**:

Add missing target to Makefile:
```makefile
lint-fix:
	docker exec <container> ruff format .
	docker exec <container> ruff check --fix .

lint-ensure-containers:
	docker compose up -d python-linter js-linter

lint-all:
	docker exec <container> ruff check .
	docker exec <container> flake8 .
	docker exec <container> mypy .
```

Test target:
```bash
make lint-fix
```

### Issue 4: Permission Denied

**Symptoms**:
```
Permission denied: '/workspace/app/main.py'
```

**Diagnosis**:
```bash
# Check file permissions
ls -la app/main.py

# Check container user
docker exec <container> whoami
```

**Solutions**:

**Solution A: Fix file permissions**
```bash
chmod 644 app/main.py
```

**Solution B: Run container as correct user**

Update docker-compose.yml:
```yaml
services:
  python-linter:
    user: "${UID}:${GID}"
```

**Solution C: Fix volume mount permissions**

Check docker-compose.yml:
```yaml
services:
  python-linter:
    volumes:
      - .:/workspace:rw  # Read-write access
```

### Issue 5: File Not Found

**Symptoms**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'app/main.py'
```

**Diagnosis**:
```bash
# Check file exists locally
ls -la app/main.py

# Check file exists in container
docker exec <container> ls -la /workspace/app/main.py

# Check working directory
docker exec <container> pwd
```

**Solutions**:

**Solution A: Fix working directory in hook**
```yaml
entry: bash -c 'docker exec <container> bash -c "cd /workspace && ruff check app/main.py"'
```

**Solution B: Use absolute paths**
```yaml
entry: bash -c 'docker exec <container> ruff check /workspace/app/main.py'
```

**Solution C: Check volume mount**

In docker-compose.yml:
```yaml
services:
  python-linter:
    volumes:
      - .:/workspace  # Mount current directory
```

### Issue 6: Hook Times Out

**Symptoms**:
```
Hook 'python-mypy' timed out after 60 seconds
```

**Diagnosis**:
```bash
# Run hook with time measurement
time pre-commit run python-mypy --all-files
```

**Solutions**:

**Solution A: Increase timeout**

In `.pre-commit-config.yaml`:
```yaml
- id: python-mypy
  name: MyPy (Python type checking)
  entry: bash -c '...'
  language: system
  pass_filenames: false
  stages: [pre-commit]
  timeout: 120  # Increase to 120 seconds
```

**Solution B: Optimize check**

Only check changed files:
```yaml
entry: bash -c 'files=$(git diff --cached --name-only | grep .py || true); if [ -n "$files" ]; then docker exec <container> mypy $files; fi'
```

**Solution C: Move to pre-push**

Move expensive checks to pre-push:
```yaml
- id: python-mypy
  stages: [pre-push]  # Run on push, not commit
```

### Issue 7: Branch Protection Not Working

**Symptoms**:
Can commit directly to main branch without error.

**Diagnosis**:
```bash
# Check current branch
git branch --show-current

# Run branch protection hook manually
pre-commit run no-commit-to-main --all-files
```

**Solutions**:

**Solution A: Check hook is installed**
```bash
# Reinstall hooks
pre-commit install
```

**Solution B: Check hook configuration**

Verify in `.pre-commit-config.yaml`:
```yaml
- id: no-commit-to-main
  name: Prevent commits to main branch
  entry: bash -c 'branch=$(git rev-parse --abbrev-ref HEAD); if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then echo "❌ Direct commits to main/master branch are not allowed!"; exit 1; fi'
  language: system
  pass_filenames: false
  stages: [pre-commit]
  always_run: true  # Important: always run
```

**Solution C: Test manually**
```bash
git checkout main
pre-commit run no-commit-to-main
# Should fail with error message
```

### Issue 8: Auto-fix Not Working

**Symptoms**:
Hooks fail even after running `make lint-fix`.

**Diagnosis**:
```bash
# Run auto-fix manually
make lint-fix

# Check for errors
echo $?  # Should be 0 if successful

# Run hooks again
pre-commit run --all-files
```

**Solutions**:

**Solution A: Check make lint-fix works**
```bash
# Test make target
make lint-fix

# Check what it does
grep -A 10 "lint-fix:" Makefile
```

**Solution B: Ensure files are staged**

Auto-fix hook should stage changes:
```yaml
- id: make-lint-fix
  entry: bash -c 'make lint-fix && git add -u'  # git add -u is important
  language: system
  pass_filenames: false
  stages: [pre-commit]
```

**Solution C: Check tool configurations**

Ensure ruff/prettier configurations don't conflict:
```bash
# Check ruff config
cat pyproject.toml | grep -A 20 "\[tool.ruff\]"

# Check prettier config
cat .prettierrc.json
```

---

## Debugging Docker Issues

### Check Container Status

```bash
# List all containers
docker ps -a

# Check specific container
docker ps --filter "name=linter"

# Check container logs
docker logs <container-name>
```

### Test Container Interactively

```bash
# Enter container
docker exec -it <container-name> bash

# Inside container:
pwd
ls -la
which ruff
ruff --version

# Test command
ruff check app/main.py

# Exit
exit
```

### Restart Containers

```bash
# Restart all containers
docker compose restart

# Restart specific container
docker compose restart python-linter

# Rebuild and restart
docker compose up -d --build
```

### Check Volume Mounts

```bash
# Inspect container
docker inspect <container-name> | grep -A 10 "Mounts"

# Check if files are accessible
docker exec <container> ls -la /workspace/
```

---

## Advanced Debugging

### Enable Pre-commit Debug Mode

```bash
# Set environment variable
export PRE_COMMIT_DEBUG=1

# Run hooks
pre-commit run --all-files

# Shows detailed execution information
```

### Trace Hook Execution

Add debug output to hook:
```yaml
- id: debug-hook
  entry: bash -c 'set -x; your-command; set +x'  # set -x enables tracing
  language: system
```

### Check Pre-commit Cache

```bash
# Clear pre-commit cache
pre-commit clean

# Reinstall hooks
pre-commit install --install-hooks

# Run again
pre-commit run --all-files
```

---

## When to Skip Hooks

### Legitimate Reasons to Skip

✅ **Emergency hotfixes**:
```bash
git commit --no-verify -m "Emergency: Fix production outage"
```

✅ **Infrastructure failures**:
```bash
# Docker is down, need to commit urgently
git commit --no-verify -m "Commit before Docker restart"
```

✅ **Pre-push skip for emergency push**:
```bash
PRE_PUSH_SKIP=1 git push
```

### Follow-up Required

After skipping hooks:
1. Fix the issues immediately
2. Run hooks manually: `pre-commit run --all-files`
3. Create follow-up commit with fixes
4. Document why skip was necessary

### Never Skip For

❌ "I'm in a hurry"
❌ "Tests are flaky"
❌ "Linter is wrong"
❌ "I'll fix it later"

---

## Systematic Debugging Checklist

When a hook fails, go through this checklist:

- [ ] **Run hook in isolation**: `pre-commit run <hook-id> --verbose --all-files`
- [ ] **Check Docker containers running**: `docker ps | grep linter`
- [ ] **Test Docker container access**: `docker exec <container> echo "test"`
- [ ] **Check tool exists in container**: `docker exec <container> which <tool>`
- [ ] **Test tool directly**: `docker exec <container> <tool> --version`
- [ ] **Check file detection**: Test file glob patterns
- [ ] **Check Makefile targets**: `grep <target> Makefile`
- [ ] **Test command manually**: Copy entry command and run it
- [ ] **Check configuration syntax**: `cat .pre-commit-config.yaml`
- [ ] **Clear cache and retry**: `pre-commit clean && pre-commit install`
- [ ] **Review recent changes**: `git log -p .pre-commit-config.yaml`

---

## Getting Help

### Information to Gather

When asking for help, provide:

1. **Hook configuration**:
   ```bash
   grep -A 10 "id: <hook-id>" .pre-commit-config.yaml
   ```

2. **Verbose output**:
   ```bash
   pre-commit run <hook-id> --all-files --verbose 2>&1 | tee hook-output.log
   ```

3. **Docker status**:
   ```bash
   docker ps
   docker logs <container-name>
   ```

4. **Environment info**:
   ```bash
   pre-commit --version
   docker --version
   docker compose version
   ```

### Check Documentation

- Pre-commit framework: https://pre-commit.com/
- Project standards: `.ai/docs/PRE_COMMIT_STANDARDS.md`
- Installation guide: `.ai/howtos/how-to-install-pre-commit.md`
- Custom hooks: `.ai/howtos/how-to-add-custom-hook.md`

---

## Prevention

### Best Practices to Avoid Issues

1. **Test hooks after changes**:
   ```bash
   pre-commit run --all-files
   ```

2. **Keep containers running**:
   ```bash
   docker compose up -d
   ```

3. **Run lint-fix before committing**:
   ```bash
   make lint-fix
   git add -u
   git commit
   ```

4. **Update hooks regularly**:
   ```bash
   pre-commit autoupdate
   pre-commit run --all-files  # Test after update
   ```

5. **Document custom hooks**:
   Add comments to `.pre-commit-config.yaml`

6. **Version control configuration**:
   Commit `.pre-commit-config.yaml` changes

---

## Summary

### Quick Fix Reference

| Issue | Quick Fix |
|-------|-----------|
| Container not found | `make lint-ensure-containers` |
| Command not found | Check tool exists in container |
| Permission denied | Check file permissions |
| Hook times out | Move to pre-push or increase timeout |
| Hooks don't run | `pre-commit install` |
| Auto-fix not working | Check `make lint-fix && git add -u` |
| Branch protection fails | Check `always_run: true` |

### Debugging Steps

1. Run hook in isolation with `--verbose`
2. Test Docker container and tools
3. Break down hook command and test parts
4. Fix identified issue
5. Test again with `pre-commit run --all-files`
6. Commit configuration changes

### Remember

- Most issues are Docker or configuration related
- Verbose output is your friend
- Test commands directly to isolate problems
- Document solutions for team
- Only skip hooks for genuine emergencies

---

## Next Steps

- **Review standards**: `.ai/docs/PRE_COMMIT_STANDARDS.md`
- **Installation guide**: `.ai/howtos/how-to-install-pre-commit.md`
- **Custom hooks**: `.ai/howtos/how-to-add-custom-hook.md`
- **Share solutions**: Document fixes for team
