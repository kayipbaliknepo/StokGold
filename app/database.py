# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

from datetime import datetime
from .models import Urun
import sqlite3
from .utils import DATABASE_PATH
import os


def get_db_connection():
    """AppData'daki veritabanı dosyasına bağlanır."""
    conn = sqlite3.connect(DATABASE_PATH)
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

        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS hareketler (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        urun_id INTEGER NOT NULL,
                        tip TEXT NOT NULL, -- 'Alış' veya 'Satış'
                        adet INTEGER NOT NULL,
                        birim_fiyat REAL NOT NULL,
                        toplam_tutar REAL NOT NULL,
                        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (urun_id) REFERENCES urunler (id)
                    )
                """)

        conn.commit()

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
        return cursor.lastrowid
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



        query_term = f"%{search_term}%"

        # LIKE operatörü ile arama yapıyoruz. COLLATE NOCASE, büyük/küçük harf duyarsız arama yapar.
        sql = """SELECT * FROM urunler 
                 WHERE urun_kodu LIKE ? OR cins LIKE ? COLLATE NOCASE
                 ORDER BY id DESC"""

        cursor.execute(sql, (query_term, query_term))
        rows = cursor.fetchall()


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




def get_total_inventory_value():
    """Stoktaki tüm ürünlerin toplam maliyet değerini hesaplar."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()


        sql = "SELECT SUM(maliyet * stok_adeti) FROM urunler"
        cursor.execute(sql)


        result = cursor.fetchone()[0]


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



        sql = "UPDATE urunler SET stok_adeti = stok_adeti + ? WHERE id = ?"

        cursor.execute(sql, (quantity_change, product_id))
        conn.commit()


        return cursor.rowcount > 0

    except sqlite3.Error as e:
        print(f"Veritabanı hatası (update_stock): {e}")
        return False
    finally:
        if conn:
            conn.close()


def log_transaction(urun_id: int, tip: str, adet: int, birim_fiyat: float):
    """Yapılan bir alış veya satış işlemini hareketler tablosuna kaydeder."""
    conn = get_db_connection()
    cursor = conn.cursor()
    toplam_tutar = adet * birim_fiyat
    sql = """INSERT INTO hareketler (urun_id, tip, adet, birim_fiyat, toplam_tutar)
             VALUES (?, ?, ?, ?, ?)"""
    try:
        cursor.execute(sql, (urun_id, tip, adet, birim_fiyat, toplam_tutar))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Hareket loglama hatası: {e}")
    finally:
        conn.close()


def get_daily_summary(selected_date: str):
    """Belirli bir tarihteki toplam alış ve satış tutarlarını döndürür."""
    conn = get_db_connection()
    cursor = conn.cursor()
    summary = {'alis': 0.0, 'satis': 0.0}
    try:
        # Toplam Alış
        sql_alis = "SELECT SUM(toplam_tutar) FROM hareketler WHERE tip = 'Alış' AND date(tarih) = ?"
        cursor.execute(sql_alis, (selected_date,))
        result_alis = cursor.fetchone()[0]
        if result_alis:
            summary['alis'] = result_alis

        # Toplam Satış
        sql_satis = "SELECT SUM(toplam_tutar) FROM hareketler WHERE tip = 'Satış' AND date(tarih) = ?"
        cursor.execute(sql_satis, (selected_date,))
        result_satis = cursor.fetchone()[0]
        if result_satis:
            summary['satis'] = result_satis

    except sqlite3.Error as e:
        print(f"Günlük özet alınırken hata: {e}")
    finally:
        conn.close()
    return summary


def get_transactions_for_date(selected_date: str):
    """
    Belirli bir tarihteki tüm hareketleri, ürün detaylarıyla birlikte döndürür.
    """
    conn = get_db_connection()
    # Sonuçları sözlük olarak almak için row_factory'i geçici olarak değiştiriyoruz
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # hareketler (h) ve urunler (u) tablolarını JOIN ile birleştiriyoruz.
    sql = """SELECT 
                h.tip, 
                h.adet, 
                h.birim_fiyat, 
                h.toplam_tutar,
                h.tarih,
                u.urun_kodu,
                u.cins,
                u.ayar,
                u.gram
             FROM hareketler h
             JOIN urunler u ON h.urun_id = u.id
             WHERE date(h.tarih) = ?
             ORDER BY h.tarih DESC"""

    try:
        cursor.execute(sql, (selected_date,))
        # Her satırı bir sözlüğe çevirerek liste halinde döndür
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Günlük hareketler alınırken hata: {e}")
        return []
    finally:
        conn.close()
def get_statistics_for_period(start_date: str, end_date: str):
    """
    Belirli bir tarih aralığı için satış istatistiklerini hesaplar.
    Toplam Satış, Toplam Maliyet ve Net Kâr döndürür.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    stats = {
        'total_sales': 0.0,
        'total_cogs': 0.0,  # Cost of Goods Sold (Satılan Malın Maliyeti)
        'net_profit': 0.0
    }

    try:
        # 1. Belirtilen aralıktaki Toplam Satış Tutarını Hesapla
        sql_sales = """SELECT SUM(toplam_tutar) FROM hareketler 
                       WHERE tip = 'Satış' AND date(tarih) BETWEEN ? AND ?"""
        cursor.execute(sql_sales, (start_date, end_date))
        total_sales_result = cursor.fetchone()[0]
        if total_sales_result:
            stats['total_sales'] = total_sales_result

        # 2. Aynı aralıkta Satılan Malların Maliyetini Hesapla
        sql_cogs = """SELECT SUM(h.adet * u.maliyet) 
                      FROM hareketler h
                      JOIN urunler u ON h.urun_id = u.id
                      WHERE h.tip = 'Satış' AND date(h.tarih) BETWEEN ? AND ?"""
        cursor.execute(sql_cogs, (start_date, end_date))
        total_cogs_result = cursor.fetchone()[0]
        if total_cogs_result:
            stats['total_cogs'] = total_cogs_result

        # 3. Net Kârı Hesapla
        stats['net_profit'] = stats['total_sales'] - stats['total_cogs']

    except sqlite3.Error as e:
        print(f"İstatistik hesaplama hatası: {e}")
    finally:
        if conn:
            conn.close()

    return stats


