# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

import sys
import os
import traceback
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QStackedWidget, QVBoxLayout,
    QToolBar, QMessageBox, QSizePolicy
)
from PySide6.QtGui import QIcon, QAction, QGuiApplication
from PySide6.QtCore import QSize, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint

# Yerel modül importları
from app.utils import get_icon_path
from app.agent.agent_core import StokGoldAgent
from .pages.dashboard_page import DashboardPage
from .pages.inventory_page import InventoryPage
from .pages.report_page import ReportPage
from .pages.repair_page import RepairPage
from .pages.data_management_page import DataManagementPage
from .assistant_dialog import AssistantDialog


class MainApplicationWindow(QMainWindow):
    """
    Uygulamanın ana çerçevesi. Tüm sayfaları yönetir ve aralarındaki geçişi sağlar.
    """

    def __init__(self):
        super().__init__()

        # 1. Ana Pencere Ayarları
        self.setWindowTitle("StokGold")
        self.setWindowIcon(QIcon(get_icon_path('app_icon.ico')))
        self.setStyleSheet("background-color: #f0f0f0;")

        # 2. Boyutlandırma ve Ortalama
        screen_size = QGuiApplication.primaryScreen().availableGeometry().size()
        self.resize(int(screen_size.width() * 0.85), int(screen_size.height() * 0.85))
        self._center_window()

        # 3. Arayüzü Kur ve Sinyalleri Bağla
        self._setup_ui()
        self._connect_signals()

        # 4. Başlangıç Sayfasını Ayarla
        self.go_to_dashboard()

    def _setup_ui(self):
        """Arayüzün ana iskeletini oluşturur."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Geri Butonu için Araç Çubuğu
        self.toolbar = QToolBar("Ana Araç Çubuğu")
        self.toolbar.setIconSize(QSize(22, 22))
        self.toolbar.setStyleSheet("QToolBar { background-color: #F4F7FC; border: none; padding: 5px; }")

        self.back_action = QAction(QIcon(get_icon_path("back.png")), "Geri", self)
        self.toolbar.addAction(self.back_action)

        main_layout.addWidget(self.toolbar)

        # Sayfa Yöneticisi (Kart Destesi)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Sayfaları oluştur
        self._create_pages()

    def _center_window(self):
        """Pencereyi ekranın ortasına konumlandırır."""
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen_geometry.center() - self.frameGeometry().center())

    def _create_pages(self):
        """Tüm sayfa widget'larının birer kopyasını oluşturur ve stack'e ekler."""
        self.dashboard_page = DashboardPage(self)
        self.inventory_page = InventoryPage(self)
        self.reports_page = ReportPage(self)
        self.repair_page = RepairPage(self)  # Yeni tamir sayfasını da ekliyoruz
        self.data_management_page = DataManagementPage(self)

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.inventory_page)
        self.stacked_widget.addWidget(self.reports_page)
        self.stacked_widget.addWidget(self.repair_page)
        self.stacked_widget.addWidget(self.data_management_page)



    def _connect_signals(self):
        """Tüm sinyal-slot bağlantılarını tek bir yerden yönetir."""
        # Dashboard butonları tıklandığında ilgili sayfaya git
        self.dashboard_page.inventory_button_clicked.connect(lambda: self.go_to_page(self.inventory_page))
        self.dashboard_page.reports_button_clicked.connect(lambda: self.go_to_page(self.reports_page))
        self.dashboard_page.repair_button_clicked.connect(lambda: self.go_to_page(self.repair_page))
        self.dashboard_page.data_management_button_clicked.connect(lambda: self.go_to_page(self.data_management_page))
        self.dashboard_page.assistant_button_clicked.connect(self._open_assistant_dialog)

        # Alış ve Satış diyalogları, envanter sayfasının kendi fonksiyonları tarafından açılır
        self.dashboard_page.purchase_button_clicked.connect(self.inventory_page._open_purchase_dialog)
        self.dashboard_page.sale_button_clicked.connect(self.inventory_page._open_sale_dialog)

        # Araç çubuğundaki Geri butonuna basıldığında kontrol paneline dön
        self.back_action.triggered.connect(self.go_to_dashboard)

    def _animate_transition(self, old_widget: QWidget, new_widget: QWidget, direction: str):
        """İki sayfa arasında yumuşak bir kayma animasyonu uygular."""
        width = self.frameGeometry().width()
        offset_x = width if direction == 'forward' else -width

        new_widget.setGeometry(0, 0, width, self.frameGeometry().height())
        p = new_widget.pos()
        new_widget.move(p.x() + offset_x, p.y())

        self.stacked_widget.setCurrentWidget(new_widget)

        anim_old = QPropertyAnimation(old_widget, b"pos")
        anim_old.setEndValue(QPoint(p.x() - offset_x, p.y()))
        anim_old.setDuration(300)
        anim_old.setEasingCurve(QEasingCurve.Type.InOutCubic)

        anim_new = QPropertyAnimation(new_widget, b"pos")
        anim_new.setStartValue(QPoint(p.x() + offset_x, p.y()))
        anim_new.setEndValue(p)
        anim_new.setDuration(300)
        anim_new.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.anim_group = QParallelAnimationGroup(self)
        self.anim_group.addAnimation(anim_old)
        self.anim_group.addAnimation(anim_new)
        self.anim_group.start()

    def go_to_page(self, page_widget: QWidget):
        """Belirtilen sayfaya ileri doğru animasyonla geçiş yapar."""
        # Sayfaya geçmeden önce verilerini yenile (eğer yenileme fonksiyonu varsa)
        if hasattr(page_widget, 'load_all_data'):  # Genel bir isim kullanalım
            page_widget.load_all_data()

        current_widget = self.stacked_widget.currentWidget()
        if current_widget != page_widget:
            self._animate_transition(current_widget, page_widget, direction='forward')
        self.toolbar.setVisible(True)

    def go_to_dashboard(self):
        """Kontrol paneline geri doğru animasyonla döner."""
        current_widget = self.stacked_widget.currentWidget()
        if current_widget != self.dashboard_page:
            # Dashboard'a dönmeden önce onun da verilerini yenile
            if hasattr(self.dashboard_page, 'update_dashboard_data'):
                self.dashboard_page.update_dashboard_data()
            self._animate_transition(current_widget, self.dashboard_page, direction='backward')
        self.toolbar.setVisible(False)

    def _open_assistant_dialog(self):
        """Akıllı Asistan sohbet diyalogunu açar."""
        try:
            dialog = AssistantDialog(parent=self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Asistan Hatası",
                                 f"Akıllı Asistan başlatılırken bir hata oluştu:\n\n{e}\n\nLütfen .env dosyasını ve API anahtarınızı kontrol edin.")