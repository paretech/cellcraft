# Implement Milestone

Implement the CellCraft milestone specified in the argument (e.g. `/implement-milestone 1`).

## Steps

1. Read `docs/design/1_implementation_plan.md` to find the milestone's scope and definition of done.
2. Read `docs/design/0_design_spec.md` for the full API contract of any class being implemented.
3. Read the current stub files in `cellcraft/` to understand what already exists.
4. Implement only the classes and methods required by the specified milestone — do not implement future phases.
5. Write tests in the corresponding `tests/test_*.py` file(s) covering every behavioral rule stated in the plan.
6. Add or update the relevant example script in `examples/` to demonstrate the new API.
7. Update `README.md` if the quickstart or usage section needs to reflect the new capability.
8. Run `python -m unittest discover -s tests -v`, then `ruff check cellcraft/ tests/`, and fix any failures before finishing. Assumes the project venv is activated.

## Rules

- Follow the module responsibilities in the plan exactly: keep parsing in `pattern.py`, keep pixel logic out of `CellPattern` and `LogicalCanvas`, keep palette logic out of `canvas.py`.
- All public methods must be fully typed (Python 3.12+).
- Use `unittest.TestCase` for all tests — no bare pytest functions.
- Raise the specific custom exception from `cellcraft/errors.py` that matches each error case (never raise a raw `ValueError` or `Exception`).
- `rot90(1)` always means clockwise 90 degrees.
- Transforms (`rot90`, `flip_x`, `flip_y`, `tile`, `pad`, `replace`) must return new objects, not mutate in place.
- Do not write comments that describe what the code does — only write a comment when there is a non-obvious constraint or invariant.
- Do not silently clip or swallow errors; prefer explicit validation.

## Deliverable

After completing the milestone, report:

1. Which files were changed and why.
2. The test command output (pass/fail summary).
3. Anything that diverges from the plan, and why.
4. Any spec ambiguity that needed a judgment call — flag it so the user can confirm or override.
