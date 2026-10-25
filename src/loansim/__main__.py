"""Launch the minimal LoanSim desktop shell."""

import sys

from PySide6.QtWidgets import QApplication

from loansim.gui.main_window import create_window


def main() -> int:
    """Show the startup window and run the Qt event loop."""
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    window = create_window()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
