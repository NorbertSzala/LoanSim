"""Minimal desktop window used to verify Qt startup."""

from PySide6.QtWidgets import QLabel, QMainWindow


def create_window() -> QMainWindow:
    """Create the Phase 0 shell without product or financial behavior."""
    window = QMainWindow()
    window.setWindowTitle("LoanSim")
    window.setCentralWidget(QLabel("LoanSim foundation"))
    window.resize(640, 400)
    return window
