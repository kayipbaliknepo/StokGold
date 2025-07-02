# app/tamir_model.py (YENİ DOSYA)

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

@dataclass
class Tamir:
    """
    Bir tamir kaydını temsil eden veri sınıfı.
    """
    id: int = None
    musteri_ad_soyad: str = ""
    musteri_telefon: Optional[str] = None
    urun_aciklamasi: str = ""
    hasar_tespiti: str = ""
    alinan_tarih: date = field(default_factory=date.today)
    tahmini_teslim_tarihi: Optional[date] = None
    tamir_ucreti: Optional[float] = None
    durum: str = "Beklemede"
    notlar: Optional[str] = None