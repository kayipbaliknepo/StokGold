# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableView, QPushButton, QHeaderView,
    QFrame, QTabWidget, QCalendarWidget, QGridLayout, QHBoxLayout, QDateEdit
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt, QDate
from ..daily_detail_dialog import DailyDetailDialog
from ...database import (
    get_total_inventory_value, get_product_counts_by_type,
    get_total_grams, get_daily_summary, get_statistics_for_period
)


class ReportPage(QWidget):
    CALENDAR_STYLE = """
        QCalendarWidget QToolButton {
            height: 40px; font-size: 14px; background-color: #f8f9fa;
            border: none; margin: 5px; border-radius: 5px;
        }
        QCalendarWidget QToolButton:hover { background-color: #e9ecef; }
        QCalendarWidget QMenu { background-color: white; border: 1px solid #ddd; }
        QCalendarWidget QSpinBox { font-size: 14px; color: #333; }
        QCalendarWidget QTableView {
            selection-background-color: #007bff;
            selection-color: white;
        }
        QCalendarWidget QHeaderView::section {
            background-color: #f1f3f4; padding: 6px;
            border: none; font-weight: bold;
        }
        QCalendarWidget #qt_calendar_calendarview::item#today {
            background-color: #e7f3ff;
            border: 1px solid #80bdff;
            color: #0056b3;
        }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self._create_statistics_tab()
        self._create_daily_activity_tab()
        self._create_inventory_summary_tab()
        self.layout.addWidget(self.tabs)

    def _create_statistics_tab(self):
        tab = QWidget();
        layout = QVBoxLayout(tab);
        layout.setContentsMargins(15, 15, 15, 15);
        layout.setSpacing(15);
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        date_selection_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit(QDate.currentDate().addDays(-30));
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True);
        self.end_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("dd.MM.yyyy");
        self.end_date_edit.setDisplayFormat("dd.MM.yyyy")
        calculate_button = QPushButton("Hesapla");
        calculate_button.setStyleSheet("padding: 5px 15px;")
        date_selection_layout.addWidget(QLabel("Başlangıç:"));
        date_selection_layout.addWidget(self.start_date_edit)
        date_selection_layout.addWidget(QLabel("Bitiş:"));
        date_selection_layout.addWidget(self.end_date_edit)
        date_selection_layout.addStretch();
        date_selection_layout.addWidget(calculate_button)
        layout.addLayout(date_selection_layout)
        results_frame = QFrame();
        results_frame.setFrameShape(QFrame.Shape.StyledPanel)
        results_layout = QGridLayout(results_frame);
        font = QFont();
        font.setPointSize(14);
        font.setBold(True)
        self.stats_total_sales_label = QLabel("Toplam Satış: 0,00 TL");
        self.stats_total_sales_label.setFont(font)
        self.stats_total_cogs_label = QLabel("Satılan Malın Maliyeti: 0,00 TL");
        self.stats_total_cogs_label.setFont(font)
        self.stats_net_profit_label = QLabel("Net Kâr / Zarar: 0,00 TL");
        self.stats_net_profit_label.setFont(font)
        results_layout.addWidget(self.stats_total_sales_label, 0, 0);
        results_layout.addWidget(self.stats_total_cogs_label, 1, 0);
        results_layout.addWidget(self.stats_net_profit_label, 2, 0)
        layout.addWidget(results_frame);
        layout.addStretch()
        calculate_button.clicked.connect(self._calculate_and_show_statistics)
        self.tabs.addTab(tab, "Satış İstatistikleri")

    def _calculate_and_show_statistics(self):
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd");
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        stats = get_statistics_for_period(start_date, end_date)
        total_sales = stats.get('total_sales', 0.0);
        total_cogs = stats.get('total_cogs', 0.0);
        net_profit = stats.get('net_profit', 0.0)
        self.stats_total_sales_label.setText(
            f"<b>Toplam Satış:</b> <span style='font-size:18pt; color:#0275d8;'>{total_sales:,.2f} TL</span>")
        self.stats_total_cogs_label.setText(
            f"<b>Satılan Malın Maliyeti:</b> <span style='font-size:18pt; color:#d9534f;'>{total_cogs:,.2f} TL</span>")
        profit_color = "#5cb85c" if net_profit >= 0 else "#d9534f"
        self.stats_net_profit_label.setText(
            f"<b>Net Kâr / Zarar:</b> <span style='font-size:18pt; color:{profit_color};'>{net_profit:,.2f} TL</span>")

    def _create_daily_activity_tab(self):
        tab = QWidget();
        layout = QVBoxLayout(tab);
        layout.setContentsMargins(15, 15, 15, 15)
        self.calendar = QCalendarWidget();
        self.calendar.setStyleSheet(self.CALENDAR_STYLE);
        self.calendar.clicked.connect(self._open_daily_detail_dialog)
        layout.addWidget(QLabel("İşlem detaylarını görmek için takvimden bir güne tıklayın:"));
        layout.addWidget(self.calendar)
        self.tabs.addTab(tab, "Günlük Hareket Detayları")

    def _create_inventory_summary_tab(self):
        tab = QWidget();
        layout = QVBoxLayout(tab);
        layout.setContentsMargins(15, 15, 15, 15);
        layout.setSpacing(10)
        self.total_grams_label = QLabel();
        self.total_value_label = QLabel();
        font = QFont();
        font.setPointSize(12);
        self.total_grams_label.setFont(font);
        self.total_value_label.setFont(font)
        self.type_counts_table = QTableView();
        self.type_counts_model = QStandardItemModel();
        self.type_counts_table.setModel(self.type_counts_model);
        self.type_counts_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers);
        self.type_counts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        refresh_button = QPushButton("Raporu Yenile");
        refresh_button.clicked.connect(self._load_inventory_data);
        refresh_button.setFixedWidth(120)
        layout.addWidget(self.total_grams_label);
        layout.addWidget(self.total_value_label);
        layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken));
        layout.addWidget(QLabel("Ürün Cinsine Göre Toplam Stok:"));
        layout.addWidget(self.type_counts_table);
        layout.addWidget(refresh_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.tabs.addTab(tab, "Genel Envanter Özeti")

    def _load_inventory_data(self):
        total_grams = get_total_grams();
        self.total_grams_label.setText(f"<b>Stoktaki Toplam Gram:</b> {total_grams:,.2f} gr");
        total_value = get_total_inventory_value();
        self.total_value_label.setText(f"<b>Stoktaki Toplam Maliyet:</b> {total_value:,.2f} TL")
        type_counts = get_product_counts_by_type();
        self.type_counts_model.clear();
        self.type_counts_model.setHorizontalHeaderLabels(['Ürün Cinsi', 'Toplam Stok Adedi']);
        for cins, toplam_stok in type_counts: self.type_counts_model.appendRow(
            [QStandardItem(cins), QStandardItem(str(toplam_stok))])

    def _open_daily_detail_dialog(self, date: QDate):
        detail_dialog = DailyDetailDialog(selected_date=date, parent=self);
        detail_dialog.exec()

    def showEvent(self, event):
        super().showEvent(event)
        self._load_inventory_data()
        self._calculate_and_show_statistics()