# python-cli Meta-Plugin Installation - Progress Tracker

**Purpose**: AI agent handoff document for systematic installation of python-cli meta-plugin

**Scope**: Orchestrated installation of 7 atomic plugins with user-controlled options

**Overview**: This roadmap breaks down the python-cli meta-plugin installation into 7 separate PRs,
    each focused on a single phase. This prevents agents from rushing, skipping steps, or taking shortcuts.
    Each PR must be completed and validated before proceeding to the next. User questions are asked upfront
    in PR0, and user choices determine which optional PRs are executed.

**Dependencies**: ai-projen framework, target repository initialized with git

**Exports**: Complete python-cli installation with all infrastructure and application code

**Related**: python-cli/AGENT_INSTRUCTIONS.md for detailed phase instructions

**Implementation**: Sequential PR execution with validation checkpoints between each phase

---

## 🤖 How This Roadmap Works

**CRITICAL**: This is NOT a normal feature roadmap. This is a **meta-plugin installation roadmap** that:

1. **PR0**: Agent asks ALL user questions upfront and records answers
2. **PR1-PR7**: Agent executes one phase per PR, cannot skip or combine phases
3. **Validation**: Each PR must pass validation before moving to next PR
4. **User Control**: User decides which optional PRs to execute based on PR0 answers

**Why separate PRs?**
- Prevents agents from rushing or taking shortcuts
- Natural stopping points between phases
- Clear failure isolation (know exactly which phase broke)
- Forces sequential execution (can't skip ahead)

---

## 📍 Current Status

**Current PR**: PR3 (Infrastructure)
**Installation Target**: /home/stevejackson/Projects/thai-lint
**Project Name**: thai-lint

---

## 🎯 Next PR to Implement

### ➡️ START HERE: PR3 - Install Docker and CI/CD

**What this PR does**: Install infrastructure/docker and infrastructure/github-actions plugins. Creates Dockerfile, docker-compose.yml, and GitHub Actions workflows for test, lint, build.

**Pre-flight Checklist**:
- [ ] Previous PR is marked complete in this document
- [ ] Previous PR's validation passed
- [ ] No errors or warnings from previous PR
- [ ] Git branch created for this PR: `feature/{{BRANCH_NAME}}`

**After completing this PR**:
1. Run validation commands listed in PR instructions
2. Mark PR as ✅ Complete in "PR Status Dashboard" below
3. **Add commit hash to Notes column**: Get short hash with `git log --oneline -1`
   - Format: "Description (commit abc1234)"
4. Update "Current PR" to next PR number
5. Commit this updated PROGRESS_TRACKER.md
6. Merge PR branch to main
7. User will then request next PR execution

---

## Overall Progress

**Total Completion**: 29% (2/7 PRs completed)

```
[████░░░░░░░░░░] 29%
```

---

## User Choices (from PR0)

**Collected in PR0 - Planning Phase**:
- **Docker Infrastructure**: {{DOCKER_CHOICE}} (yes/no)
- **UI Scaffold**: {{UI_SCAFFOLD_CHOICE}} (yes/no)
- **Terraform AWS Deployment**: {{TERRAFORM_CHOICE}} (yes/no)

**Impact on PR execution**:
- If Docker = no: Skip PR3, use host-based Makefiles
- If UI Scaffold = no: Skip PR6
- If Terraform = no: Skip PR7

---

## PR Status Dashboard

| PR | Phase | Title | Status | Dependencies | Notes |
|----|-------|-------|--------|--------------|-------|
| PR0 | Planning | Create roadmap | ✅ Complete | None | MUST be completed first |
| PR1 | Foundation | Install foundation/ai-folder plugin | ✅ Complete | PR0 complete | Foundation installed (commit 28d26f0) |
| PR2 | Languages | Install Python plugin | ✅ Complete | PR1 complete | Python tooling installed (commit 9aeae69) |
| PR3 | Infrastructure | Install Docker + CI/CD plugins | 🔴 Not Started | PR2 complete | Creates docker-compose.yml |
| PR4 | Standards | Install security, docs, pre-commit plugins | 🔴 Not Started | PR3 complete | Sets up quality gates |
| PR5 | Application | Copy CLI code, configure, install deps | 🔴 Not Started | PR4 complete | Installs app code |
| PR6 | Finalization | Validate setup, create AGENTS.md | 🔴 Not Started | PR5 complete | Final validation |

### Status Legend
- 🔴 Not Started
- 🟡 In Progress
- ✅ Complete
- ⏭️ Skipped (user chose "no")

---

## Detailed PR Instructions

### PR0: Planning Phase (Ask User Questions)

**Objective**: Collect all user choices upfront so agent knows which PRs to execute

**Steps**:
1. Present Docker infrastructure question to user
2. Present UI scaffold question to user
3. Present Terraform deployment question to user
4. Record answers in "User Choices" section above
5. Update PR status dashboard based on answers (mark skipped PRs)
6. Create this PROGRESS_TRACKER.md in `.roadmap/python-cli-install/`

**Validation**:
```bash
# Verify roadmap created
test -f .roadmap/python-cli-install/PROGRESS_TRACKER.md && echo "✅ Roadmap created"

# Verify user choices recorded
grep "DOCKER_CHOICE" .roadmap/python-cli-install/PROGRESS_TRACKER.md && echo "✅ Choices recorded"
```

**Mark complete when**: All 3 questions answered, roadmap file created with user choices

---

### PR1: Install Foundation Plugin

**Objective**: Create `.ai/` directory structure for AI navigation

**Key Steps**:
1. Create feature branch: `git checkout -b feature/pr1-foundation`
2. Create installation directory:
   ```bash
   mkdir -p {{FOUNDATION_INSTALL_PATH}}
   ```
3. Execute foundation plugin:
   ```
   Follow: plugins/foundation/ai-folder/AGENT_INSTRUCTIONS.md
     with INSTALL_PATH={{FOUNDATION_INSTALL_PATH}}
   ```
4. Validate .ai/ folder exists with index.yaml, layout.yaml
5. Update this PROGRESS_TRACKER.md: mark PR1 as ✅ Complete

**Validation**:
```bash
test -d {{FOUNDATION_INSTALL_PATH}}.ai && echo "✅ .ai folder created"
test -f {{FOUNDATION_INSTALL_PATH}}.ai/index.yaml && echo "✅ index.yaml exists"
test -f {{FOUNDATION_INSTALL_PATH}}.ai/layout.yaml && echo "✅ layout.yaml exists"
```

**Mark complete when**: All validation passes, PROGRESS_TRACKER updated

---

### PR2: Install Language Plugins

**Objective**: Install Python and TypeScript language tooling

**Key Steps**:
1. Create feature branch: `git checkout -b feature/pr2-languages`
2. Create language directories:
   ```bash
   mkdir -p {{PYTHON_INSTALL_PATH}}
   mkdir -p {{TYPESCRIPT_INSTALL_PATH}}
   ```
3. Install Python:
   ```
   Follow: plugins/languages/python/core/AGENT_INSTRUCTIONS.md
     with INSTALL_PATH={{PYTHON_INSTALL_PATH}}
   ```
4. Install TypeScript:
   ```
   Follow: plugins/languages/typescript/core/AGENT_INSTRUCTIONS.md
     with INSTALL_PATH={{TYPESCRIPT_INSTALL_PATH}}
   ```
5. Validate configuration files exist in correct locations
6. Update PROGRESS_TRACKER.md: mark PR2 as ✅ Complete

**Validation**:
```bash
# Verify configuration files created in subdirectories
test -f {{PYTHON_INSTALL_PATH}}pyproject.toml && echo "✅ pyproject.toml created"
test -f {{TYPESCRIPT_INSTALL_PATH}}package.json && echo "✅ package.json created"
test -f {{TYPESCRIPT_INSTALL_PATH}}tsconfig.json && echo "✅ tsconfig.json created"
test -f {{PYTHON_INSTALL_PATH}}.flake8 && echo "✅ Python linter configs created"

# Verify NO configuration files at root (critical check)
! test -f pyproject.toml && echo "✅ No root pyproject.toml"
! test -f package.json && echo "✅ No root package.json"

# Note: Poetry and npm should already be installed (verified in Prerequisites Check)
# Dependencies will be installed in PR5 when application structure exists
```

**Mark complete when**: All config files exist in correct locations, no root configs, PROGRESS_TRACKER updated

---

### PR3: Install Docker Infrastructure (Conditional)

**Objective**: Create Docker containerization with .docker/ folder and docker-compose files

**Condition**: Only execute if user chose "Docker Infrastructure = yes" in PR0

**Key Steps**:
1. Create feature branch: `git checkout -b feature/pr3-docker`
2. Execute Docker plugin:
   ```
   Follow: plugins/infrastructure/containerization/docker/AGENT_INSTRUCTIONS.md
     with LANGUAGES={{LANGUAGES}}
     with SERVICES={{SERVICES}}
     with INSTALL_PATH={{DOCKER_INSTALL_PATH}}
   ```
3. Validate .docker/ folder and docker-compose.yml exist
4. Update PROGRESS_TRACKER.md: mark PR3 as ✅ Complete or ⏭️ Skipped

**Validation**:
```bash
# Verify Docker infrastructure files created
test -d {{DOCKER_INSTALL_PATH}} && echo "✅ .docker folder created"
test -f {{DOCKER_INSTALL_PATH}}dockerfiles/Dockerfile.backend && echo "✅ Backend Dockerfile exists"
test -f {{DOCKER_INSTALL_PATH}}dockerfiles/Dockerfile.frontend && echo "✅ Frontend Dockerfile exists"
test -f {{DOCKER_INSTALL_PATH}}compose/lint.yml && echo "✅ Lint compose file exists"
test -f {{DOCKER_INSTALL_PATH}}compose/test.yml && echo "✅ Test compose file exists"

# Note: Docker Compose tool availability was verified in Prerequisites Check
```

**Mark complete when**: All validation passes (or marked Skipped if user chose "no")

---

### PR4: Install Standards Plugins

**Objective**: Install security, documentation, and pre-commit hook plugins

**Instructions**:
1. Follow `plugins/standards/security/AGENT_INSTRUCTIONS.md`
2. Follow `plugins/standards/documentation/AGENT_INSTRUCTIONS.md`
3. Follow `plugins/standards/pre-commit-hooks/AGENT_INSTRUCTIONS.md`

**Key Steps**:
1. Create feature branch: `git checkout -b feature/pr4-standards`
2. Execute security plugin installation
3. Execute documentation plugin installation
4. Execute pre-commit-hooks plugin installation
5. Update PROGRESS_TRACKER.md: mark PR4 as ✅ Complete

**Validation**:
```bash
test -f .pre-commit-config.yaml && echo "✅ Pre-commit hooks configured"
test -f .gitignore && grep -q "secrets" .gitignore && echo "✅ Security patterns added"
test -f .ai/docs/file-headers.md && echo "✅ Documentation standards added"
```

**Mark complete when**: All validation passes, PROGRESS_TRACKER updated

---

### PR5: Install Application Structure

**Objective**: Copy application code and configure for thai-lint

**Instructions**: Follow Phase 5 of `plugins/applications/python-cli/AGENT_INSTRUCTIONS.md`

**Key Steps**:
1. Create feature branch: `git checkout -b feature/pr5-application`
2. Create thai-lint-app/ wrapper directory
3. Copy application structure from plugin
4. Process template files (remove .template extensions)
5. Copy root-level Makefiles
6. Configure environment (.env.example → .env)
7. Install dependencies (poetry install, npm install)
8. Update PROGRESS_TRACKER.md: mark PR5 as ✅ Complete

**Validation**:
```bash
test -d thai-lint-app/backend && echo "✅ Backend structure exists"
test -d thai-lint-app/frontend && echo "✅ Frontend structure exists"
test -f Makefile && echo "✅ Makefile exists"
test -f .env && echo "✅ Environment configured"
cd thai-lint-app/backend && poetry install && echo "✅ Backend deps installed"
cd thai-lint-app/frontend && npm install && echo "✅ Frontend deps installed"
```

**Mark complete when**: All validation passes, dependencies installed

---

### PR6: Install UI Scaffold (Optional)

**Objective**: Add modern UI scaffold with hero banner and tab navigation

**Condition**: Only execute if user chose "UI Scaffold = yes" in PR0

**Instructions**: Follow Phase 6 of `plugins/applications/python-cli/AGENT_INSTRUCTIONS.md`

**Key Steps**:
1. Create feature branch: `git checkout -b feature/pr6-ui-scaffold`
2. Copy UI scaffold components
3. Process template files
4. Update App.tsx to use AppShell
5. Update PROGRESS_TRACKER.md: mark PR6 as ✅ Complete or ⏭️ Skipped

**Validation**:
```bash
test -f thai-lint-app/frontend/src/components/AppShell/AppShell.tsx && echo "✅ AppShell exists"
test -f thai-lint-app/frontend/src/pages/HomePage/HomePage.tsx && echo "✅ HomePage exists"
test -f thai-lint-app/frontend/src/config/tabs.config.ts && echo "✅ Tabs config exists"
```

**Mark complete when**: All validation passes (or marked Skipped)

---

### PR7: Install Terraform Infrastructure (Optional)

**Objective**: Add AWS deployment infrastructure with Terraform

**Condition**: Only execute if user chose "Terraform = yes" in PR0

**Instructions**: Follow Phase 7 of `plugins/applications/python-cli/AGENT_INSTRUCTIONS.md`

**Key Steps**:
1. Create feature branch: `git checkout -b feature/pr7-terraform`
2. Copy Terraform configuration
3. Copy infrastructure Makefile
4. Copy Terraform documentation
5. Update .ai/index.yaml with Terraform entries
6. Update PROGRESS_TRACKER.md: mark PR7 as ✅ Complete or ⏭️ Skipped

**Validation**:
```bash
test -d infra/terraform && echo "✅ Terraform directory exists"
test -f infra/Makefile.infra && echo "✅ Infrastructure Makefile exists"
test -f .ai/howtos/python-cli/how-to-manage-terraform-infrastructure.md && echo "✅ Terraform docs exist"
```

**Mark complete when**: All validation passes (or marked Skipped)

---

### PR8: Finalization & Validation

**Objective**: Run complete validation and create AGENTS.md

**Instructions**: Follow Phase 8 of `plugins/applications/python-cli/AGENT_INSTRUCTIONS.md`

**Key Steps**:
1. Create feature branch: `git checkout -b feature/pr8-finalize`
2. Copy validation script
3. Run complete setup validation
4. Copy AGENTS.md template
5. Update PROGRESS_TRACKER.md: mark PR8 as ✅ Complete
6. Mark entire roadmap as COMPLETE

**Validation**:
```bash
chmod +x ./scripts/validate-fullstack-setup.sh
./scripts/validate-fullstack-setup.sh && echo "✅ All validation passed"
test -f AGENTS.md && echo "✅ AGENTS.md exists"
```

**Mark complete when**: Validation script passes, AGENTS.md created

---

## Success Criteria

Installation is complete when:
- [ ] All required PRs are marked ✅ Complete
- [ ] All optional PRs are either ✅ Complete or ⏭️ Skipped based on user choices
- [ ] Validation script passes (PR8)
- [ ] AGENTS.md exists in repository root
- [ ] No errors or warnings

---

## Troubleshooting

### If a PR fails validation:
1. DO NOT proceed to next PR
2. Fix issues in current PR
3. Re-run validation
4. Only mark complete when validation passes

### If agent tries to combine PRs:
- This violates the roadmap approach
- Each PR MUST be separate
- Combining PRs defeats the purpose of preventing shortcuts

### If user wants to skip a required PR:
- Required PRs (1-5, 8) cannot be skipped
- Optional PRs (6, 7) can only be skipped if user chose "no" in PR0

---

## Notes for AI Agents

**Read this every time you start work on this roadmap**:

1. **One PR at a time**: Do NOT combine PRs or skip ahead
2. **Validation required**: Each PR must pass validation before marking complete
3. **Update this file**: After each PR, update status and commit this file
4. **User choices matter**: Respect the user's answers from PR0
5. **No shortcuts**: Even though you see the final app structure, you MUST execute each PR

**This roadmap exists because**:
- Agents tend to rush through meta-plugin installations
- Breaking into PRs forces systematic execution
- Each PR is a natural checkpoint
- User maintains control over optional features
