# MIT License
# Copyright (c) 2025 Aykut Yahya Ay
# See LICENSE file for full license details.

import os
import sqlite3
import traceback
from dotenv import load_dotenv


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

from . import tools


AGENT_TOOLS = [
    tools.gunluk_islem_detaylari_getir,
    tools.stok_guncelle,
    tools.get_stock_count_for_product,
    tools.add_new_product,
    tools.get_inventory_summary,
    tools.urun_detaylarini_getir,
    tools.satis_kari_hesapla,
    tools.hesap_makinesi,
    tools.dusuk_stok_raporu,
    tools.kar_zarar_raporu,
]


class StokGoldAgent:
    """
    LangChain ve Google Gemini API'sini kullanarak envanterle ilgili soruları yanıtlayan
    yüksek stabiliteye sahip Agent sınıfı.
    """

    def __init__(self):
        print("StokGold Agent (Google Gemini) başlatılıyor...")
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")  # <-- Google API anahtarını okuyoruz
        if not api_key:
            raise ValueError("GOOGLE_API_KEY bulunamadı. Lütfen .env dosyasını kontrol edin.")

        # LLM olarak ChatGroq yerine ChatGoogleGenerativeAI kullanıyoruz
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            google_api_key=api_key,
            temperature=0,
            # Bu satır, sistem prompt'umuzun Gemini ile uyumlu çalışmasını sağlar. Önemlidir.
            convert_system_message_to_human=True
        )

        # En son geliştirdiğimiz stabil prompt'u kullanıyoruz
        prompt_template = """
        Sen, StokGold programı için geliştirilmiş, uzman bir kuyumcu envanter yönetimi asistanısın.
        Görevin, kullanıcının sorularını, sana verilen araçları en verimli ve doğru şekilde kullanarak yanıtlamaktır.

        **KARAR VERME KURALLARIN:**
        1.  **En Uygun Aracı Seç:** Bir soruyu cevaplamak için her zaman en basit ve en direkt aracı tercih et.
        2.  **Sayısal Hesaplama Yap:** Fark, toplam gibi basit matematiksel işlemler yapman gerektiğinde, önce gerekli sayısal verileri diğer araçlarla topla, sonra bu sayıları `hesap_makinesi` aracına vererek sonucu bul.
        3.  **Bilgiyi Al ve Dur:** Bir aracın çıktısı soruyu cevaplamak için yeterliyse, görevinin bittiğini anla ve kullanıcıya son cevabını ver.
        4.  **Güvenliği Sağla:** Veritabanını değiştiren araçları sadece kullanıcıdan açık bir komut geldiğinde kullan.

        Cevapların daima profesyonel, net ve Türkçe olsun.

        Sohbet Geçmişi: {chat_history}
        Kullanıcının Sorusu: {input}
        Düşünce ve Araç Kullanım Adımların: {agent_scratchpad}
        """
        self.prompt = ChatPromptTemplate.from_template(prompt_template)

        agent = create_tool_calling_agent(self.llm, AGENT_TOOLS, self.prompt)

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=AGENT_TOOLS,
            verbose=True,
            handle_parsing_errors="Lütfen tekrar dener misin, isteğini anlayamadım.",
            max_iterations=8  # Çok adımlı görevler için biraz daha fazla iterasyon hakkı
        )
        print("StokGold Agent (Google Gemini) başarıyla yüklendi.")

    def run(self, user_query: str, chat_history: list = None) -> str:
        # Bu fonksiyon aynı kalabilir
        if chat_history is None:
            chat_history = []
        try:
            response = self.agent_executor.invoke({
                "input": user_query,
                "chat_history": chat_history
            })
            return response.get('output', "Üzgünüm, bir cevap oluşturamadım.")
        except Exception as e:
            error_message = f"Agent çalışırken bir hata oluştu: {e}"
            print(f"{error_message}\n--- Traceback ---\n{traceback.format_exc()}")
            return "Üzgünüm, beklenmedik bir hata oluştu. Detaylar konsola yazdırıldı."



