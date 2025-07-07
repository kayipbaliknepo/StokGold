# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFrame,
    QDialogButtonBox, QComboBox, QDateEdit, QWidget, QFormLayout, QStyle

)
from PySide6.QtGui import QFont, QIcon, QDoubleValidator
from PySide6.QtCore import Qt, QDate, QSize

from app.utils import get_icon_path
from app.tamir_model import Tamir
from datetime import date


class AddRepairDialog(QDialog):
    """
    Yeni bir tamir kaydı eklemek veya mevcut birini düzenlemek için kullanılan
    modern ve kullanıcı dostu diyalog penceresi.
    """

    class Styles:
        """Tüm arayüz stillerini merkezi olarak yöneten sınıf."""
        DIALOG_BACKGROUND = "background-color: #F4F7FC;"
        GROUP_BOX_STYLE = """
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #1F2937;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                background-color: #F4F7FC;
            }
        """
        INPUT_FIELD_STYLE = """
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 1px solid #4A90E2;
            }
            QComboBox::drop-down {
                border: none;
            }
        """
        BUTTON_PRIMARY = """
            QPushButton {
                background-color: #4A90E2; color: white; border: none;
                padding: 10px 24px; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #4281CB; }
        """
        BUTTON_SECONDARY = """
            QPushButton {
                background-color: #E5E7EB; color: #374151; border: none;
                padding: 10px 24px; border-radius: 6px; font-weight: bold;
            }
            QPushButton:hover { background-color: #D1D5DB; }
        """

    def __init__(self, tamir_to_edit: Tamir = None, parent=None):
        super().__init__(parent)
        self.tamir_to_edit = tamir_to_edit

        # Pencere başlığını ve ikonunu ayarla
        title = "Tamir Kaydını Düzenle" if self.tamir_to_edit else "Yeni Tamir Kaydı"
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(get_icon_path("repair.png")))  # repair.png ikonu olmalı

        self.setMinimumWidth(500)
        self.setStyleSheet(self.Styles.DIALOG_BACKGROUND)

        # Ana layout ve UI kurulumu
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self._create_widgets()
        self._setup_layouts()
        self._connect_signals()

        if self.tamir_to_edit:
            self._populate_form()

    def _create_widgets(self):
        """Arayüzdeki tüm giriş alanlarını ve butonları oluşturur."""
        # Müşteri Bilgileri
        self.musteri_ad_soyad_input = QLineEdit()
        self.musteri_telefon_input = QLineEdit()

        # Ürün Bilgileri
        self.urun_aciklamasi_input = QLineEdit()
        self.hasar_tespiti_input = QTextEdit()
        self.hasar_tespiti_input.setFixedHeight(80)

        # İşlem Detayları
        self.alinan_tarih_input = QDateEdit(QDate.currentDate())
        self.alinan_tarih_input.setCalendarPopup(True)
        self.tahmini_teslim_tarihi_input = QDateEdit()
        self.tahmini_teslim_tarihi_input.setCalendarPopup(True)
        self.tahmini_teslim_tarihi_input.setSpecialValueText("Belirtilmedi")  # Boş bırakılabilir
        self.tahmini_teslim_tarihi_input.setDate(QDate(2000, 1, 1))  # Varsayılan olarak boş

        self.tamir_ucreti_input = QLineEdit()
        self.tamir_ucreti_input.setPlaceholderText("0.00")
        self.tamir_ucreti_input.setValidator(QDoubleValidator(0.0, 999999.0, 2))

        self.durum_input = QComboBox()
        self.durum_input.addItems(["Beklemede", "Tamirde", "Tamamlandı", "Teslim Edildi"])

        self.notlar_input = QTextEdit()
        self.notlar_input.setFixedHeight(80)

        # Tüm inputlara ortak stil uygula
        for widget in self.findChildren(QWidget):
            if isinstance(widget, (QLineEdit, QTextEdit, QComboBox, QDateEdit)):
                widget.setStyleSheet(self.Styles.INPUT_FIELD_STYLE)

        # Kaydet ve İptal Butonları
        self.buttonBox = QDialogButtonBox()
        save_button = self.buttonBox.addButton("Kaydet", QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_button = self.buttonBox.addButton("İptal", QDialogButtonBox.ButtonRole.RejectRole)
        save_button.setStyleSheet(self.Styles.BUTTON_PRIMARY)
        cancel_button.setStyleSheet(self.Styles.BUTTON_SECONDARY)

    def _setup_layouts(self):
        """Giriş alanlarını gruplar ve layout'lara yerleştirir."""
        # Müşteri Bilgileri Grubu
        musteri_group = QFrame();
        musteri_group.setStyleSheet(self.Styles.GROUP_BOX_STYLE)
        musteri_layout = QFormLayout(musteri_group)
        musteri_layout.setContentsMargins(15, 25, 15, 15)
        musteri_layout.addRow("Adı Soyadı:", self.musteri_ad_soyad_input)
        musteri_layout.addRow("Telefon Numarası:", self.musteri_telefon_input)

        # Tamir Detayları Grubu
        tamir_group = QFrame();
        tamir_group.setStyleSheet(self.Styles.GROUP_BOX_STYLE)
        tamir_layout = QFormLayout(tamir_group)
        tamir_layout.setContentsMargins(15, 25, 15, 15)
        tamir_layout.addRow("Ürün Açıklaması:", self.urun_aciklamasi_input)
        tamir_layout.addRow("Hasar Tespiti:", self.hasar_tespiti_input)
        tamir_layout.addRow("Alınan Tarih:", self.alinan_tarih_input)
        tamir_layout.addRow("Tahmini Teslim Tarihi:", self.tahmini_teslim_tarihi_input)
        tamir_layout.addRow("Tamir Ücreti (TL):", self.tamir_ucreti_input)
        tamir_layout.addRow("Durum:", self.durum_input)
        tamir_layout.addRow("Ek Notlar:", self.notlar_input)

        self.main_layout.addWidget(musteri_group)
        self.main_layout.addWidget(tamir_group)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.buttonBox)

    def _connect_signals(self):
        """Buton sinyallerini bağlar."""
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def _populate_form(self):
        """Düzenleme modunda, formu mevcut verilerle doldurur."""
        self.musteri_ad_soyad_input.setText(self.tamir_to_edit.musteri_ad_soyad)
        self.musteri_telefon_input.setText(self.tamir_to_edit.musteri_telefon or "")
        self.urun_aciklamasi_input.setText(self.tamir_to_edit.urun_aciklamasi)
        self.hasar_tespiti_input.setText(self.tamir_to_edit.hasar_tespiti or "")
        self.alinan_tarih_input.setDate(self.tamir_to_edit.alinan_tarih)
        if self.tamir_to_edit.tahmini_teslim_tarihi:
            self.tahmini_teslim_tarihi_input.setDate(self.tamir_to_edit.tahmini_teslim_tarihi)
        if self.tamir_to_edit.tamir_ucreti is not None:
            self.tamir_ucreti_input.setText(str(self.tamir_to_edit.tamir_ucreti).replace('.', ','))
        self.durum_input.setCurrentText(self.tamir_to_edit.durum)
        self.notlar_input.setText(self.tamir_to_edit.notlar or "")

    def get_tamir_data(self) -> Tamir:
        """Formdaki verileri okur ve bir Tamir nesnesi olarak döndürür."""
        ucret_text = self.tamir_ucreti_input.text().strip().replace(',', '.')

        tamir_kaydi = Tamir(
            id=self.tamir_to_edit.id if self.tamir_to_edit else None,
            musteri_ad_soyad=self.musteri_ad_soyad_input.text().strip(),
            musteri_telefon=self.musteri_telefon_input.text().strip() or None,
            urun_aciklamasi=self.urun_aciklamasi_input.text().strip(),
            hasar_tespiti=self.hasar_tespiti_input.toPlainText().strip() or None,
            alinan_tarih=self.alinan_tarih_input.date().toPython(),
            tahmini_teslim_tarihi=self.tahmini_teslim_tarihi_input.date().toPython() if self.tahmini_teslim_tarihi_input.date() != QDate(
                2000, 1, 1) else None,
            tamir_ucreti=float(ucret_text) if ucret_text else None,
            durum=self.durum_input.currentText(),
            notlar=self.notlar_input.toPlainText().strip() or None
        )
        return tamir_kaydi
