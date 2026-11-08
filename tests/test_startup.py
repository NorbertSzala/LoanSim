"""Foundation smoke tests for package and Qt startup."""

import os
import subprocess
import sys
import tempfile


def _run_offscreen(script: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    with tempfile.TemporaryDirectory(prefix="loansim-startup-") as data_dir:
        environment["LOANSIM_DATA_DIR"] = data_dir
        return subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            check=False,
            env=environment,
            text=True,
            timeout=15,
        )


def test_window_can_show_offscreen() -> None:
    result = _run_offscreen(
        "from PySide6.QtCore import QCoreApplication; "
        "from PySide6.QtWidgets import QApplication; "
        "from loansim.gui.main_window import create_window; "
        "app = QApplication([]); window = create_window(); window.show(); "
        "app.processEvents(); assert window.isVisible(); "
        "assert QCoreApplication.applicationName() == 'LoanSim'; "
        "assert window.windowTitle() == 'LoanSim'; window.close()"
    )
    assert result.returncode == 0, result.stderr


def test_module_entry_point_runs_qt_event_loop() -> None:
    result = _run_offscreen(
        "from PySide6.QtCore import QTimer; "
        "from PySide6.QtWidgets import QApplication; "
        "app = QApplication([]); QTimer.singleShot(0, app.quit); "
        "from loansim.__main__ import main; raise SystemExit(main())"
    )
    assert result.returncode == 0, result.stderr
