# app/ui/pages/inventory_page.py

import os
import traceback
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QLineEdit, QLabel, QFrame, QMessageBox
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont, QPixmap
from PyQt6.QtCore import Qt, QSortFilterProxyModel

# --- DİKKAT: Import Yolları Değişti ---
# Artık 'pages' klasörünün içinde olduğumuz için, bir üst dizindeki modüllere '..' ile erişiyoruz.
from ...utils import BARCODE_DIR
from ..transaction_dialog import TransactionDialog
from ...models import Urun
from ..add_product import AddProductDialog
from ...database import (
    add_product, get_all_products, delete_product,
    update_product, search_products, update_stock, log_transaction
)


class NumericSortProxyModel(QSortFilterProxyModel):
    """Sayısal sütunların doğru sıralanmasını sağlayan özel proxy model."""
    NUMERIC_COLUMNS = {3, 4, 5, 6}

    def lessThan(self, source_left, source_right):
        column = source_left.column()
        if column in self.NUMERIC_COLUMNS:
            left_data = self.sourceModel().data(source_left, Qt.ItemDataRole.UserRole)
            right_data = self.sourceModel().data(source_right, Qt.ItemDataRole.UserRole)
            if left_data is None: return True
            if right_data is None: return False
            return left_data < right_data
        return super().lessThan(source_left, source_right)


# --- SINIF DEĞİŞİKLİĞİ: QMainWindow -> QWidget ---
class InventoryPage(QWidget):
    """
    Ürün envanterini (tablo, önizleme, yönetim butonları) gösteren ana sayfa.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._urunler_cache = {}

        # Arayüzü doğrudan bu widget'ın kendi layout'una kuruyoruz
        main_hbox_layout = QHBoxLayout(self)

        # Sol Panel (Butonlar ve Tablo)
        left_vbox_layout = QVBoxLayout()
        self._create_top_bar(left_vbox_layout)
        self._create_product_table(left_vbox_layout)

        # Sağ Panel (Önizleme)
        right_vbox_layout = QVBoxLayout()
        self._create_preview_pane(right_vbox_layout)

        main_hbox_layout.addLayout(left_vbox_layout, stretch=2)
        main_hbox_layout.addLayout(right_vbox_layout, stretch=1)

        self._connect_signals()
        self.load_all_products()
        self.update_button_states()

    # Not: Geri kalan tüm fonksiyonlar (_create_top_bar, _populate_table, open_add_product_dialog vb.)
    # daha önceki MainWindow sınıfındaki ile birebir aynıdır. Hiçbir değişiklik gerekmez.

    def _create_top_bar(self, layout: QVBoxLayout):
        top_bar_layout = QHBoxLayout()
        self.add_product_button = QPushButton("Yeni Ürün Ekle")
        self.edit_product_button = QPushButton("Seçili Ürünü Düzenle")
        self.delete_product_button = QPushButton("Seçili Ürünü Sil")
        self.add_product_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        self.delete_product_button.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")
        top_bar_layout.addWidget(self.add_product_button)
        top_bar_layout.addWidget(self.edit_product_button)
        top_bar_layout.addWidget(self.delete_product_button)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(QLabel("Ürün Ara:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ürün kodu veya cinsine göre ara...")
        top_bar_layout.addWidget(self.search_input)
        layout.addLayout(top_bar_layout)

    def _create_product_table(self, layout: QVBoxLayout):
        line = QFrame();
        line.setFrameShape(QFrame.Shape.HLine);
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line);
        layout.addWidget(QLabel("Stoktaki Ürünler:"))
        self.product_table = QTableView();
        self.product_table.setAlternatingRowColors(True)
        self.product_table.setSortingEnabled(True);
        self.product_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.product_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.product_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.source_model = QStandardItemModel();
        self.proxy_model = NumericSortProxyModel()
        self.proxy_model.setSourceModel(self.source_model);
        self.product_table.setModel(self.proxy_model)
        layout.addWidget(self.product_table)

    def _create_preview_pane(self, layout: QVBoxLayout):
        preview_label = QLabel("Ürün Önizleme");
        font = preview_label.font();
        font.setBold(True);
        preview_label.setFont(font)
        layout.addWidget(preview_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.image_preview_label = QLabel("Bir ürün seçin...");
        self.image_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview_label.setMinimumSize(300, 300);
        self.image_preview_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.image_preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        layout.addWidget(self.image_preview_label)
        self.product_code_label = QLabel();
        self.product_code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.product_code_label.setFont(QFont("Arial", 10, QFont.Weight.Bold));
        layout.addWidget(self.product_code_label)
        self.barcode_image_label = QLabel();
        self.barcode_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.barcode_image_label.setMinimumHeight(80);
        layout.addWidget(self.barcode_image_label)
        layout.addStretch()

    def _connect_signals(self):
        self.add_product_button.clicked.connect(self.open_add_product_dialog)
        self.delete_product_button.clicked.connect(self.delete_selected_product)
        self.edit_product_button.clicked.connect(self.open_edit_product_dialog)
        self.product_table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.search_input.textChanged.connect(self.filter_products)

    def _on_selection_changed(self):
        self.update_button_states()
        secili_urun = self._get_selected_product()
        self._update_preview_image(secili_urun)
        self._update_preview_barcode(secili_urun)

    def _update_preview_image(self, urun: Urun | None):
        if urun and urun.resim_yolu and os.path.exists(urun.resim_yolu):
            pixmap = QPixmap(urun.resim_yolu)
            self.image_preview_label.setPixmap(
                pixmap.scaled(self.image_preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation))
        else:
            self.image_preview_label.setText("Resim Yok");
            self.image_preview_label.setPixmap(QPixmap())

    def _update_preview_barcode(self, urun: Urun | None):
        if urun:
            self.product_code_label.setText(urun.urun_kodu)
            barcode_path = os.path.join(BARCODE_DIR, f"{urun.urun_kodu}.png")
            if os.path.exists(barcode_path):
                barcode_pixmap = QPixmap(barcode_path)
                self.barcode_image_label.setPixmap(barcode_pixmap.scaled(300, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                                                         Qt.TransformationMode.SmoothTransformation))
            else:
                self.barcode_image_label.setText("Barkod Üretilmemiş");
                self.barcode_image_label.setPixmap(QPixmap())
        else:
            self.product_code_label.clear();
            self.barcode_image_label.clear();
            self.barcode_image_label.setPixmap(QPixmap())

    def update_button_states(self):
        has_selection = self.product_table.selectionModel().hasSelection()
        self.edit_product_button.setEnabled(has_selection)
        self.delete_product_button.setEnabled(has_selection)

    def load_all_products(self):
        self._populate_table(get_all_products())

    def filter_products(self, text: str):
        if not text:
            self.load_all_products()
        else:
            self._populate_table(search_products(text))

    def _populate_table(self, urunler_listesi: list):
        self.source_model.clear();
        self._urunler_cache.clear()
        self.source_model.setHorizontalHeaderLabels(
            ['ID', 'Ürün Kodu', 'Cins', 'Ayar', 'Gram', 'Maliyet', 'Stok', 'Eklenme Tarihi'])
        for urun in urunler_listesi:
            self._urunler_cache[urun.id] = urun
            item_id = QStandardItem(str(urun.id));
            item_kod = QStandardItem(urun.urun_kodu);
            item_cins = QStandardItem(urun.cins)
            item_tarih = QStandardItem(urun.eklenme_tarihi.strftime('%d-%m-%Y') if urun.eklenme_tarihi else "")
            item_ayar = QStandardItem();
            item_ayar.setData(str(urun.ayar), Qt.ItemDataRole.DisplayRole);
            item_ayar.setData(urun.ayar, Qt.ItemDataRole.UserRole);
            item_ayar.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_gram = QStandardItem()
            if urun.gram is not None: item_gram.setData(f"{urun.gram:.2f}",
                                                        Qt.ItemDataRole.DisplayRole); item_gram.setData(urun.gram,
                                                                                                        Qt.ItemDataRole.UserRole)
            item_gram.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_maliyet = QStandardItem();
            item_maliyet.setData(f"{urun.maliyet:,.2f} TL", Qt.ItemDataRole.DisplayRole);
            item_maliyet.setData(urun.maliyet, Qt.ItemDataRole.UserRole);
            item_maliyet.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_stok = QStandardItem();
            item_stok.setData(str(urun.stok_adeti), Qt.ItemDataRole.DisplayRole);
            item_stok.setData(urun.stok_adeti, Qt.ItemDataRole.UserRole);
            item_stok.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row_items = [item_id, item_kod, item_cins, item_ayar, item_gram, item_maliyet, item_stok, item_tarih]
            self.source_model.appendRow(row_items)
        self.product_table.resizeColumnsToContents();
        self.product_table.setColumnHidden(0, True)

    def _get_selected_product(self) -> Urun | None:
        indexes = self.product_table.selectionModel().selectedRows()
        if not indexes: return None
        proxy_index = indexes[0]
        source_index = self.proxy_model.mapToSource(proxy_index)
        product_id = int(self.source_model.item(source_index.row(), 0).text())
        return self._urunler_cache.get(product_id)

    def open_add_product_dialog(self):
        dialog = AddProductDialog(parent=self)
        if dialog.exec():
            yeni_urun = dialog.get_product_data()
            if not yeni_urun.urun_kodu or not yeni_urun.cins:
                QMessageBox.warning(self, "Eksik Bilgi", "Ürün Kodu ve Cins alanları boş bırakılamaz.")
                return
            yeni_urun_id = add_product(yeni_urun)
            if yeni_urun_id:
                log_transaction(urun_id=yeni_urun_id, tip='Alış', adet=yeni_urun.stok_adeti,
                                birim_fiyat=yeni_urun.maliyet)
                QMessageBox.information(self, "Başarılı", f"'{yeni_urun.cins}' başarıyla eklendi.")
                self.load_all_products()
            else:
                QMessageBox.critical(self, "Veritabanı Hatası", "Ürün eklenirken bir hata oluştu.")

    def open_edit_product_dialog(self):
        secili_urun = self._get_selected_product()
        if not secili_urun: return
        dialog = AddProductDialog(urun_to_edit=secili_urun, parent=self)
        if dialog.exec():
            guncellenmis_urun = dialog.get_product_data()
            if update_product(guncellenmis_urun):
                QMessageBox.information(self, "Başarılı", f"'{guncellenmis_urun.cins}' başarıyla güncellendi.")
                self.load_all_products()
            else:
                QMessageBox.critical(self, "Veritabanı Hatası", "Ürün güncellenirken bir hata oluştu.")

    def _delete_associated_files(self, urun: Urun):
        if urun.resim_yolu and os.path.exists(urun.resim_yolu):
            try:
                os.remove(urun.resim_yolu)
            except OSError as e:
                print(f"Resim silinirken hata: {e}")
        barcode_path = os.path.join(BARCODE_DIR, f"{urun.urun_kodu}.png")
        if os.path.exists(barcode_path):
            try:
                os.remove(barcode_path)
            except OSError as e:
                print(f"Barkod silinirken hata: {e}")

    def delete_selected_product(self):
        secili_urun = self._get_selected_product()
        if not secili_urun: return
        cevap = QMessageBox.question(self, "Silme Onayı",
                                     f"'{secili_urun.cins}' (ID: {secili_urun.id}) ürününü kalıcı olarak silmek istediğinize emin misiniz?\n\nBu işlem geri alınamaz!",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if cevap == QMessageBox.StandardButton.Yes:
            if delete_product(secili_urun.id):
                self._delete_associated_files(secili_urun)
                QMessageBox.information(self, "Başarılı", "Ürün ve ilişkili dosyaları başarıyla silindi.")
                self.load_all_products()
            else:
                QMessageBox.critical(self, "Hata", "Ürün veritabanından silinirken bir hata oluştu.")

    def _open_purchase_dialog(self):
        dialog = TransactionDialog(mode='alış', parent=self)
        if dialog.exec(): self.load_all_products()

    def _open_sale_dialog(self):
        dialog = TransactionDialog(mode='satış', parent=self)
        if dialog.exec(): self.load_all_products()