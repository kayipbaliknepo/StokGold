import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QWidget, QHBoxLayout, QInputDialog, QMessageBox
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QSize

from app.models import Urun
from app.database import get_all_products, update_stock


# --- Listede Gösterilecek Özel Bir Widget Oluşturalım ---
class ProductListItem(QWidget):
    def __init__(self, urun: Urun):
        super().__init__()
        self.urun = urun

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Resim Alanı
        image_label = QLabel()
        if urun.resim_yolu and os.path.exists(urun.resim_yolu):
            pixmap = QPixmap(urun.resim_yolu)
            image_label.setPixmap(
                pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            image_label.setText("Resim\nYok")
            image_label.setFixedSize(64, 64)
            image_label.setStyleSheet("background-color: #eee; border: 1px solid #ccc;")

        layout.addWidget(image_label)

        # Bilgi Alanı
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        kod_label = QLabel(f"<b>Kod:</b> {urun.urun_kodu}")
        cins_label = QLabel(urun.cins)
        font = cins_label.font();
        font.setPointSize(12);
        cins_label.setFont(font)
        stok_label = QLabel(f"Mevcut Stok: {urun.stok_adeti}")

        info_layout.addWidget(cins_label)
        info_layout.addWidget(kod_label)
        info_layout.addWidget(stok_label)

        layout.addLayout(info_layout)
        layout.addStretch()


# --- Ana Diyalog Penceresi ---
class TransactionDialog(QDialog):
    def __init__(self, mode: str, parent=None):
        super().__init__(parent)
        self.mode = mode  # 'alış' veya 'satış'

        self.setWindowTitle(f"Stok {mode.capitalize()} İşlemi")
        self.setMinimumSize(600, 700)

        self.layout = QVBoxLayout(self)

        title_text = "Stok'a Eklemek İçin Bir Ürün Seçin" if mode == 'alış' else "Stok'tan Düşmek İçin Bir Ürün Seçin"
        title_label = QLabel(title_text)
        font = title_label.font();
        font.setPointSize(14);
        font.setBold(True);
        title_label.setFont(font)
        self.layout.addWidget(title_label)

        self.product_list_widget = QListWidget()
        self.product_list_widget.setStyleSheet("QListWidget::item { border-bottom: 1px solid #eee; }")
        self.product_list_widget.itemClicked.connect(self._on_product_selected)
        self.layout.addWidget(self.product_list_widget)

        self._populate_product_list()

    def _populate_product_list(self):
        """Veritabanından ürünleri çeker ve listeyi doldurur."""
        urunler = get_all_products()
        for urun in urunler:
            list_item = QListWidgetItem(self.product_list_widget)
            custom_widget = ProductListItem(urun)

            # Her bir item'ın boyutunu widget'ın boyutuna göre ayarla
            list_item.setSizeHint(custom_widget.sizeHint())
            self.product_list_widget.addItem(list_item)
            self.product_list_widget.setItemWidget(list_item, custom_widget)

    def _on_product_selected(self, item: QListWidgetItem):
        """Bir ürün seçildiğinde miktar sorar ve işlemi gerçekleştirir."""
        widget = self.product_list_widget.itemWidget(item)
        urun = widget.urun

        is_purchase = self.mode == 'alış'
        title = "Alış Miktarı" if is_purchase else "Satış Miktarı"
        label = f"'{urun.cins}' için {self.mode} yapılacak adet:"

        quantity, ok = QInputDialog.getInt(self, title, label, value=1, min=1, max=9999)

        if ok:
            # Satış işleminde stok kontrolü yap
            if not is_purchase and quantity > urun.stok_adeti:
                QMessageBox.warning(self, "Yetersiz Stok",
                                    f"Satış yapmak istediğiniz miktar ({quantity}) mevcut stoktan ({urun.stok_adeti}) fazla olamaz.")
                return

            # Alış için pozitif, satış için negatif miktar
            quantity_change = quantity if is_purchase else -quantity

            success = update_stock(urun.id, quantity_change)

            if success:
                QMessageBox.information(self, "İşlem Başarılı",
                                        f"{urun.cins} ürününün stoğu {quantity} adet {'arttırıldı' if is_purchase else 'azaltıldı'}.")
                self.accept()  # Diyalogu kapat ve başarılı sinyali gönder
            else:
                QMessageBox.critical(self, "İşlem Başarısız", "Stok güncellenirken bir veritabanı hatası oluştu.")
