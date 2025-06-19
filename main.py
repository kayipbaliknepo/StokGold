import sys
from PyQt6.QtWidgets import QApplication

# Gerekli kurulum ve veritabanı fonksiyonlarını import et
from app.database import create_table
from app.utils import ensure_data_dirs_exist

# ESKİ PENCEREYİ DEĞİL, YENİ ANA UYGULAMA ÇERÇEVESİNİ IMPORT ET
from app.ui.main_app_window import MainApplicationWindow


def main():
    """Uygulamanın ana giriş noktası."""

    # Program başlamadan önce AppData içindeki veri klasörlerinin var olduğundan emin ol
    ensure_data_dirs_exist()

    # Veritabanı tablosunu kontrol et/oluştur
    create_table()

    app = QApplication(sys.argv)

    # YENİ ANA PENCEREMİZİ OLUŞTURUYORUZ
    window = MainApplicationWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()