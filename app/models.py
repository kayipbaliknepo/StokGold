# app/models.py
from dataclasses import dataclass, field
from datetime import date
from typing import Optional # Optional'ı import et

@dataclass
class Urun:
    # ... (diğer alanlar aynı)
    id: int = None
    urun_kodu: str = ""
    cins: str = ""
    ayar: int = 22
    gram: Optional[float] = None  # <-- float ya da None olabilir ve varsayılanı None.
    maliyet: float = 0.0
    # ... (kalan alanlar aynı)
    satis_fiyati: float = 0.0
    stok_adeti: int = 1
    aciklama: str = ""
    resim_yolu: str = None
    eklenme_tarihi: date = field(default_factory=date.today)

    def __post_init__(self):
        # Gram None değilse pozitif olmalı
        if self.gram is not None and (not isinstance(self.gram, (int, float)) or self.gram < 0):
            raise ValueError("Gram değeri pozitif bir sayı olmalıdır.")
        if not isinstance(self.stok_adeti, int) or self.stok_adeti < 0:
            raise ValueError("Stok adeti pozitif bir tam sayı olmalıdır.")