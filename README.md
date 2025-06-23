# StokGold - AI-Powered Jewelry Inventory Management v2.0

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Qt for Python](https://img.shields.io/badge/Qt_for_Python-PySide6-217346?style=for-the-badge&logo=qt)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

StokGold is a modern desktop inventory management application developed for jewelers, now enhanced with an AI-powered Smart Assistant. It offers a fluid user experience, simplifying data management with its single-window, page-based architecture, animated transitions, and advanced, conversational reporting capabilities powered by local Large Language Models (LLMs).

---

## 🚀 Key Features

### AI-Powered Smart Assistant (New in v2.0)
* **🧠 Natural Language Queries:** Interact with your inventory using plain Turkish. Ask complex questions like *"Stoğu 5'ten az olan yüzükler hangileri?"* (Which rings have less than 5 in stock?) or *"Geçen ayki karım ne kadardı?"* (What was my profit last month?).
* **🤖 Local & Private:** Powered by Ollama, the assistant runs 100% locally on your machine. Your data never leaves your computer.
* **⚙️ Tool-Using Agent:** The LLM uses a set of defined "tools" to query the database, ensuring accurate and structured answers based on your real data.

### UI & User Experience
* **Central Dashboard:** A modern welcome screen provides quick access to all major functions.
* **Single-Window Architecture:** All modules are presented as "pages" with smooth, animated slide transitions inside a single main window.
* **Easy Navigation:** A "Back" button allows for intuitive navigation from sub-pages back to the dashboard.

### Inventory & Reporting
* **Advanced Product Management:** Full CRUD, multi-select for bulk delete, and "Export to Excel" functionality.
* **Conditional Formatting:** The inventory table automatically highlights low-stock items in orange and out-of-stock items in red.
* **Detailed Sales Statistics:** A dedicated report tab calculates and displays Total Sales, Cost of Goods Sold, and Net Profit/Loss for any selected date range.
* **Interactive Daily Drill-Down:** The calendar in the report section is interactive. Clicking a day opens a detailed list of all transactions for that specific day.

---

## 🛠️ Technologies Used

* **Language:** Python 3.11 (stable)
* **GUI Framework:** PySide6
* **AI Framework:** LangChain
* **Local LLM Runner:** Ollama
* **Database:** SQLite
* **Dependencies:** `python-barcode`, `Pillow`, `openpyxl`, `python-dateutil`, `numpy<2`

---

## 🚀 Installation

### For End-Users

1.  **Prerequisite: Install Ollama:** To use the Smart Assistant feature, you must first install Ollama from [ollama.com](https://ollama.com). After installing, run the following command in your terminal to download a compatible model:
    ```bash
    # Recommended for most systems
    ollama run llama3
    
    # For systems with low RAM
    ollama run phi3:mini
    ```
2.  **Install StokGold:** Navigate to the **"Releases"** section of this GitHub repository and download the `StokGold-Kurulum.exe` file from the latest release. Run the installer and follow the on-screen instructions.

### For Developers

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/kayipbaliknepo/StokGold.git](https://github.com/kayipbaliknepo/StokGold.git)
    cd StokGold
    ```

2.  **Create and activate the virtual environment using a stable Python version:**
    ```bash
    py -3.11 -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required libraries from `requirements.txt`:**
    ```bash
    python -m pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python main.py
    ```

---

## 📄 License

This project is licensed under the MIT License.