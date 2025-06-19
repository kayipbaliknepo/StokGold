# app/ui/pages/dashboard_page.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from app.utils import get_icon_path


class DashboardPage(QWidget):
    """
    Uygulamanın ana kontrol paneli (karşılama ekranı) sayfası.
    Bu sayfa, hangi eylemin seçildiğini ana pencereye sinyaller aracılığıyla bildirir.
    """
    # --- Sinyaller: Ana pencereye haber vermek için ---
    # Her buton için bir sinyal tanımlıyoruz. Butona basıldığında bu sinyal "yayını" yapılacak.
    inventory_button_clicked = pyqtSignal()
    reports_button_clicked = pyqtSignal()
    purchase_button_clicked = pyqtSignal()
    sale_button_clicked = pyqtSignal()

    # Butonların ortak stilini burada tanımlıyoruz.
    BUTTON_STYLE = """
        QPushButton {
            background-color: #FFFFFF;
            border: 1px solid #DADCE0;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            color: #3c4043;
            padding: 30px;
            min-width: 200px;
            min-height: 80px;
        }
        QPushButton:hover {
            background-color: #F8F9FA;
            border-color: #C6C6C6;
        }
        QPushButton:pressed {
            background-color: #F1F3F4;
            border-color: #B0B0B0;
        }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Arayüz elemanlarını (logo, butonlar) oluşturur ve yerleştirir."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 50, 40, 50)
        main_layout.setSpacing(50)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        # Logo Alanı
        logo_label = QLabel()
        logo_pixmap = QPixmap(get_icon_path('logo.png'))
        logo_label.setPixmap(logo_pixmap.scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(logo_label)

        # Butonları 2x2'lik bir grid içine yerleştiriyoruz
        button_layout = QGridLayout()
        button_layout.setSpacing(25)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.purchase_button = self._create_dashboard_button("Stok Alış")
        self.sale_button = self._create_dashboard_button("Stok Satış")
        self.inventory_button = self._create_dashboard_button("Stok Envanteri")
        self.reports_button = self._create_dashboard_button("Raporlar")

        button_layout.addWidget(self.purchase_button, 0, 0)
        button_layout.addWidget(self.sale_button, 0, 1)
        button_layout.addWidget(self.inventory_button, 1, 0)
        button_layout.addWidget(self.reports_button, 1, 1)

        main_layout.addLayout(button_layout)
        main_layout.addStretch()

    def _create_dashboard_button(self, text: str) -> QPushButton:
        """Belirtilen metinle standart bir kontrol paneli butonu oluşturur."""
        button = QPushButton(text)
        button.setStyleSheet(self.BUTTON_STYLE)
        return button

    def _connect_signals(self):
        """Butonların 'clicked' sinyalini, bizim özel sinyallerimizin 'emit' metoduna bağlar."""
        self.purchase_button.clicked.connect(self.purchase_button_clicked.emit)
        self.sale_button.clicked.connect(self.sale_button_clicked.emit)
        self.inventory_button.clicked.connect(self.inventory_button_clicked.emit)
        self.reports_button.clicked.connect(self.reports_button_clicked.emit)