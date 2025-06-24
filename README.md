# StokGold - AI-Powered Jewelry Inventory Management v3.1 (Alpha)

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Qt for Python](https://img.shields.io/badge/Qt_for_Python-PySide6-217346?style=for-the-badge&logo=qt)
![Status](https://img.shields.io/badge/Status-Unstable_Development-red?style=for-the-badge)

StokGold is a modern desktop inventory management application for jewelers. This version introduces an **experimental** AI-powered Smart Assistant using LangChain and the Groq API for natural language queries.

**Current Status:** The AI Assistant feature is a work-in-progress and currently has known stability issues. The agent can correctly select tools but may enter into loops or fail to return a final answer. This version is committed for backup and further debugging purposes.

---

## 🚀 Key Features

* **📦 Comprehensive Product Management:** Full CRUD, multi-select & bulk delete, Excel export.
* **📈 Advanced Reporting & Transactions:** Detailed sales statistics (Profit/Loss), daily transaction drill-down, and stock management.
* **🧠 AI-Powered Smart Assistant (Experimental - Unstable):**
    * Connects to the ultra-fast Groq cloud API.
    * Designed to understand natural language queries about inventory (e.g., "how many gold rings are in stock?").
    * Uses a tool-based architecture via LangChain to query the database.
    * **Known Issue:** The agent currently gets stuck in loops after successfully executing a tool, failing to produce a final answer.

---

## 🛠️ Technologies Used

* **Language:** Python 3.11
* **GUI Framework:** PySide6
* **AI Framework:** LangChain
* **LLM Service:** Groq API (using Llama 3 70B)
* **Database:** SQLite
* **Key Libraries:** `python-dotenv`, `langchain-groq`, `openpyxl`, `python-barcode`

---

## 🚀 Installation & Setup

### For End-Users (Note: AI feature is unstable)

1.  **Get a Groq API Key:** To use the Smart Assistant, you must first get a free API key from [groq.com](https://groq.com).
2.  **Create `.env` file:** Create a file named `.env` in the installation directory and add your key like this: `GROQ_API_KEY="gsk_YourActualKey"`
3.  **Install:** Run the `StokGold-Kurulum.exe` from the "Releases" section.

### For Developers

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/kayipbaliknepo/StokGold.git](https://github.com/kayipbaliknepo/StokGold.git)
    cd StokGold
    ```
2.  **Create `.env` file:** Create a `.env` file in the root directory and add your Groq API key: `GROQ_API_KEY="gsk_YourActualKey"`.
3.  **Create and activate the virtual environment:**
    ```bash
    py -3.11 -m venv venv
    .\venv\Scripts\activate
    ```
4.  **Install dependencies:**
    ```bash
    python -m pip install -r requirements.txt
    ```
5.  **Run the application:**
    ```bash
    python main.py
    ```