# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

import os
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFrame, QGraphicsDropShadowEffect,
    QSizePolicy
)
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor
from PySide6.QtCore import Qt, Signal, QSize

from app.utils import get_icon_path
from app.database import (
    get_daily_summary,
    get_low_stock_products,
    get_latest_products,
    get_product_variety_count
)


class DashboardPage(QWidget):
    """
    Uygulamanın ana kontrol paneli. Sol navigasyon menüsü, canlı veri kartları
    ve akıllı asistan erişimi sunan modern bir arayüz.
    """
    inventory_button_clicked = Signal()
    reports_button_clicked = Signal()
    purchase_button_clicked = Signal()
    sale_button_clicked = Signal()
    assistant_button_clicked = Signal()
    repair_button_clicked = Signal()

    class Styles:
        """Tüm arayüz stillerini merkezi olarak yöneten sınıf."""
        PAGE_BACKGROUND = "background-color: #F0F2F5;"
        SIDEBAR_BACKGROUND = "background-color: #FFFFFF;"
        CONTENT_BACKGROUND = "background-color: transparent;"  # Sayfa arkaplanını kullanır

        # Sol Menü Butonları
        SIDEBAR_BUTTON = """
            QPushButton {
                background-color: transparent;
                border: none;
                color: #4A5568;
                text-align: left;
                padding: 12px 15px;
                font-size: 15px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #F4F7FC;
                color: #2C6EC2;
            }
            QPushButton:pressed {
                background-color: #EBF5FF;
            }
        """
        # Veri Kartları
        KPI_CARD_STYLE = """
            QFrame {
                background-color: white;
                border: none;
                border-radius: 12px;
            }
        """
        KPI_VALUE_STYLE = "font-size: 28px; font-weight: bold; color: #1F2937;"
        KPI_TITLE_STYLE = "font-size: 14px; font-weight: bold; color: #6B7280;"

        # Akıllı Asistan Butonu
        AI_BUTTON_STYLE = """
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 #4F46E5, stop:1 #7C3AED);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 18px;
            }
            QPushButton:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 #4338CA, stop:1 #6D28D9);
            }
            QPushButton:pressed {
                background-color: #4338CA;
            }
        """
        HEADER_TITLE = "font-size: 24px; font-weight: bold; color: #1F2937;"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self.Styles.PAGE_BACKGROUND)
        self._setup_ui()
        self._connect_signals()

    def showEvent(self, event):
        super().showEvent(event)
        self.update_dashboard_data()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self._create_sidebar()
        content_area = self._create_content_area()

        main_layout.addWidget(sidebar, stretch=1)
        main_layout.addWidget(content_area, stretch=4)

    def _create_sidebar(self) -> QWidget:
        sidebar_widget = QWidget()
        sidebar_widget.setStyleSheet(self.Styles.SIDEBAR_BACKGROUND)
        sidebar_widget.setFixedWidth(260)

        layout = QVBoxLayout(sidebar_widget)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)

        logo_label = QLabel()
        logo_pixmap = QPixmap(get_icon_path('logo.png'))
        logo_label.setPixmap(
            logo_pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setContentsMargins(0, 0, 0, 20)

        self.purchase_button = self._create_sidebar_button("Stok Alış Yap", "purchase.png")
        self.sale_button = self._create_sidebar_button("Stok Satışı Yap", "sale.png")
        self.inventory_button = self._create_sidebar_button("Envanteri Görüntüle", "inventory.png")
        self.reports_button = self._create_sidebar_button("Raporları Görüntüle", "report.png")
        self.repair_button = self._create_sidebar_button("Tamir Takibi", "repair.png")

        self.assistant_button = QPushButton(" Akıllı Asistan")
        self.assistant_button.setIcon(QIcon(get_icon_path("assistant.png")))
        self.assistant_button.setIconSize(QSize(24, 24))
        self.assistant_button.setStyleSheet(self.Styles.AI_BUTTON_STYLE)

        layout.addWidget(logo_label)
        layout.addWidget(self.purchase_button)
        layout.addWidget(self.sale_button)
        layout.addWidget(self.inventory_button)
        layout.addWidget(self.reports_button)
        layout.addWidget(self.repair_button)
        layout.addStretch()
        layout.addWidget(self.assistant_button)

        return sidebar_widget

    def _create_content_area(self) -> QWidget:
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(40, 25, 40, 40)
        layout.setSpacing(25)

        header_layout = self._create_header()
        kpi_layout = self._create_kpi_grid()

        layout.addLayout(header_layout)
        layout.addLayout(kpi_layout)
        layout.addStretch()
        return content_widget

    def _create_header(self) -> QHBoxLayout:
        header_layout = QHBoxLayout()
        title_label = QLabel("Genel Bakış")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setStyleSheet(self.Styles.HEADER_TITLE)

        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(QIcon(get_icon_path("refresh.png")))
        self.refresh_button.setFixedSize(40, 40)
        self.refresh_button.setStyleSheet(
            "QPushButton { border: 1px solid #E5E7EB; border-radius: 20px; background-color: white; } QPushButton:hover { background-color: #F9FAFB; }")
        self.refresh_button.setToolTip("Verileri Yenile")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)
        return header_layout

    def _create_kpi_grid(self) -> QGridLayout:
        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(25)

        self.daily_sales_card = self._create_kpi_card("Bugünkü Satış Tutarı", "sales.png")
        self.product_variety_card = self._create_kpi_card("Toplam Ürün Çeşidi", "inventory.png")
        self.low_stock_card = self._create_kpi_card("Kritik Stoktaki Ürünler", "stock_alert.png", is_list=True)
        self.recent_products_card = self._create_kpi_card("Son Eklenenler", "recent.png", is_list=True)

        kpi_layout.addWidget(self.daily_sales_card, 0, 0)
        kpi_layout.addWidget(self.product_variety_card, 0, 1)
        kpi_layout.addWidget(self.low_stock_card, 1, 0)
        kpi_layout.addWidget(self.recent_products_card, 1, 1)
        return kpi_layout

    def _create_kpi_card(self, title: str, icon_name: str, is_list=False) -> QFrame:
        card = QFrame()
        card.setStyleSheet(self.Styles.KPI_CARD_STYLE)
        card.setMinimumHeight(150)

        # Gölge efekti ekliyoruz
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 5)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setStyleSheet(self.Styles.KPI_TITLE_STYLE)

        if is_list:
            data_widget = QTextEdit()
            data_widget.setReadOnly(True)
            data_widget.setStyleSheet(
                "QTextEdit { border:none; background-color:transparent; font-size: 14px; color: #374151; }")
        else:
            data_widget = QLabel("...")
            data_widget.setStyleSheet(self.Styles.KPI_VALUE_STYLE)

        variable_name = title.lower().replace(' ', '_').replace('ı', 'i').replace('ö', 'o').replace('ü', 'u').replace(
            'ç', 'c').replace('ş', 's').replace('ğ', 'g')
        setattr(self, f"{variable_name}_data", data_widget)

        layout.addWidget(title_label)
        layout.addWidget(data_widget, stretch=1)
        return card

    def _create_sidebar_button(self, text, icon_name):
        button = QPushButton(f"  {text}")
        button.setIcon(QIcon(get_icon_path(icon_name)))
        button.setIconSize(QSize(22, 22))
        button.setStyleSheet(self.Styles.SIDEBAR_BUTTON)
        return button

    def _connect_signals(self):
        self.refresh_button.clicked.connect(self.update_dashboard_data)
        self.purchase_button.clicked.connect(self.purchase_button_clicked.emit)
        self.sale_button.clicked.connect(self.sale_button_clicked.emit)
        self.inventory_button.clicked.connect(self.inventory_button_clicked.emit)
        self.reports_button.clicked.connect(self.reports_button_clicked.emit)
        self.assistant_button.clicked.connect(self.assistant_button_clicked.emit)
        self.repair_button.clicked.connect(self.repair_button_clicked.emit)

    def update_dashboard_data(self):
        print("Kontrol Paneli verileri yenileniyor...")
        try:
            today_str = date.today().strftime("%Y-%m-%d")
            daily_summary = get_daily_summary(today_str)
            self.bugunku_satis_tutari_data.setText(f"{daily_summary.get('satis', 0.0):,.2f} TL")

            low_stock_items = get_low_stock_products(threshold=5)
            if low_stock_items:
                low_stock_html = "<ul style='margin:0; padding-left:15px; list-style-type: none;'>" + "".join([
                                                                                                                  f"<li style='margin-bottom:6px;'>&#8226; {row['cins']} (<b style=color:#D9534F>{row['stok_adeti']}</b>)</li>"
                                                                                                                  for
                                                                                                                  row in
                                                                                                                  low_stock_items]) + "</ul>"
                self.kritik_stoktaki_urunler_data.setHtml(low_stock_html)
            else:
                self.kritik_stoktaki_urunler_data.setHtml(
                    "<p style='color: #16A34A; font-weight:bold; font-size:14px;'>Kritik seviyede ürün yok.</p>")

            variety_count = get_product_variety_count()
            self.toplam_urun_cesidi_data.setText(str(variety_count))

            latest_products = get_latest_products(limit=5)
            if latest_products:
                latest_html = "<ul style='margin:0; padding-left:15px; list-style-type: none;'>" + "".join(
                    [f"<li style='margin-bottom:6px;'>&#8226; {cins}</li>" for cins, kod in latest_products]) + "</ul>"
                self.son_eklenenler_data.setHtml(latest_html)
            else:
                self.son_eklenenler_data.setHtml("<p style='color: #9CA3AF;'>Veritabanına henüz ürün eklenmemiş.</p>")
        except Exception as e:
            print(f"Dashboard verileri güncellenirken hata: {e}")