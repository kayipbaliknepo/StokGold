# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

import os
import re

from langchain_core.tools import tool
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

# Veritabanı fonksiyonlarımıza erişmek için import ediyoruz
from app.database import (
    search_products,
    get_low_stock_products,
    get_statistics_for_period,
    get_total_grams,
    get_total_inventory_value,
    get_product_variety_count,
    add_product,
    update_stock,
    log_transaction,
    get_transactions_for_date
)
from app.models import Urun

# --- YARDIMCI FONKSİYON ---
def _format_product_list(urunler: list[Urun]) -> str:
    """Gelen ürün listesini LLM'in anlayacağı temiz bir metne dönüştürür."""
    if not urunler:
        return "Belirtilen kritere uygun ürün bulunamadı."
    lines = ["Bulunan ürünler:"]
    for urun in urunler:
        line = (
            f"- Cins: {urun.cins}, Kod: {urun.urun_kodu}, Stok: {urun.stok_adeti}"
        )
        if urun.gram:
            line += f", Gram: {urun.gram}"
        lines.append(line)
    return "\n".join(lines)


# --- MEVCUT VE YENİ TÜM ARAÇLAR ---

@tool
def urun_ara(sorgu: str) -> str:
    """Veritabanında ürün kodu veya ürün cinsi ile genel bir arama yapmak için kullanılır."""
    print(f">>> Araç Kullanılıyor: urun_ara, Sorgu: {sorgu}")
    sonuclar = search_products(sorgu)
    return _format_product_list(sonuclar)



@tool(return_direct=True)
def get_stock_count_for_product(urun_adi: str) -> str:
    """Sadece bir ürünün stok adedini öğrenmek için kullanılır. Kullanıcı 'sayı', 'adet', 'stok durumu' sorduğunda bu en iyi araçtır."""
    print(f">>> Araç Kullanılıyor (Doğrudan Cevap): get_stock_count_for_product, Ürün: {urun_adi}")
    results = search_products(urun_adi)
    if not results: return f"'{urun_adi}' adında bir ürün bulunamadı."
    if len(results) == 1:
        urun = results[0]
        return f"'{urun.cins}' ürününden stokta {urun.stok_adeti} adet bulunmaktadır."
    response_lines = [f"'{urun_adi}' aramasıyla birden fazla ürün bulundu:"]
    for urun in results: response_lines.append(f"- {urun.cins}: {urun.stok_adeti} adet")
    return "\n".join(response_lines)

@tool
def stok_guncelle(urun_adi: str, miktar: int) -> str:
    """Mevcut bir ürünün stok adedini artırmak veya azaltmak için kullanılır. Artış için pozitif (3), azalış için negatif (-2) miktar verilir."""
    print(f">>> Araç Kullanılıyor (Yazma): stok_guncelle, Ürün: {urun_adi}, Miktar: {miktar}")
    results = search_products(urun_adi)
    if not results: return f"'{urun_adi}' adında bir ürün bulunamadı."
    if len(results) > 1: return f"'{urun_adi}' aramasıyla birden fazla ürün bulundu. Lütfen daha spesifik olun."
    urun = results[0]
    if miktar < 0 and abs(miktar) > urun.stok_adeti:
        return f"İşlem başarısız. Stok yeterli değil. Mevcut stok: {urun.stok_adeti}"
    islem_tipi = 'Alış' if miktar > 0 else 'Satış'
    birim_fiyat = urun.maliyet if islem_tipi == 'Alış' else urun.satis_fiyati
    if update_stock(urun.id, miktar):
        log_transaction(urun.id, islem_tipi, abs(miktar), birim_fiyat)
        yeni_stok = urun.stok_adeti + miktar
        return f"Başarılı! '{urun.cins}' ürününün stoğu güncellendi. Yeni stok: {yeni_stok} adet."
    else:
        return "Stok güncellenirken bir veritabanı hatası oluştu."

@tool
def add_new_product(urun_kodu: str, cins: str, stok_adeti: int, maliyet: float, satis_fiyati: float, ayar: int = 22, gram: float = None) -> str:
    """Veritabanına YENİ bir ürün ekler. Kullanıcı 'yeni ürün oluştur', 'kaydet' gibi bir komut verdiğinde kullanılır."""
    print(f">>> Araç Kullanılıyor (Yazma): add_new_product, Cins: {cins}")
    try:
        yeni_urun = Urun(
            urun_kodu=urun_kodu, cins=cins, stok_adeti=stok_adeti,
            maliyet=maliyet, satis_fiyati=satis_fiyati, ayar=ayar, gram=gram,
            eklenme_tarihi=date.today()
        )
        yeni_id = add_product(yeni_urun)
        if yeni_id:
            log_transaction(yeni_id, 'Alış', stok_adeti, maliyet)
            return f"Başarılı! '{cins}' ürünü, '{urun_kodu}' koduyla sisteme eklendi."
        else: return "Ürün eklenirken bir veritabanı hatası oluştu."
    except Exception as e: return f"Ürün eklenirken bir hata oluştu: {e}"

@tool(return_direct=True)
def dusuk_stok_raporu(esik_deger: int) -> str:
    """Stoğu belirtilen eşik değerinin altına düşmüş olan ürünleri listeler."""
    print(f">>> Araç Kullanılıyor (Doğrudan Cevap): dusuk_stok_raporu, Eşik Değer: {esik_deger}")
    sonuclar = get_low_stock_products(esik_deger)
    if not sonuclar: return f"Stoğu {esik_deger} adedinin altında olan ürün bulunmuyor."
    response_lines = [f"Stoğu {esik_deger} adedinin altında olan ürünler:"]
    for row in sonuclar: response_lines.append(f"- Cins: {row['cins']}, Kod: {row['urun_kodu']}, Mevcut Stok: {row['stok_adeti']}")
    return "\n".join(response_lines)

@tool(return_direct=True)
def kar_zarar_raporu(baslangic_tarihi: str, bitis_tarihi: str) -> str:
    """
        SADECE finansal özet almak için kullanılır. Belirtilen tarihler arasındaki
        toplam satış, maliyet ve net kar/zarar durumunu raporlar.
        Eğer kullanıcı tek tek ürün listesi istiyorsa bu aracı KULLANMA.
        """
    print(f">>> Araç Kullanılıyor (Doğrudan Cevap): kar_zarar_raporu, Başlangıç: {baslangic_tarihi}, Bitiş: {bitis_tarihi}")
    today = date.today()
    try:
        if baslangic_tarihi == 'bugün': start_date = today
        elif baslangic_tarihi == 'dün': start_date = today - timedelta(days=1)
        elif baslangic_tarihi == 'bu ay': start_date = today.replace(day=1)
        elif baslangic_tarihi == 'geçen ay': start_date = (today - relativedelta(months=1)).replace(day=1)
        else: start_date = datetime.strptime(baslangic_tarihi, "%Y-%m-%d").date()
        if bitis_tarihi == 'bugün': end_date = today
        elif bitis_tarihi == 'dün': end_date = today - timedelta(days=1)
        elif bitis_tarihi == 'bu ay': end_date = today
        elif bitis_tarihi == 'geçen ay': end_date = today.replace(day=1) - timedelta(days=1)
        else: end_date = datetime.strptime(bitis_tarihi, "%Y-%m-%d").date()
    except ValueError:
        return "Tarih formatı anlaşılamadı. Lütfen 'YYYY-MM-DD' formatını veya 'bugün', 'geçen ay' gibi ifadeleri kullanın."
    stats = get_statistics_for_period(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    return (f"Rapor Dönemi: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
            f"----------------------------------------\n"
            f"- Toplam Satış Tutarı: {stats['total_sales']:,.2f} TL\n"
            f"- Satılan Malların Maliyeti: {stats['total_cogs']:,.2f} TL\n"
            f"- Net Kâr / Zarar: {stats['net_profit']:,.2f} TL")


@tool(return_direct=True)
def gunluk_islem_detaylari_getir(tarih: str, islem_tipi: str = "Tümü") -> str:
    """
    Belirli bir tarihte yapılan 'Alış' veya 'Satış' işlemlerinin detaylı listesini almak için kullanılır.
    Kullanıcı 'alınan mallar', 'satılan ürünler' veya 'bugünkü işlemler' gibi bir liste istediğinde bu aracı kullan.
    'islem_tipi' olarak 'Alış', 'Satış' veya 'Tümü' belirtilebilir.
    ÖNEMLİ: Bu aracı çağırmadan önce, kullanıcıdan gelen '27 Haziran' gibi bir tarihi mutlaka 'YYYY-MM-DD' formatına çevirmelisin.
    """
    print(f">>> Araç Kullanılıyor (Doğrudan Cevap): gunluk_islem_detaylari_getir, Tarih: {tarih}, Tip: {islem_tipi}")

    # Arka planda, daha önce yazdığımız veritabanı fonksiyonunu kullanıyoruz
    from app.database import get_transactions_for_date

    try:
        # Tarih formatını doğrula
        datetime.strptime(tarih, "%Y-%m-%d")
    except ValueError:
        return f"Geçersiz tarih formatı. Lütfen 'YYYY-MM-DD' formatında bir tarih belirtin. Örneğin bugünün tarihi: {date.today().strftime('%Y-%m-%d')}"

    transactions = get_transactions_for_date(tarih)

    if not transactions:
        return f"{tarih} tarihinde herhangi bir işlem bulunamadı."

    if islem_tipi != "Tümü":
        transactions = [tx for tx in transactions if tx['tip'] == islem_tipi]

    if not transactions:
        return f"{tarih} tarihinde '{islem_tipi}' tipinde bir işlem bulunamadı."

    response_lines = [f"{tarih} tarihli '{islem_tipi}' işlemleri:"]
    for tx in transactions:
        response_lines.append(
            f"- Saat: {tx['tarih'][11:16]}, Cins: {tx['cins']}, Adet: {tx['adet']}, "
            f"Toplam Tutar: {tx['toplam_tutar']:,.2f} TL"
        )
    return "\n".join(response_lines)


# Bu araçları daha önce eklemiştik, burada olmaları önemli.
@tool(return_direct=True)
def get_inventory_summary() -> str:
    """Envanterin genel bir özetini almak için kullanılır."""
    print(f">>> Araç Kullanılıyor (Doğrudan Cevap): get_inventory_summary")
    total_value = get_total_inventory_value(); total_grams = get_total_grams(); variety_count = get_product_variety_count()
    return (f"Envanter Özeti:\n- Toplam Ürün Çeşidi: {variety_count}\n- Toplam Gramaj: {total_grams:,.2f} gr\n- Toplam Maliyet: {total_value:,.2f} TL")

@tool
def hesap_makinesi(ifade: str) -> str:
    """Basit matematiksel işlemleri (toplama, çıkarma, çarpma, bölme) yapmak için kullanılır."""
    print(f">>> Araç Kullanılıyor (Hesaplama): hesap_makinesi, İfade: {ifade}")
    if not re.match(r"^[0-9\s\.\+\-\*\/()]+$", ifade):
        return "Geçersiz ifade. Sadece sayılar ve +, -, *, / operatörleri kullanılabilir."
    try:
        sonuc = eval(ifade, {"__builtins__": None}, {})
        return str(sonuc)
    except Exception as e: return f"Hesaplama hatası: {e}"

# Bu da daha önce eklediğimiz urun_detaylarini_getir aracı
@tool(return_direct=True)
def urun_detaylarini_getir(sorgu: str) -> str:
    """Bir ürün hakkında stok, maliyet, satış fiyatı gibi BİRDEN FAZLA VEYA DETAYLI bilgiyi almak için kullanılır."""
    print(f">>> Araç Kullanılıyor (Doğrudan Cevap): urun_detaylarini_getir, Sorgu: {sorgu}")
    sonuclar = search_products(sorgu)
    if not sonuclar: return f"'{sorgu}' aramasına uygun ürün bulunamadı."
    lines = ["Bulunan ürün detayları:"]
    for urun in sonuclar:
        line = (f"- Cins: {urun.cins}, Kod: {urun.urun_kodu}, Stok: {urun.stok_adeti}, "
                f"Maliyet: {urun.maliyet:,.2f} TL, Satış Fiyatı: {urun.satis_fiyati:,.2f} TL")
        if urun.gram: line += f", Gram: {urun.gram}"
        lines.append(line)
    return "\n".join(lines)

@tool(return_direct=True)
def satis_kari_hesapla(urun_adi: str, adet: int) -> str:
    """Belirli bir üründen belirtilen adette satılırsa ne kadar TOPLAM KÂR elde edileceğini hesaplar."""
    print(f">>> Araç Kullanılıyor (Hesaplama): satis_kari_hesapla, Ürün: {urun_adi}, Adet: {adet}")
    results = search_products(urun_adi)
    if not results: return f"'{urun_adi}' adında bir ürün bulunamadı."
    if len(results) > 1: return f"'{urun_adi}' aramasıyla birden fazla ürün bulundu. Lütfen daha spesifik olun."
    urun = results[0]
    if urun.satis_fiyati <= 0 or urun.maliyet <= 0:
        return f"'{urun.cins}' ürününün kâr hesaplaması için satış fiyatı ve maliyet bilgileri eksik."
    birim_kar = urun.satis_fiyati - urun.maliyet
    toplam_kar = birim_kar * adet
    return (f"'{urun.cins}' ürününden birim kâr: {birim_kar:,.2f} TL. Toplam {adet} adet satıştan elde edilecek kâr: {toplam_kar:,.2f} TL.")