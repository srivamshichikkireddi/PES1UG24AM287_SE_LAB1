# Issues Found and Fixed — gym_membership_system.py

Baseline: Pylint 4.81/10 · Bandit 6 issues (2 High, 1 Medium, 3 Low) · Flake8 9 issues.
Final: Pylint 10.00/10 · Bandit 0 issues · Flake8 0 issues.

| Issue | Type | Line(s) | Description | Fix Approach |
| ----- | ---- | ------- | ----------- | ------------ |
| `os.system("echo ..." + filename)` (B605) | Security – High | 58 | Shell command built from a string; `filename` could inject shell commands. | Removed the shell call; replaced with `print(...)`. |
| MD5 hashing (B324) | Security – High | 47 | MD5 is cryptographically broken; unsafe for ID hashing. | Switched to `hashlib.sha256`. |
| `eval(discount_expr)` (B307 / W0123) | Security – Medium | 42 | Arbitrary code execution through the discount string. | `calculate_renewal_rate` now takes a numeric `discount` (0–1), validates it, returns `fee * (1 - discount)`. |
| `random.randint` for PIN (B311) | Security – Low | 51 | Predictable PRNG not suitable for secrets/PINs. | Replaced with `secrets.randbelow` (`1000 + randbelow(9000)`). |
| Hardcoded secret (B105) | Security – Low | 70 | API secret committed in source and printed to stdout. | Read from env var `GYM_API_SECRET`; stopped printing it (prints only whether it is configured). |
| `try/except/pass` with bare except (B110 / E722 / W0702) | Security/Bug | 24-27 | Swallows every error silently, incl. `KeyboardInterrupt`. | `members.pop(m_id, None)`; returns whether the member existed. |
| Mutable default `member_log=[]` (W0102) | Bug | 15 | List shared across all calls; log leaks between calls. | Default `None`, create a fresh list inside the function. |
| camelCase function names (C0103) | Style | 15, 23, 30, 40 | Violates PEP 8 snake_case. | Renamed to `register_member`, `cancel_membership`, `check_membership_status`, `calculate_renewal_rate`. |
| Missing docstrings (C0116) | Style | 15-69 | No function documentation. | Added one-line docstrings to every function. |
| Unused import `math` (W0611 / F401) | Quality | 6 | Dead import. | Removed. |
| Unused variables `locker_deposit`, `base_fee`, `m` (W0612 / F841) | Quality | 31, 41, 63 | Assigned but never used. | Removed; loop rewritten with `sum(...)` over `.values()`. |
| `== None` (C0121 / E711) | Style | 32 | Should use identity check. | `member is None`. |
| Redundant if/else returning bool (R1703, R1705) | Quality | 33-37 | Verbose branch. | `return member["months_left"] > 0`. |
| `open()` without `with` / encoding (R1732, W1514) | Bug-risk | 55-57 | File leaks if write fails; encoding platform-dependent. | `with open(..., encoding="utf-8")`. |
| `%` string formatting (C0209) | Style | 19 | Old-style formatting. | f-string. |
| Param `members` shadows global (W0621) | Quality | 61 | Hides module-level name. | Renamed to `member_records`. |
| Lines > 79 chars (E501) | Style | 10, 11, 18 | PEP 8 line length. | Wrapped dict literals and call chains. |
| No newline at EOF (W292 / C0304) | Style | 82 | Missing trailing newline. | Added. |
| `main()` runs on import | Design | 82 | Importing the module executes the program. | Added `if __name__ == "__main__":` guard. |

## Logic issues no tool flags
- `fee` is always `50.0 * months`; the `plan` (Gold/Silver/Platinum) never affects price.
- `calculate_renewal_rate` raises `KeyError` for an unknown member ID (unhandled).
- Roster export writes `str(dict)` (Python repr), not a parseable format; `json.dump` would be better.
- Original code printed the secret to stdout (fixed).
# Reflection

*(The handout text I had did not list the four questions; these are the standard Lab 5 ones — swap in the exact wording from your handout if it differs.)*

**1. Which issues were the easiest and hardest to fix?**
Easiest: Flake8 and most Pylint items (unused import/variables, `== None`, naming, docstrings, final newline) — mechanical and behaviour-preserving. Hardest: `eval()` and the shell call. They can't be patched in place; the design had to change (a numeric `discount` parameter instead of an arbitrary expression string, and dropping the shell call), which also meant updating the caller. Replacing MD5 changes the output hash, so anything that stored old hashes would need migration.

**2. Did the tools report any false positives?**
Mostly no, but some findings are context-dependent. B324 (MD5) is only truly dangerous when used for security; here it is an ID hash, so `usedforsecurity=False` would also have silenced it — I chose SHA-256 for safety. B105 flagged a string that is a placeholder-style secret, not a real password, yet hardcoded secrets are still bad practice. B110 (try/except/pass) is Low but pointed at a real bug (silent failure). Pylint's `C0103` on `m_id`-style names was not flagged, correctly.

**3. How would you integrate static analysis into a development workflow?**
Run Flake8/Pylint/Bandit as a pre-commit hook for fast local feedback, and again in CI (e.g. GitHub Actions) on every pull request with failure thresholds: Bandit High/Medium blocks merge, Pylint score ≥ 9.5, Flake8 clean. Keep config (`.pylintrc`, `setup.cfg`) in the repo so everyone gets identical rules, and require justification for any `# nosec` / `# pylint: disable`.

**4. What tangible improvements did you observe?**
Pylint went 4.81 → 10.00, Bandit 6 issues → 0 (both High-severity issues removed), Flake8 9 → 0. Beyond numbers: removed a remote-code-execution vector (`eval`), a shell-injection vector (`os.system`), a leaked secret, a shared mutable default that corrupted state across calls, and silent error swallowing. The code is also easier to read (snake_case, docstrings, simpler branching) and can be imported without side effects. Static analysis can't catch everything though — the plan-independent pricing bug needed manual review.
