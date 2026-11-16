# -*- coding: utf-8 -*-
"""
Execução de tarefas em segundo plano (requisições SIDRA e malhas IBGE) via QThread,
garantindo que a interface do QGIS permaneça fluida e responsiva sem congelar.
"""

import logging
import traceback
from typing import Any, Callable, Set

from qgis.PyQt.QtCore import QThread, pyqtSignal

LOGGER = logging.getLogger("GeoSIDRA")

_ACTIVE_JOBS: Set["BackgroundJob"] = set()


class JobCancelled(Exception):
    """Sinaliza que o usuário cancelou a tarefa."""


class BackgroundJob(QThread):
    """Executa tarefa em background emitindo progresso."""

    progress = pyqtSignal(int, str)
    succeeded = pyqtSignal(object)
    failed = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(self, fn: Callable[[Callable[[int, str], None]], Any]):
        super().__init__(None)
        self._fn = fn
        self._cancel_requested = False
        _ACTIVE_JOBS.add(self)
        self.finished.connect(self._release)

    def request_cancel(self) -> None:
        self._cancel_requested = True

    @property
    def cancel_requested(self) -> bool:
        return self._cancel_requested

    def report(self, pct: int, msg: str) -> None:
        if self._cancel_requested:
            raise JobCancelled()
        self.progress.emit(int(pct), str(msg))

    def run(self) -> None:
        try:
            result = self._fn(self.report)
            if self._cancel_requested:
                self.cancelled.emit()
            else:
                self.succeeded.emit(result)
        except JobCancelled:
            self.cancelled.emit()
        except Exception as exc:
            LOGGER.error("Falha na tarefa em segundo plano: %s\n%s", exc, traceback.format_exc())
            if self._cancel_requested:
                self.cancelled.emit()
            else:
                self.failed.emit(str(exc) or exc.__class__.__name__)

    def _release(self) -> None:
        self.wait(10000)
        _ACTIVE_JOBS.discard(self)
