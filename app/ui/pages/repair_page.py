import os
import traceback
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableView, QPushButton, QHeaderView,
    QFrame, QGridLayout, QHBoxLayout, QLineEdit, QStyledItemDelegate,
    QTextEdit, QStyleOptionViewItem, QMessageBox, QStyle, QMenu
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont, QPixmap, QColor, QIcon, QPainter
from PySide6.QtCore import Qt, QSize, QRect, QEvent, Signal

from ...utils import get_icon_path
from app.tamir_model import Tamir
from ..add_repair_dialog import AddRepairDialog
from ...database import (
    get_all_tamirler, add_tamir, update_tamir, delete_tamir, search_repairs
)


class StatusDelegate(QStyledItemDelegate):
    """
    Tablodaki 'Durum' sütununu renkli, yuvarlak etiketler olarak çizer.
    Tıklandığında durum değiştirme menüsü açar.
    """
    STATUS_COLORS = {
        "Beklemede": QColor("#F59E0B"), "Tamirde": QColor("#3B82F6"),
        "Tamamlandı": QColor("#10B981"), "Teslim Edildi": QColor("#6B7280")
    }


    status_changed = Signal(int, str) # Satır indeksi ve yeni durumu gönderen sinyal

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        status = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        color = self.STATUS_COLORS.get(status, QColor("lightgray"))

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # --- NİHAİ DÜZELTME BURADA ---
        # 1. Arka planı manuel olarak kontrol et ve boya
        if option.state & QStyle.StateFlag.State_Selected:
            # Eğer satır seçili ise, Qt'nin standart vurgu rengini kullan
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            # Seçili değilse, normal arkaplanı (beyaz veya alternatif renk) koru
            # Bu satır, arka planın şeffaf kalmamasını sağlar.
            painter.fillRect(option.rect, QColor(Qt.GlobalColor.white) if not (index.row() % 2) else QColor("#F9FAFB"))

        # 2. Renkli durum etiketini (pill) çiz
        rect = option.rect
        pill_rect = QRect(rect.x() + 8, rect.y() + 8, rect.width() - 16, rect.height() - 16)

        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(pill_rect, 8, 8)

        # 3. Durum metnini etiketin içine çiz
        painter.setPen(Qt.GlobalColor.white)
        font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pill_rect, Qt.AlignmentFlag.AlignCenter, status)

    def editorEvent(self, event, model, option, index):
        """Hücreye tıklandığında menüyü açar."""
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            menu = QMenu()
            for status in self.STATUS_COLORS.keys():
                action = menu.addAction(status)
                # action.triggered.connect(lambda checked=False, s=status: print(f"Seçilen: {s} for row {index.row()}"))
                action.triggered.connect(lambda checked=False, s=status: self.status_changed.emit(index.row(), s))

            # Menüyü farenin tıkladığı yerde göster
            menu.exec(event.globalPosition().toPoint())
            return True
        return super().editorEvent(event, model, option, index)


class RepairPage(QWidget):
    """Tamir kayıtlarını yönetmek için modern ve estetik arayüz sayfası."""
    STATUS_ORDER = ["Beklemede", "Tamirde", "Tamamlandı", "Teslim Edildi"]

    class Styles:
        PAGE_BACKGROUND = "background-color: #F4F7FC;"
        BUTTON_PRIMARY = "QPushButton { background-color: #4A90E2; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; } QPushButton:hover { background-color: #4281CB; }"
        BUTTON_DANGER = "QPushButton { background-color: #D9534F; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; } QPushButton:hover { background-color: #C9302C; } QPushButton:disabled { background-color: #E9967A; border-color: #D9534F; }"
        SEARCH_BAR = "QLineEdit { background-color: white; border: 1px solid #D1D5DB; border-radius: 6px; padding: 8px; font-size: 14px; } QLineEdit:focus { border: 1px solid #4A90E2; }"
        TABLE_STYLE = "QTableView { background-color: white; border: 1px solid #E5E7EB; border-radius: 8px; gridline-color: #F3F4F6; font-size: 14px; selection-behavior: SelectRows; } QTableView::item:selected { background-color: #EBF5FF; color: #1E3A8A; } QHeaderView::section { background-color: #F9FAFB; border: none; border-bottom: 2px solid #E5E7EB; padding: 12px 8px; font-weight: bold; color: #374151; }"
        DETAIL_FRAME = "QFrame#DetailFrame { background-color: white; border-left: 1px solid #E5E7EB; }"
        DETAIL_TITLE = "font-size: 18px; font-weight: bold; color: #1F2937; margin-bottom: 10px;"
        DETAIL_FIELD_TITLE = "font-size: 12px; font-weight: bold; color: #6B7280; margin-top: 10px;"
        DETAIL_FIELD_VALUE = "font-size: 14px; color: #374151;"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_repairs = []
        self.setStyleSheet(self.Styles.PAGE_BACKGROUND)
        main_hbox_layout = QHBoxLayout(self)
        main_hbox_layout.setContentsMargins(0, 0, 0, 0);
        main_hbox_layout.setSpacing(0)
        left_panel = self._create_left_panel()
        self.right_panel = self._create_right_panel()
        main_hbox_layout.addWidget(left_panel, stretch=3)
        main_hbox_layout.addWidget(self.right_panel, stretch=1)
        self._connect_signals()
        self.load_all_repairs()

    def _create_left_panel(self) -> QWidget:
        panel = QWidget();
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20);
        layout.setSpacing(15)
        top_bar = self._create_top_bar()
        table = self._create_repair_table()
        layout.addLayout(top_bar);
        layout.addWidget(table)
        return panel

    def _create_right_panel(self) -> QWidget:
        panel = QFrame();
        panel.setObjectName("DetailFrame");
        panel.setStyleSheet(self.Styles.DETAIL_FRAME)
        self.right_panel_layout = QVBoxLayout(panel)
        self.right_panel_layout.setContentsMargins(20, 20, 20, 20);
        self.right_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.detail_placeholder = QLabel("Detayları görmek için bir tamir kaydı seçin.");
        self.detail_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter);
        self.detail_placeholder.setStyleSheet("color: #9CA3AF; font-style: italic;")
        self.right_panel_layout.addWidget(self.detail_placeholder)
        self.detail_widget = QWidget();
        self.detail_widget.setVisible(False);
        self.right_panel_layout.addWidget(self.detail_widget)
        detail_layout = QVBoxLayout(self.detail_widget);
        detail_layout.setContentsMargins(0, 0, 0, 0)
        title = QLabel("Tamir Detayları");
        title.setStyleSheet(self.Styles.DETAIL_TITLE);
        detail_layout.addWidget(title)
        self.musteri_label = self._create_detail_field(detail_layout, "Müşteri Bilgisi");
        self.urun_label = self._create_detail_field(detail_layout, "Ürün Açıklaması");
        self.hasar_label = self._create_detail_field(detail_layout, "Hasar Tespiti");
        self.tarih_label = self._create_detail_field(detail_layout, "Alınan / Tahmini Teslim Tarihi");
        self.ucret_label = self._create_detail_field(detail_layout, "Tamir Ücreti")
        self.notlar_text = QTextEdit();
        self.notlar_text.setReadOnly(True);
        self.notlar_text.setStyleSheet("border:none; background:transparent;")
        detail_layout.addWidget(QLabel("Notlar:", styleSheet=self.Styles.DETAIL_FIELD_TITLE));
        detail_layout.addWidget(self.notlar_text)
        detail_layout.addStretch()
        return panel

    def _create_detail_field(self, layout: QVBoxLayout, title: str) -> QLabel:
        layout.addWidget(QLabel(title, styleSheet=self.Styles.DETAIL_FIELD_TITLE));
        value_label = QLabel()
        value_label.setStyleSheet(self.Styles.DETAIL_FIELD_VALUE);
        value_label.setWordWrap(True)
        layout.addWidget(value_label)
        return value_label

    def _create_top_bar(self) -> QHBoxLayout:
        top_bar_layout = QHBoxLayout();
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.add_repair_button = QPushButton(" Yeni Tamir Kaydı");
        self.add_repair_button.setIcon(QIcon(get_icon_path("add.png")));
        self.add_repair_button.setStyleSheet(self.Styles.BUTTON_PRIMARY)
        self.delete_repair_button = QPushButton(" Kaydı Sil");
        self.delete_repair_button.setIcon(QIcon(get_icon_path("delete.png")));
        self.delete_repair_button.setStyleSheet(self.Styles.BUTTON_DANGER)
        self.search_input = QLineEdit();
        self.search_input.setPlaceholderText("Müşteri veya ürüne göre ara...");
        self.search_input.setStyleSheet(self.Styles.SEARCH_BAR)
        top_bar_layout.addWidget(self.add_repair_button);
        top_bar_layout.addWidget(self.delete_repair_button);
        top_bar_layout.addStretch();
        top_bar_layout.addWidget(self.search_input, stretch=1)
        return top_bar_layout

    def _create_repair_table(self) -> QTableView:
        self.repair_table = QTableView();
        self.repair_table.setStyleSheet(self.Styles.TABLE_STYLE)
        self.repair_table.setAlternatingRowColors(True);
        self.repair_table.setSortingEnabled(True)
        self.repair_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers);
        self.repair_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.repair_table.setSelectionMode(QTableView.SelectionMode.SingleSelection);
        self.repair_table.verticalHeader().setVisible(False)
        self.repair_table.horizontalHeader().setHighlightSections(False);
        self.repair_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.repair_model = QStandardItemModel();
        self.repair_table.setModel(self.repair_model)
        self.status_delegate = StatusDelegate(self)
        self.repair_table.setItemDelegateForColumn(3, self.status_delegate)
        return self.repair_table

    def _connect_signals(self):
        self.add_repair_button.clicked.connect(self.open_add_repair_dialog)
        self.delete_repair_button.clicked.connect(self.delete_selected_repair)
        self.repair_table.clicked.connect(self.on_table_click)
        self.repair_table.doubleClicked.connect(self.open_edit_repair_dialog)
        self.repair_table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.search_input.textChanged.connect(self.filter_repairs)
        self.status_delegate.status_changed.connect(self.on_status_changed)

    def load_all_repairs(self):
        """Veritabanından tüm tamir kayıtlarını çeker ve tabloyu doldurur."""
        current_selection_id = None
        if self.repair_table.selectionModel().hasSelection():
            current_selection_id = self._get_selected_repair_id()

        self.repair_model.clear()
        self.repair_model.setHorizontalHeaderLabels(['Müşteri Adı Soyadı', 'Ürün', 'Alınan Tarih', 'Durum'])
        self.all_repairs = get_all_tamirler()

        new_selection_row = -1
        for i, tamir in enumerate(self.all_repairs):
            row = [QStandardItem(tamir.musteri_ad_soyad), QStandardItem(tamir.urun_aciklamasi),
                   QStandardItem(tamir.alinan_tarih.strftime('%d-%m-%Y')), QStandardItem(tamir.durum)]
            row[0].setData(tamir.id, Qt.ItemDataRole.UserRole)
            self.repair_model.appendRow(row)
            self.repair_table.setRowHeight(i, 40)
            if tamir.id == current_selection_id:
                new_selection_row = i

        self.repair_table.resizeColumnsToContents()
        self.repair_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.repair_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        if new_selection_row != -1:
            self.repair_table.selectRow(new_selection_row)

        self.update_button_states()

    def filter_repairs(self, text: str):
        filtered_data = search_repairs(text)
        self.load_all_repairs()  # Önce tümünü yükle
        # Sonra filtreye uymayanları gizle
        all_ids = {tamir.id for tamir in filtered_data}
        for row in range(self.repair_model.rowCount()):
            tamir_id = self.repair_model.item(row, 0).data(Qt.ItemDataRole.UserRole)
            if tamir_id not in all_ids:
                self.repair_table.setRowHidden(row, True)

    def _on_selection_changed(self, selected, deselected):
        self.update_button_states()
        selected_tamir = self._get_selected_repair()
        if selected_tamir:
            self.detail_placeholder.setVisible(False);
            self.detail_widget.setVisible(True)
            self.musteri_label.setText(
                f"{selected_tamir.musteri_ad_soyad} ({selected_tamir.musteri_telefon or 'Telefon Yok'})")
            self.urun_label.setText(selected_tamir.urun_aciklamasi)
            self.hasar_label.setText(selected_tamir.hasar_tespiti or "Belirtilmemiş")
            alinan = selected_tamir.alinan_tarih.strftime('%d.%m.%Y')
            teslim = selected_tamir.tahmini_teslim_tarihi.strftime(
                '%d.%m.%Y') if selected_tamir.tahmini_teslim_tarihi else "Belirtilmemiş"
            self.tarih_label.setText(f"{alinan}  ->  {teslim}")
            ucret = selected_tamir.tamir_ucreti
            self.ucret_label.setText(f"{ucret:,.2f} TL" if ucret is not None else "Fiyat Belirlenmemiş")
            self.notlar_text.setText(selected_tamir.notlar or "")
        else:
            self.detail_widget.setVisible(False);
            self.detail_placeholder.setVisible(True)

    def update_button_states(self):
        has_selection = self.repair_table.selectionModel().hasSelection()
        self.delete_repair_button.setEnabled(has_selection)

    def _get_selected_repair_id(self) -> int | None:
        indexes = self.repair_table.selectionModel().selectedRows()
        if not indexes: return None
        return self.repair_model.item(indexes[0].row(), 0).data(Qt.ItemDataRole.UserRole)

    def _get_selected_repair(self) -> Tamir | None:
        tamir_id = self._get_selected_repair_id()
        if tamir_id is None: return None
        return next((t for t in self.all_repairs if t.id == tamir_id), None)

    def on_table_click(self, index):
        """Tabloya tıklandığında hangi sütuna tıklandığını kontrol eder."""
        selected_tamir = self._get_selected_repair()
        if not selected_tamir: return
        if index.column() == 3:  # Durum sütunu
            self.cycle_repair_status(selected_tamir)

    def cycle_repair_status(self, tamir: Tamir):
        """Bir tamir kaydının durumunu bir sonraki aşamaya geçirir."""
        try:
            current_index = self.STATUS_ORDER.index(tamir.durum)
            next_index = (current_index + 1) % len(self.STATUS_ORDER)
            tamir.durum = self.STATUS_ORDER[next_index]
            update_tamir(tamir)
            self.load_all_repairs()
        except ValueError:
            print(f"'{tamir.durum}' durumu listede bulunamadı.")

    def open_add_repair_dialog(self):
        dialog = AddRepairDialog(parent=self)
        if dialog.exec():
            yeni_tamir_kaydi = dialog.get_tamir_data()
            if not yeni_tamir_kaydi.musteri_ad_soyad or not yeni_tamir_kaydi.urun_aciklamasi:
                QMessageBox.warning(self, "Eksik Bilgi",
                                    "Müşteri Adı Soyadı ve Ürün Açıklaması alanları boş bırakılamaz.")
                return
            add_tamir(yeni_tamir_kaydi)
            self.load_all_repairs()
            self.repair_table.clearSelection()

    def open_edit_repair_dialog(self, index):
        """Mevcut bir tamir kaydını düzenleme penceresini açar (çift tıklama ile)."""
        if index.column() == 3: return  # Durum sütununa çift tıklanırsa bir şey yapma
        selected_tamir = self._get_selected_repair()
        if not selected_tamir: return
        dialog = AddRepairDialog(tamir_to_edit=selected_tamir, parent=self)
        if dialog.exec():
            guncellenmis_kayit = dialog.get_tamir_data()
            update_tamir(guncellenmis_kayit)
            self.load_all_repairs()
            self.clear_selection()


    def delete_selected_repair(self):
        selected_tamir = self._get_selected_repair()
        if not selected_tamir: return
        cevap = QMessageBox.question(self, "Silme Onayı",
                                     f"<b>{selected_tamir.musteri_ad_soyad}</b> adına kayıtlı olan<br>"
                                     f"<b>'{selected_tamir.urun_aciklamasi}'</b> tamir kaydını kalıcı olarak silmek istediğinize emin misiniz?<br><br>"
                                     "Bu işlem geri alınamaz!",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if cevap == QMessageBox.StandardButton.Yes:
            if delete_tamir(selected_tamir.id):
                QMessageBox.information(self, "Başarılı", "Tamir kaydı başarıyla silindi.")
                self.load_all_repairs()
                self.clear_selection()
            else:
                QMessageBox.critical(self, "Hata", "Kayıt silinirken bir veritabanı hatası oluştu.")

    def clear_selection(self):
        """Tablodaki mevcut seçimi temizler."""
        self.repair_table.clearSelection()

    def on_status_changed(self, row_index: int, new_status: str):
        """Delegate'ten gelen sinyali yakalar ve durumu günceller."""
        try:
            tamir_id = self.repair_model.item(row_index, 0).data(Qt.ItemDataRole.UserRole)
            tamir_to_update = next((t for t in self.all_repairs if t.id == tamir_id), None)

            if tamir_to_update:
                tamir_to_update.durum = new_status
                update_tamir(tamir_to_update)
                self.load_all_repairs()  # Tabloyu yenile
                self.clear_selection()  # Seçimi temizle
        except Exception as e:
            print(f"Durum değiştirilirken hata: {e}")

