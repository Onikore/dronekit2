from __future__ import annotations

import logging
import sys
from typing import Any, Callable


def errprinter(*args: Any) -> None:
    logger(*args)


def logger(*args: Any) -> None:
    print(*args, file=sys.stderr)
    sys.stderr.flush()


class ErrprinterHandler(logging.Handler):
    """Logging handler to support the deprecated `errprinter` argument to connect()"""

    def __init__(self, errprinter: Callable[..., Any]) -> None:
        logging.Handler.__init__(self)
        self.errprinter = errprinter

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        self.errprinter(msg)
