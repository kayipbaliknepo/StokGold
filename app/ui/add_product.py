# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

import os
import shutil
import time
import traceback
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QDialogButtonBox, QSpinBox, QHBoxLayout, QLabel, QFileDialog
)
from PyQt6.QtGui import QDoubleValidator
from app.models import Urun
from app.utils import IMAGE_DIR, BARCODE_DIR
from datetime import date
import barcode
from barcode.writer import ImageWriter


class AddProductDialog(QDialog):
    def __init__(self, urun_to_edit: Urun = None, parent=None):
        super().__init__(parent)
        self.urun_to_edit = urun_to_edit
        self.selected_image_path = None
        if self.urun_to_edit:
            self.setWindowTitle("Ürünü Düzenle")
        else:
            self.setWindowTitle("Yeni Ürün Ekle")
        self.setMinimumWidth(450)
        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Form Elemanları
        self.urun_kodu_input = QLineEdit()
        self.cins_input = QLineEdit()
        self.ayar_input = QSpinBox()
        self.ayar_input.setRange(8, 24)
        self.ayar_input.setValue(22)

        self.gram_input = QLineEdit()
        self.gram_input.setPlaceholderText("Boş bırakılabilir")
        validator = QDoubleValidator(0.0, 5000.0, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.gram_input.setValidator(validator)

        self.maliyet_input = QLineEdit()
        self.maliyet_input.setValidator(QDoubleValidator(0.0, 1_000_000.0, 2))

        self.stok_adeti_input = QSpinBox()
        self.stok_adeti_input.setMaximum(99999)
        self.stok_adeti_input.setValue(1)

        form_layout.addRow("Ürün Kodu:", self.urun_kodu_input)
        form_layout.addRow("Cins:", self.cins_input)
        form_layout.addRow("Ayar:", self.ayar_input)
        form_layout.addRow("Gram:", self.gram_input)
        form_layout.addRow("Maliyet (TL):", self.maliyet_input)
        form_layout.addRow("Stok Adeti:", self.stok_adeti_input)

        image_layout = QHBoxLayout()
        self.image_path_label = QLabel("Resim Seçilmedi")
        self.image_path_label.setStyleSheet("font-style: italic; color: grey;")
        select_image_button = QPushButton("Resim Seç...")
        select_image_button.clicked.connect(self._select_image)
        image_layout.addWidget(self.image_path_label)
        image_layout.addWidget(select_image_button)
        form_layout.addRow("Ürün Resmi:", image_layout)

        self.layout.addLayout(form_layout)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)

        if self.urun_to_edit:
            self.populate_form()
        else:
            self.urun_kodu_input.setText(f"URUN-{int(time.time())}")

    def _select_image(self):
        """Dosya seçme diyalogunu açar ve seçilen resmi işler."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Bir Resim Seçin", "", "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp)"
        )


        if file_path:
            self.selected_image_path = file_path
            self.image_path_label.setText(os.path.basename(file_path))
            self.image_path_label.setStyleSheet("")

    def populate_form(self):

        self.urun_kodu_input.setText(self.urun_to_edit.urun_kodu)
        self.cins_input.setText(self.urun_to_edit.cins)
        self.ayar_input.setValue(self.urun_to_edit.ayar)
        self.stok_adeti_input.setValue(self.urun_to_edit.stok_adeti)

        gram_degeri = self.urun_to_edit.gram
        self.gram_input.setText(str(gram_degeri).replace('.', ',') if gram_degeri is not None else "")

        self.maliyet_input.setText(str(self.urun_to_edit.maliyet).replace('.', ','))

        if self.urun_to_edit.resim_yolu:
            self.image_path_label.setText(os.path.basename(self.urun_to_edit.resim_yolu))
            self.image_path_label.setStyleSheet("")

    def _generate_barcode(self, product_code: str):

        try:

            generated_barcode = barcode.get('code128', product_code, writer=ImageWriter())

            barcode_path = os.path.join(BARCODE_DIR, f"{product_code}.png")
            generated_barcode.write(barcode_path, options={"write_text": False})
            print(f"BAŞARILI: Barkod oluşturuldu: {barcode_path}")
        except Exception as e:
            print(f"!!! HATA: Barkod oluşturulamadı: {e}")
            print(traceback.format_exc())

    def get_product_data(self) -> Urun:

        urun = Urun()
        urun.urun_kodu = self.urun_kodu_input.text()
        urun.cins = self.cins_input.text()
        urun.ayar = self.ayar_input.value()
        urun.stok_adeti = self.stok_adeti_input.value()

        gram_text = self.gram_input.text().strip().replace(',', '.')
        urun.gram = float(gram_text) if gram_text else None

        maliyet_text = self.maliyet_input.text().strip().replace(',', '.')
        urun.maliyet = float(maliyet_text) if maliyet_text else 0.0

        is_new_product = not self.urun_to_edit
        code_changed = self.urun_to_edit and self.urun_to_edit.urun_kodu != urun.urun_kodu
        if is_new_product or code_changed:
            self._generate_barcode(urun.urun_kodu)

        new_image_relative_path = None
        if self.selected_image_path:
            source_path = self.selected_image_path
            _, extension = os.path.splitext(source_path)
            new_filename = f"{urun.urun_kodu}{extension}"

            destination_path = os.path.join(IMAGE_DIR, new_filename)
            try:
                shutil.copy(source_path, destination_path)
                new_image_relative_path = destination_path # Veritabanına tam yolu kaydediyoruz
            except Exception as e:
                print(f"!!! HATA: Resim kopyalanamadı: {e}")

        if self.urun_to_edit:
            urun.id = self.urun_to_edit.id
            urun.eklenme_tarihi = self.urun_to_edit.eklenme_tarihi
            urun.resim_yolu = new_image_relative_path if new_image_relative_path else self.urun_to_edit.resim_yolu
        else:
            urun.eklenme_tarihi = date.today()
            urun.resim_yolu = new_image_relative_path

        return urun