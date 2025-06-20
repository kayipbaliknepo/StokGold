# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

# app/ui/main_app_window.py (NİHAİ DÜZELTİLMİŞ HALİ)

import os
import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QToolBar
from PySide6.QtGui import QIcon, QAction, QGuiApplication  # <-- DOĞRU IMPORT BURADA
from PySide6.QtCore import QSize, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint

from app.utils import get_icon_path
from .pages.dashboard_page import DashboardPage
from .pages.inventory_page import InventoryPage
from .pages.report_page import ReportPage


class MainApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StokGold")

        # Dinamik boyutlandırma
        screen_size = QGuiApplication.primaryScreen().availableGeometry().size()
        self.resize(int(screen_size.width() * 0.85), int(screen_size.height() * 0.85))

        self.setWindowIcon(QIcon(get_icon_path('app_icon.ico')))
        self.setStyleSheet("background-color: #f0f0f0;")

        # Araç çubuğu ve Geri butonu
        self.toolbar = QToolBar("Ana Araç Çubuğu")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)

        back_icon = QIcon(get_icon_path("back.png"))
        self.back_action = QAction(back_icon, "Geri", self)
        self.toolbar.addAction(self.back_action)

        # Sayfa yöneticisi
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Kurulum fonksiyonları
        self._create_pages()
        self._connect_signals()
        self.go_to_dashboard()
        self._center_window()

    def _center_window(self):
        """Pencereyi, açıldığı ekranın tam ortasına konumlandırır."""
        # HATALI IMPORT SATIRI BURADAN KALDIRILDI.
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    def _create_pages(self):
        self.dashboard_page = DashboardPage()
        self.inventory_page = InventoryPage(self)
        self.reports_page = ReportPage(self)

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.inventory_page)
        self.stacked_widget.addWidget(self.reports_page)

    def _connect_signals(self):
        self.dashboard_page.inventory_button_clicked.connect(lambda: self.go_to_page(self.inventory_page))
        self.dashboard_page.reports_button_clicked.connect(lambda: self.go_to_page(self.reports_page))

        self.dashboard_page.purchase_button_clicked.connect(self.inventory_page._open_purchase_dialog)
        self.dashboard_page.sale_button_clicked.connect(self.inventory_page._open_sale_dialog)

        self.back_action.triggered.connect(self.go_to_dashboard)

    def _animate_transition(self, old_widget: QWidget, new_widget: QWidget, direction: str):
        """İki sayfa arasında yumuşak bir kayma animasyonu uygular."""
        width = self.frameGeometry().width()
        offset_x = width if direction == 'forward' else -width

        self.stacked_widget.setCurrentWidget(new_widget)
        new_widget.setGeometry(0, 0, width, self.frameGeometry().height())  # Yeni sayfayı başta doğru konuma al

        # Eski sayfayı dışarı kaydıracak animasyon
        anim_old = QPropertyAnimation(old_widget, b"pos")
        anim_old.setStartValue(old_widget.pos())  # Mevcut pozisyondan başla
        anim_old.setEndValue(QPoint(-offset_x, 0))
        anim_old.setDuration(300)
        anim_old.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Yeni sayfayı içeri kaydıracak animasyon
        anim_new = QPropertyAnimation(new_widget, b"pos")
        anim_new.setStartValue(QPoint(offset_x, 0))  # <-- DÜZELTME BURADA
        anim_new.setEndValue(QPoint(0, 0))
        anim_new.setDuration(300)
        anim_new.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # İki animasyonu aynı anda çalıştır
        self.anim_group = QParallelAnimationGroup(self)
        self.anim_group.addAnimation(anim_old)
        self.anim_group.addAnimation(anim_new)
        self.anim_group.start()

    def go_to_page(self, page_widget: QWidget):
        current_widget = self.stacked_widget.currentWidget()
        if current_widget != page_widget:
            self._animate_transition(current_widget, page_widget, direction='forward')
        self.toolbar.setVisible(True)

    def go_to_dashboard(self):
        current_widget = self.stacked_widget.currentWidget()
        if current_widget != self.dashboard_page:
            if hasattr(self.inventory_page, 'load_all_products'):
                self.inventory_page.load_all_products()

            self._animate_transition(current_widget, self.dashboard_page, direction='backward')

        self.toolbar.setVisible(False)