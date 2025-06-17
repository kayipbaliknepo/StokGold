# app/database.py - GÜNCELLENMİŞ VE DOĞRU KOD
from datetime import datetime
from .models import Urun
import sqlite3
import configparser
import os


def get_db_connection():
    """
    Proje ana dizinindeki config.ini dosyasını bularak veritabanı
    bağlantısı oluşturur ve bu bağlantıyı geri döner.
    """
    # 1. Projenin ana (kök) dizinini güvenilir bir şekilde bulalım
    #    __file__ -> app/database.py
    #    os.path.dirname(__file__) -> app
    #    os.path.join(..., '..') -> kuyumcu_stok_takip/ (Proje ana dizini)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # 2. config.ini dosyasının tam yolunu oluşturalım
    config_path = os.path.join(project_root, 'config.ini')

    config = configparser.ConfigParser()
    config.read(config_path)

    # 3. Veritabanı adını alalım. Bulamazsa 'kuyumcu.db' kullansın
    db_name = config.get('Database', 'name', fallback='kuyumcu.db')

    # 4. Veritabanı dosyasının da tam yolunu ana dizine göre oluşturalım
    db_path = os.path.join(project_root, db_name)

    # 5. Tam yola göre bağlantı kuralım
    print(f"Veritabanına bağlanılıyor: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    """
    Veritabanı bağlantısı kurar ve 'urunler' tablosunu, eğer
    zaten mevcut değilse, Urun modeline uygun şema ile oluşturur.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urunler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                urun_kodu TEXT NOT NULL UNIQUE,
                cins TEXT NOT NULL,
                ayar INTEGER DEFAULT 22,
                gram REAL,  -- <-- NOT NULL KALDIRILDI
                maliyet REAL DEFAULT 0.0,
                satis_fiyati REAL DEFAULT 0.0,
                stok_adeti INTEGER NOT NULL DEFAULT 1,
                aciklama TEXT,
                resim_yolu TEXT,
                eklenme_tarihi DATE NOT NULL
            )
        """)

        conn.commit()
        print("Tablo şeması başarıyla kontrol edildi/güncellendi.")

    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
    finally:
        if conn:
            conn.close()

def add_product(urun: Urun):
    """Veritabanına yeni bir Urun nesnesi ekler."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """INSERT INTO urunler (urun_kodu, cins, ayar, gram, maliyet, satis_fiyati, stok_adeti, aciklama, resim_yolu, eklenme_tarihi)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, (
            urun.urun_kodu, urun.cins, urun.ayar, urun.gram, urun.maliyet,
            urun.satis_fiyati, urun.stok_adeti, urun.aciklama, urun.resim_yolu,
            urun.eklenme_tarihi.strftime('%Y-%m-%d')
        ))
        conn.commit()
        return cursor.lastrowid  # Eklenen ürünün ID'sini döndür
    except sqlite3.Error as e:
        print(f"Veritabanı hatası (add_product): {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_all_products():
    """Veritabanındaki tüm ürünleri Urun nesneleri listesi olarak döndürür."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM urunler ORDER BY id DESC")
        rows = cursor.fetchall()

        urunler = []
        for row in rows:
            # Veritabanından gelen tarihi date objesine çevir
            tarih_objesi = datetime.strptime(row['eklenme_tarihi'], '%Y-%m-%d').date() if row[
                'eklenme_tarihi'] else None

            urunler.append(Urun(
                id=row['id'],
                urun_kodu=row['urun_kodu'],
                cins=row['cins'],
                ayar=row['ayar'],
                gram=row['gram'],
                maliyet=row['maliyet'],
                satis_fiyati=row['satis_fiyati'],
                stok_adeti=row['stok_adeti'],
                aciklama=row['aciklama'],
                resim_yolu=row['resim_yolu'],
                eklenme_tarihi=tarih_objesi
            ))
        return urunler
    except sqlite3.Error as e:
        print(f"Veritabanı hatası (get_all_products): {e}")
        return []
    finally:
        if conn:
            conn.close()

def delete_product(product_id: int):
    """Verilen ID'ye sahip ürünü veritabanından siler."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM urunler WHERE id = ?", (product_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Veritabanı hatası (delete_product): {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_product(urun: Urun):
    """Verilen Urun nesnesine göre veritabanındaki ilgili kaydı günceller."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """UPDATE urunler SET
                    urun_kodu = ?,
                    cins = ?,
                    ayar = ?,
                    gram = ?,
                    maliyet = ?,
                    satis_fiyati = ?,
                    stok_adeti = ?,
                    aciklama = ?,
                    resim_yolu = ?
                 WHERE id = ?"""
        cursor.execute(sql, (
            urun.urun_kodu, urun.cins, urun.ayar, urun.gram, urun.maliyet,
            urun.satis_fiyati, urun.stok_adeti, urun.aciklama, urun.resim_yolu,
            urun.id
        ))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Veritabanı hatası (update_product): {e}")
        return False
    finally:
        if conn:
            conn.close()


def search_products(search_term: str):
    """Verilen arama terimine göre ürün kodu veya cinsine göre ürünleri arar."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Arama teriminin başına ve sonuna % ekleyerek kısmi eşleşmeleri bulmasını sağlıyoruz.
        # Örn: 'yüz' araması, 'Yüzük' sonucunu getirecektir.
        query_term = f"%{search_term}%"

        # LIKE operatörü ile arama yapıyoruz. COLLATE NOCASE, büyük/küçük harf duyarsız arama yapar.
        sql = """SELECT * FROM urunler 
                 WHERE urun_kodu LIKE ? OR cins LIKE ? COLLATE NOCASE
                 ORDER BY id DESC"""

        cursor.execute(sql, (query_term, query_term))
        rows = cursor.fetchall()

        # get_all_products fonksiyonundaki ile aynı mantıkla Urun nesneleri oluşturuyoruz.
        urunler = []
        for row in rows:
            tarih_objesi = datetime.strptime(row['eklenme_tarihi'], '%Y-%m-%d').date() if row[
                'eklenme_tarihi'] else None
            urunler.append(Urun(
                id=row['id'], urun_kodu=row['urun_kodu'], cins=row['cins'], ayar=row['ayar'],
                gram=row['gram'], maliyet=row['maliyet'], satis_fiyati=row['satis_fiyati'],
                stok_adeti=row['stok_adeti'], aciklama=row['aciklama'], resim_yolu=row['resim_yolu'],
                eklenme_tarihi=tarih_objesi
            ))
        return urunler

    except sqlite3.Error as e:
        print(f"Veritabanı hatası (search_products): {e}")
        return []
    finally:
        if conn:
            conn.close()


# app/database.py (en alta eklenecek kod)

def get_total_inventory_value():
    """Stoktaki tüm ürünlerin toplam maliyet değerini hesaplar."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Her ürünün maliyeti ile stok adedini çarpıp genel toplamı alırız.
        sql = "SELECT SUM(maliyet * stok_adeti) FROM urunler"
        cursor.execute(sql)

        # fetchone() tek bir sonuç satırı döndürür, örn: (toplam_deger,)
        result = cursor.fetchone()[0]

        # Eğer veritabanı boşsa sonuç None olabilir, bu durumu kontrol edelim.
        return result if result is not None else 0.0

    except sqlite3.Error as e:
        print(f"Veritabanı hatası (get_total_inventory_value): {e}")
        return 0.0
    finally:
        if conn:
            conn.close()


def get_product_counts_by_type():
    """Ürünleri cinslerine göre gruplayıp her cinsten TOPLAM STOK ADEDİNİ sayar."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # COUNT(*) yerine SUM(stok_adeti) kullanarak toplam stok sayısını alıyoruz.
        sql = """SELECT cins, SUM(stok_adeti) as toplam_stok 
                 FROM urunler 
                 GROUP BY cins 
                 ORDER BY toplam_stok DESC"""
        cursor.execute(sql)

        return cursor.fetchall()

    except sqlite3.Error as e:
        print(f"Veritabanı hatası (get_product_counts_by_type): {e}")
        return []
    finally:
        if conn:
            conn.close()


# app/database.py dosyasının en altına YENİ fonksiyonu EKLEYİN:
def get_total_grams():
    """Stoktaki tüm ürünlerin toplam gramajını hesaplar."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Her ürünün gramını stok adedi ile çarpıp genel toplamı alırız.
        sql = "SELECT SUM(gram * stok_adeti) FROM urunler"
        cursor.execute(sql)

        result = cursor.fetchone()[0]
        return result if result is not None else 0.0

    except sqlite3.Error as e:
        print(f"Veritabanı hatası (get_total_grams): {e}")
        return 0.0
    finally:
        if conn:
            conn.close()


def update_stock(product_id: int, quantity_change: int):
    """
    Verilen ID'ye sahip ürünün stok miktarını değiştirir.
    quantity_change pozitif ise stok artar (alış), negatif ise azalır (satış).
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # stok_adeti = stok_adeti + ? sorgusu, mevcut değere ekleme/çıkarma yapar.
        # Bu, race condition'ları önleyen en güvenli yöntemdir.
        sql = "UPDATE urunler SET stok_adeti = stok_adeti + ? WHERE id = ?"

        cursor.execute(sql, (quantity_change, product_id))
        conn.commit()

        # Güncellemenin başarılı olup olmadığını kontrol et
        return cursor.rowcount > 0

    except sqlite3.Error as e:
        print(f"Veritabanı hatası (update_stock): {e}")
        return False
    finally:
        if conn:
            conn.close()

