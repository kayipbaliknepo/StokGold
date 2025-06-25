# app/agent/tools.py (Nihai, Stabil ve Güvenilir Sürüm)

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
    log_transaction
)
from app.models import Urun

# --- YARDIMCI FONKSİYON ---

def _format_product_list(urunler: list[Urun]) -> str:
    """Gelen ürün listesini LLM'in anlayacağı temiz ve detaylı bir metne dönüştürür."""
    if not urunler:
        return "Belirtilen kritere uygun ürün bulunamadı."

    lines = ["Bulunan ürünler:"]
    for urun in urunler:
        line = (
            f"- Cins: {urun.cins}, Kod: {urun.urun_kodu}, Stok: {urun.stok_adeti}, "
            f"Maliyet: {urun.maliyet:,.2f} TL, Satış Fiyatı: {urun.satis_fiyati:,.2f} TL"
        )
        if urun.gram:
            line += f", Gram: {urun.gram}"
        lines.append(line)
    return "\n".join(lines)


# --- DOĞRUDAN CEVAP VEREN 'OKUMA' VE 'RAPORLAMA' ARAÇLARI ---
# Not: Bu araçlar, Groq API hatasını engellemek için `return_direct=True` kullanır.

@tool(return_direct=True)
def stok_bilgisi_ver(urun_adi: str) -> str:
    """
    Kullanıcı bir ürünün SADECE ve SADECE stok adedini veya sayısını sorduğunda kullanılır.
    Bu araç en basit ve en hızlı yoldur. Örnek: 'ata altın stoğu', 'kaç adet tektaş var?'.
    Eğer kullanıcı maliyet, satış fiyatı gibi BAŞKA BİR DETAY daha istiyorsa bu aracı KESİNLİKLE KULLANMA.
    """
    print(f">>> Araç Kullanılıyor (Doğrudan Cevap): stok_bilgisi_ver, Ürün: {urun_adi}")
    results = search_products(urun_adi)
    if not results:
        return f"'{urun_adi}' adında bir ürün bulunamadı."
    if len(results) > 1:
        response_lines = [f"'{urun_adi}' aramasıyla birden fazla ürün bulundu, lütfen ürün kodu ile tekrar sorun:"]
        for urun in results:
            response_lines.append(f"- Cins: {urun.cins}, Kod: {urun.urun_kodu}, Stok: {urun.stok_adeti}")
        return "\n".join(response_lines)
    urun = results[0]
    return f"{urun.cins} (Kod: {urun.urun_kodu}) ürününden stokta şu an {urun.stok_adeti} adet bulunmaktadır."

@tool(return_direct=True)
def urun_detaylarini_getir(sorgu: str) -> str:
    """
    Bir ürün hakkında stok, maliyet, satış fiyatı gibi BİRDEN FAZLA VEYA DETAYLI bilgiyi almak için kullanılır.
    Eğer kullanıcı SADECE stok adedi soruyorsa, bu aracı KULLANMA; onun yerine `stok_bilgisi_ver` aracını kullanmalısın.
    """
    print(f">>> Araç Kullanılıyor (Doğrudan Cevap): urun_detaylarini_getir, Sorgu: {sorgu}")
    sonuclar = search_products(sorgu)
    return _format_product_list(sonuclar)

@tool(return_direct=True)
def get_inventory_summary() -> str:
    """Envanterin genel bir özetini (toplam ürün çeşidi, toplam gram, toplam maliyet) almak için kullanılır."""
    print(f">>> Araç Kullanılıyor (Doğrudan Cevap): get_inventory_summary")
    total_value = get_total_inventory_value()
    total_grams = get_total_grams()
    variety_count = get_product_variety_count()
    return (
        f"İşte envanterinizin genel özeti:\n"
        f" - Toplamda {variety_count} çeşit ürün bulunmaktadır.\n"
        f" - Stoktaki ürünlerin toplam gramajı {total_grams:,.2f} gramdır.\n"
        f" - Envanterin toplam maliyet değeri ise {total_value:,.2f} TL'dir."
    )

@tool(return_direct=True)
def dusuk_stok_raporu(esik_deger: int) -> str:
    """Stoğu belirtilen eşik değerinin altına düşmüş olan ürünleri listeler. Sadece raporlama amaçlıdır."""
    print(f">>> Araç Kullanılıyor (Doğrudan Cevap): dusuk_stok_raporu, Eşik Değer: {esik_deger}")
    sonuclar = get_low_stock_products(esik_deger)
    if not sonuclar:
        return f"Stoğu {esik_deger} adedinin altında olan ürün bulunmuyor."
    response_lines = [f"Stoğu {esik_deger} adedinin altında olan ürünler:"]
    for row in sonuclar:
        response_lines.append(f"- Cins: {row['cins']}, Kod: {row['urun_kodu']}, Mevcut Stok: {row['stok_adeti']}")
    return "\n".join(response_lines)

@tool(return_direct=True)
def kar_zarar_raporu(baslangic_tarihi: str, bitis_tarihi: str) -> str:
    """Belirtilen tarihler arasındaki toplam satış, maliyet ve net kar/zarar durumunu raporlar."""
    print(f">>> Araç Kullanılıyor (Doğrudan Cevap): kar_zarar_raporu, Başlangıç: {baslangic_tarihi}, Bitiş: {bitis_tarihi}")
    today = date.today()
    start_date, end_date = None, None
    if baslangic_tarihi == 'bugün': start_date = today
    elif baslangic_tarihi == 'dün': start_date = today - timedelta(days=1)
    elif baslangic_tarihi == 'bu ay': start_date = today.replace(day=1)
    elif baslangic_tarihi == 'geçen ay': start_date = (today - relativedelta(months=1)).replace(day=1)
    else: start_date = datetime.strptime(baslangic_tarihi, "%Y-%m-%d").date()
    if bitis_tarihi == 'bugün': end_date = today
    elif bitis_tarihi == 'dün': end_date = today - timedelta(days=1)
    elif bitis_tarihi == 'geçen ay': end_date = start_date.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
    else: end_date = datetime.strptime(bitis_tarihi, "%Y-%m-%d").date()
    stats = get_statistics_for_period(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    return (
        f"Rapor Dönemi: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
        f"----------------------------------------\n"
        f"- Toplam Satış Tutarı: {stats['total_sales']:,.2f} TL\n"
        f"- Satılan Malların Maliyeti: {stats['total_cogs']:,.2f} TL\n"
        f"- Net Kâr / Zarar: {stats['net_profit']:,.2f} TL"
    )

# --- ÇOK ADIMLI MANTIK VE VERİ YAZMA ARAÇLARI ---
# Not: Bu araçlar, agent'ın düşünüp karar vermesi gerektiği için `return_direct=False` (varsayılan) olarak kalır.

@tool
def satis_kari_hesapla(urun_adi: str, adet: int) -> str:
    """
    Belirli bir üründen belirtilen adette satılırsa ne kadar TOPLAM KÂR elde edileceğini hesaplar.
    Bu araç, çok adımlı 'ne kadar kazanırım?' gibi sorular için bir hesaplama yardımcısıdır.
    """
    print(f">>> Araç Kullanılıyor (Hesaplama): satis_kari_hesapla, Ürün: {urun_adi}, Adet: {adet}")
    results = search_products(urun_adi)
    if not results: return f"'{urun_adi}' adında bir ürün bulunamadı."
    if len(results) > 1: return f"'{urun_adi}' aramasıyla birden fazla ürün bulundu. Lütfen daha spesifik olun."
    urun = results[0]
    if urun.satis_fiyati <= 0 or urun.maliyet <= 0:
        return f"'{urun.cins}' ürününün kâr hesaplaması için satış fiyatı ve maliyet bilgileri eksik."
    birim_kar = urun.satis_fiyati - urun.maliyet
    toplam_kar = birim_kar * adet
    return (f"'{urun.cins}' ürününden birim kâr: {birim_kar:,.2f} TL. "
            f"Toplam {adet} adet satıştan elde edilecek kâr: {toplam_kar:,.2f} TL.")

@tool
def stok_guncelle(urun_adi: str, miktar: int) -> str:
    """
    DİKKAT: Veritabanını DEĞİŞTİRİR. Sadece kullanıcı 'satıldı', 'stoktan düş', 'ekle' gibi net bir komut verdiğinde kullan.
    Miktar, artış için pozitif (örn: 3), azalış için negatif (örn: -2) olmalıdır.
    """
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
    """
    DİKKAT: Veritabanına YENİ KAYIT EKLER. Sadece kullanıcı 'yeni ürün oluştur', 'bunu kaydet' gibi net bir komut verdiğinde kullan.
    urun_kodu, cins, stok_adeti, maliyet ve satis_fiyati bilgileri zorunludur.
    """
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
        else:
            return "Ürün eklenirken bir veritabanı hatası oluştu."
    except Exception as e:
        return f"Ürün eklenirken bir hata oluştu: {e}"


@tool
def hesap_makinesi(ifade: str) -> str:
    """
    Basit matematiksel işlemleri (toplama, çıkarma, çarpma, bölme) yapmak için kullanılır.
    İki veya daha fazla sayının sonucunu bulman gerektiğinde bu aracı kullan.
    Örnek: '71 - 46' veya '5 * 250'.
    Bu araç SADECE sayısal hesaplama yapar.
    """
    print(f">>> Araç Kullanılıyor (Hesaplama): hesap_makinesi, İfade: {ifade}")

    # Güvenlik Önlemi: Sadece sayılar ve temel operatörlere izin ver
    if not re.match(r"^[0-9\s\.\+\-\*\/()]+$", ifade):
        return "Geçersiz ifade. Sadece sayılar ve +, -, *, / operatörleri kullanılabilir."

    try:
        # Güvenli eval kullanımı ile matematiksel ifadeyi hesapla
        sonuc = eval(ifade, {"__builtins__": None}, {})
        return str(sonuc)
    except Exception as e:
        return f"Hesaplama hatası: {e}"