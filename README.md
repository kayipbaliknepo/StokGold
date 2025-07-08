# StokGold - AI-Powered Jewelry Inventory Management

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python) ![Qt for Python](https://img.shields.io/badge/Qt_for_Python-PySide6-217346?style=for-the-badge&logo=qt) ![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge) ![Status](https://img.shields.io/badge/Status-Development-blue?style=for-the-badge)

StokGold is a modern, feature-rich desktop inventory management application designed specifically for jewelers. It provides a comprehensive suite of tools to manage products, track repairs, and gain financial insights. The application features an AI-powered Smart Assistant that allows users to query their inventory using natural language.

---

## 🚀 Key Features

* **Comprehensive Inventory Management**
    * Full CRUD (Create, Read, Update, Delete) functionality for products.
    * Image and barcode support for each product.
    * Advanced search and filtering capabilities.
    * Bulk deletion of multiple selected items.
    * Export inventory data to Excel files.

* **Repair Tracking Module**
    * Log and manage customer repair jobs.
    * Track repair status (Pending, In Progress, Completed, Delivered).
    * Store customer information, product descriptions, and repair details.

* **Insightful Reporting**
    * **Dashboard:** A central hub showing key metrics like daily sales, product variety, and low-stock alerts.
    * **Sales Statistics:** Calculate total sales, cost of goods sold, and net profit for any date range.
    * **Daily Transactions:** View a detailed log of all sales and purchases for any selected day.
    * **Inventory Summary:** Get reports on total inventory value, total weight (grams), and stock counts by product type.

* **AI-Powered Smart Assistant**
    * Powered by **Google's Gemini** model via LangChain for fast and intelligent responses.
    * Understand natural language queries (e.g., "How many gold rings are in stock?", "Show me the profit from last month").
    * Execute tasks like adding products, updating stock, and generating reports through conversation.

* **Backup Save & Load**
    * Backup Database.
    * Safe and easy to load old version databases.
    * Easy to share databases and tables.	

---

## 🛠️ Technologies Used

* **Language:** Python 3.11
* **GUI Framework:** PySide6
* **AI Framework:** LangChain
* **LLM Service:** Google Gemini (gemini-1.5-flash-latest)
* **Database:** SQLite
* **Key Libraries:** `python-dotenv`, `langchain-google-genai`, `openpyxl`, `python-barcode`

---

## 🚀 Installation & Setup

### For End-Users

1.  **Get a Google API Key:** To use the Smart Assistant, you must first get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  **Create `.env` file:** In the application's root directory, create a file named `.env` and add your API key to it like this:
    ```
    GOOGLE_API_KEY="YourActualApiKey"
    ```

### For Developers

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/kayipbaliknepo/StokGold.git](https://github.com/kayipbaliknepo/StokGold.git)
    cd StokGold
    ```
2.  **Create a `.env` file:** Create the `.env` file in the root directory as described above and add your `GOOGLE_API_KEY`.
3.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
4.  **Install dependencies from `requirements.txt`:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Run the application:**
    ```bash
    python main.py
    ```
---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE.txt](LICENSE.txt) file for full details.