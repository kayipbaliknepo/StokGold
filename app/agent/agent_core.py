# app/agent/agent_core.py (Tüm Düzeltmeleri İçeren Son Hali)

import os
import traceback
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory

# Kendi oluşturduğumuz araçları import ediyoruz
from . import tools

# Agent'ımızın kullanabileceği araçların listesi
AGENT_TOOLS = [
    tools.stok_guncelle, # <-- YENİ VE EN SPESİFİK ARACIMIZ
    tools.get_stock_count_for_product,
    tools.add_new_product,
    tools.get_inventory_summary,
    tools.urun_ara,
    tools.dusuk_stok_raporu,
    tools.kar_zarar_raporu
]

class StokGoldAgent:
    """
    LangChain ve Groq API'sini kullanarak envanterle ilgili soruları yanıtlayan ana Agent sınıfı.
    """

    def __init__(self):  # <-- Artık dışarıdan 'model_name' parametresi almıyor
        print("StokGold Agent (Groq) başlatılıyor...")

        # 1. API Anahtarını .env dosyasından güvenli bir şekilde yükle
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY bulunamadı. Lütfen projenizin ana dizinindeki .env dosyasını kontrol edin.")

        # 2. LLM'i ChatGroq olarak, model adı sabit olacak şekilde tanımla
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama3-70b-8192"
        )

        # 3. Prompt ve Agent kurulumu aynı kalıyor...
        prompt_template = """
        Sen bir kuyumcu envanter yönetimi asistanısın. Görevin, sana verilen araçları kullanarak kullanıcının sorularını yanıtlamaktır. Cevapların her zaman Türkçe ve net olsun.

        İşlem adımların şunlar olmalı:
        1. Kullanıcının sorusunu ve sohbet geçmişini analiz et.
        2. Soruyu cevaplamak için hangi aracı kullanman gerektiğine karar ver.
        3. Aracı çalıştır ve sonucunu al.
        4. ÖNEMLİ KURAL: Eğer bu sonuç kullanıcının sorusunu doğrudan yanıtlıyorsa, görevin tamamlanmıştır. KESİNLİKLE başka bir araç çağırma. Sadece bu sonucu kullanarak kullanıcıya nihai cevabını ver.

        Sohbet Geçmişi:
        {chat_history}

        Kullanıcının Sorusu:
        {input}

        Düşünce ve Araç Kullanım Adımların:
        {agent_scratchpad}
        """
        self.prompt = ChatPromptTemplate.from_template(prompt_template)

        agent = create_tool_calling_agent(self.llm, AGENT_TOOLS, self.prompt)

        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=AGENT_TOOLS,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
        print("StokGold Agent (Groq) başarıyla yüklendi.")

    def run(self, user_query: str, chat_history: list = None) -> str:
        """
        Kullanıcıdan gelen sorguyu ve sohbet geçmişini alır, agent'ı çalıştırır.
        """
        if chat_history is None:
            chat_history = []
        try:
            # Sohbet geçmişi artık burada, invoke içinde gönderiliyor.
            response = self.agent_executor.invoke({
                "input": user_query,
                "chat_history": chat_history
            })
            return response.get('output', "Bir hata oluştu, cevap alınamadı.")
        except Exception as e:
            print(f"Agent çalışırken bir hata oluştu: {traceback.format_exc()}")
            return f"Üzgünüm, API isteği sırasında bir hata oluştu: {e}"