from langchain_core.tools import tool
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Veritabanı fonksiyonlarımıza erişmek için import ediyoruz
from app.database import (
    search_products,
    get_low_stock_products,
    get_statistics_for_period
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
