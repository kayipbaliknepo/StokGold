# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

import sys
from PySide6.QtWidgets import QApplication
from app.database import create_table
from app.utils import ensure_data_dirs_exist
from app.ui.main_app_window import MainApplicationWindow

def main():
    """Uygulamanın ana giriş noktası."""

    ensure_data_dirs_exist()
    create_table()
    app = QApplication(sys.argv)
    window = MainApplicationWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()