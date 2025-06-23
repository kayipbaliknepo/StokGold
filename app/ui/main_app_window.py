# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

# app/ui/main_app_window.py (NİHAİ DÜZELTİLMİŞ HALİ)

import sys
import os
import traceback
from PySide6.QtWidgets import QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QToolBar, QMessageBox
from PySide6.QtGui import QIcon, QAction, QGuiApplication
from PySide6.QtCore import QSize, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint

# Yerel modül importları
from app.utils import get_icon_path
from app.agent.agent_core import check_ollama_status
from .pages.dashboard_page import DashboardPage
from .pages.inventory_page import InventoryPage
from .pages.report_page import ReportPage
from .assistant_dialog import AssistantDialog

from app.agent.agent_core import check_ollama_status



class MainApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- DEĞİŞİKLİK BURADA ---
        # 1. Program başlar başlamaz durumu kontrol et ve sonucu self.assistant_status'a kaydet.
        self._check_assistant_availability()

        # 2. Pencerenin geri kalanını kurmaya devam et.
        self.setWindowTitle("StokGold")

        screen_size = QGuiApplication.primaryScreen().availableGeometry().size()
        self.resize(int(screen_size.width() * 0.85), int(screen_size.height() * 0.85))

        self.setWindowIcon(QIcon(get_icon_path('app_icon.ico')))
        self.setStyleSheet("background-color: #f0f0f0;")

        self.toolbar = QToolBar("Ana Araç Çubuğu")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        back_icon = QIcon(get_icon_path("back.png"))
        self.back_action = QAction(back_icon, "Geri", self)
        self.toolbar.addAction(self.back_action)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self._create_pages()
        self._configure_assistant_button()
        self._connect_signals()

        self.go_to_dashboard()
        self._center_window()

    def _check_assistant_availability(self):
        """Uygulama başlangıcında Ollama'nın durumunu kontrol eder ve sonucu saklar."""
        print("Akıllı Asistan durumu kontrol ediliyor...")
        self.assistant_status = check_ollama_status()
        # Gelen sonucu ve mesajı terminale yazdırarak kontrol ediyoruz
        print(f"Asistan Durumu: {self.assistant_status['message']}")


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


        if self.assistant_status.get('ok'):
            self.dashboard_page.assistant_button.setEnabled(True)
            self.dashboard_page.assistant_button.setToolTip(self.assistant_status.get('message'))
        else:
            self.dashboard_page.assistant_button.setEnabled(False)
            self.dashboard_page.assistant_button.setToolTip(self.assistant_status.get('message'))

    def _connect_signals(self):
        self.dashboard_page.inventory_button_clicked.connect(lambda: self.go_to_page(self.inventory_page))
        self.dashboard_page.reports_button_clicked.connect(lambda: self.go_to_page(self.reports_page))

        self.dashboard_page.purchase_button_clicked.connect(self.inventory_page._open_purchase_dialog)
        self.dashboard_page.sale_button_clicked.connect(self.inventory_page._open_sale_dialog)

        self.back_action.triggered.connect(self.go_to_dashboard)
        self.dashboard_page.assistant_button_clicked.connect(self._open_assistant_dialog)

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

    def _open_assistant_dialog(self):
        """Akıllı Asistan sohbet diyalogunu açar."""
        # Diyalog bir QDialog olduğu için .exec() ile açmak en iyisidir
        dialog = AssistantDialog(self)
        dialog.exec()

    def _configure_assistant_button(self):
        """Ollama durumuna göre Akıllı Asistan butonunu ayarlar."""
        if self.assistant_status.get('ok'):
            self.dashboard_page.assistant_button.setEnabled(True)
            self.dashboard_page.assistant_button.setToolTip(self.assistant_status.get('message', 'Asistan hazır.'))
        else:
            self.dashboard_page.assistant_button.setEnabled(False)
            self.dashboard_page.assistant_button.setToolTip(self.assistant_status.get('message'))

    def _open_assistant_dialog(self):
        """Akıllı Asistan sohbet diyalogunu açar ve gerekli model adını iletir."""

        # 1. Program başında sakladığımız status'tan model adını al
        model_to_use = self.assistant_status.get('model_name')

        # 2. Bir model adı bulunamazsa hata göster ve işlemi durdur (güvenlik önlemi)
        if not model_to_use:
            QMessageBox.warning(self, "Model Bulunamadı",
                                "Kullanılacak bir LLM modeli bulunamadı. Lütfen Ollama ayarlarınızı kontrol edin.")
            return

        # 3. Diyalogu bu spesifik ve doğrulanmış model adıyla başlat
        dialog = AssistantDialog(model_name=model_to_use, parent=self)
        dialog.exec()