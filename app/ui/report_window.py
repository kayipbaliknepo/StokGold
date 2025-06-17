# app/ui/report_window.py (GÜNCELLENMİŞ VE TAM HALİ)

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableView, QPushButton, QHeaderView, QFrame
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt6.QtCore import Qt

# Yeni get_total_grams fonksiyonunu da import ediyoruz
from app.database import get_total_inventory_value, get_product_counts_by_type, get_total_grams


class ReportWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Envanter Raporu")
        self.setMinimumSize(500, 450)

        self.layout = QVBoxLayout(self)

        # Rapor başlığı
        title_label = QLabel("Genel Stok Raporu")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title_label)

        # Ayırıcı çizgi
        self.layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        # Özet Bilgiler
        # Toplam gram miktarı için etiket
        self.total_grams_label = QLabel("Toplam Gram Miktarı: Hesaplanıyor...")
        self.total_grams_label.setFont(QFont("Arial", 10))
        self.layout.addWidget(self.total_grams_label)

        # Toplam envanter değeri için etiket
        self.total_value_label = QLabel("Toplam Envanter Değeri: Hesaplanıyor...")
        self.total_value_label.setFont(QFont("Arial", 10))
        self.layout.addWidget(self.total_value_label)

        # Ayırıcı çizgi
        self.layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine, frameShadow=QFrame.Shadow.Sunken))

        # Ürün cinsine göre adetleri gösterecek tablo
        self.layout.addWidget(QLabel("Ürün Cinsine Göre Toplam Stok Miktarları:"))
        self.type_counts_table = QTableView()
        self.type_counts_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.type_counts_model = QStandardItemModel()
        self.type_counts_table.setModel(self.type_counts_model)
        self.layout.addWidget(self.type_counts_table)

        # Raporu Yenile Butonu
        self.refresh_button = QPushButton("Raporu Yenile")
        self.refresh_button.clicked.connect(self.load_report_data)
        self.layout.addWidget(self.refresh_button)

        self.load_report_data()

    def load_report_data(self):
        """Veritabanından rapor verilerini çeker ve arayüzü günceller."""
        # 1. Toplam gramı al ve etiketi güncelle
        total_grams = get_total_grams()
        self.total_grams_label.setText(f"<b>Toplam Gram Miktarı:</b> {total_grams:,.2f} gr")

        # 2. Toplam değeri al ve etiketi güncelle
        total_value = get_total_inventory_value()
        self.total_value_label.setText(f"<b>Toplam Envanter Değeri:</b> {total_value:,.2f} TL")

        # 3. Cinslere göre adetleri al ve tabloyu doldur
        type_counts = get_product_counts_by_type()
        self.type_counts_model.clear()
        self.type_counts_model.setHorizontalHeaderLabels(['Ürün Cinsi', 'Toplam Stok Adedi'])  # <-- Başlık güncellendi

        for cins, toplam_stok in type_counts:
            row = [
                QStandardItem(cins),
                QStandardItem(str(toplam_stok))
            ]
            self.type_counts_model.appendRow(row)

        self.type_counts_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)