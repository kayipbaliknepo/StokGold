# app/ui/main_app_window.py

import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QToolBar
from PyQt6.QtGui import QIcon, QAction, QGuiApplication
from PyQt6.QtCore import QSize

from app.utils import get_icon_path
# Oluşturduğumuz tüm sayfa sınıflarını import ediyoruz
from .pages.dashboard_page import DashboardPage
from .pages.inventory_page import InventoryPage
from .pages.report_page import ReportPage
# Alış/Satış diyalogları hala envanter sayfası üzerinden açılacak
from .transaction_dialog import TransactionDialog


class MainApplicationWindow(QMainWindow):
    """
    Uygulamanın ana çerçevesi. QStackedWidget kullanarak sayfalar arası geçişi yönetir.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("StokGold")

        screen_size = QGuiApplication.primaryScreen().availableGeometry().size()
        self.resize(int(screen_size.width() * 0.8), int(screen_size.height() * 0.85))

        self.setWindowIcon(QIcon(get_icon_path('app_icon.ico')))
        self.setStyleSheet("background-color: #eef1f5;")



        self.setWindowIcon(QIcon(get_icon_path('app_icon.ico')))
        self.setStyleSheet("background-color: #eef1f5;")

        # --- Geri Butonu için Araç Çubuğu ---
        self.toolbar = QToolBar("Ana Araç Çubuğu")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)

        back_icon = QIcon(get_icon_path("back.png"))
        self.back_action = QAction(back_icon, "Geri", self)
        self.toolbar.addAction(self.back_action)

        # --- Sayfa Yöneticisi ---
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Sayfaları oluştur ve sinyalleri bağla
        self._create_pages()
        self._connect_signals()

        # Uygulamayı Kontrol Paneli (Dashboard) ile başlat
        self.go_to_dashboard()
        self._center_window()

    def _create_pages(self):
        """Tüm sayfa widget'larının birer kopyasını oluşturur ve stack'e ekler."""
        self.dashboard_page = DashboardPage()
        self.inventory_page = InventoryPage(self)
        self.reports_page = ReportPage(self)

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.inventory_page)
        self.stacked_widget.addWidget(self.reports_page)

    def _connect_signals(self):
        """Sayfalar ve butonlar arası tüm sinyal-slot bağlantılarını kurar."""

        # Dashboard sayfasından gelen sinyalleri, sayfa değiştirme fonksiyonlarına bağla
        self.dashboard_page.inventory_button_clicked.connect(lambda: self.go_to_page(self.inventory_page))
        self.dashboard_page.reports_button_clicked.connect(lambda: self.go_to_page(self.reports_page))

        # Alış ve Satış diyalogları, envanter sayfasının kendi fonksiyonları tarafından açılır.
        # Bu, mantığın ilgili sayfada kalmasını sağlar.
        self.dashboard_page.purchase_button_clicked.connect(self.inventory_page._open_purchase_dialog)
        self.dashboard_page.sale_button_clicked.connect(self.inventory_page._open_sale_dialog)

        # Araç çubuğundaki Geri butonuna basıldığında kontrol paneline dön
        self.back_action.triggered.connect(self.go_to_dashboard)

    def go_to_page(self, page_widget: QWidget):
        """Belirtilen sayfaya geçiş yapar ve Geri butonunu görünür kılar."""
        self.stacked_widget.setCurrentWidget(page_widget)
        self.toolbar.setVisible(True)

    def go_to_dashboard(self):
        """Kontrol paneline döner ve Geri butonunu gizler."""
        # Diğer sayfalardaki verilerin güncel kalması için envanter tablosunu yenile
        if hasattr(self.inventory_page, 'load_all_products'):
            self.inventory_page.load_all_products()

        self.stacked_widget.setCurrentWidget(self.dashboard_page)
        self.toolbar.setVisible(False)

    def _center_window(self):
        """Pencereyi, açıldığı ekranın tam ortasına konumlandırır."""
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())