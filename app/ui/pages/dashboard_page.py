# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6.QtCore import Qt, Signal, QSize
from app.utils import get_icon_path


class DashboardPage(QWidget):
    """
    Uygulamanın ana kontrol paneli (karşılama ekranı) sayfası.
    Bu sayfa, hangi eylemin seçildiğini ana pencereye sinyaller aracılığıyla bildirir.
    """
    # Ana pencereye hangi butona basıldığını bildirmek için sinyaller
    inventory_button_clicked = Signal()
    reports_button_clicked = Signal()
    purchase_button_clicked = Signal()
    sale_button_clicked = Signal()
    assistant_button_clicked = Signal()

    # Butonlar için kullanılacak olan CSS benzeri stil şablonu
    BUTTON_STYLE = """
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            color: #333;
            padding: 10px;
            min-width: 160px;
            text-align: center;
        }
        QPushButton:hover {
            background-color: #f5f5f5;
            border-color: #007bff;
        }
        QPushButton:pressed {
            background-color: #e9e9e9;
        }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40);
        main_layout.setSpacing(30)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        logo_label = QLabel()
        logo_pixmap = QPixmap(get_icon_path('logo.png'))
        logo_label.setPixmap(logo_pixmap.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(logo_label)
        main_layout.addStretch(1)

        button_grid_layout = QGridLayout();
        button_grid_layout.setSpacing(20)
        self.purchase_button = self._create_action_button("Stok Alış", "purchase.png")
        self.sale_button = self._create_action_button("Stok Satış", "sale.png")
        self.inventory_button = self._create_action_button("Stok Envanteri", "inventory.png")
        self.reports_button = self._create_action_button("Raporlar", "report.png")
        button_grid_layout.addWidget(self.purchase_button, 0, 0)
        button_grid_layout.addWidget(self.sale_button, 0, 1)
        button_grid_layout.addWidget(self.inventory_button, 1, 0)
        button_grid_layout.addWidget(self.reports_button, 1, 1)
        main_layout.addLayout(button_grid_layout)

        main_layout.addStretch(2)

        ASSISTANT_BUTTON_STYLE = """
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(80, 50, 180, 255), stop:1 rgba(50, 150, 255, 255));
                color: white; border: none; border-radius: 8px; font-size: 18px;
                font-weight: bold; padding: 15px;
            }
            QPushButton:hover { background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(90, 60, 190, 255), stop:1 rgba(60, 160, 255, 255)); }
            QPushButton:pressed { background-color: #5A3E99; }
            QPushButton:disabled { background-color: #aaa; border: 1px solid #999; }
        """
        self.assistant_button = QPushButton(" Akıllı Asistan")
        self.assistant_button.setIcon(QIcon(get_icon_path("assistant.png")))
        self.assistant_button.setIconSize(QSize(32, 32))
        self.assistant_button.setStyleSheet(ASSISTANT_BUTTON_STYLE)
        main_layout.addWidget(self.assistant_button)
        main_layout.addStretch(1)

    def _create_action_button(self, text: str, icon_name: str) -> QPushButton:
        """Belirtilen metin ve ikonla standart bir kontrol paneli butonu oluşturur."""
        button = QPushButton(f" {text}")  # Metnin önüne boşluk

        icon_path = get_icon_path(icon_name)
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(24, 24))

        button.setStyleSheet(self.BUTTON_STYLE)
        return button

    def _connect_signals(self):
        """Butonların 'clicked' sinyalini, bizim özel sinyallerimizin 'emit' metoduna bağlar."""
        self.purchase_button.clicked.connect(self.purchase_button_clicked.emit)
        self.sale_button.clicked.connect(self.sale_button_clicked.emit)
        self.inventory_button.clicked.connect(self.inventory_button_clicked.emit)
        self.reports_button.clicked.connect(self.reports_button_clicked.emit)
        self.assistant_button.clicked.connect(self.assistant_button_clicked.emit)