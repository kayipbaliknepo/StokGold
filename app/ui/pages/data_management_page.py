import os
import traceback
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QSizePolicy, QFileDialog, QMessageBox,
    QGraphicsDropShadowEffect
)
from PySide6.QtGui import QFont, QIcon, QColor
from PySide6.QtCore import Qt, QSize

from ...utils import get_icon_path
from app.backup_manager import backup_database, restore_database


class DataManagementPage(QWidget):
    """
    Veritabanı yedekleme ve geri yükleme işlemlerinin yapıldığı modern ve estetik arayüz sayfası.
    """

    class Styles:
        """Tüm arayüz stillerini merkezi olarak yöneten sınıf."""
        PAGE_BACKGROUND = "background-color: #F4F7FC;"
        CARD_STYLE = """
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
                padding: 25px;
            }
        """
        TITLE_LABEL = "font-size: 18px; font-weight: bold; color: #1F2937; margin-bottom: 5px;"
        DESCRIPTION_LABEL = "font-size: 14px; color: #6B7280; margin-bottom: 20px;"
        BACKUP_BUTTON = """
            QPushButton {
                background-color: #10B981; color: white; border: none;
                padding: 12px 20px; border-radius: 8px; font-weight: bold; font-size: 15px;
            }
            QPushButton:hover { background-color: #059669; }
            QPushButton:pressed { background-color: #047857; }
        """
        RESTORE_BUTTON = """
            QPushButton {
                background-color: #F59E0B; color: white; border: none;
                padding: 12px 20px; border-radius: 8px; font-weight: bold; font-size: 15px;
            }
            QPushButton:hover { background-color: #D97706; }
            QPushButton:pressed { background-color: #B45309; }
        """
        WARNING_LABEL = "color: #EF4444; font-weight: bold; font-size: 13px;"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self.Styles.PAGE_BACKGROUND)

        # Ana layout, içeriği dikeyde ve yatayda ortalamak için
        main_layout = QHBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # İçeriği tutacak olan ve genişliği sınırlanmış dikey layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(30)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # İçerik widget'ı, maksimum genişliği ayarlamak için
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        content_widget.setMaximumWidth(1000)  # Sayfanın maksimum genişliği

        # Başlık
        page_title = QLabel("Veri Yönetimi")
        page_title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        page_title.setStyleSheet("color: #1F2937; margin-bottom: 10px;")
        content_layout.addWidget(page_title, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Kartları yan yana koymak için yeni bir yatay layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)

        # Kartları oluştur ve yatay layout'a ekle
        backup_card = self._create_backup_card()
        restore_card = self._create_restore_card()
        cards_layout.addWidget(backup_card)
        cards_layout.addWidget(restore_card)

        content_layout.addLayout(cards_layout)
        content_layout.addStretch()

        main_layout.addWidget(content_widget)

        self._connect_signals()

    def _apply_shadow(self, widget: QWidget):
        """Widget'a standart bir gölge efekti uygular."""
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 35))
        shadow.setOffset(0, 4)
        widget.setGraphicsEffect(shadow)

    def _create_backup_card(self) -> QFrame:
        """Yedekleme bölümünü oluşturan kartı döndürür."""
        card = QFrame()
        card.setStyleSheet(self.Styles.CARD_STYLE)
        self._apply_shadow(card)
        layout = QVBoxLayout(card)

        title = QLabel("Veritabanı Yedekleme")
        title.setStyleSheet(self.Styles.TITLE_LABEL)

        description = QLabel(
            "Tüm stok, tamir ve işlem verilerinizin bir kopyasını oluşturarak güvende tutun.\n"
            "Oluşturulan `.db` dosyasını güvenli bir konumda saklayın."
        )
        description.setStyleSheet(self.Styles.DESCRIPTION_LABEL)
        description.setWordWrap(True)

        self.backup_button = QPushButton(" Yedekleme Konumu Seç ve Başlat")
        self.backup_button.setIcon(QIcon(get_icon_path("save.png")))
        self.backup_button.setIconSize(QSize(20, 20))
        self.backup_button.setStyleSheet(self.Styles.BACKUP_BUTTON)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.backup_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        return card

    def _create_restore_card(self) -> QFrame:
        """Geri Yükleme bölümünü oluşturan kartı döndürür."""
        card = QFrame()
        card.setStyleSheet(self.Styles.CARD_STYLE)
        self._apply_shadow(card)
        layout = QVBoxLayout(card)

        title = QLabel("Yedekten Geri Yükleme")
        title.setStyleSheet(self.Styles.TITLE_LABEL)

        description = QLabel(
            'Daha önce aldığınız bir yedek dosyasını seçerek tüm verilerinizi o tarihe geri döndürebilirsiniz.<br>'
            '<span style="color:red; font-weight:bold;">DİKKAT:</span> Bu işlem mevcut tüm verilerinizin üzerine yazacaktır ve geri alınamaz!'
        )
        description.setStyleSheet(self.Styles.DESCRIPTION_LABEL)
        description.setWordWrap(True)
        description.setTextFormat(Qt.RichText) 

        self.restore_button = QPushButton(" Yedek Dosyasını Seç ve Geri Yükle")
        self.restore_button.setIcon(QIcon(get_icon_path("load.png")))
        self.restore_button.setIconSize(QSize(20, 20))
        self.restore_button.setStyleSheet(self.Styles.RESTORE_BUTTON)

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()

        # --- DEĞİŞİKLİK BURADA ---
        # Bu butonu da aynı şekilde ortalıyoruz.
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.restore_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        return card

    def _connect_signals(self):
        """Butonların tıklanma olaylarını ilgili fonksiyonlara bağlar."""
        self.backup_button.clicked.connect(self._handle_backup)
        self.restore_button.clicked.connect(self._handle_restore)

    def _handle_backup(self):
        """Kullanıcıya yedekleme konumu seçtirir ve yedekleme işlemini başlatır."""
        directory = QFileDialog.getExistingDirectory(self, "Yedekleme Klasörünü Seçin")
        if directory:
            success, message = backup_database(directory)
            if success:
                QMessageBox.information(self, "Başarılı", message)
            else:
                QMessageBox.critical(self, "Hata", message)

    def _handle_restore(self):
        """Kullanıcıya yedek dosyasını seçtirir ve geri yükleme işlemini başlatır."""
        source_path, _ = QFileDialog.getOpenFileName(
            self,
            "Geri Yüklenecek Veritabanı Yedeğini Seçin",
            "",
            "Veritabanı Dosyaları (*.db);;Tüm Dosyalar (*)"
        )

        if source_path:
            reply = QMessageBox.warning(
                self,
                "Geri Yükleme Onayı",
                "Bu işlem mevcut veritabanınızın üzerine yazacaktır. Tüm kaydedilmemiş değişiklikler kaybolacaktır.\n\nDEVAM ETMEK İSTEDİĞİNİZE EMİN MİSİNİZ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                success, message = restore_database(source_path)
                if success:
                    QMessageBox.information(self, "Başarılı", message)
                else:
                    QMessageBox.critical(self, "Hata", message)