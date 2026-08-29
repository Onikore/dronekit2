## What does this change?

<!-- Briefly describe what this PR does and why. Link any related issue. -->

## Checklist

- [ ] `pytest dronekit/test` passes locally (SITL tests are skipped without
      `DRONEKIT_TEST_CONNECTION` - that's fine, CI runs them separately).
- [ ] `ruff check .` / `ruff format --check .` pass (or `pre-commit run --all-files`).
- [ ] Docs (`docs/`) updated if this changes public API behavior.
- [ ] `CHANGELOG.md` updated if this is a user-facing change.
