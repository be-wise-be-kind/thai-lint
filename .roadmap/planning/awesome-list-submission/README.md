# analysis-tools-dev/static-analysis submission

**Status**: ready to submit once the repository reaches 20 GitHub stars.

## Why this list

14,751 stars, pushed daily, and `vinta/awesome-python` defers to it for code
analysis. It is a catalog rather than a shortlist, so there is no
"category is full" rejection path. It already defines an `ai-generated-code`
tag, which is the project's exact positioning.

## Their stated requirements

| Requirement | Status |
|---|---|
| Existed at least six months | Met — first release 2025-10-07 |
| More than one contributor | Met — 7 |
| At least 20 GitHub stars | **Blocked** — see below |

## Submission steps

1. Confirm the star count is at least 20: `gh api repos/be-wise-be-kind/thai-lint --jq .stargazers_count`
2. Fork `analysis-tools-dev/static-analysis`
3. Copy `thailint.yml` in this directory to `data/tools/thailint.yml`
4. Optionally run `make render` to check for errors before opening the PR
5. Open the pull request, disclosing maintainership

The README of that repository is generated from the YAML. Do not edit it.

## Validation already done

- Parses as YAML
- Description is 394 characters against their 500 limit
- Every tag checked against `data/tags.yml`: python, typescript, javascript,
  rust, yaml, terraform, shell, ai-generated-code all valid
- `docker`, `toml` and `hcl` are **not** tags in their vocabulary and were
  dropped rather than invented
- Category `linter` matches the value used by 710 of their existing entries
