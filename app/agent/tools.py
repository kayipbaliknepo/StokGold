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


def _format_product_list(urunler: list[Urun]) -> str:
    """Gelen ürün listesini LLM'in anlayacağı temiz bir metne dönüştürür."""
    if not urunler:
        return "Belirtilen kritere uygun ürün bulunamadı."

    response_lines = ["Bulunan ürünler:"]
    for urun in urunler:
        line = f"- Cins: {urun.cins}, Kod: {urun.urun_kodu}, Stok: {urun.stok_adeti}"
        if urun.gram:
            line += f", Gram: {urun.gram}"
        response_lines.append(line)
    return "\n".join(response_lines)


@tool
def urun_ara(sorgu: str) -> str:
    """
    Veritabanında ürün kodu veya ürün cinsi (adı) ile arama yapmak için kullanılır.
    Örneğin 'yüzük', 'tektaş' veya 'URUN-12345' gibi bir metinle arama yapabilirsin.
    """
    print(f">>> Araç Kullanılıyor: urun_ara, Sorgu: {sorgu}")
    sonuclar = search_products(sorgu)
    return _format_product_list(sonuclar)


@tool
def dusuk_stok_raporu(esik_deger: int) -> str:
    """
    Stoğu belirtilen eşik değerinin altına düşmüş olan ürünleri listeler.
    Örneğin 'stoğu 5'ten az olan ürünler' için bu aracı esik_deger=5 ile kullan.
    """
    print(f">>> Araç Kullanılıyor: dusuk_stok_raporu, Eşik Değer: {esik_deger}")
    sonuclar = get_low_stock_products(esik_deger)
    if not sonuclar:
        return f"Stoğu {esik_deger} adedinin altında olan ürün bulunmuyor."

    response_lines = [f"Stoğu {esik_deger} adedinin altında olan ürünler:"]
    for row in sonuclar:
        response_lines.append(f"- Cins: {row['cins']}, Kod: {row['urun_kodu']}, Mevcut Stok: {row['stok_adeti']}")
    return "\n".join(response_lines)


@tool
def kar_zarar_raporu(baslangic_tarihi: str, bitis_tarihi: str) -> str:
    """
    Belirtilen başlangıç ve bitiş tarihleri arasındaki toplam satış, toplam maliyet ve net kar/zarar durumunu raporlar.
    'bugün', 'dün', 'bu ay', 'geçen ay' gibi ifadeleri anlar. Diğer durumlar için tarihleri 'YYYY-MM-DD' formatında ver.
    """
    print(f">>> Araç Kullanılıyor: kar_zarar_raporu, Başlangıç: {baslangic_tarihi}, Bitiş: {bitis_tarihi}")
    today = date.today()

    # Doğal dil tarih ifadelerini gerçek tarihlere çevirme
    if baslangic_tarihi == 'bugün':
        start_date = today
    elif baslangic_tarihi == 'dün':
        start_date = today - timedelta(days=1)
    elif baslangic_tarihi == 'bu ay':
        start_date = today.replace(day=1)
    elif baslangic_tarihi == 'geçen ay':
        last_month = today - relativedelta(months=1)
        start_date = last_month.replace(day=1)
    else:
        start_date = datetime.strptime(baslangic_tarihi, "%Y-%m-%d").date()

    if bitis_tarihi == 'bugün':
        end_date = today
    elif bitis_tarihi == 'dün':
        end_date = today - timedelta(days=1)
    elif bitis_tarihi == 'geçen ay':
        end_date = start_date.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
    else:
        end_date = datetime.strptime(bitis_tarihi, "%Y-%m-%d").date()

    stats = get_statistics_for_period(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

    return (
        f"Rapor Dönemi: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
        f"----------------------------------------\n"
        f"- Toplam Satış Tutarı: {stats['total_sales']:,.2f} TL\n"
        f"- Satılan Malların Maliyeti: {stats['total_cogs']:,.2f} TL\n"
        f"- Net Kâr / Zarar: {stats['net_profit']:,.2f} TL"
    )


@tool(return_direct=True)  # <-- DEĞİŞİKLİK 1: return_direct=True eklendi.
def get_stock_count_for_product(urun_adi: str) -> str:
    """
    Belirli bir ürünün adını vererek, o ürünün veya o ada uyan ürünlerin mevcut stok adetlerini öğrenmek için kullanılır.
    Kullanıcı bir şeyin 'sayısını', 'adedini' veya 'stok durumunu' sorduğunda bu araç ilk tercihin olmalı.
    """
    print(f">>> Araç Kullanılıyor: get_stock_count_for_product, Ürün Adı: {urun_adi}")
    results = search_products(urun_adi)

    if not results:
        return f"'{urun_adi}' adında bir ürün bulunamadı."

    # --- DEĞİŞİKLİK 2: Artık tam ve kullanıcıya hazır bir cümle döndürüyoruz ---
    if len(results) == 1:
        urun = results[0]
        return f"'{urun.cins}' ürününden stokta şu an {urun.stok_adeti} adet bulunmaktadır."

    response_lines = [f"'{urun_adi}' aramasıyla birden fazla ürün bulundu:"]
    for urun in results:
        response_lines.append(f"- {urun.cins} (Kod: {urun.urun_kodu}): {urun.stok_adeti} adet")

    return "\n".join(response_lines)


@tool(return_direct=True)  # <-- DEĞİŞİKLİK 1: return_direct=True eklendi.
def get_inventory_summary() -> str:
    """
    Envanterin genel bir özetini almak için kullanılır. Toplam ürün çeşidi, toplam gram ve toplam maliyet gibi bilgileri döndürür.
    """
    print(f">>> Araç Kullanılıyor: get_inventory_summary")
    total_value = get_total_inventory_value()
    total_grams = get_total_grams()
    variety_count = get_product_variety_count()

    # --- DEĞİŞİKLİK 2: Kullanıcıya hazır bir cümle döndürüyoruz ---
    return (
        f"İşte envanterinizin genel özeti:\n"
        f" - Toplamda {variety_count} çeşit ürün bulunmaktadır.\n"
        f" - Stoktaki ürünlerin toplam gramajı {total_grams:,.2f} gramdır.\n"
        f" - Envanterin toplam maliyet değeri ise {total_value:,.2f} TL'dir."
    )

@tool
def add_new_product(urun_kodu: str, cins: str, stok_adeti: int, maliyet: float, ayar: int = 22,
                    gram: float = None) -> str:
    """
    Sisteme yeni bir ürün eklemek için kullanılır. 'yeni ürün ekle', 'kaydet', 'listeye ekle' gibi komutlar için idealdir.
    Bu aracı kullanmak için urun_kodu, cins, stok_adeti ve maliyet bilgileri zorunludur.
    Eğer bu bilgiler eksikse, kullanıcıdan bu bilgileri iste.
    """
    print(f">>> Araç Kullanılıyor: add_new_product, Cins: {cins}")
    try:
        yeni_urun = Urun(
            urun_kodu=urun_kodu,
            cins=cins,
            stok_adeti=stok_adeti,
            maliyet=maliyet,
            ayar=ayar,
            gram=gram,
            eklenme_tarihi=date.today()
        )
        yeni_id = add_product(yeni_urun)
        if yeni_id:
            # Yeni ürün ekleme işlemini de bir 'Alış' olarak hareketler tablosuna loglayalım
            from app.database import log_transaction
            log_transaction(yeni_id, 'Alış', stok_adeti, maliyet)
            return f"Başarılı! '{cins}' ürünü, '{urun_kodu}' koduyla sisteme eklendi."
        else:
            return "Ürün eklenirken bir veritabanı hatası oluştu."
    except Exception as e:
        return f"Ürün eklenirken bir hata oluştu: {e}"


@tool
def stok_guncelle(urun_adi: str, miktar: int) -> str:
    """
    Mevcut bir ürünün stok adedini artırmak veya azaltmak için kullanılır.
    'arttır', 'azalt', 'ekle', 'düş' gibi ifadelerle birlikte kullanılır.
    Miktar, stok artışı için pozitif (örn: 3), stok azalışı için negatif (örn: -2) olmalıdır.
    Bu araç YENİ ürün oluşturmaz, sadece mevcut olanı günceller.
    """
    print(f">>> Araç Kullanılıyor: stok_guncelle, Ürün: {urun_adi}, Miktar: {miktar}")

    # Önce güncellenecek ürünü bulalım
    results = search_products(urun_adi)

    if not results:
        return f"'{urun_adi}' adında bir ürün bulunamadı. Lütfen önce ürünü aratın veya yeni ürün olarak ekleyin."

    if len(results) > 1:
        return f"'{urun_adi}' aramasıyla birden fazla ürün bulundu. Lütfen daha spesifik bir ürün adı veya ürün kodu belirtin."

    # Tek bir ürün bulundu, işleme devam et
    urun = results[0]

    # Satış ise stok kontrolü yap
    if miktar < 0 and abs(miktar) > urun.stok_adeti:
        return f"İşlem başarısız. '{urun.cins}' için stoktan düşülecek miktar ({abs(miktar)}) mevcut stoktan ({urun.stok_adeti}) fazla."

    # Stok ve hareket kaydını güncelle
    islem_tipi = 'Alış' if miktar > 0 else 'Satış'
    birim_fiyat = urun.maliyet if islem_tipi == 'Alış' else urun.satis_fiyati

    if update_stock(urun.id, miktar):
        log_transaction(urun.id, islem_tipi, abs(miktar), birim_fiyat)
        yeni_stok = urun.stok_adeti + miktar
        return f"Başarılı! '{urun.cins}' ürününün stoğu güncellendi. Yeni stok: {yeni_stok} adet."
    else:
        return "Stok güncellenirken bir veritabanı hatası oluştu."