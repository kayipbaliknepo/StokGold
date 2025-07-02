# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableView, QHeaderView,
    QTabWidget, QWidget, QFrame, QHBoxLayout
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt

from app.database import get_transactions_for_date


class DailyDetailDialog(QDialog):
    """
    Belirli bir günün alış ve satış işlemlerini modern bir arayüzde
    detaylı olarak gösteren diyalog penceresi.
    """

    class Styles:
        """Tüm arayüz stillerini merkezi olarak yöneten sınıf."""
        DIALOG_BACKGROUND = "background-color: #F4F7FC;"
        TITLE_LABEL = "font-size: 20px; font-weight: bold; color: #1F2937;"
        TAB_WIDGET = """
            QTabWidget::pane {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
                margin-top: -1px;
            }
            QTabBar::tab {
                background-color: #F3F4F6;
                border: 1px solid #E5E7EB;
                border-bottom: none; 
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 120px;
                font-size: 14px;
                padding: 10px 20px;
                font-weight: bold;
                color: #4B5563;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background-color: white;
                color: #1F2937;
            }
        """
        TABLE_STYLE = """
            QTableView {
                background-color: white;
                border: none;
                gridline-color: #F3F4F6;
                font-size: 14px;
            }
            QTableView::item { padding: 10px 8px; border-bottom: 1px solid #F3F4F6; }
            QTableView::item:selected { background-color: #EBF5FF; color: #1E3A8A; }
            QHeaderView::section {
                background-color: #F9FAFB;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                padding: 12px 8px;
                font-weight: bold;
                color: #374151;
            }
        """
        SUMMARY_FRAME = "background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 15px;"
        SUMMARY_LABEL = "font-size: 14pt; font-weight: bold;"

    def __init__(self, selected_date, parent=None):
        super().__init__(parent)
        self.selected_date = selected_date

        self.setWindowTitle("Günlük İşlem Detayları")
        self.setMinimumSize(900, 650)
        self.setStyleSheet(self.Styles.DIALOG_BACKGROUND)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Başlık
        formatted_date = self.selected_date.toString("dd MMMM yyyy")
        title_label = QLabel(f"{formatted_date} Günü İşlemleri")
        title_label.setStyleSheet(self.Styles.TITLE_LABEL)
        self.layout.addWidget(title_label)

        # Sekmeli yapı
        tabs = QTabWidget()
        tabs.setStyleSheet(self.Styles.TAB_WIDGET)

        self.sales_table = self._create_table()
        self.purchases_table = self._create_table()

        tabs.addTab(self.sales_table, "Günün Satışları")
        tabs.addTab(self.purchases_table, "Günün Alışları")

        self.layout.addWidget(tabs)

        # Özet Alanı
        summary_frame = self._create_summary_frame()
        self.layout.addWidget(summary_frame)

        self._load_details()

    def _create_table(self) -> QTableView:
        """Detay tabloları için standart bir QTableView oluşturur."""
        table = QTableView()
        table.setStyleSheet(self.Styles.TABLE_STYLE)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(True)
        table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        return table

    def _create_summary_frame(self) -> QFrame:
        """Günün toplam alış ve satış tutarlarını gösteren özet alanını oluşturur."""
        frame = QFrame()
        frame.setStyleSheet(self.Styles.SUMMARY_FRAME)
        layout = QHBoxLayout(frame)

        self.total_sales_label = QLabel("Toplam Satış: 0,00 TL")
        self.total_sales_label.setStyleSheet(f"color: #5cb85c; {self.Styles.SUMMARY_LABEL}")

        self.total_purchases_label = QLabel("Toplam Alış: 0,00 TL")
        self.total_purchases_label.setStyleSheet(f"color: #d9534f; {self.Styles.SUMMARY_LABEL}")

        layout.addStretch()
        layout.addWidget(self.total_purchases_label)
        layout.addSpacing(40)
        layout.addWidget(self.total_sales_label)
        layout.addStretch()

        return frame

    def _load_details(self):
        """Veritabanından o günün işlemlerini çeker, tabloları ve özet alanını doldurur."""
        date_str = self.selected_date.toString("yyyy-MM-dd")
        transactions = get_transactions_for_date(date_str)

        sales_model = QStandardItemModel()
        sales_model.setHorizontalHeaderLabels(['Saat', 'Ürün Kodu', 'Cins', 'Adet', 'Birim Fiyat', 'Toplam Tutar'])

        purchases_model = QStandardItemModel()
        purchases_model.setHorizontalHeaderLabels(['Saat', 'Ürün Kodu', 'Cins', 'Adet', 'Birim Fiyat', 'Toplam Tutar'])

        total_sales = 0.0
        total_purchases = 0.0

        for tx in transactions:
            time_str = datetime.strptime(tx['tarih'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')

            item_saat = QStandardItem(time_str)
            item_kod = QStandardItem(tx['urun_kodu'])
            item_cins = QStandardItem(tx['cins'])
            item_adet = QStandardItem(str(tx['adet']));
            item_adet.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_fiyat = QStandardItem(f"{tx['birim_fiyat']:,.2f} TL");
            item_fiyat.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_tutar = QStandardItem(f"{tx['toplam_tutar']:,.2f} TL");
            item_tutar.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            row = [item_saat, item_kod, item_cins, item_adet, item_fiyat, item_tutar]

            if tx['tip'] == 'Satış':
                sales_model.appendRow(row)
                total_sales += tx['toplam_tutar']
            elif tx['tip'] == 'Alış':
                purchases_model.appendRow(row)
                total_purchases += tx['toplam_tutar']

        self.sales_table.setModel(sales_model)
        self.purchases_table.setModel(purchases_model)

        self.sales_table.resizeColumnsToContents()
        self.purchases_table.resizeColumnsToContents()

        # Özet etiketlerini güncelle
        self.total_sales_label.setText(f"Toplam Satış: {total_sales:,.2f} TL")
        self.total_purchases_label.setText(f"Toplam Alış: {total_purchases:,.2f} TL")
