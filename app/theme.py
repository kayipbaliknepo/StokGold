LIGHT_THEME_QSS = """
    /* === GENEL SAYFA VE PENCERE STİLİ === */
    QWidget#MainPage, QDialog {
        background-color: #F4F7FC; /* Açık mavi-gri pastel arka plan */
    }

    /* === ETİKETLER VE YAZILAR === */
    QLabel {
        color: #1F2937; /* Koyu antrasit yazı */
        font-size: 14px;
    }
    QLabel#HeaderTitle {
        font-size: 24px;
        font-weight: bold;
    }
    QLabel#KpiTitle {
        font-size: 14px;
        font-weight: bold;
        color: #6B7280; /* Daha soluk başlık rengi */
    }
    QLabel#KpiValue {
        font-size: 28px;
        font-weight: bold;
        color: #1F2937;
    }

    /* === BUTONLAR === */
    QPushButton {
        background-color: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        font-size: 14px;
        font-weight: bold;
        color: #374151;
        padding: 12px;
    }
    QPushButton:hover {
        background-color: #F9FAFB;
        border-color: #4A90E2;
    }
    QPushButton:pressed {
        background-color: #F3F4F6;
    }
    QPushButton:disabled {
        background-color: #F3F4F6;
        color: #9CA3AF;
        border-color: #E5E7EB;
    }

    /* === ÖZEL BUTONLAR === */
    QPushButton#AiButton {
        background-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 #4A90E2, stop:1 #2C6EC2);
        color: white;
        border: none;
        font-size: 16px;
    }
    QPushButton#AiButton:hover { background-color: #4281CB; }
    QPushButton#RefreshButton {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 20px; /* Tam yuvarlak */
    }
    QPushButton#RefreshButton:hover { background-color: #F9FAFB; }

    /* === TABLOLAR === */
    QTableView {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        gridline-color: #F3F4F6;
    }
    QTableView::item:selected {
        background-color: #D1E4FF; /* Pastel Mavi */
        color: #1E3A8A;
    }
    QHeaderView::section {
        background-color: #F9FAFB;
        padding: 12px 8px;
        border: none;
        border-bottom: 2px solid #E5E7EB;
        font-weight: bold;
        color: #374151;
    }

    /* === VERİ KARTLARI VE DİĞER BİLEŞENLER === */
    QFrame#KpiCard, QFrame#PreviewFrame {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
    }
    QLineEdit, QTextEdit {
        background-color: white;
        border: 1px solid #D1D5DB;
        border-radius: 6px;
        padding: 8px;
        color: #111827;
    }
    QTabBar::tab {
        background-color: #F3F4F6;
        color: #4B5563;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 12px 20px;
    }
    QTabBar::tab:selected {
        background-color: white;
        color: #1F2937;
    }
    QCalendarWidget {
        background-color: white;
        border: none;
    }
"""

# =============================================================================
# KOYU TEMA RENK PALETİ VE STİLLERİ
# =============================================================================
DARK_THEME_QSS = """
    /* === GENEL SAYFA VE PENCERE STİLİ === */
    QWidget#MainPage, QDialog {
        background-color: #111827; /* Koyu Mavi/Antrasit */
    }

    /* === ETİKETLER VE YAZILAR === */
    QLabel, QTabBar::tab, QCalendarWidget QHeaderView::section, QDateEdit {
        color: #D1D5DB; /* Açık Gri Yazı */
        border: none;
    }
    QLabel#HeaderTitle, QLabel#KpiValue {
        color: #F9FAFB; /* Neredeyse Beyaz */
    }
    QLabel#KpiTitle {
        color: #9CA3AF; /* Soluk Gri */
    }

    /* === BUTONLAR === */
    QPushButton {
        background-color: #374151; /* Koyu Gri */
        border: 1px solid #4B5563;
        border-radius: 8px;
        font-size: 14px;
        font-weight: bold;
        color: #F3F4F6; /* Çok Açık Gri Yazı */
        padding: 12px;
    }
    QPushButton:hover {
        background-color: #4B5563;
        border-color: #60A5FA; /* Açık Mavi */
    }
    QPushButton:pressed {
        background-color: #1F2937;
    }
    QPushButton:disabled {
        background-color: #374151;
        color: #6B7280;
        border-color: #4B5563;
    }

    /* === ÖZEL BUTONLAR === */
    QPushButton#AiButton {
        background-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 #4A90E2, stop:1 #60A5FA);
        color: white; border: none; font-size: 16px;
    }
    QPushButton#AiButton:hover { background-color: #4281CB; }
    QPushButton#RefreshButton {
        background-color: #1F2937;
        border: 1px solid #4B5563;
        border-radius: 20px;
    }
    QPushButton#RefreshButton:hover { background-color: #374151; }

    /* === TABLOLAR === */
    QTableView {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 8px;
        gridline-color: #374151;
        color: #D1D5DB;
    }
    QTableView::item:selected {
        background-color: #3B82F6;
        color: white;
    }
    QHeaderView::section {
        background-color: #111827;
        padding: 12px 8px;
        border: none;
        border-bottom: 2px solid #374151;
        font-weight: bold;
    }

    /* === VERİ KARTLARI VE DİĞER BİLEŞENLER === */
    QFrame#KpiCard, QFrame#PreviewFrame {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 12px;
    }
    QLineEdit, QTextEdit, QCalendarWidget, QDateEdit QAbstractItemView {
        background-color: #374151;
        border: 1px solid #4B5563;
        border-radius: 6px;
        padding: 8px;
        color: #F9FAFB;
    }
    QLineEdit:focus { border: 1px solid #60A5FA; }
    QTabBar::tab {
        background-color: #1F2937;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        padding: 12px 20px;
    }
    QTabBar::tab:selected {
        background-color: #374151;
    }
"""
