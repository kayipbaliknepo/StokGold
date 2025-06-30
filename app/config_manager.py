import configparser
from .utils import CONFIG_PATH  # AppData içindeki config.ini yolunu alıyoruz

# Ayar dosyasını okumak için bir ConfigParser nesnesi oluşturuyoruz
config = configparser.ConfigParser()


def load_theme() -> str:
    """
    config.ini dosyasından kaydedilmiş tema ayarını okur.
    Eğer dosya veya ayar bulunamazsa, varsayılan olarak 'light' temasını döndürür.
    """
    try:
        config.read(CONFIG_PATH)
        # [Settings] bölümündeki 'theme' anahtarını oku
        # fallback='light', değer bulunamazsa ne döndüreceğini belirtir.
        theme = config.get('Settings', 'theme', fallback='light')
        print(f"Tema yüklendi: {theme}")
        return theme
    except Exception as e:
        print(f"Tema ayarları okunurken hata oluştu: {e}")
        return 'light'  # Herhangi bir hata durumunda güvenli moda (açık tema) dön


def save_theme(theme_name: str):
    """
    Kullanıcının seçtiği tema adını ('light' veya 'dark') config.ini dosyasına kaydeder.
    """
    try:
        # Eğer [Settings] bölümü yoksa oluştur
        if not config.has_section('Settings'):
            config.add_section('Settings')

        # 'theme' anahtarının değerini ayarla
        config.set('Settings', 'theme', theme_name)

        # Değişiklikleri dosyaya yaz
        with open(CONFIG_PATH, 'w') as configfile:
            config.write(configfile)
        print(f"Tema kaydedildi: {theme_name}")
        return True
    except Exception as e:
        print(f"Tema ayarları kaydedilirken hata oluştu: {e}")
        return False
