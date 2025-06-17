import sys

from PyQt6.QtWidgets import QApplication
from app.database import create_table
from app.ui.main_window import MainWindow

def main():
    """Uygulamanın ana giriş noktası."""

    # 1. Veritabanı ve Tabloyu Hazırla
    # Uygulama başlamadan önce veritabanı tablosunun mevcut olduğundan emin ol.
    # create_table() fonksiyonu tablo zaten varsa hiçbir şey yapmaz.
    print("Veritabanı kontrol ediliyor...")
    create_table()
    print("Veritabanı hazır.")

    # 2. PyQt Uygulamasını Oluştur
    # Her PyQt uygulamasının bir QApplication nesnesine ihtiyacı vardır.
    app = QApplication(sys.argv)

    # 3. Ana Pencereyi Oluştur
    # Kendi yazdığımız MainWindow sınıfından bir nesne yaratıyoruz.
    window = MainWindow()
    window.show()  # Pencereyi ekranda görünür yap

    # 4. Uygulamanın Olay Döngüsünü Başlat
    # Bu satır, uygulama kapanana kadar programı çalışır durumda tutar.
    # Pencerenin açık kalmasını ve etkileşime girilebilmesini sağlar.
    sys.exit(app.exec())


if __name__ == '__main__':
    # Bu script doğrudan çalıştırıldığında main() fonksiyonunu çağır.
    # Bu, Python'da standart bir başlangıç yöntemidir.
    main()
