# ollama_test.py (En Detaylı Hata Ayıklama Versiyonu)

import ollama

print(">>> Ollama servisine bağlanılıyor...")
try:
    # ollama.list() komutunu çağır ve ham cevabı al
    response = ollama.list()

    print("\n--- OLLAMA'DAN GELEN HAM CEVAP ---")
    print(response)
    print("---------------------------------\n")

    # Ham cevabın içindeki 'models' listesini ayıkla
    models_data = response.get('models', [])

    print(">>> 'models' ANAHTARINDAN ÇIKARILAN LİSTE:")
    if not models_data:
        print("    (Liste boş veya okunamadı)")

    # Listedeki her bir modelin tüm detaylarını yazdır
    for model_info in models_data:
        print(f"    - {model_info}")

except Exception as e:
    print(f">>> HATA: Ollama servisine bağlanılamadı.")
    print(f">>> SEBEP: {e}")