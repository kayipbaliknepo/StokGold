import sys
import os
import traceback
from PySide6.QtWidgets import QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QToolBar, QMessageBox
from PySide6.QtGui import QIcon, QAction, QGuiApplication
from PySide6.QtCore import QSize, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint

from app.utils import get_icon_path
# Artık check_ollama_status'u import etmiyoruz
from .pages.dashboard_page import DashboardPage
from .pages.inventory_page import InventoryPage
from .pages.report_page import ReportPage
from .assistant_dialog import AssistantDialog


class MainApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StokGold")
        self.setWindowIcon(QIcon(get_icon_path('app_icon.ico')))
        self.setStyleSheet("background-color: #f0f0f0;")

        screen_size = QGuiApplication.primaryScreen().availableGeometry().size()
        self.resize(int(screen_size.width() * 0.85), int(screen_size.height() * 0.85))
        self._center_window()

        self._setup_ui()
        self._connect_signals()
        self.go_to_dashboard()

    def _setup_ui(self):
        self.toolbar = QToolBar("Ana Araç Çubuğu")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        back_icon = QIcon(get_icon_path("back.png"))
        self.back_action = QAction(back_icon, "Geri", self)
        self.toolbar.addAction(self.back_action)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self._create_pages()
        # Buton yapılandırma fonksiyonu kaldırıldı

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
        self.dashboard_page.assistant_button_clicked.connect(self._open_assistant_dialog)
        self.dashboard_page.purchase_button_clicked.connect(self.inventory_page._open_purchase_dialog)
        self.dashboard_page.sale_button_clicked.connect(self.inventory_page._open_sale_dialog)
        self.back_action.triggered.connect(self.go_to_dashboard)

    def _open_assistant_dialog(self):
        """Akıllı Asistan sohbet diyalogunu doğrudan açar."""
        dialog = AssistantDialog(parent=self)
        dialog.exec()

    # Geri kalan tüm fonksiyonlar (_center_window, _animate_transition, go_to..., vb.) aynı kalır.
    def _center_window(self):
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry();
        self.move(screen_geometry.center() - self.frameGeometry().center())

    def _animate_transition(self, old_widget: QWidget, new_widget: QWidget, direction: str):
        width = self.frameGeometry().width();
        offset_x = width if direction == 'forward' else -width;
        new_widget.setGeometry(offset_x, 0, width, self.frameGeometry().height());
        self.stacked_widget.setCurrentWidget(new_widget);
        anim_old = QPropertyAnimation(old_widget, b"pos");
        anim_old.setEndValue(QPoint(-offset_x, 0));
        anim_old.setDuration(300);
        anim_old.setEasingCurve(QEasingCurve.Type.InOutCubic);
        anim_new = QPropertyAnimation(new_widget, b"pos");
        anim_new.setStartValue(QPoint(offset_x, 0));
        anim_new.setEndValue(QPoint(0, 0));
        anim_new.setDuration(300);
        anim_new.setEasingCurve(QEasingCurve.Type.InOutCubic);
        self.anim_group = QParallelAnimationGroup(self);
        self.anim_group.addAnimation(anim_old);
        self.anim_group.addAnimation(anim_new);
        self.anim_group.start()

    def go_to_page(self, page_widget: QWidget):
        current_widget = self.stacked_widget.currentWidget();
        if current_widget != page_widget: self._animate_transition(current_widget, page_widget, direction='forward')
        self.toolbar.setVisible(True)

    def go_to_dashboard(self):
        current_widget = self.stacked_widget.currentWidget()
        if current_widget != self.dashboard_page:
            if hasattr(self.inventory_page, 'load_all_products'): self.inventory_page.load_all_products()
            self._animate_transition(current_widget, self.dashboard_page, direction='backward')
        self.toolbar.setVisible(False)
