# How to Address GitHub Issues

**Purpose**: Guide for handling incoming GitHub issues for thai-lint

**Scope**: Issue triage, duplicate detection, fix implementation, release, and closure workflow

**Overview**: Step-by-step instructions for processing GitHub issues from initial submission through
    resolution. Covers reading issues, community acknowledgment, duplicate checking, legitimacy
    evaluation, test-first fixes, PR creation, PyPI publishing, verification, and issue closure.
    Ensures consistent, community-friendly issue handling with proper testing and release procedures.

**Prerequisites**: GitHub CLI (`gh`) authenticated, repository access, PyPI publishing permissions

**Dependencies**: gh CLI, Poetry, pytest, PyPI account with trusted publishing configured

**Related**: docs/releasing.md, how-to-publish-to-pypi.md, how-to-write-tests.md

---

## Workflow Overview

When a user reports an issue (e.g., "Please address this GH issue <link>"), follow these steps:

1. Read the issue
2. Acknowledge the community contribution
3. Check for duplicates
4. Evaluate legitimacy (STOP point)
5. Propose and implement the fix (test-first)
6. Create a PR
7. Publish to PyPI
8. Verify the fix from PyPI
9. Report the fix to the issue
10. Close the issue

---

## Step 1: Read the Issue

Use the GitHub CLI to read the issue details:

```bash
# View issue by number
gh issue view <issue-number>

# View issue from URL (extracts number automatically)
gh issue view <issue-url>

# View with comments
gh issue view <issue-number> --comments
```

**Gather key information:**
- Issue type (bug report, feature request, question)
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Environment details (Python version, OS, thai-lint version)
- Any error messages or stack traces

---

## Step 2: Acknowledge the Community Contribution

Respond to the issue with gratitude. The user took time to help improve thai-lint for everyone.

```bash
gh issue comment <issue-number> --body "Thank you for taking the time to submit this issue! Your contribution helps improve thai-lint for the entire community. We'll review this and get back to you shortly."
```

**Key points:**
- Express genuine appreciation
- Acknowledge the value of community contributions
- Set expectations for follow-up

---

## Step 3: Check for Duplicates

Search for existing similar issues:

```bash
# Search open issues
gh issue list --search "<keywords>" --state open

# Search all issues (including closed)
gh issue list --search "<keywords>" --state all

# Search with labels
gh issue list --search "<keywords>" --label "bug"
```

**If duplicate found:**

```bash
# Comment pointing to existing issue
gh issue comment <issue-number> --body "Thank you for reporting this! This appears to be a duplicate of #<existing-issue>. We're tracking the fix there. Closing this issue in favor of the original, but please add any additional context to #<existing-issue> if you have more details."

# Close as duplicate
gh issue close <issue-number> --reason "not planned" --comment "Closing as duplicate of #<existing-issue>"
```

---

## Step 4: Evaluate Legitimacy

**STOP - Confer with the maintainer/user before proceeding.**

Present findings to the user:
- Summarize the issue
- Indicate whether it appears to be a valid bug/feature
- Note any concerns or questions
- Recommend: **FIX** or **CLOSE with comment**

**If closing (not a valid issue):**

```bash
gh issue comment <issue-number> --body "After investigation, [explanation of why this isn't a bug/won't be implemented]. Thank you for your understanding, and please feel free to open new issues if you encounter other problems."

gh issue close <issue-number> --reason "not planned"
```

**If proceeding with fix:** Continue to Step 5.

---

## Step 5: Propose and Implement the Fix

### 5a. Start with a Failing Test

Always begin with a test that demonstrates the bug:

```bash
# Create/edit test file
# tests/unit/test_<module>.py or tests/integration/test_<feature>.py
```

**Test structure:**

```python
def test_issue_<number>_<brief_description>():
    """Regression test for GitHub issue #<number>.

    Issue: <link to issue>
    Problem: <brief description of the bug>
    """
    # Arrange: Set up the conditions that trigger the bug

    # Act: Perform the action that should work

    # Assert: Verify correct behavior
    assert result == expected  # This should FAIL before the fix
```

**Run the test to confirm it fails:**

```bash
just test tests/unit/test_<module>.py::test_issue_<number>_<brief_description>
```

### 5b. Implement the Fix

- Make minimal changes to fix the issue
- Follow existing code patterns
- Maintain code quality standards

### 5c. Verify the Fix

```bash
# Run the specific test (should now pass)
just test tests/unit/test_<module>.py::test_issue_<number>_<brief_description>

# Run full test suite
just test

# Run full linting
just lint-full
```

---

## Step 6: Create a PR

Create a branch and PR linked to the issue:

```bash
# Create feature branch (if not already on one)
git checkout -b fix/issue-<number>-<brief-description>

# Stage and commit changes
git add .
git commit -m "fix(<scope>): <description> (#<issue-number>)

<detailed description of the fix>

Fixes #<issue-number>

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push and create PR
git push -u origin fix/issue-<number>-<brief-description>

gh pr create --title "fix(<scope>): <description> (#<issue-number>)" --body "## Summary
Fixes #<issue-number>

## Changes
- <change 1>
- <change 2>

## Test Plan
- [ ] New regression test added
- [ ] All existing tests pass
- [ ] Linting passes

Generated with [Claude Code](https://claude.com/claude-code)"
```

---

## Step 7: Publish to PyPI

After PR is merged, publish the fix.

### 7a. Check Current PyPI Version

```bash
# Get current version from PyPI
pip index versions thailint 2>/dev/null | head -1

# Or check PyPI directly
curl -s https://pypi.org/pypi/thailint/json | jq -r '.info.version'
```

### 7b. Bump Version

Determine the next version (typically a PATCH for bug fixes):

```bash
# Current version in pyproject.toml
grep '^version = ' pyproject.toml

# Bump patch version
poetry version patch
```

### 7c. Update CHANGELOG

Add entry to CHANGELOG.md under the new version section.

### 7d. Commit, Tag, and Push

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: Publish v<X.Y.Z> (#<issue-number>)

Co-Authored-By: Claude <noreply@anthropic.com>"

git tag -a v<X.Y.Z> -m "Release v<X.Y.Z>"
git push origin main
git push origin v<X.Y.Z>
```

The tag push triggers the GitHub Actions workflow to publish to PyPI.

**Reference:** See `docs/releasing.md` for complete release process details.

---

## Step 8: Verify the Fix from PyPI

Test the published fix in a clean environment:

```bash
# Create clean environment
python -m venv /tmp/test-fix-env
source /tmp/test-fix-env/bin/activate

# Install from PyPI (may take a few minutes to propagate)
pip install thailint==<X.Y.Z>

# Verify version
thailint --version

# Test the specific fix
# <run commands that reproduce the original issue - should now work>

# Cleanup
deactivate
rm -rf /tmp/test-fix-env
```

---

## Step 9: Report the Fix to the Issue

Comment on the issue with the fix details:

```bash
gh issue comment <issue-number> --body "This issue has been fixed in **thailint v<X.Y.Z>**!

You can update to the latest version:

\`\`\`bash
pip install --upgrade thailint
\`\`\`

Thank you again for reporting this issue. Your contribution helps make thai-lint better for everyone!"
```

---

## Step 10: Close the Issue

Close the issue with the appropriate reason:

```bash
gh issue close <issue-number> --reason "completed"
```

---

## Quick Reference

| Step | Command | Purpose |
|------|---------|---------|
| Read issue | `gh issue view <num>` | Understand the problem |
| Comment | `gh issue comment <num> --body "..."` | Communicate with reporter |
| Search duplicates | `gh issue list --search "<terms>"` | Find existing issues |
| Close duplicate | `gh issue close <num> --reason "not planned"` | Close duplicate |
| Run tests | `just test` | Verify fix works |
| Create PR | `gh pr create` | Submit fix for review |
| Check PyPI version | `pip index versions thailint` | Determine next version |
| Bump version | `poetry version patch` | Increment version |
| Tag release | `git tag -a v<X.Y.Z>` | Trigger PyPI publish |
| Close completed | `gh issue close <num> --reason "completed"` | Mark as resolved |

---

## Troubleshooting

### Issue: PyPI version not updating

**Solution:** PyPI propagation can take several minutes. Wait and retry:

```bash
pip install --no-cache-dir thailint==<X.Y.Z>
```

### Issue: Test passes but shouldn't

**Solution:** Ensure the test accurately reproduces the reported bug. Re-read the issue for edge cases.

### Issue: CI fails on PR

**Solution:** Run `just lint-full` and `just test` locally. Fix all issues before pushing.

---

## Related Resources

- **Release Process:** `docs/releasing.md`
- **PyPI Publishing:** `.ai/howtos/python-cli/how-to-publish-to-pypi.md`
- **Writing Tests:** `.ai/howtos/how-to-write-tests.md`
- **Creating PRs:** AGENTS.md (Git Workflow section)
