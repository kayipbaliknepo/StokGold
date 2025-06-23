import ollama
from langchain_ollama.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Kendi oluşturduğumuz araçları import ediyoruz
from . import tools

# Agent'ımızın kullanabileceği tüm araçların bir listesi
AGENT_TOOLS = [
    tools.urun_ara,
    tools.dusuk_stok_raporu,
    tools.kar_zarar_raporu
]


class StokGoldAgent:
    """
    LangChain ve Ollama kullanarak envanterle ilgili soruları yanıtlayan ana Agent sınıfı.
    """

    def __init__(self, model_name: str):
        print(f"StokGold Agent '{model_name}' modeli ile başlatılıyor...")

        # Dışarıdan gelen, doğrulanmış ve tam model adını kullanıyoruz.
        self.llm = ChatOllama(model=model_name)

        prompt_template = """
        Sen bir kuyumcu envanter yönetimi programı olan StokGold içinde çalışan, 'StokGold Asistanı' adında bir uzmansın.
        Görevin, kullanıcının envanterle ilgili sorularını, sana verilen araçları kullanarak net ve doğru bir şekilde yanıtlamaktır.
        Cevapların her zaman Türkçe olmalı.
        Kullanıcının sorusu aşağıdadır. Bu soruyu cevaplamak için hangi aracı/araçları hangi sırayla kullanman gerektiğini adım adım düşün.
        Düşünce sürecini ve araçlardan gelen sonuçları gözlem olarak kaydet.
        Son olarak, tüm bu bilgilere dayanarak kullanıcıya nihai, anlaşılır bir cevap ver.

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
            handle_parsing_errors=True
        )
        print("StokGold Agent başarıyla yüklendi.")

    def run(self, user_query: str, chat_history: list = None) -> str:
        """
        Kullanıcıdan gelen bir sorguyu alır, agent'ı çalıştırır ve cevabı döndürür.
        """
        if chat_history is None:
            chat_history = []

        try:
            response = self.agent_executor.invoke({
                "input": user_query,
                "chat_history": chat_history
            })
            return response.get('output', "Bir hata oluştu, cevap alınamadı.")
        except Exception as e:
            print(f"Agent çalışırken bir hata oluştu: {e}")
            return "Üzgünüm, isteğinizi işlerken bir hata oluştu. Lütfen Ollama'nın çalıştığından emin olun."


def check_ollama_status():
    """
    Ollama servisinin çalışıp çalışmadığını ve Llama3 modelinin
    kurulu olup olmadığını kontrol eder.
    """
    try:
        models_data = ollama.list().get('models', [])

        # Artık 'llama3:' ile başlayan bir model arıyoruz.
        found_model = next(
            (model.get('model') for model in models_data if
             model.get('model') and model['model'].startswith('llama3:')),
            None
        )

        if found_model:
            return {'ok': True, 'message': f'Akıllı Asistan hazır (Model: {found_model})', 'model_name': found_model}
        else:
            return {
                'ok': False,
                'message': "Ollama çalışıyor ancak 'llama3' modeli kurulu değil.\n"
                           "Lütfen terminalde 'ollama run llama3' komutunu çalıştırın.",
                'model_name': None
            }
    except Exception as e:
        print(f"Ollama servis kontrol hatası: {e}")
        return {
            'ok': False,
            'message': "Akıllı Asistan kullanılamıyor.\nLütfen bilgisayarınızda Ollama'nın çalıştığından emin olun.",
            'model_name': None
        }