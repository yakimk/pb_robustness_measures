README — pb-robustness-measures
Summary

pb-robustness-measures is a Python library for measuring stability and robustness of outcomes in approval-based multiwinner elections and participatory budgeting (PB). It implements several local and global robustness measures (e.g., add-complement, perfect-approval, removal measures, sampling-based SRM) and includes utilities, example scripts, and tests that use real PB instances.

This README shows how to test the package using pip (local wheel / source / editable installs), how to run the test-suite and examples, and gives a short API / usage guide based on the repository's tests and examples.

## Quick prerequisites

- Python 3.12 (project pyproject.toml requires >=3.12,<3.13).

- git (optional) to clone repository.

- Basic tools for packaging if you want to build/upload: build, twine (optional).



If you use **Poetry** (recommended for development):

```bash
# install poetry if needed: https://python-poetry.org/docs/
poetry install
poetry env activate # can also simply run commands with poetry run <COMANND>
```

## How to test using pip

You already have a built distribution in dist/ (.whl and .tar.gz). here are straightforward, reproducible ways to test the package with pip.

### 1) Create an isolated virtual environment (recommended)
```bash
python -m venv .venv
# mac / linux
source .venv/bin/activate
# windows (powershell)
.venv\Scripts\Activate.ps1
```

Confirm Python version:

```bash
python --version
# must show 3.12.x
```

### 2) Install from the local wheel (fast, exact built artifact)

From the project root:
```bash
pip install --upgrade pip setuptools wheel
pip install dist/pb_robustness_measures-0.1.0-py3-none-any.whl
```

If you prefer the sdist:
```bash
pip install dist/pb_robustness_measures-0.1.0.tar.gz
```

After installing, verify import:
```bash
python -c "import pb_robustness_measures; print('OK', pb_robustness_measures.__file__)"
```

### 3) Install from source (build-on-install)

This will let you install directly from the repository (builds the package during install):

```bash
pip install -e .
# or non-editable
pip install .
```

Note: `pip install -e .` requires your build backend to support editable installs. If you use Poetry for development, simply poetry install and poetry shell is the preferred route.

### 4) Install development dependencies (if not using Poetry)

`pyproject.toml` lists dev dependencies (pytest, black, flake8, isort, sphinx). To run tests you at minimum need pytest and runtime dependencies. If you installed the wheel made with Poetry, wheel already encodes runtime dependencies; otherwise install:

```bash
pip install pabutools matplotlib pyyaml pytest
# plus other dev tools if you want linting/docs
pip install black flake8 isort sphinx
```

## Running the test-suite

From the project root (with the virtualenv active and dependencies installed):

```bash
# all tests
pytest

# skip slow (quick tests)
pytest -q -m "not slow"

# run only slow tests
pytest -q -m "slow"
```

### Notes / tips:

Some tests use real-world PB instances in tests/pabulib/ and are marked @pytest.mark.slow. These can take significantly longer.

If you installed a local wheel, running pytest from the repo root still works because the tests import modules from the installed package. If you prefer to run tests against the checked-out source (editable), use `pip install -e .` before `pytest`.

## Running examples and utilities

There are several example scripts under examples/. Two common usage scenarios:

## Example: run SRM computation on a folder of .pb instances

The script examples/srm_chart_csv.py supports a config file (examples/config/tests_config.yaml) or CLI invocation.

## Example (uses bundled examples or real PB data if available):

 Use a specific folder and sample sizes (CLI args). Sample sizes can be integers or fractions.
```bash
python examples/srm_tests.py examples/data/config/tests_config.yaml
```

```bash
python examples/chart_csv.py examples/data/config/plot_srm_config.yaml
```

The script writes CSV results into res/csv/ by default.

## Example: using library functions 

A minimal interactive example based on the tests (requires pabutools):

```python
from pabutools.election import Project, Instance, ApprovalBallot, ApprovalProfile, Cost_Sat
from pabutools.rules.mes.mes_rule import method_of_equal_shares
from pb_robustness_measures.add_complement.add_complement_mes import add_complement_mes

# Build tiny instance:
p1 = Project("p1", 10)
p2 = Project("p2", 10)
p3 = Project("p3", 15)

inst = Instance()
inst.update([p1, p2, p3])
inst.budget_limit = 30

b1 = ApprovalBallot([p1, p2])
b2 = ApprovalBallot([p1, p2, p3])
b3 = ApprovalBallot([p1, p2])
b4 = ApprovalBallot([p1, p2])
b5 = ApprovalBallot([p3])
profile = ApprovalProfile([b1, b2, b3, b4, b5])

# compute add-complement robustness for p2
ell = add_complement_mes(p2, inst, profile, step=1)
print("add-complement ell:", ell)
```

## API snapshot & important modules

The tests and examples exercise the following public-facing modules (use these imports as examples):

```python
pb_robustness_measures.rules.greedyAV — greedy_av(instance, profile, initial_budget_allocation=None, ...)

pb_robustness_measures.add_complement.add_complement_mes — add_complement_mes(project, instance, profile, step=1, ...)

pb_robustness_measures.remove_approval.perfect_approval_av — perfect_approval_av(instance, profile, project, initial_budget_allocation=None, ...)

pb_robustness_measures.sampling_robustness_measure.srm — plurality_sampling_robustness_measure(instance, profile, target=None, samples=...)

pb_robustness_measures.utils — misc helpers used across tests and examples.
```

Look into src/pb_robustness_measures/ for implementation details.

### Interpreting common test behaviors

Tests marked slow use real-world .pb instances in tests/pabulib/ and may take long or require more memory.

Many tests rely on pabutools and on the pabulib instance parser — if tests fail with import errors, ensure pabutools is installed into the same environment (pip install pabutools or poetry add pabutools).

Some test asserts expect deterministic tie-breaking; if you change tie-breaking rules or randomness, those tests could fail.

<!-- ### Troubleshooting

ModuleNotFoundError: pabutools — install runtime dependency: pip install pabutools.

Wrong Python version — ensure you use Python 3.12.

Tests failing only on CI but not locally — check installed versions of dependencies and whether tests rely upon files under tests/pabulib. Ensure working directory is project root when running pytest.

PermissionError on uploading to TestPyPI — ensure you have the right credentials and correct repository URL. -->

## Contributing & development notes

Use Poetry for local development: poetry install then poetry shell.

Linting and formatting: black, isort, flake8.

Tests: pytest (marker slow separates long-running, real-world instance tests).

When adding new functionality, include at least one unit test in tests/ that demonstrates the intended behavior; real-world examples belong in examples/ and should have deterministic, small seeds if possible.

## Minimal checklist you can follow now

- Create and activate a virtualenv.

- Install runtime deps: either poetry install or pip install pabutools matplotlib pyyaml.

- Install this package via wheel: pip install dist/*.whl.

- Run pytest -q (or pytest -q -m "not slow" to avoid long tests).

- Run an example: python examples/srm_chart_csv.py examples/config/plot_srm_config.yaml.