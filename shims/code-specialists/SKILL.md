---
name: code-specialists
summary: Six focused engineering, security, and API specialists behind Jev
source: https://github.com/getsentry/skills and https://github.com/lassejlv/skills
description: Use for bug finding in code diffs, backend security and authorization audits, high-confidence security reviews, simplifying code without changing behavior, scanning third-party skills for prompt injection, or minimizing exposed API response fields while respecting consumer contracts. Jev selects from six Sentry and lassejlv specialist skills.
---

Use the Skillshare-managed hidden code specialist collection: the four original Sentry techniques (`find-bugs`, `code-simplifier`, `security-review`, `skill-scanner`) plus lassejlv's `backend-security-audit` and `minimize-api-responses`. Do not use Sentry's commit, branch, issue triage, or company-specific lifecycle workflows. Aegis remains the engineering workflow owner.

1. `jevshelf search --collection sentry --mode jev --task "<specific review or simplification task>" --max-results 2`.
2. `jevshelf load --collection sentry --id <selected id> --expected-digest <selected digest>`.
3. Read skill-local helper code and references through `load --file <relative path>`; a read does **not** run it. The `skill-scanner` has a Python helper script and requires `uv` for its documented execution. Use only when the task authorizes the scan.
4. Limit reported findings to the user-requested code or skill scope; verify exploitability rather than claim a vulnerability based on a pattern. Do not add unrequested fixes. Preserve Aegis and repository workflow rules.
5. Distinguish Jev no-match, uncertain, and API failure; do not claim the selector ran if it didn't.
