import traceback
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QHBoxLayout, QApplication, QLabel
)
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt

from app.agent.agent_core import StokGoldAgent


class AgentWorker(QObject):
    """Zaman alan LLM sorgusunu arayüzü dondurmadan arka planda çalıştırır."""
    response_ready = Signal(str)
    error_occurred = Signal(str)
    finished = Signal()

    def __init__(self, agent: StokGoldAgent, query: str, history: list):
        super().__init__()
        self.agent = agent
        self.query = query
        self.history = history

    @Slot()
    def run(self):
        """Agent'ı, sohbet geçmişiyle birlikte çalıştırır."""
        try:
            print(f"Agent çalıştırılıyor... Sorgu: {self.query}")
            response = self.agent.run(self.query, self.history)
            self.response_ready.emit(response)
        except Exception as e:
            # Hata mesajını string'e çevirerek gönder
            error_msg = f"Bir hata oluştu: {e}"
            print(f"AgentWorker hatası: {error_msg}")
            self.error_occurred.emit(error_msg)
        finally:
            self.finished.emit()


class AssistantDialog(QDialog):
    """Kullanıcının Akıllı Asistan ile konuştuğu sohbet penceresi."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("StokGold Akıllı Asistan")
        self.resize(600, 650)
        self.setStyleSheet("background-color: #f5f5f5;")

        # Agent, parametre almadan kendi içinde kuruluyor.
        self.agent = StokGoldAgent()
        self.chat_history = []

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setFont(QFont("Arial", 12))
        self.history_display.setStyleSheet("background-color: white; border: 1px solid #ddd;")
        layout.addWidget(self.history_display)

        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Sorunuzu buraya yazın...")
        self.input_line.setFont(QFont("Arial", 12))
        self.input_line.returnPressed.connect(self._send_message)

        self.send_button = QPushButton("Gönder")
        self.send_button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.send_button.clicked.connect(self._send_message)

        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        self.status_label = QLabel()
        self.status_label.setFont(QFont("Arial", 10, italic=True))
        self.status_label.setStyleSheet("color: #666;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.status_label)

        self.append_message("<b>Asistan:</b> Merhaba! StokGold envanterinizle ilgili size nasıl yardımcı olabilirim?",
                            "assistant")

    def append_message(self, message: str, role: str):
        """Sohbet ekranına yeni bir mesaj ekler."""
        if role == "user":
            # Kullanıcı mesajları için HTML formatı
            formatted_message = f"<p style='margin-bottom: 10px; text-align: right; color: #0055A4;'>{message}</p>"
        else:  # Asistan mesajları için
            formatted_message = f"<p style='margin-bottom: 10px; color: #333;'>{message}</p>"

        self.history_display.append(formatted_message)
        self.history_display.moveCursor(QTextCursor.MoveOperation.End)

    @Slot()
    def _send_message(self):
        """Kullanıcının yazdığı mesajı alır ve agent'ı arka planda çalıştırır."""
        user_text = self.input_line.text().strip()
        if not user_text or not self.send_button.isEnabled():
            return

        self.append_message(f"<b>Siz:</b> {user_text}", "user")
        self.input_line.clear()

        self.input_line.setEnabled(False)
        self.send_button.setEnabled(False)
        self.status_label.setText("Asistan düşünüyor...")
        QApplication.processEvents()

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
        self.status_label.clear()

        self.append_message(f"<b>Asistan:</b> {response}", "assistant")

        # Sohbet geçmişini (hem kullanıcının sorusu hem de agent'ın cevabı) güncelle
        last_query = self.worker.query
        self.chat_history.append((last_query, response))

        self.input_line.setEnabled(True);
        self.send_button.setEnabled(True);
        self.input_line.setFocus()

    def _handle_agent_error(self, error_message: str):
        """Agent'ta bir hata oluştuğunda çağrılır."""
        self.status_label.clear()
        self.append_message(f"<b>Hata:</b> {error_message}", "assistant")
        self.input_line.setEnabled(True);
        self.send_button.setEnabled(True);
        self.input_line.setFocus()