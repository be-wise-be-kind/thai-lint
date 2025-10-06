# How to Use Roadmaps in thai-lint

**Purpose**: Guide for creating and managing roadmaps in this project

**Quick Start**: Roadmaps help plan and track complex, multi-PR features through structured templates and lifecycle management.

---

## What Are Roadmaps?

Roadmaps are structured planning documents that break down complex features into manageable, trackable work units (pull requests). They provide:

- **Comprehensive planning** before implementation begins
- **Progress tracking** across multiple PRs
- **AI agent coordination** through handoff documents
- **Context preservation** for future work

## When to Use Roadmaps

Use roadmaps for:

✅ **Multi-PR Features** - Features requiring 3+ pull requests
✅ **Complex Upgrades** - Major repository or infrastructure changes
✅ **Coordinated Work** - Features spanning multiple components or systems
✅ **Long-Running Development** - Work spanning multiple sessions or days

Don't use roadmaps for:

❌ **Simple Features** - Single PR features or minor changes
❌ **Bug Fixes** - Unless the fix requires major refactoring
❌ **Documentation Updates** - Unless part of a larger documentation overhaul

## Roadmap Structure

Every roadmap follows a **three-document structure**:

### 1. PROGRESS_TRACKER.md (Required)
**The primary AI agent handoff document**

- Current status and next PR to implement
- Overall progress dashboard
- Prerequisites validation
- AI agent instructions
- Update protocol after each PR

**This is the FIRST document AI agents read when continuing work.**

### 2. PR_BREAKDOWN.md (Required for multi-PR)
**Detailed implementation guide**

- Complete PR breakdown with step-by-step instructions
- File structures and code patterns
- Testing requirements
- Success criteria for each PR
- Dependencies between PRs

### 3. AI_CONTEXT.md (Optional)
**Comprehensive feature context**

- Feature vision and architecture
- Design decisions and rationale
- Integration points with existing code
- Technical constraints and considerations
- Common patterns to follow

## Roadmap Lifecycle

Roadmaps move through three phases:

```
PLANNING → IN-PROGRESS → COMPLETE
```

### 1. Planning Phase
**Location**: `.roadmap/planning/[feature-name]/`

Activities:
- Create roadmap from templates
- Fill in all placeholders
- Break feature into atomic PRs
- Define success criteria
- Review and refine plan

### 2. In-Progress Phase
**Location**: `.roadmap/in-progress/[feature-name]/`

Activities:
- Implement PRs sequentially
- Update PROGRESS_TRACKER.md after each PR
- Coordinate AI agent work
- Track blockers and notes
- Adjust plan if needed

### 3. Complete Phase
**Location**: `.roadmap/complete/[feature-name]/`

Activities:
- Archive completed roadmap
- Preserve for future reference
- Extract learnings and patterns
- Reference for similar features

## Creating a New Roadmap

### Step 1: Create Roadmap Directory

```bash
mkdir -p .roadmap/planning/[feature-name]
```

Replace `[feature-name]` with your feature name (use kebab-case, e.g., `user-authentication`).

### Step 2: Copy Templates

```bash
cp .ai/templates/roadmap-progress-tracker.md.template .roadmap/planning/[feature-name]/PROGRESS_TRACKER.md
cp .ai/templates/roadmap-pr-breakdown.md.template .roadmap/planning/[feature-name]/PR_BREAKDOWN.md
cp .ai/templates/roadmap-ai-context.md.template .roadmap/planning/[feature-name]/AI_CONTEXT.md
```

### Step 3: Fill in Placeholders

Edit each file and replace placeholders:

**Common placeholders**:
- `{{FEATURE_NAME}}` - Name of your feature
- `{{FEATURE_SCOPE}}` - What the feature does and doesn't do
- `{{FEATURE_OVERVIEW}}` - Brief description
- `{{NUM_PRS}}` - Total number of PRs
- `{{DEPENDENCIES}}` - External dependencies
- And others specific to each template

### Step 4: Break Down into PRs

In `PR_BREAKDOWN.md`, create detailed PR sections:

```markdown
## PR1: [Title]
**Scope**: What this PR does
**Files**: Files to modify/create
**Steps**:
1. Step one
2. Step two
**Testing**: How to test
**Success**: How to know it's complete
```

### Step 5: Set Initial Status

In `PROGRESS_TRACKER.md`:
- Set current status to "Planning"
- Mark all PRs as "Not Started"
- Fill in "Next PR to Implement" with PR1

### Step 6: Review and Refine

Review the roadmap for:
- ✅ All PRs are atomic and testable
- ✅ Dependencies are clear
- ✅ Success criteria are defined
- ✅ Placeholders are replaced
- ✅ Architecture is documented (if complex)

### Step 7: Move to In-Progress

When ready to start implementation:

```bash
mv .roadmap/planning/[feature-name] .roadmap/in-progress/
```

## Continuing an Existing Roadmap

### Step 1: Find Active Roadmaps

```bash
ls .roadmap/in-progress/
```

### Step 2: Read PROGRESS_TRACKER.md

**Always read this document FIRST:**

```bash
cat .roadmap/in-progress/[feature-name]/PROGRESS_TRACKER.md
```

Key sections to review:
- **Current Status** - Where we are
- **Next PR to Implement** - What to do next
- **Prerequisites** - What must be done first
- **Notes** - Important context or blockers

### Step 3: Follow Next PR Instructions

Go to `PR_BREAKDOWN.md` and find the PR number from PROGRESS_TRACKER.md. Follow the detailed steps.

### Step 4: Update PROGRESS_TRACKER.md

**After completing each PR**, update:

1. Change PR status from 🔴 Not Started → 🟢 Complete
2. **Add commit hash to Notes column**:
   ```bash
   # Get the short commit hash from the PR you just completed
   git log --oneline -1

   # Add to Notes in format: "Description (commit abc1234)"
   # Example: "INSTALL_PATH parameter added (commit c124b88)"
   ```
3. Add completion percentage (100%)
4. Add any additional notes or learnings
5. Update "Next PR to Implement" to the next PR
6. Update overall progress percentage
7. Commit the changes

Example update:
```markdown
| PR1 | Setup Infrastructure | 🟢 Complete | 100% | Low | P0 | Infrastructure setup complete (commit a1b2c3d) |
```

## Completing a Roadmap

When all PRs are implemented and tested:

### Step 1: Final PROGRESS_TRACKER.md Update

- Mark all PRs as 🟢 Complete
- Set overall progress to 100%
- Add final notes and learnings

### Step 2: Move to Complete

```bash
mv .roadmap/in-progress/[feature-name] .roadmap/complete/
```

### Step 3: Update Documentation

If the feature introduced new patterns:
- Update `.ai/docs/` with new documentation
- Add how-to guides if applicable
- Update AGENTS.md with new capabilities

## AI Agent Guidance

### For Planning Requests

When user says:
- "I want to plan out..."
- "Create a roadmap for..."
- "Plan the implementation of..."

**AI Agent Actions**:
1. Read this guide (how-to-roadmap.md)
2. Ask user for feature details
3. Create roadmap in `.roadmap/planning/[feature-name]/`
4. Use the three templates
5. Help user break down into PRs
6. Review and refine together

### For Continuation Requests

When user says:
- "Continue with..."
- "What's next in..."
- "Resume work on..."

**AI Agent Actions**:
1. Check `.roadmap/in-progress/` for active roadmaps
2. Read the roadmap's PROGRESS_TRACKER.md FIRST
3. Go to "Next PR to Implement" section
4. Reference PR_BREAKDOWN.md for detailed steps
5. Implement the PR
6. Update PROGRESS_TRACKER.md
7. Commit changes

## Best Practices

### Planning Best Practices

1. **Start with Architecture** - Document in AI_CONTEXT.md before breaking into PRs
2. **Atomic PRs** - Each PR should be independently testable and revertible
3. **Clear Dependencies** - Document which PRs depend on others
4. **Success Criteria** - Define "done" for each PR
5. **Realistic Estimates** - Don't underestimate complexity

### Implementation Best Practices

1. **Read PROGRESS_TRACKER.md First** - Always start here
2. **Update Immediately** - Update PROGRESS_TRACKER.md right after completing a PR
3. **Follow the Plan** - Don't skip steps or change order without updating docs
4. **Track Blockers** - Document issues in PROGRESS_TRACKER.md
5. **Commit Often** - Commit roadmap updates frequently

### Coordination Best Practices

1. **One Roadmap at a Time** - Focus on completing one before starting another
2. **Keep Context Updated** - Update notes and learnings as you go
3. **Archive When Done** - Move completed roadmaps to complete/ directory
4. **Reference Past Work** - Check complete/ for similar features
5. **Maintain Templates** - Keep roadmap structure consistent

## Troubleshooting

### Issue: Can't find active roadmaps
**Check**: `.roadmap/in-progress/` directory
**Solution**: If empty, no roadmaps are active. Check planning/ or complete/

### Issue: PROGRESS_TRACKER.md doesn't show next PR
**Check**: "Next PR to Implement" section
**Solution**: Manually update to point to the correct PR

### Issue: Lost context between sessions
**Check**: PROGRESS_TRACKER.md and AI_CONTEXT.md
**Solution**: These documents preserve context. Read them fully to restore context.

### Issue: Roadmap structure changed
**Check**: All three documents exist
**Solution**: Recreate missing documents from templates

### Issue: Can't determine PR order
**Check**: PR_BREAKDOWN.md dependencies section
**Solution**: Follow the dependency graph to determine correct order

## Example Roadmap

### Directory Structure
```
.roadmap/in-progress/user-authentication/
├── PROGRESS_TRACKER.md    # Current: PR3 - OAuth Integration
├── PR_BREAKDOWN.md        # 5 PRs total with detailed steps
└── AI_CONTEXT.md          # Security architecture, auth flow
```

### Typical Workflow
1. User: "Create a roadmap for user authentication"
2. AI creates roadmap in planning/user-authentication/
3. Together break down into 5 PRs
4. User reviews and approves
5. Move to in-progress/user-authentication/
6. AI implements PR1, updates PROGRESS_TRACKER.md
7. AI implements PR2, updates PROGRESS_TRACKER.md
8. Continue until all PRs complete
9. Move to complete/user-authentication/

## Resources

- **Roadmap Templates**: `.ai/templates/roadmap-*.md.template`
- **Workflow Documentation**: `.ai/docs/ROADMAP_WORKFLOW.md`
- **Active Roadmaps**: `.roadmap/in-progress/`
- **Completed Roadmaps**: `.roadmap/complete/` (reference examples)

---

**Remember**: Roadmaps are about planning and tracking, not perfection. Start simple, iterate, and improve as you learn what works for your project.
