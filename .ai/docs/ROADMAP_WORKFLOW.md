# Roadmap Workflow Documentation

**Purpose**: Comprehensive documentation of the roadmap-driven development workflow

**Scope**: Roadmap lifecycle, document structure, AI agent coordination, and workflow patterns

**Overview**: Technical documentation for the roadmap workflow system used in AI-ready repositories. Describes
    the three-document structure, lifecycle management (planning → in-progress → complete), AI agent handoff
    protocols, and best practices for roadmap-driven development. Essential for understanding how roadmaps
    coordinate complex, multi-PR feature development.

**Dependencies**: foundation/ai-folder plugin, roadmap plugin

**Exports**: Workflow patterns, coordination protocols, lifecycle management guidelines

**Related**: how-to-roadmap.md (user guide), roadmap templates, AGENTS.md (roadmap routing)

**Implementation**: Lifecycle-based workflow with structured handoff documentation

---

## Overview

The roadmap workflow is a systematic approach to planning, implementing, and tracking complex features that require multiple pull requests. It provides:

1. **Structured Planning** - Templates for comprehensive feature breakdown
2. **Progress Tracking** - Clear visibility into implementation status
3. **AI Agent Coordination** - Handoff documents for seamless continuation
4. **Lifecycle Management** - Organized progression from planning to completion

## Core Concepts

### Three-Document Structure

Every roadmap consists of three documents, each serving a specific purpose:

#### 1. PROGRESS_TRACKER.md
**Role**: Primary AI agent handoff document

**Contains**:
- Current status and implementation state
- Next PR to implement (clear directive)
- Overall progress dashboard
- Prerequisites and validation checklist
- Update protocol for AI agents
- Notes and blockers

**Usage**: This is the FIRST document AI agents read when continuing work. It answers "Where are we?" and "What's next?"

#### 2. PR_BREAKDOWN.md
**Role**: Detailed implementation guide

**Contains**:
- Complete PR breakdown (all PRs numbered)
- Step-by-step implementation instructions
- File structures and code patterns
- Testing requirements for each PR
- Success criteria and validation
- Dependencies between PRs

**Usage**: AI agents reference this for detailed implementation steps after consulting PROGRESS_TRACKER.md.

#### 3. AI_CONTEXT.md (Optional)
**Role**: Comprehensive feature architecture

**Contains**:
- Feature vision and goals
- Design decisions and rationale
- System architecture and integration points
- Technical constraints and considerations
- Common patterns and anti-patterns

**Usage**: Provides deep context for complex features. AI agents read this to understand "why" decisions were made.

### Why Three Documents?

**Separation of Concerns**:
- **PROGRESS_TRACKER.md** - Current state (changes frequently)
- **PR_BREAKDOWN.md** - Implementation plan (stable after planning)
- **AI_CONTEXT.md** - Architecture context (stable, deep knowledge)

**AI Agent Efficiency**:
- Quick status check: Read PROGRESS_TRACKER.md only
- Implementation guidance: Add PR_BREAKDOWN.md
- Architectural understanding: Add AI_CONTEXT.md

**Maintenance**:
- Update PROGRESS_TRACKER.md after each PR (lightweight)
- PR_BREAKDOWN.md rarely changes after planning
- AI_CONTEXT.md evolves slowly as architecture solidifies

## Roadmap Lifecycle

### Phase 1: Planning
**Location**: `.roadmap/planning/[feature-name]/`

**Activities**:
1. Create roadmap directory
2. Copy templates (all three documents)
3. Replace placeholders with feature details
4. Break feature into atomic PRs
5. Define success criteria for each PR
6. Document architecture (if complex)
7. Review and refine plan

**Completion Criteria**:
- All placeholders replaced
- PRs are atomic and testable
- Dependencies mapped
- Success criteria defined
- Ready to start implementation

**Transition**: Move to `.roadmap/in-progress/` when ready

### Phase 2: In-Progress
**Location**: `.roadmap/in-progress/[feature-name]/`

**Activities**:
1. Read PROGRESS_TRACKER.md to identify next PR
2. Reference PR_BREAKDOWN.md for implementation steps
3. Implement PR following detailed instructions
4. Test according to success criteria
5. Update PROGRESS_TRACKER.md immediately
6. Move to next PR

**Update Protocol** (after each PR):
- Change PR status: 🔴 → 🟢
- Add completion percentage
- Add notes and learnings
- Update "Next PR to Implement"
- Update overall progress
- Commit changes

**Completion Criteria**:
- All PRs implemented and tested
- PROGRESS_TRACKER.md shows 100%
- No blockers remain
- Success metrics achieved

**Transition**: Move to `.roadmap/complete/` when done

### Phase 3: Complete
**Location**: `.roadmap/complete/[feature-name]/`

**Activities**:
1. Final PROGRESS_TRACKER.md update
2. Document learnings and insights
3. Archive for future reference
4. Extract reusable patterns

**Purpose**:
- Preserve knowledge for similar features
- Provide examples for new roadmaps
- Track historical decisions
- Learn from past work

**No Transition**: Roadmap stays in complete/ indefinitely

## AI Agent Coordination

### Handoff Protocol

**Starting Work**:
1. Check `.roadmap/in-progress/` for active roadmaps
2. Read PROGRESS_TRACKER.md FIRST
3. Note "Next PR to Implement"
4. Read PR_BREAKDOWN.md for that PR
5. Reference AI_CONTEXT.md if architecture questions arise

**During Work**:
1. Follow PR_BREAKDOWN.md steps exactly
2. Track deviations in PROGRESS_TRACKER.md notes
3. Document blockers immediately
4. Test according to success criteria

**After Work**:
1. Update PROGRESS_TRACKER.md immediately
2. Mark PR complete
3. Set next PR to implement
4. Commit roadmap updates
5. Create actual code PR (separate commit)

### Detection Patterns

AI agents detect roadmap requests through keywords:

**Planning Requests** (create new roadmap):
- "I want to plan out..."
- "Create a roadmap for..."
- "Plan the implementation of..."
- "Break down the feature..."

**Continuation Requests** (continue existing roadmap):
- "Continue with..."
- "What's next in..."
- "Resume work on..."
- "Continue roadmap for..."

**Status Requests** (check progress):
- "What's the status of..."
- "How far along is..."
- "Show roadmap progress..."

### Routing Logic

```
User Request → Detection → Routing → Action

Planning Request:
  → Read how-to-roadmap.md
  → Create .roadmap/planning/[feature]/
  → Copy templates
  → Guide user through planning

Continuation Request:
  → Read .roadmap/in-progress/[feature]/PROGRESS_TRACKER.md
  → Identify next PR
  → Read PR_BREAKDOWN.md for steps
  → Implement PR
  → Update PROGRESS_TRACKER.md

Status Request:
  → Read PROGRESS_TRACKER.md
  → Report current status
  → Show next PR
  → Highlight any blockers
```

## Workflow Patterns

### Pattern 1: Sequential PR Implementation

**Use Case**: PRs have clear dependencies (PR2 needs PR1)

**Workflow**:
1. Implement PR1 completely
2. Update PROGRESS_TRACKER.md
3. Implement PR2 using PR1's output
4. Update PROGRESS_TRACKER.md
5. Continue sequentially

**Benefits**: Predictable, easy to track, clear handoff

### Pattern 2: Parallel PR Implementation

**Use Case**: Independent PRs (frontend and backend separately)

**Workflow**:
1. Identify independent PRs in PR_BREAKDOWN.md
2. Implement in any order
3. Update PROGRESS_TRACKER.md for each
4. Integration PR at the end

**Benefits**: Faster completion, flexible order

**Caution**: Document independence clearly in PR_BREAKDOWN.md

### Pattern 3: Iterative Refinement

**Use Case**: Architecture evolves during implementation

**Workflow**:
1. Implement initial PRs
2. Discover architectural needs
3. Update AI_CONTEXT.md with new insights
4. Adjust remaining PRs in PR_BREAKDOWN.md
5. Update PROGRESS_TRACKER.md with changes
6. Continue with refined plan

**Benefits**: Adapts to learning, maintains documentation

**Caution**: Document all changes with rationale

## Best Practices

### Planning Phase

✅ **DO**:
- Break features into truly atomic PRs (each PR independently testable)
- Define clear success criteria for each PR
- Document architecture in AI_CONTEXT.md for complex features
- Map dependencies between PRs explicitly
- Include rollback plans for risky PRs

❌ **DON'T**:
- Create PRs that depend on incomplete work
- Skip AI_CONTEXT.md for complex features
- Leave placeholders unfilled
- Plan too many PRs (>10 suggests feature is too large)

### Implementation Phase

✅ **DO**:
- Read PROGRESS_TRACKER.md before every work session
- Update PROGRESS_TRACKER.md immediately after each PR
- Follow PR_BREAKDOWN.md steps exactly
- Document deviations and reasons
- Test thoroughly per success criteria

❌ **DON'T**:
- Skip PROGRESS_TRACKER.md updates
- Change PR order without documenting
- Implement multiple PRs without updates
- Ignore success criteria
- Leave blockers undocumented

### Completion Phase

✅ **DO**:
- Update PROGRESS_TRACKER.md with final status
- Document learnings and insights
- Archive promptly to `.roadmap/complete/`
- Extract reusable patterns
- Update project documentation if needed

❌ **DON'T**:
- Leave roadmap in in-progress/ after completion
- Forget to document learnings
- Delete roadmaps (archive instead)
- Skip final documentation updates

## Integration Points

### With AGENTS.md

Roadmap plugin updates AGENTS.md with:
- Roadmap detection patterns
- Routing instructions to how-to-roadmap.md
- Lifecycle management guidance
- Update protocols

**Location in AGENTS.md**: "Roadmap-Driven Development" section

### With .ai/index.yaml

Roadmap resources added to index.yaml:
```yaml
roadmaps:
  location: .roadmap/
  guide: .roadmap/how-to-roadmap.md
  workflow_docs: .ai/docs/ROADMAP_WORKFLOW.md
  templates: .ai/templates/roadmap-*.md.template
```

### With Templates

Roadmap templates in `.ai/templates/`:
- `roadmap-progress-tracker.md.template`
- `roadmap-pr-breakdown.md.template`
- `roadmap-ai-context.md.template`

Used to create new roadmaps consistently.

## Common Scenarios

### Scenario 1: New Complex Feature

1. User requests feature planning
2. AI detects "plan out" pattern
3. AI creates roadmap in planning/
4. AI helps break down into PRs
5. User reviews and approves
6. AI moves to in-progress/
7. AI implements PR by PR
8. AI updates PROGRESS_TRACKER.md after each
9. AI moves to complete/ when done

### Scenario 2: Resuming Work After Break

1. User says "continue with authentication"
2. AI reads `.roadmap/in-progress/authentication/PROGRESS_TRACKER.md`
3. AI identifies next PR from "Next PR to Implement"
4. AI reads PR_BREAKDOWN.md for that PR
5. AI implements PR
6. AI updates PROGRESS_TRACKER.md
7. User can break again, cycle repeats

### Scenario 3: Blocked PR

1. AI implements PR, encounters blocker
2. AI documents blocker in PROGRESS_TRACKER.md notes
3. AI marks PR status as 🔵 Blocked
4. AI sets next PR to workaround or fix blocker
5. AI updates PROGRESS_TRACKER.md
6. User addresses blocker
7. AI resumes original PR

### Scenario 4: Roadmap Needs Revision

1. During implementation, architecture changes
2. AI updates AI_CONTEXT.md with new decisions
3. AI revises remaining PRs in PR_BREAKDOWN.md
4. AI documents changes in PROGRESS_TRACKER.md notes
5. AI continues with revised plan
6. Final roadmap reflects reality

## Metrics and Success Indicators

### Planning Quality Metrics
- All PRs are atomic (pass review)
- Dependencies clearly mapped
- Success criteria measurable
- Architecture documented (if complex)
- Placeholders all replaced

### Implementation Quality Metrics
- PROGRESS_TRACKER.md updated after each PR
- All PRs meet success criteria
- Blockers documented and resolved
- Code PRs align with roadmap PRs
- Tests pass per success criteria

### Completion Quality Metrics
- 100% progress achieved
- All PRs implemented
- Documentation updated
- Learnings documented
- Roadmap archived

## Troubleshooting

### Issue: Lost track of progress
**Check**: PROGRESS_TRACKER.md "Next PR to Implement"
**Solution**: This section always shows current state

### Issue: AI agent skips PROGRESS_TRACKER.md
**Symptom**: Implements wrong PR or duplicates work
**Solution**: Enforce reading PROGRESS_TRACKER.md first in AGENTS.md

### Issue: Roadmap doesn't match reality
**Symptom**: Code differs from PR_BREAKDOWN.md
**Solution**: Update both PR_BREAKDOWN.md and PROGRESS_TRACKER.md notes to reflect actual implementation

### Issue: Multiple roadmaps active
**Symptom**: Confusion about which to work on
**Solution**: Move all but one to planning/, focus on single roadmap in in-progress/

### Issue: Can't find completed roadmaps
**Location**: `.roadmap/complete/`
**Solution**: Check complete/ directory for archived roadmaps

## Version History

- v1.0 - Initial roadmap workflow documentation

## References

- **User Guide**: `.roadmap/how-to-roadmap.md`
- **Templates**: `.ai/templates/roadmap-*.md.template`
- **Plugin Docs**: `plugins/foundation/roadmap/README.md`
- **Agent Instructions**: `plugins/foundation/roadmap/AGENT_INSTRUCTIONS.md`
