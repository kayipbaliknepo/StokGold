# StokGold - Jewelry Inventory Management System

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

StokGold is a modern and user-friendly desktop inventory management application developed for jewelers and jewelry retailers. With this application, you can easily manage your products, track stock movements, and generate important reports about your business.


---

## 🌟 Features

* **📦 Comprehensive Product Management:** Full CRUD (Create, Read, Update, Delete) functionality for products.
* **📷 Visual Inventory:** Attach an image to each product and view it in the main window's preview pane.
* **║█║ Automatic Barcode System:** Automatically generates a unique product code and a corresponding Code128 barcode image for each new item.
* **📈 Real-time Stock Transactions:** Easily increase or decrease stock quantities for purchases and sales through a visual interface, including insufficient stock checks for sales.
* **🔍 Live Search and Filtering:** Instantly filter the product list by product code or type as you type.
* **📊 Detailed Reporting:** A dedicated report window provides key business insights:
    * Total inventory value based on cost.
    * Total gram weight of all products.
    * Stock counts grouped by product type.
    * Daily transaction details and financial summaries (profit/loss) for selected date ranges.
* **⚙️ Professional Data Management:** Stores all user-generated data (database, images, barcodes) in the user's local `AppData` folder, adhering to modern Windows application standards.
* **📦 Professional Installer:** A user-friendly `setup.exe` created with Inno Setup allows for easy distribution and installation.

---

## 🛠️ Technologies Used

* **Language:** Python 3.11
* **GUI Framework:** PyQt6
* **Database:** SQLite
* **Barcode Generation:** `python-barcode` & `Pillow`
* **Packaging:** `PyInstaller`
* **Installer Creation:** `Inno Setup`

---

## 🚀 Installation

### For End-Users

1.  Navigate to the **"Releases"** section of this GitHub repository.
2.  Download the `StokGold-Kurulum.exe` file from the latest release.
3.  Run the downloaded executable and follow the steps in the installation wizard.

### For Developers

To run this project locally for development purposes, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/kayipbaliknepo/StokGold.git](https://github.com/kayipbaliknepo/StokGold.git)
    cd StokGold
    ```
    *(Replace `kayipbaliknepo` with your actual username if different.)*

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