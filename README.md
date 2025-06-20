# StokGold - Modern Jewelry Inventory Management System v1.5

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Qt for Python](https://img.shields.io/badge/Qt_for_Python-PySide6-217346?style=for-the-badge&logo=qt)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

StokGold is a modern, user-friendly desktop inventory management application developed for jewelers and jewelry retailers. It offers a fluid user experience, simplifying data management through its single-window, page-based architecture with animated transitions and advanced reporting capabilities.

---

## 🚀 Key Features

### UI & User Experience
* **Central Dashboard:** The application launches into a modern dashboard, providing quick access to all major functions.
* **Single-Window Architecture:** All modules (Inventory, Reports, etc.) are presented as "pages" within a single main window, not separate windows.
* **Fluid Page Transitions:** Smooth "slide" animations between pages create a modern and seamless user experience.
* **Easy Navigation:** A "Back" button allows for intuitive navigation from sub-pages back to the main dashboard.
* **Dynamic Window Sizing:** The application automatically sizes itself based on the user's screen resolution and always starts centered.

### Inventory Management
* **Advanced Product Management:** Full CRUD (Create, Read, Update, Delete) functionality.
* **Multi-Select & Bulk Operations:** Users can select multiple products using `Ctrl` or `Shift` keys to perform bulk actions, such as deleting multiple items at once.
* **Export to Excel:** The entire current inventory list can be exported to a `.xlsx` Excel file with a single click.
* **Conditional Formatting:** The inventory table automatically highlights products with low stock (`<5`) in **orange** and out-of-stock (`0`) products in **red**, including a warning icon for at-a-glance status checks.
* **Advanced Sorting & Searching:** All numeric columns (Stock, Cost, Grams, etc.) sort correctly as numbers, not text. The live search functionality is case-insensitive and fully supports special characters (including Turkish).

### Stock Transactions & Reporting
* **Transactional Logging:** All stock movements—new product entries, purchases, and sales—are logged into a dedicated `transactions` table in the database.
* **Detailed Sales Statistics:** A dedicated report tab calculates and displays **Total Sales**, **Cost of Goods Sold**, and **Net Profit/Loss** for a user-selected date range.
* **Interactive Daily Reports:** The report features an interactive calendar. Clicking on any day opens a detailed drill-down dialog showing all individual purchase and sale transactions for that specific day, including time, product, quantity, and value.

### Automation & Data Management
* **Automated Product Code & Barcode:** New products are automatically assigned an editable, timestamp-based unique product code, and a corresponding Code128 barcode image is generated and saved.
* **Professional Data Storage:** All user-generated data (database, product images, barcodes) is stored securely in the user's local `AppData` folder, adhering to modern Windows application standards and preventing permissions issues.

---

## 🛠️ Technologies Used

* **Language:** Python 3.11
* **GUI Framework:** PySide6 (The official Qt for Python)
* **Database:** SQLite
* **Excel Operations:** `openpyxl`
* **Barcode Generation:** `python-barcode` & `Pillow`
* **Packaging:** `PyInstaller`
* **Installer Creation:** `Inno Setup`

---

## 🚀 Installation

### For End-Users

1.  Navigate to the **"Releases"** section of this GitHub repository.
2.  Download the `StokGold-Kurulum.exe` (or `StokGold-Installer.exe`) file from the latest release.
3.  Run the downloaded executable and follow the steps in the installation wizard.

### For Developers

To run this project locally for development, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/kayipbaliknepo/StokGold.git](https://github.com/kayipbaliknepo/StokGold.git)
    cd StokGold
    ```

2.  **Create and activate the virtual environment:**
    ```bash
    # Ensure you are using Python 3.11
    py -3.11 -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required libraries:**
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

---

## 📫 Contact

Aykut Yahya Ay – ayaykut3@gmail.com

Project Link: [https://github.com/kayipbaliknepo/StokGold](https://github.com/kayipbaliknepo/StokGold)