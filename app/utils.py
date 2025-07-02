# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

import os
import sys  # sys modülünü import ediyoruz

def get_base_path():
    """
    Paketlendiğinde (.exe) veya normal script olarak çalıştırıldığında
    uygulamanın ana yolunu güvenilir bir şekilde bulur.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller tarafından oluşturulan geçici klasörün yolu (.exe modu)
        return sys._MEIPASS
    else:
        # Normal .py script'i olarak çalıştırıldığındaki yol
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_app_data_path():
    """
    Kullanıcının AppData klasöründe uygulama için bir veri klasörü oluşturur
    ve bu klasörün yolunu döndürür.
    """
    path = os.path.join(os.environ['LOCALAPPDATA'], 'StokGold')
    os.makedirs(path, exist_ok=True)
    return path


def get_icon_path(icon_name: str) -> str:
    """
    Gerekli ikon dosyasının tam yolunu, programın çalışma şekline
    (geliştirme veya .exe) göre doğru bir şekilde döndürür.
    """
    return os.path.join(get_base_path(), "assets", "icons", icon_name)


APP_DATA_PATH = get_app_data_path()

CONFIG_PATH = os.path.join(APP_DATA_PATH, "config.ini")

DATABASE_PATH = os.path.join(APP_DATA_PATH, "stokgold.db")
IMAGE_DIR = os.path.join(APP_DATA_PATH, "product_images")
BARCODE_DIR = os.path.join(APP_DATA_PATH, "barcodes")

# Bu artık sadece ikon yolu oluşturmak için kullanılacak
# ASSETS_PATH = os.path.join(get_base_path(), "assets")
# ICON_PATH = os.path.join(ASSETS_PATH, "icons", "app_icon.ico")


def ensure_data_dirs_exist():
    """Resim ve barkod klasörlerinin AppData içinde var olduğundan emin olur."""
    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs(BARCODE_DIR, exist_ok=True)