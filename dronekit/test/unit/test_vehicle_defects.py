"""Regression tests for task E4's D5/D6/D8/D10 fixes.
"""

import ast
import pathlib

import dronekit
import dronekit.mavlink


# ---------------------------------------------------------------------------
# D5 - no bare `except:` clauses left in either module
# ---------------------------------------------------------------------------

def _bare_except_lines(module):
    source = pathlib.Path(module.__file__).read_text()
    tree = ast.parse(source)
    return [node.lineno for node in ast.walk(tree)
            if isinstance(node, ast.ExceptHandler) and node.type is None]


def test_no_bare_except_clauses_in_dronekit_init():
    lines = _bare_except_lines(dronekit)
    assert lines == [], (
        "Bare `except:` clauses (swallow BaseException, incl. "
        "KeyboardInterrupt/SystemExit) found at dronekit/__init__.py "
        "line(s): %r" % lines
    )


def test_no_bare_except_clauses_in_mavlink_module():
    lines = _bare_except_lines(dronekit.mavlink)
    assert lines == [], (
        "Bare `except:` clauses found at dronekit/mavlink.py line(s): %r" % lines
    )
