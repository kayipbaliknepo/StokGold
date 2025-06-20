# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

import os
import traceback
import openpyxl
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QLineEdit, QLabel, QFrame, QMessageBox, QApplication, QStyle, QFileDialog
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont, QPixmap, QColor, QIcon
from PySide6.QtCore import Qt, QSortFilterProxyModel
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


class InventoryPage(QWidget):
    """Ürün envanterini gösteren ve yöneten ana sayfa."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._urunler_cache = {}

        main_hbox_layout = QHBoxLayout(self)

        left_vbox_layout = QVBoxLayout()
        self._create_top_bar(left_vbox_layout)
        self._create_product_table(left_vbox_layout)

        right_vbox_layout = QVBoxLayout()
        self._create_preview_pane(right_vbox_layout)

        main_hbox_layout.addLayout(left_vbox_layout, stretch=2)
        main_hbox_layout.addLayout(right_vbox_layout, stretch=1)

        self._connect_signals()
        self.load_all_products()

    def _create_top_bar(self, layout: QVBoxLayout):
        top_bar_layout = QHBoxLayout()
        self.add_product_button = QPushButton("Yeni Ürün Ekle")
        self.edit_product_button = QPushButton("Seçili Ürünü Düzenle")
        self.delete_product_button = QPushButton("Seçili Ürünü Sil")
        self.export_excel_button = QPushButton("Excel'e Aktar")

        self.add_product_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        self.delete_product_button.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")
        self.export_excel_button.setStyleSheet("background-color: #1D6F42; color: white; padding: 5px;")

        top_bar_layout.addWidget(self.add_product_button)
        top_bar_layout.addWidget(self.edit_product_button)
        top_bar_layout.addWidget(self.delete_product_button)
        top_bar_layout.addWidget(self.export_excel_button)
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
        self.product_table.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
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
        self.export_excel_button.clicked.connect(self._export_to_excel)
        self.product_table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.search_input.textChanged.connect(self.filter_products)

    def _on_selection_changed(self):
        self.update_button_states()
        secili_urun = self._get_selected_product()
        self._update_preview_image(secili_urun)
        self._update_preview_barcode(secili_urun)

    def update_button_states(self):
        has_selection = self.product_table.selectionModel().hasSelection()
        self.edit_product_button.setEnabled(has_selection)
        self.delete_product_button.setEnabled(has_selection)

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
        warning_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        for urun in urunler_listesi:
            self._urunler_cache[urun.id] = urun
            item_id = QStandardItem(str(urun.id));
            item_kod = QStandardItem(urun.urun_kodu);
            item_cins = QStandardItem(urun.cins);
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
            stok_adeti = urun.stok_adeti
            if stok_adeti == 0:
                color = QColor("red")
                for item in row_items: item.setData(color, Qt.ItemDataRole.ForegroundRole)
                item_stok.setData(warning_icon, Qt.ItemDataRole.DecorationRole)
            elif 0 < stok_adeti < 5:
                color = QColor("#FD7E14")
                for item in row_items: item.setData(color, Qt.ItemDataRole.ForegroundRole)
                item_stok.setData(warning_icon, Qt.ItemDataRole.DecorationRole)
            self.source_model.appendRow(row_items)
        self.product_table.resizeColumnsToContents();
        self.product_table.setColumnHidden(0, True)

    def _get_selected_product(self, proxy_index=None) -> Urun | None:
        if not proxy_index:
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
        selected_rows = self.product_table.selectionModel().selectedRows()
        if not selected_rows: QMessageBox.warning(self, "Uyarı",
                                                  "Lütfen silmek için bir veya daha fazla ürün seçin."); return
        urun_to_delete_list = []
        for index in selected_rows:
            urun = self._get_selected_product(index)
            if urun: urun_to_delete_list.append(urun)
        if not urun_to_delete_list: return
        item_count = len(urun_to_delete_list)
        onay_mesaji = (
            f"Seçtiğiniz {item_count} ürünü kalıcı olarak silmek istediğinize emin misiniz?\n\nBu işlem geri alınamaz!")
        cevap = QMessageBox.question(self, "Toplu Silme Onayı", onay_mesaji,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if cevap == QMessageBox.StandardButton.Yes:
            silinen_sayisi = 0;
            basarisiz_sayisi = 0
            for urun in urun_to_delete_list:
                if delete_product(urun.id):
                    self._delete_associated_files(urun);
                    silinen_sayisi += 1
                else:
                    basarisiz_sayisi += 1
            QMessageBox.information(self, "İşlem Tamamlandı",
                                    f"{silinen_sayisi} adet ürün başarıyla silindi.\n{basarisiz_sayisi} adet ürün silinirken hata oluştu.")
            self.load_all_products()

    def _open_purchase_dialog(self):
        dialog = TransactionDialog(mode='alış', parent=self);
        if dialog.exec(): self.load_all_products()

    def _open_sale_dialog(self):
        dialog = TransactionDialog(mode='satış', parent=self)
        if dialog.exec(): self.load_all_products()

    def _export_to_excel(self):
        """Tüm envanter verisini bir Excel dosyasına aktarır."""
        urunler = get_all_products()
        if not urunler:
            QMessageBox.information(self, "Bilgi", "Aktarılacak ürün bulunmuyor.")
            return

        # Kullanıcıya dosyayı nereye kaydedeceğini sor
        default_filename = f"Stok_Raporu_{datetime.now().strftime('%Y-%m-%d_%H%M')}.xlsx"
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Excel Dosyasını Kaydet",
            default_filename,
            "Excel Dosyaları (*.xlsx)"
        )

        if save_path:
            try:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.title = "Stok Envanteri"

                # Başlık satırını yaz
                headers = ["Ürün Kodu", "Cins", "Ayar", "Gram", "Maliyet (TL)", "Satış Fiyatı (TL)", "Stok Adedi",
                           "Eklenme Tarihi", "Açıklama"]
                sheet.append(headers)

                # Veri satırlarını yaz
                for urun in urunler:
                    row = [
                        urun.urun_kodu,
                        urun.cins,
                        urun.ayar,
                        urun.gram if urun.gram is not None else 0,
                        urun.maliyet,
                        urun.satis_fiyati,
                        urun.stok_adeti,
                        urun.eklenme_tarihi.strftime("%Y-%m-%d") if urun.eklenme_tarihi else "",
                        urun.aciklama
                    ]
                    sheet.append(row)

                workbook.save(save_path)

                QMessageBox.information(self, "Başarılı", f"Envanter başarıyla şu dosyaya aktarıldı:\n{save_path}")

            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya aktarılırken bir hata oluştu:\n{e}")