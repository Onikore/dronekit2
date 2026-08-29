.. _coding_standards:

==========================
Coding Standards
==========================

DroneKit-Python does not impose (or recommend) a particular set of coding standards
for third party code.

Internally the project is linted and formatted with `ruff <https://docs.astral.sh/ruff/>`_,
configured in the ``[tool.ruff]`` section of :file:`pyproject.toml`. The current settings are:

* Line length: 120 characters.
* Target Python version: 3.9 (the package's minimum supported version - see
  :ref:`installing_dronekit`).
* Enabled rule sets: ``E``/``W`` (pycodestyle), ``F`` (Pyflakes), ``I`` (import sorting),
  ``UP`` (pyupgrade - flags code that can use newer Python syntax) and ``B`` (flake8-bugbear).

Contributors should install the ``dev`` extra and run ruff before submitting changes:

.. code-block:: bash

    pip install -e ".[dev]"
    ruff check .
    ruff format --check .

CI runs both of these commands (see :file:`.github/workflows/ci.yml`) and will report any
violations, but we also expect contributors to copy the patterns used in similar code within
the existing code base.
