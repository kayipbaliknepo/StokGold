# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

import os
import shutil
from datetime import datetime
from .utils import DATABASE_PATH

def backup_database(target_directory: str) -> (bool, str):
    """
    Mevcut veritabanını belirtilen klasöre yedekler.
    Başarı durumunu ve mesajı döndürür.
    """
    try:
        if not os.path.exists(DATABASE_PATH):
            return False, "Yedeklenecek veritabanı dosyası bulunamadı."

        # Yedek dosyası için tarih damgalı bir isim oluştur
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        backup_file_name = f"stokgold_backup_{timestamp}.db"
        destination_path = os.path.join(target_directory, backup_file_name)

        # Veritabanı dosyasını kopyala
        shutil.copy2(DATABASE_PATH, destination_path)
        return True, f"Veritabanı başarıyla '{destination_path}' konumuna yedeklendi."
    except Exception as e:
        return False, f"Yedekleme sırasında bir hata oluştu: {e}"

def restore_database(source_path: str) -> (bool, str):
    """
    Seçilen yedek dosyasından geri yükleme yapar.
    Bu işlem mevcut veritabanının üzerine yazar.
    """
    try:
        if not os.path.exists(source_path):
            return False, "Seçilen yedek dosyası bulunamadı."

        # Mevcut veritabanı dosyasını yedekten gelenle değiştir
        shutil.copy2(source_path, DATABASE_PATH)

        return True, "Veritabanı başarıyla geri yüklendi. Değişikliklerin etkili olması için lütfen uygulamayı yeniden başlatın."
    except Exception as e:
        return False, f"Geri yükleme sırasında bir hata oluştu: {e}"