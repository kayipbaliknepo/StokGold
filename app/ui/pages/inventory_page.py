# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

import os
import traceback
import openpyxl
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView,
    QLineEdit, QLabel, QFrame, QMessageBox, QApplication, QStyle,
    QFileDialog, QHeaderView, QSizePolicy # <-- EKLENDİ
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont, QPixmap, QColor, QIcon
from PySide6.QtCore import Qt, QSortFilterProxyModel, QSize

from ...utils import BARCODE_DIR, get_icon_path
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
    """Ürün envanterini gösteren ve yöneten, modern tasarımlı ana sayfa."""

    class Styles:
        """Tüm arayüz stillerini merkezi olarak yöneten sınıf."""
        PAGE_BACKGROUND = "background-color: #F4F7FC;"
        BUTTON_PRIMARY = """
            QPushButton {
                background-color: #4A90E2; color: white; border: none;
                padding: 8px 16px; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #4281CB; }
            QPushButton:pressed { background-color: #3B72B5; }
            QPushButton:disabled { background-color: #B0C4DE; }
        """
        BUTTON_DANGER = """
            QPushButton {
                background-color: #D9534F; color: white; border: none;
                padding: 8px 16px; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #C9302C; }
            QPushButton:pressed { background-color: #AC2925; }
            QPushButton:disabled { background-color: #E9967A; }
        """
        BUTTON_SECONDARY = """
            QPushButton {
                background-color: #778899; color: white; border: none;
                padding: 8px 16px; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #6A7989; }
            QPushButton:pressed { background-color: #5C6A78; }
            QPushButton:disabled { background-color: #BCC6D0; }
        """
        SEARCH_BAR = """
            QLineEdit {
                background-color: white; border: 1px solid #D1D5DB;
                border-radius: 6px; padding: 8px; font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #4A90E2; }
        """
        TABLE_STYLE = """
            QTableView {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                gridline-color: #F3F4F6;
                font-size: 14px;
                selection-behavior: SelectRows;
            }
            QTableView::item { padding: 10px 8px; border-bottom: 1px solid #F3F4F6; }
            QTableView::item:selected {
                background-color: #EBF5FF;
                color: #1E3A8A;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid #E5E7EB;
                padding: 10px 8px;
                font-size: 13px;
                font-weight: bold;
                color: #374151;
            }
        """
        PREVIEW_FRAME = """
            QFrame#PreviewFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
        """
        PREVIEW_IMAGE_LABEL = "background-color: #F9FAFB; border: 1px dashed #D1D5DB; border-radius: 6px;"
        PREVIEW_TITLE = "font-size: 16px; font-weight: bold; color: #1F2937;"
        PRODUCT_CODE_LABEL = "font-size: 14px; color: #4B5563; font-weight: bold;"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._urunler_cache = {}
        self.setStyleSheet(self.Styles.PAGE_BACKGROUND)

        main_hbox_layout = QHBoxLayout(self)
        main_hbox_layout.setContentsMargins(20, 20, 20, 20)
        main_hbox_layout.setSpacing(20)

        left_panel = self._create_left_panel()
        right_panel = self._create_right_panel()

        main_hbox_layout.addWidget(left_panel, stretch=3)
        main_hbox_layout.addWidget(right_panel, stretch=1)

        self._connect_signals()
        self.load_all_products()

    def _create_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        top_bar = self._create_top_bar()
        table_area = self._create_product_table()
        layout.addLayout(top_bar)
        layout.addLayout(table_area)
        return panel

    def _create_right_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("PreviewFrame")
        panel.setStyleSheet(self.Styles.PREVIEW_FRAME)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        preview_title = QLabel("Ürün Önizleme")
        preview_title.setStyleSheet(self.Styles.PREVIEW_TITLE)
        preview_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.image_preview_label = QLabel("Bir ürün seçin...")
        self.image_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview_label.setMinimumHeight(300)
        self.image_preview_label.setStyleSheet(self.Styles.PREVIEW_IMAGE_LABEL)

        self.product_code_label = QLabel()
        self.product_code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.product_code_label.setStyleSheet(self.Styles.PRODUCT_CODE_LABEL)

        self.barcode_image_label = QLabel()
        self.barcode_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Barkodun büyümesi için burayı esnek bırakıyoruz
        self.barcode_image_label.setMinimumHeight(100)
        self.barcode_image_label.setSizePolicy(self.sizePolicy().horizontalPolicy(), QSizePolicy.Policy.Expanding)

        layout.addWidget(preview_title)
        layout.addWidget(self.image_preview_label, stretch=2)  # Resme daha çok yer
        layout.addStretch(1)
        layout.addWidget(self.product_code_label)
        layout.addWidget(self.barcode_image_label, stretch=1)  # Barkoda resimden daha az yer

        return panel

    def _create_top_bar(self) -> QHBoxLayout:
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        top_bar_layout.setSpacing(10)

        button_font = QFont("Segoe UI", 10)

        self.add_product_button = QPushButton(" Yeni Ekle")
        self.add_product_button.setFont(button_font)
        self.edit_product_button = QPushButton(" Düzenle")
        self.edit_product_button.setFont(button_font)
        self.delete_product_button = QPushButton(" Sil")
        self.delete_product_button.setFont(button_font)
        self.export_excel_button = QPushButton(" Excel'e Aktar")
        self.export_excel_button.setFont(button_font)

        icon_size = QSize(16, 16)
        self.add_product_button.setIcon(QIcon(get_icon_path("add.png")));
        self.add_product_button.setIconSize(icon_size)
        self.edit_product_button.setIcon(QIcon(get_icon_path("edit.png")));
        self.edit_product_button.setIconSize(icon_size)
        self.delete_product_button.setIcon(QIcon(get_icon_path("delete.png")));
        self.delete_product_button.setIconSize(icon_size)
        self.export_excel_button.setIcon(QIcon(get_icon_path("excel.png")));
        self.export_excel_button.setIconSize(icon_size)

        self.add_product_button.setStyleSheet(self.Styles.BUTTON_PRIMARY)
        self.delete_product_button.setStyleSheet(self.Styles.BUTTON_DANGER)
        self.edit_product_button.setStyleSheet(self.Styles.BUTTON_SECONDARY)
        self.export_excel_button.setStyleSheet(self.Styles.BUTTON_SECONDARY)

        top_bar_layout.addWidget(self.add_product_button)
        top_bar_layout.addWidget(self.edit_product_button)
        top_bar_layout.addWidget(self.delete_product_button)
        top_bar_layout.addWidget(self.export_excel_button)
        top_bar_layout.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ürün ara...")
        self.search_input.setMinimumWidth(250)
        self.search_input.setStyleSheet(self.Styles.SEARCH_BAR)

        top_bar_layout.addWidget(self.search_input)

        return top_bar_layout

    def _create_product_table(self) -> QVBoxLayout:
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        self.product_table = QTableView()
        self.product_table.setStyleSheet(self.Styles.TABLE_STYLE)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.product_table.setSortingEnabled(True)
        self.product_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.product_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.product_table.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
        self.product_table.verticalHeader().setVisible(False)
        self.product_table.horizontalHeader().setStretchLastSection(True)
        self.product_table.horizontalHeader().setHighlightSections(False)

        self.source_model = QStandardItemModel()
        self.proxy_model = NumericSortProxyModel()
        self.proxy_model.setSourceModel(self.source_model)
        self.product_table.setModel(self.proxy_model)

        table_layout.addWidget(self.product_table)
        return table_layout

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
        selection_count = len(self.product_table.selectionModel().selectedRows())
        self.edit_product_button.setEnabled(selection_count == 1)
        self.delete_product_button.setEnabled(has_selection)

    def _update_preview_image(self, urun: Urun | None):
        if urun and urun.resim_yolu and os.path.exists(urun.resim_yolu):
            pixmap = QPixmap(urun.resim_yolu)
            scaled_pixmap = pixmap.scaled(
                self.image_preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_preview_label.setPixmap(scaled_pixmap)
        else:
            self.image_preview_label.setText("Resim Yok")
            self.image_preview_label.setPixmap(QPixmap())

    def _update_preview_barcode(self, urun: Urun | None):
        if urun:
            self.product_code_label.setText(urun.urun_kodu)
            barcode_path = os.path.join(BARCODE_DIR, f"{urun.urun_kodu}.png")
            if os.path.exists(barcode_path):
                barcode_pixmap = QPixmap(barcode_path)
                self.barcode_image_label.setPixmap(barcode_pixmap.scaled(
                    self.barcode_image_label.width(),
                    self.barcode_image_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
            else:
                self.barcode_image_label.setText("Barkod Üretilmemiş")
                self.barcode_image_label.setPixmap(QPixmap())
        else:
            self.product_code_label.clear()
            self.barcode_image_label.clear()
            self.barcode_image_label.setPixmap(QPixmap())

    def load_all_products(self):
        self._populate_table(get_all_products())
        self.update_button_states()

    def filter_products(self, text: str):
        if not text:
            self.load_all_products()
        else:
            self._populate_table(search_products(text))
        self.update_button_states()

    def _populate_table(self, urunler_listesi: list):
        self.source_model.clear();
        self._urunler_cache.clear()
        self.source_model.setHorizontalHeaderLabels(
            ['ID', 'Ürün Kodu', 'Cins', 'Ayar', 'Gram', 'Maliyet', 'Stok', 'Eklenme Tarihi'])
        warning_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        for urun in urunler_listesi:
            self._urunler_cache[urun.id] = urun
            item_id = QStandardItem(str(urun.id))
            item_kod = QStandardItem(urun.urun_kodu)
            item_cins = QStandardItem(urun.cins)
            item_tarih = QStandardItem(urun.eklenme_tarihi.strftime('%d-%m-%Y') if urun.eklenme_tarihi else "")

            item_ayar = QStandardItem();
            item_ayar.setData(urun.ayar, Qt.ItemDataRole.UserRole);
            item_ayar.setData(str(urun.ayar), Qt.ItemDataRole.DisplayRole);
            item_ayar.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_gram = QStandardItem()
            if urun.gram is not None: item_gram.setData(urun.gram, Qt.ItemDataRole.UserRole); item_gram.setData(
                f"{urun.gram:.2f}", Qt.ItemDataRole.DisplayRole)
            item_gram.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_maliyet = QStandardItem();
            item_maliyet.setData(urun.maliyet, Qt.ItemDataRole.UserRole);
            item_maliyet.setData(f"{urun.maliyet:,.2f} TL", Qt.ItemDataRole.DisplayRole);
            item_maliyet.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_stok = QStandardItem();
            item_stok.setData(urun.stok_adeti, Qt.ItemDataRole.UserRole);
            item_stok.setData(str(urun.stok_adeti), Qt.ItemDataRole.DisplayRole);
            item_stok.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            row_items = [item_id, item_kod, item_cins, item_ayar, item_gram, item_maliyet, item_stok, item_tarih]

            stok_adeti = urun.stok_adeti
            if stok_adeti == 0:
                color = QColor("#D9534F");
                [item.setForeground(color) for item in row_items];
                item_stok.setIcon(warning_icon)
            elif 0 < stok_adeti < 5:
                color = QColor("#F0AD4E");
                [item.setForeground(color) for item in row_items];
                item_stok.setIcon(warning_icon)

            self.source_model.appendRow(row_items)

        self.product_table.resizeColumnsToContents()
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
        urun_to_delete_list = [self._get_selected_product(index) for index in selected_rows if
                               self._get_selected_product(index)]
        if not urun_to_delete_list: return
        item_count = len(urun_to_delete_list)
        onay_mesaji = (
            f"Seçtiğiniz {item_count} ürünü kalıcı olarak silmek istediğinize emin misiniz?\n\nBu işlem geri alınamaz!")
        cevap = QMessageBox.question(self, "Toplu Silme Onayı", onay_mesaji,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if cevap == QMessageBox.StandardButton.Yes:
            silinen_sayisi, basarisiz_sayisi = 0, 0
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
        dialog = TransactionDialog(mode='alış', parent=self)
        if dialog.exec(): self.load_all_products()

    def _open_sale_dialog(self):
        dialog = TransactionDialog(mode='satış', parent=self)
        if dialog.exec(): self.load_all_products()

    def _export_to_excel(self):
        urunler = get_all_products()
        if not urunler:
            QMessageBox.information(self, "Bilgi", "Aktarılacak ürün bulunmuyor.")
            return
        default_filename = f"Stok_Raporu_{datetime.now().strftime('%Y-%m-%d_%H%M')}.xlsx"
        save_path, _ = QFileDialog.getSaveFileName(self, "Excel Dosyasını Kaydet", default_filename,
                                                   "Excel Dosyaları (*.xlsx)")
        if save_path:
            try:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                sheet.title = "Stok Envanteri"
                headers = ["Ürün Kodu", "Cins", "Ayar", "Gram", "Maliyet (TL)", "Satış Fiyatı (TL)", "Stok Adedi",
                           "Eklenme Tarihi", "Açıklama"]
                sheet.append(headers)
                for urun in urunler:
                    row = [
                        urun.urun_kodu, urun.cins, urun.ayar, urun.gram if urun.gram is not None else 0,
                        urun.maliyet, urun.satis_fiyati, urun.stok_adeti,
                        urun.eklenme_tarihi.strftime("%Y-%m-%d") if urun.eklenme_tarihi else "", urun.aciklama
                    ]
                    sheet.append(row)
                workbook.save(save_path)
                QMessageBox.information(self, "Başarılı", f"Envanter başarıyla şu dosyaya aktarıldı:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya aktarılırken bir hata oluştu:\n{e}")
