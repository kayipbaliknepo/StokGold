import os
import sys
import traceback
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableView, QLineEdit, QLabel, QFrame, QMessageBox
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont, QPixmap
from PyQt6.QtCore import Qt

from app.ui.transaction_dialog import TransactionDialog
from app.models import Urun
from app.ui.add_product import AddProductDialog
from app.ui.report_window import ReportWindow
from app.database import (
    add_product, get_all_products, delete_product,
    update_product, search_products
)


class MainWindow(QMainWindow):
    """
    Uygulamanın ana penceresi. Tüm UI elemanlarını ve işlevleri yönetir.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("StokGold v1.0")
        self.setGeometry(100, 100, 1200, 750)

        self._urunler_cache = {}

        self._setup_ui()
        self.load_all_products()

    def _setup_ui(self):
        """Arayüzü oluşturan tüm alt fonksiyonları çağırır."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_hbox_layout = QHBoxLayout(central_widget)

        left_vbox_layout = QVBoxLayout()
        self._create_top_bar(left_vbox_layout)
        self._create_product_table(left_vbox_layout)

        right_vbox_layout = QVBoxLayout()
        self._create_preview_pane(right_vbox_layout)

        main_hbox_layout.addLayout(left_vbox_layout, stretch=2)
        main_hbox_layout.addLayout(right_vbox_layout, stretch=1)

        self._connect_signals()
        self.update_button_states()

    def _create_top_bar(self, layout: QVBoxLayout):
        """Üst kısımdaki butonları, işlem ve arama alanlarını oluşturur."""
        top_bar_layout = QHBoxLayout()

        # --- Grup 1: Ürün Yönetim Butonları ---
        self.add_product_button = QPushButton("Yeni Ürün Ekle")
        self.edit_product_button = QPushButton("Seçili Ürünü Düzenle")
        self.delete_product_button = QPushButton("Seçili Ürünü Sil")

        # Stil atamaları
        self.add_product_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        self.delete_product_button.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")

        top_bar_layout.addWidget(self.add_product_button)
        top_bar_layout.addWidget(self.edit_product_button)
        top_bar_layout.addWidget(self.delete_product_button)

        # --- Gruplar arasına boşluk koy ---
        top_bar_layout.addStretch()

        # --- Grup 2: Rapor ve İşlem Butonları ---
        self.report_button = QPushButton("Raporlar")
        self.purchase_button = QPushButton("Stok Alış")
        self.sale_button = QPushButton("Stok Satış")

        # Stil atamaları
        self.purchase_button.setStyleSheet("background-color: #2196F3; color: white; padding: 5px;")
        self.sale_button.setStyleSheet("background-color: #FF9800; color: white; padding: 5px;")

        top_bar_layout.addWidget(self.report_button)
        top_bar_layout.addWidget(self.purchase_button)
        top_bar_layout.addWidget(self.sale_button)

        # --- Gruplar arasına boşluk koy ---
        top_bar_layout.addStretch()

        # --- Grup 3: Arama Alanı ---
        top_bar_layout.addWidget(QLabel("Ürün Ara:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ürün kodu veya cinsine göre ara...")
        top_bar_layout.addWidget(self.search_input)

        # Oluşturulan bu komple yatay bar'ı, ana dikey layout'a ekle
        layout.addLayout(top_bar_layout)

    def _create_product_table(self, layout: QVBoxLayout):
        """Ürünlerin listeleneceği tabloyu oluşturur."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        layout.addWidget(QLabel("Stoktaki Ürünler:"))

        self.product_table = QTableView()
        self.product_table.setAlternatingRowColors(True)
        self.product_table.setSortingEnabled(True)
        self.product_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.product_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.product_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)

        self.model = QStandardItemModel()
        self.product_table.setModel(self.model)
        layout.addWidget(self.product_table)

    def _create_preview_pane(self, layout: QVBoxLayout):
        """Sağ tarafta ürün resmi ve barkod önizleme alanını oluşturur."""
        preview_label = QLabel("Ürün Önizleme")
        font = preview_label.font()
        font.setBold(True)
        preview_label.setFont(font)
        layout.addWidget(preview_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.image_preview_label = QLabel("Bir ürün seçin...")
        self.image_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview_label.setMinimumSize(300, 300)
        self.image_preview_label.setFrameShape(QFrame.Shape.StyledPanel)
        self.image_preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        layout.addWidget(self.image_preview_label)

        self.product_code_label = QLabel()
        self.product_code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.product_code_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.product_code_label)

        self.barcode_image_label = QLabel()
        self.barcode_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.barcode_image_label.setMinimumHeight(80)
        layout.addWidget(self.barcode_image_label)

        layout.addStretch()

    def _connect_signals(self):
        """Tüm sinyal-slot bağlantılarını tek bir yerden yönetir."""
        self.add_product_button.clicked.connect(self.open_add_product_dialog)
        self.delete_product_button.clicked.connect(self.delete_selected_product)
        self.edit_product_button.clicked.connect(self.open_edit_product_dialog)
        self.report_button.clicked.connect(self.open_report_window)
        self.product_table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.purchase_button.clicked.connect(self._open_purchase_dialog)  # <-- YENİ BAĞLANTI
        self.sale_button.clicked.connect(self._open_sale_dialog)  # <-- YENİ BAĞLANTI
        self.search_input.textChanged.connect(self.filter_products)

    def _on_selection_changed(self):
        """Tabloda seçim değiştiğinde çağrılır. Butonları ve önizleme panelini günceller."""
        self.update_button_states()

        secili_urun = self._get_selected_product()

        # --- Hata Ayıklama İçin Eklendi ---
        if secili_urun:
            print(f"--- SEÇİM DEĞİŞTİ ---")
            print(f"Seçilen Ürün Kodu: {secili_urun.urun_kodu}")
            barcode_yolu = os.path.join("assets", "barcodes", f"{secili_urun.urun_kodu}.png")
            print(f"Aranan Barkod Dosyası: {barcode_yolu}")
            print(f"Dosya Mevcut mu?: {os.path.exists(barcode_yolu)}")
            print(f"----------------------")
        # ------------------------------------

        self._update_preview_image(secili_urun)
        self._update_preview_barcode(secili_urun)

    def _update_preview_image(self, urun: Urun | None):
        """Önizleme panelindeki ürün resmini günceller."""
        if urun and urun.resim_yolu and os.path.exists(urun.resim_yolu):
            pixmap = QPixmap(urun.resim_yolu)
            self.image_preview_label.setPixmap(pixmap.scaled(
                self.image_preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.image_preview_label.setText("Resim Yok")
            self.image_preview_label.setPixmap(QPixmap())

    def _update_preview_barcode(self, urun: Urun | None):
        """Önizleme panelindeki ürün barkodunu ve kodunu günceller."""
        if urun:
            self.product_code_label.setText(urun.urun_kodu)
            barcode_path = os.path.join("assets", "barcodes", f"{urun.urun_kodu}.png")
            if os.path.exists(barcode_path):
                barcode_pixmap = QPixmap(barcode_path)
                self.barcode_image_label.setPixmap(barcode_pixmap.scaled(
                    300, 80,
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

    def update_button_states(self):
        """Tabloda bir seçim olup olmamasına göre butonları aktif/pasif yapar."""
        has_selection = self.product_table.selectionModel().hasSelection()
        self.edit_product_button.setEnabled(has_selection)
        self.delete_product_button.setEnabled(has_selection)

    def load_all_products(self):
        """Veritabanındaki tüm ürünleri tabloya yükler."""
        self._populate_table(get_all_products())

    def filter_products(self, text: str):
        """Arama kutusundaki metne göre ürünleri filtreler."""
        if not text:
            self.load_all_products()
        else:
            self._populate_table(search_products(text))

    def _populate_table(self, urunler_listesi: list):
        """Verilen ürün listesine göre tabloyu temizler ve doldurur."""
        self.model.clear()
        self._urunler_cache.clear()
        self.model.setHorizontalHeaderLabels(
            ['ID', 'Ürün Kodu', 'Cins', 'Ayar', 'Gram', 'Maliyet', 'Stok', 'Eklenme Tarihi'])

        for urun in urunler_listesi:
            self._urunler_cache[urun.id] = urun

            # --- Gram Gösterimi Değişikliği ---
            # Eğer urun.gram doluysa formatla, değilse boş string göster.
            gram_str = f"{urun.gram:.2f}" if urun.gram is not None else ""

            row_items = [
                QStandardItem(str(urun.id)), QStandardItem(urun.urun_kodu), QStandardItem(urun.cins),
                QStandardItem(str(urun.ayar)), QStandardItem(gram_str),  # <-- Değişiklik burada
                QStandardItem(f"{urun.maliyet:.2f} TL"), QStandardItem(str(urun.stok_adeti)),
                QStandardItem(urun.eklenme_tarihi.strftime('%d-%m-%Y') if urun.eklenme_tarihi else "")
            ]
            self.model.appendRow(row_items)

        self.product_table.resizeColumnsToContents()
        self.product_table.setColumnHidden(0, True)

    def _get_selected_product(self) -> Urun | None:
        """Tablodan seçili olan ürünün nesnesini döndürür."""
        indexes = self.product_table.selectionModel().selectedRows()
        if not indexes:
            return None
        product_id = int(self.model.itemFromIndex(indexes[0].siblingAtColumn(0)).text())
        return self._urunler_cache.get(product_id)

    def open_add_product_dialog(self):
        """Yeni Ürün Ekle penceresini açar."""
        dialog = AddProductDialog(parent=self)
        if dialog.exec():
            yeni_urun = dialog.get_product_data()
            if not yeni_urun.urun_kodu or not yeni_urun.cins or yeni_urun.gram <= 0:
                QMessageBox.warning(self, "Eksik Bilgi", "Ürün Kodu, Cins ve Gram alanları boş bırakılamaz.")
                return
            if add_product(yeni_urun):
                QMessageBox.information(self, "Başarılı", f"'{yeni_urun.cins}' başarıyla eklendi.")
                self.load_all_products()
            else:
                QMessageBox.critical(self, "Veritabanı Hatası", "Ürün eklenirken bir hata oluştu.")

    def open_edit_product_dialog(self):
        """Seçili ürünü düzenlemek için pencereyi açar."""
        secili_urun = self._get_selected_product()
        if not secili_urun:
            return

        dialog = AddProductDialog(urun_to_edit=secili_urun, parent=self)
        if dialog.exec():
            guncellenmis_urun = dialog.get_product_data()
            if update_product(guncellenmis_urun):
                QMessageBox.information(self, "Başarılı", f"'{guncellenmis_urun.cins}' başarıyla güncellendi.")
                self.load_all_products()
            else:
                QMessageBox.critical(self, "Veritabanı Hatası", "Ürün güncellenirken bir hata oluştu.")

    def delete_selected_product(self):
        """Tablodan seçili olan ürünü ve ilişkili dosyalarını siler."""
        secili_urun = self._get_selected_product()
        if not secili_urun:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir ürün seçin.")
            return

        cevap = QMessageBox.question(self, "Silme Onayı",
                                     f"'{secili_urun.cins}' (ID: {secili_urun.id}) ürününü kalıcı olarak silmek istediğinize emin misiniz?\n\nBu işlem geri alınamaz!",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if cevap == QMessageBox.StandardButton.Yes:
            # 1. Önce veritabanından silmeyi dene
            if delete_product(secili_urun.id):
                # 2. Veritabanı işlemi başarılı olursa, diskteki dosyaları sil
                self._delete_associated_files(secili_urun)

                QMessageBox.information(self, "Başarılı", "Ürün ve ilişkili dosyaları başarıyla silindi.")
                self.load_all_products()  # Tabloyu yenile
            else:
                QMessageBox.critical(self, "Hata", "Ürün veritabanından silinirken bir hata oluştu.")

    def open_report_window(self):
        """Raporlama penceresini açar."""
        try:
            report_dialog = ReportWindow(self)
            report_dialog.exec()
        except Exception as e:
            error_mesaji = f"Rapor penceresi açılırken beklenmedik bir hata oluştu:\n\n{e}"
            print("HATA: ", error_mesaji)
            print("Detaylar: ", traceback.format_exc())
            QMessageBox.critical(self, "Kritik Hata", error_mesaji)

    def _open_purchase_dialog(self):
        """Stok Alış diyalogunu açar."""
        dialog = TransactionDialog(mode='alış', parent=self)
        if dialog.exec():
            # İşlem başarılı olduysa ana tabloyu yenile
            self.load_all_products()

    def _open_sale_dialog(self):
        """Stok Satış diyalogunu açar."""
        dialog = TransactionDialog(mode='satış', parent=self)
        if dialog.exec():
            # İşlem başarılı olduysa ana tabloyu yenile
            self.load_all_products()

    def _delete_associated_files(self, urun: Urun):
        """Verilen ürüne ait resim ve barkod dosyalarını diskten siler."""
        print(f"İlişkili dosyalar siliniyor: {urun.urun_kodu}")

        # 1. Ürün resmini sil
        if urun.resim_yolu and os.path.exists(urun.resim_yolu):
            try:
                os.remove(urun.resim_yolu)
                print(f"Resim silindi: {urun.resim_yolu}")
            except OSError as e:
                print(f"Resim silinirken hata: {e}")

        # 2. Barkod resmini sil
        barcode_path = os.path.join("assets", "barcodes", f"{urun.urun_kodu}.png")
        if os.path.exists(barcode_path):
            try:
                os.remove(barcode_path)
                print(f"Barkod silindi: {barcode_path}")
            except OSError as e:
                print(f"Barkod silinirken hata: {e}")