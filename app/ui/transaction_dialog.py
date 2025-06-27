import os
import traceback
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QWidget, QHBoxLayout, QInputDialog, QMessageBox, QLineEdit
)
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6.QtCore import Qt, QSize

from app.utils import get_icon_path
from app.models import Urun
from app.database import get_all_products, update_stock, log_transaction, search_products


class ProductListItem(QWidget):
    """
    Listede gösterilecek her bir ürün için tasarlanmış özel görsel bileşen (widget).
    """

    def __init__(self, urun: Urun):
        super().__init__()
        self.urun = urun

        # Ana layout yatay olacak (Resim solda, Bilgiler sağda)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Resim Alanı
        image_label = QLabel()
        image_label.setFixedSize(72, 72)  # Daha büyük ve sabit boyut
        image_label.setStyleSheet("background-color: #E5E7EB; border-radius: 6px;")
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if urun.resim_yolu and os.path.exists(urun.resim_yolu):
            pixmap = QPixmap(urun.resim_yolu)
            image_label.setPixmap(
                pixmap.scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            font = image_label.font();
            font.setPointSize(9);
            image_label.setFont(font)
            image_label.setText("Resim\nYok")

        layout.addWidget(image_label)

        # Bilgi Alanı (Dikey)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        cins_label = QLabel(urun.cins)
        cins_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        cins_label.setFont(cins_font)
        cins_label.setStyleSheet("color: #1F2937;")

        kod_label = QLabel(f"Kod: {urun.urun_kodu}")
        kod_label.setStyleSheet("color: #6B7280;")

        stok_label = QLabel(f"Mevcut Stok: {urun.stok_adeti}")
        stok_label.setStyleSheet("color: #374151; font-weight: bold;")

        info_layout.addWidget(cins_label)
        info_layout.addWidget(kod_label)
        info_layout.addStretch()  # Kod ile stok arasına boşluk koy
        info_layout.addWidget(stok_label)

        layout.addLayout(info_layout)
        layout.addStretch()  # Bilgilerin sağ tarafını boş bırak


class TransactionDialog(QDialog):
    """
    Modern tasarımlı Stok Alış ve Stok Satış penceresi.
    """

    def __init__(self, mode: str, parent=None):
        super().__init__(parent)
        self.mode = mode

        self.setWindowTitle(f"Stok {mode.capitalize()} İşlemi")
        self.resize(600, 700)
        self.setStyleSheet("background-color: #F4F7FC;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Arama/Filtreleme Kutusu
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filtrelemek için ürün kodu veya cinsi yazın...")
        self.filter_input.setStyleSheet("""
            QLineEdit {
                background-color: white; border: 1px solid #D1D5DB;
                border-radius: 6px; padding: 10px; font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #4A90E2; }
        """)
        self.filter_input.textChanged.connect(self._filter_product_list)
        self.layout.addWidget(self.filter_input)

        # Ürün Listesi Alanı
        self.product_list_widget = QListWidget()
        self.product_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
            }
            QListWidget::item {
                border-bottom: 1px solid #F3F4F6;
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #EBF5FF;
            }
            QListWidget::item:selected {
                background-color: #D1E4FF;
                color: #1E3A8A;
            }
        """)
        self.product_list_widget.itemClicked.connect(self._on_product_selected)
        self.layout.addWidget(self.product_list_widget)

        self._load_all_products()

    def _populate_list_with_data(self, urunler: list):
        """Verilen ürün listesine göre QListWidget'ı temizler ve doldurur."""
        self.product_list_widget.clear()
        for urun in urunler:
            list_item = QListWidgetItem(self.product_list_widget)
            custom_widget = ProductListItem(urun)
            list_item.setSizeHint(QSize(custom_widget.sizeHint().width(), 85))  # Sabit yükseklik
            self.product_list_widget.addItem(list_item)
            self.product_list_widget.setItemWidget(list_item, custom_widget)

    def _load_all_products(self):
        """Tüm ürünleri veritabanından çeker ve listeyi doldurur."""
        all_products = get_all_products()
        self._populate_list_with_data(all_products)

    def _filter_product_list(self, text: str):
        """Arama kutusundaki metne göre ürün listesini anlık olarak filtreler."""
        if not text:
            self._load_all_products()
        else:
            filtered_products = search_products(text)
            self._populate_list_with_data(filtered_products)

    def _on_product_selected(self, item: QListWidgetItem):
        """Bir ürün seçildiğinde miktar ve fiyat sorar ve işlemi gerçekleştirir."""
        try:
            widget = self.product_list_widget.itemWidget(item)
            urun = widget.urun
            is_purchase = self.mode == 'alış'

            quantity, ok1 = QInputDialog.getInt(self, f"{self.mode.capitalize()} Miktarı",
                                                f"'{urun.cins}' için işlem yapılacak adet:",
                                                value=1, minValue=1, maxValue=99999)
            if not ok1: return

            if not is_purchase and quantity > urun.stok_adeti:
                QMessageBox.warning(self, "Yetersiz Stok",
                                    f"Satış miktarı ({quantity}) mevcut stoktan ({urun.stok_adeti}) fazla olamaz.");
                return

            default_price = urun.maliyet if is_purchase else (urun.satis_fiyati or urun.maliyet)
            price, ok2 = QInputDialog.getDouble(self, f"{self.mode.capitalize()} Fiyatı",
                                                f"Birim {self.mode} fiyatı (TL):",
                                                value=default_price, minValue=0, decimals=2, maxValue=10000000)
            if not ok2: return

            quantity_change = quantity if is_purchase else -quantity

            if update_stock(urun.id, quantity_change):
                log_transaction(urun.id, self.mode.capitalize(), quantity, price)
                QMessageBox.information(self, "İşlem Başarılı",
                                        f"'{urun.cins}' ürününün stoğu {quantity} adet {'arttırıldı' if is_purchase else 'azaltıldı'}.")
                self.accept()
            else:
                QMessageBox.critical(self, "İşlem Başarısız", "Stok güncellenirken bir veritabanı hatası oluştu.")
        except Exception as e:
            QMessageBox.critical(self, "Kritik Hata",
                                 f"İşlem sırasında beklenmedik bir hata oluştu:\n\n{e}\n\nDetaylar:\n{traceback.format_exc()}")
