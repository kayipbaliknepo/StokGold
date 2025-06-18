# StokGold - Jewelry Inventory Management System

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

StokGold is a modern and user-friendly desktop inventory management application developed for jewelers and jewelry retailers. With this application, you can easily manage your products, track stock movements, and generate important reports about your business.

![Application Screenshot](https://i.imgur.com/your_screenshot_url.png)
*(Note: Replace this link with a URL from an image hosting service like [Imgur](https://imgur.com/) after uploading a screenshot of your application.)*

---

## 🌟 Features

* **📦 Comprehensive Product Management (CRUD):** Full functionality to Create, Read, Update, and Delete products.
* **📷 Visual Inventory:** Attach an image to each product and view it in the main window's preview pane.
* **║█║ Automatic Barcode System:** Automatically generates a unique product code and a corresponding Code128 barcode image for each new item.
* **📈 Real-time Stock Transactions:** Easily increase or decrease stock quantities for purchases and sales through a visual interface, including insufficient stock checks for sales.
* **🔍 Live Search and Filtering:** Instantly filter the product list by product code or type as you type in the search box.
* **📊 Detailed Reporting:** A dedicated report window provides key business insights:
    * Total inventory value based on cost.
    * Total gram weight of all products in stock.
    * Total stock counts grouped by product type.
* **⚙️ Professional Data Management:** Stores all user-generated data (database, images, barcodes) in the user's local `AppData` folder, adhering to modern Windows application standards for security and multi-user support.
* **📦 Professional Installer Package:** A user-friendly `setup.exe` created with Inno Setup allows for easy distribution and installation.

---

## 🛠️ Technologies Used

* **Programming Language:** Python 3.11
* **GUI Framework:** PyQt6
* **Database:** SQLite
* **Barcode Generation:** `python-barcode`
* **Image Processing:** `Pillow`
* **Packaging:** `PyInstaller`
* **Installer Creation:** `Inno Setup`

---

## 🚀 Installation

### For End-Users

1.  Navigate to the **"Releases"** section of this GitHub repository.
2.  Download the `StokGold-Kurulum.exe` (or `StokGold-Installer.exe`) file from the latest release.
3.  Run the downloaded executable and follow the steps in the installation wizard.

### For Developers

To run this project locally for development purposes, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR-USERNAME/StokGold.git](https://github.com/YOUR-USERNAME/StokGold.git)
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

## 📂 Project Structure

```
StokGold/
├── venv/
├── app/
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── add_product.py
│   │   └── ... (other UI files)
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   └── utils.py
├── assets/
│   └── icons/
│       └── app_icon.ico
├── .gitignore
├── config.ini
├── main.py
├── kurulum_scripti.iss
├── main.spec
└── README.md
```

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 📫 Contact

Aykut Yahya Ay – ayaykut3@gmail.com

Project Link: (https://github.com/kayipbaliknepo/StokGold)