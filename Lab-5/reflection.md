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
