# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableView, QHeaderView, QTabWidget, QWidget
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt
from app.database import get_transactions_for_date

class DailyDetailDialog(QDialog):
    def __init__(self, selected_date, parent=None):
        super().__init__(parent)
        self.selected_date = selected_date


        formatted_date = self.selected_date.toString("dd-MM-yyyy")
        self.setWindowTitle(f"{formatted_date} Günü İşlem Detayları")
        self.setMinimumSize(800, 600)

        self.layout = QVBoxLayout(self)


        self.sales_table = self._create_table()
        self.purchases_table = self._create_table()


        tabs = QTabWidget()
        tabs.addTab(self.sales_table, "Günün Satışları")
        tabs.addTab(self.purchases_table, "Günün Alışları")

        self.layout.addWidget(tabs)

        self._load_details()

    def _create_table(self):

        table = QTableView()
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(True)
        table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        return table

    def _load_details(self):

        date_str = self.selected_date.toString("yyyy-MM-dd")
        transactions = get_transactions_for_date(date_str)


        sales_model = QStandardItemModel()
        sales_model.setHorizontalHeaderLabels(['Saat', 'Ürün Kodu', 'Cins', 'Adet', 'Birim Fiyat', 'Toplam Tutar'])

        purchases_model = QStandardItemModel()
        purchases_model.setHorizontalHeaderLabels(['Saat', 'Ürün Kodu', 'Cins', 'Adet', 'Birim Fiyat', 'Toplam Tutar'])

        for tx in transactions:
            time_str = tx['tarih'][11:16]  # Sadece saati ve dakikayı al

            row = [
                QStandardItem(time_str),
                QStandardItem(tx['urun_kodu']),
                QStandardItem(tx['cins']),
                QStandardItem(str(tx['adet'])),
                QStandardItem(f"{tx['birim_fiyat']:,.2f} TL"),
                QStandardItem(f"{tx['toplam_tutar']:,.2f} TL")
            ]

            if tx['tip'] == 'Satış':
                sales_model.appendRow(row)
            elif tx['tip'] == 'Alış':
                purchases_model.appendRow(row)

        self.sales_table.setModel(sales_model)
        self.purchases_table.setModel(purchases_model)

        self.sales_table.resizeColumnsToContents()
        self.purchases_table.resizeColumnsToContents()