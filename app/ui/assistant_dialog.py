# app/ui/assistant_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QHBoxLayout, QApplication
)
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import QObject, QThread, Signal, Slot

# Agent çekirdeğimizi import ediyoruz
from app.agent.agent_core import StokGoldAgent


# --- Arka Planda Çalışacak Olan İşçi Sınıfı ---
class AgentWorker(QObject):
    """
    Zaman alan LLM sorgusunu arayüzü dondurmadan arka planda çalıştırır.
    """
    response_ready = Signal(str)
    error_occurred = Signal(str)
    finished = Signal()

    # --- DEĞİŞİKLİK 1: __init__ artık 'history' parametresini de kabul ediyor ---
    def __init__(self, agent: StokGoldAgent, query: str, history: list):
        super().__init__()
        self.agent = agent
        self.query = query
        self.history = history

    @Slot()
    def run(self):
        """Agent'ı çalıştırır ve sonucu sinyal olarak yayınlar."""
        try:
            print(f"Agent çalıştırılıyor... Sorgu: {self.query}")

            # --- DEĞİŞİKLİK 2: Agent'ı çalıştırırken sohbet geçmişini de iletiyor ---
            response = self.agent.run(self.query, self.history)

            self.response_ready.emit(response)
        except Exception as e:
            print(f"AgentWorker hatası: {e}")
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()

    @Slot()
    def run(self):
        """Agent'ı çalıştırır ve sonucu sinyal olarak yayınlar."""
        try:
            print(f"Agent çalıştırılıyor... Sorgu: {self.query}")
            response = self.agent.run(self.query, self.history)
            self.response_ready.emit(response)
        except Exception as e:
            print(f"AgentWorker hatası: {e}")
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()


# --- Kullanıcının Gördüğü Sohbet Penceresi ---
class AssistantDialog(QDialog):
    def __init__(self, model_name: str, parent=None):
        """
        Diyalogu başlatır ve kullanılacak spesifik model adını parametre olarak alır.
        """
        super().__init__(parent)
        self.setWindowTitle("StokGold Akıllı Asistan")
        self.resize(650, 700)
        self.setStyleSheet("background-color: #f5f5f5;")

        # --- DEĞİŞİKLİK BURADA ---
        # Agent, artık dışarıdan gelen bu spesifik model adıyla başlatılıyor.
        self.agent = StokGoldAgent(model_name=model_name)
        self.chat_history = []

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Sohbet geçmişinin gösterileceği alan
        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setFont(QFont("Arial", 12))
        self.history_display.setStyleSheet("background-color: white; border: 1px solid #ddd;")
        layout.addWidget(self.history_display)

        # Yazı giriş alanı ve gönder butonu
        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Sorunuzu buraya yazın...")
        self.input_line.setFont(QFont("Arial", 12))
        self.input_line.returnPressed.connect(self._send_message)  # Enter'a basınca gönder

        self.send_button = QPushButton("Gönder")
        self.send_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.send_button.clicked.connect(self._send_message)

        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        self.append_message("<b>Asistan:</b> Merhaba! StokGold envanterinizle ilgili size nasıl yardımcı olabilirim?",
                            "assistant")

    def append_message(self, message: str, role: str):
        """Sohbet ekranına yeni bir mesaj ekler."""
        if role == "user":
            formatted_message = f"<p style='margin: 5px; text-align: right; color: #0055A4;'>{message}</p>"
        else:  # assistant
            formatted_message = f"<p style='margin: 5px; color: #333;'>{message}</p>"

        self.history_display.insertHtml(formatted_message)
        self.history_display.moveCursor(QTextCursor.MoveOperation.End)  # Otomatik aşağı kaydır

    @Slot()
    def _send_message(self):
        """Kullanıcının yazdığı mesajı alır ve agent'ı arka planda çalıştırmak üzere tetikler."""
        user_text = self.input_line.text().strip()
        if not user_text:
            return

        self.append_message(f"<b>Siz:</b> {user_text}", "user")
        self.input_line.clear()

        # Kullanıcı yeni bir soru sorarken tekrar soru sormasını engelle
        self.input_line.setEnabled(False)
        self.send_button.setEnabled(False)
        self.append_message("<b>Asistan:</b> Düşünüyorum...", "assistant")
        QApplication.processEvents()  # "Düşünüyorum..." mesajının hemen görünmesini sağla

        # Arka plan iş parçacığını oluştur ve çalıştır
        self.thread = QThread()
        self.worker = AgentWorker(self.agent, user_text, self.chat_history)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.response_ready.connect(self._handle_agent_response)
        self.worker.error_occurred.connect(self._handle_agent_error)

        self.thread.start()

    def _handle_agent_response(self, response: str):
        """Agent'tan cevap geldiğinde çağrılır."""
        # "Düşünüyorum..." mesajını sil
        cursor = self.history_display.textCursor()
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()

        # Gerçek cevabı ekle
        self.append_message(f"<b>Asistan:</b> {response}", "assistant")

        # Sohbet geçmişini güncelle
        self.chat_history.append((self.worker.query, response))

        # Giriş alanlarını tekrar aktif et
        self.input_line.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_line.setFocus()

    def _handle_agent_error(self, error_message: str):
        """Agent'ta bir hata oluştuğunda çağrılır."""
        self.append_message(f"<b>Hata:</b> {error_message}", "assistant")
        self.input_line.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_line.setFocus()