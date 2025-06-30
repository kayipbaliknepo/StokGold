# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableView, QPushButton, QHeaderView,
    QFrame, QTabWidget, QCalendarWidget, QGridLayout, QHBoxLayout, QDateEdit
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont, QIcon
from PySide6.QtCore import Qt, QDate, QSize, QEvent

from ..daily_detail_dialog import DailyDetailDialog
from ...utils import get_icon_path
from ...database import (
    get_total_inventory_value, get_product_counts_by_type,
    get_total_grams, get_daily_summary, get_statistics_for_period
)


class ReportPage(QWidget):
    """Modern bir tasarıma sahip, sekmeli raporlama sayfası."""

    class Styles:
        """Tüm arayüz stillerini merkezi olarak yöneten sınıf."""
        PAGE_BACKGROUND = "background-color: #F4F7FC;"
        TAB_WIDGET = """
            QTabWidget::pane {
                border: none;
                border-top: 1px solid #E5E7EB;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-bottom: none; 
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 180px;
                font-size: 14px;
                padding: 12px 20px;
                font-weight: bold;
                color: #6B7280;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #1F2937;
            }
            QTabBar::tab:!selected:hover {
                background-color: #F0F2F5;
            }
        """
        CALENDAR_STYLE = """
            QCalendarWidget QToolButton {
                height: 40px; font-size: 14px; color: #333;
                background-color: #ffffff; border: 1px solid #dcdcdc; border-radius: 5px;
            }
            QCalendarWidget QToolButton:hover { background-color: #f0f0f0; }
            QCalendarWidget QTableView { selection-background-color: #4A90E2; selection-color: white; }
            QCalendarWidget QHeaderView::section {
                background-color: #F9FAFB; padding: 8px;
                border: none; font-weight: bold; color: #374151;
            }
            QCalendarWidget #qt_calendar_calendarview::item#today {
                outline: 2px solid #80bdff;
                color: #0056b3;
            }
        """
        FRAME_STYLE = "background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 20px;"
        TITLE_LABEL = "font-size: 12pt; color: #6B7280;"
        STATS_LABEL = "font-size: 22pt; font-weight: bold;"
        BUTTON_PRIMARY = """
            QPushButton {
                background-color: #4A90E2; color: white; border: none;
                padding: 8px 16px; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #4281CB; }
        """
        TABLE_STYLE = """
            QTableView { background-color: white; border: none; gridline-color: #F3F4F6; font-size: 14px; }
            QTableView::item { padding: 10px 8px; border-bottom: 1px solid #F3F4F6; min-height: 25px; }
            QTableView::item:selected { background-color: #EBF5FF; color: #1E3A8A; }
            QHeaderView::section {
                background-color: #F9FAFB; border: none; border-bottom: 2px solid #E5E7EB;
                padding: 12px 8px; font-weight: bold; color: #374151;
            }
        """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self.Styles.PAGE_BACKGROUND)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(self.Styles.TAB_WIDGET)

        self._create_statistics_tab()
        self._create_daily_activity_tab()
        self._create_inventory_summary_tab()

        self.layout.addWidget(self.tabs)

    def eventFilter(self, source, event):
        """Takvim üzerindeki fare tekerleği olaylarını yakalar ve engeller."""
        # Takvimin içindeki herhangi bir widget'tan gelen tekerlek olayını engelle
        if event.type() == QEvent.Type.Wheel and source.parent() == self.calendar:
            return True
        return super().eventFilter(source, event)

    def _create_daily_activity_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(25, 25, 25, 25)

        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet(self.Styles.CALENDAR_STYLE)

        # 1. Sol taraftaki hafta numarası sütununu gizle
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

        # 2. Fare tekerleği olaylarını engellemek için takvime ve alt bileşenlerine olay filtresi kur
        self.calendar.installEventFilter(self)
        for child in self.calendar.findChildren(QWidget):
            child.installEventFilter(self)

        self.calendar.clicked.connect(self._open_daily_detail_dialog)

        info_label = QLabel("İşlem detaylarını görmek için takvimden bir güne tıklayın.")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #6B7280; font-style: italic;")

        layout.addWidget(info_label)
        layout.addWidget(self.calendar)

        self.tabs.addTab(tab, "Günlük Hareket Detayları")


    def _create_statistics_tab(self):
        """Aylık/günlük kar/zarar gibi detaylı satış istatistikleri için bir sekme oluşturur."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        date_selection_layout = QHBoxLayout()
        date_selection_layout.setSpacing(10)
        self.start_date_edit = QDateEdit(QDate.currentDate().addDays(-30))
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True);
        self.end_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("dd MMMM yyyy");
        self.end_date_edit.setDisplayFormat("dd MMMM yyyy")

        calculate_button = QPushButton(" Hesapla")
        calculate_button.setIcon(QIcon(get_icon_path("calculate.png")))  # Yeni ikon
        calculate_button.setStyleSheet(self.Styles.BUTTON_PRIMARY)

        date_selection_layout.addWidget(QLabel("Başlangıç:"))
        date_selection_layout.addWidget(self.start_date_edit)
        date_selection_layout.addWidget(QLabel("Bitiş:"))
        date_selection_layout.addWidget(self.end_date_edit)
        date_selection_layout.addStretch()
        date_selection_layout.addWidget(calculate_button)
        layout.addLayout(date_selection_layout)

        results_frame = QFrame();
        results_frame.setStyleSheet(self.Styles.FRAME_STYLE)
        results_layout = QGridLayout(results_frame)
        results_layout.setSpacing(20)

        self.stats_total_sales_label = QLabel()
        self.stats_total_cogs_label = QLabel()
        self.stats_net_profit_label = QLabel()

        results_layout.addWidget(self.stats_total_sales_label, 0, 0)
        results_layout.addWidget(self.stats_total_cogs_label, 1, 0)
        results_layout.addWidget(self.stats_net_profit_label, 2, 0)

        layout.addWidget(results_frame)
        layout.addStretch()

        calculate_button.clicked.connect(self._calculate_and_show_statistics)
        self.tabs.addTab(tab, "Satış İstatistikleri")
        self._calculate_and_show_statistics()

    def _calculate_and_show_statistics(self):
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        stats = get_statistics_for_period(start_date, end_date)

        total_sales = stats.get('total_sales', 0.0)
        total_cogs = stats.get('total_cogs', 0.0)
        net_profit = stats.get('net_profit', 0.0)


        self.stats_total_sales_label.setText(
            f"<p style='color:#6B7280;font-size:12pt;'>Toplam Satış</p><p style='color:#0275d8;{self.Styles.STATS_LABEL}'>{total_sales:,.2f} TL</p>")
        self.stats_total_cogs_label.setText(
            f"<p style='color:#6B7280;font-size:12pt;'>Satılan Malın Maliyeti</p><p style='color:#d9534f;{self.Styles.STATS_LABEL}'>{total_cogs:,.2f} TL</p>")

        profit_color = "#5cb85c" if net_profit >= 0 else "#d9534f"
        self.stats_net_profit_label.setText(
            f"<p style='color:#6B7280;font-size:12pt;'>Net Kâr / Zarar</p><p style='color:{profit_color};{self.Styles.STATS_LABEL}'>{net_profit:,.2f} TL</p>")


    def _create_inventory_summary_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(25, 25, 25, 25);
        layout.setSpacing(15)

        summary_frame = QFrame();
        summary_frame.setStyleSheet(self.Styles.FRAME_STYLE)
        summary_layout = QHBoxLayout(summary_frame)

        self.total_grams_label = QLabel()
        self.total_value_label = QLabel()

        summary_layout.addWidget(self.total_grams_label, alignment=Qt.AlignmentFlag.AlignCenter)
        summary_layout.addWidget(self.total_value_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.type_counts_table = QTableView()
        self.type_counts_model = QStandardItemModel()
        self.type_counts_table.setModel(self.type_counts_model)
        self.type_counts_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.type_counts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.type_counts_table.setStyleSheet(self.Styles.TABLE_STYLE)
        self.type_counts_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        layout.addWidget(summary_frame)
        layout.addWidget(QLabel("Ürün Cinsine Göre Toplam Stok:"))
        layout.addWidget(self.type_counts_table)

        self.tabs.addTab(tab, "Genel Envanter Özeti")

    def _load_inventory_data(self):
        total_grams = get_total_grams()
        self.total_grams_label.setText(
            f"<p style='color:#6B7280;font-size:11pt;'>Stoktaki Toplam Gram</p><p style='font-size:16pt;font-weight:bold;'>{total_grams:,.2f} gr</p>")
        total_value = get_total_inventory_value()
        self.total_value_label.setText(
            f"<p style='color:#6B7280;font-size:11pt;'>Stoktaki Toplam Maliyet</p><p style='font-size:16pt;font-weight:bold;'>{total_value:,.2f} TL</p>")
        type_counts = get_product_counts_by_type()
        self.type_counts_model.clear()
        self.type_counts_model.setHorizontalHeaderLabels(['Ürün Cinsi', 'Toplam Stok Adedi'])
        for cins, toplam_stok in type_counts:
            item_cins = QStandardItem(cins)
            item_stok = QStandardItem(str(toplam_stok))
            item_stok.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.type_counts_model.appendRow([item_cins, item_stok])

    def _open_daily_detail_dialog(self, date: QDate):
        detail_dialog = DailyDetailDialog(selected_date=date, parent=self)
        detail_dialog.exec()

    def showEvent(self, event):
        super().showEvent(event)
        self._load_inventory_data()
        self._calculate_and_show_statistics()
