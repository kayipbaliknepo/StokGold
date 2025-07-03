# Security Policy

<<<<<<< HEAD
This document outlines the security policy for the StokGold application. We take the security of our users' data seriously and encourage responsible reporting of any potential vulnerabilities.

## Supported Versions

As the project is under active development, we provide security updates only for the latest version available in the `main` branch of our GitHub repository. We recommend always using the most up-to-date version of the application.

| Version | Supported          |
| ------- | ------------------ |
| Latest `main` | :white_check_mark: |
| Older Versions | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability, we would appreciate your help in disclosing it to us responsibly.

**How to Report:**

1.  **Preferred Method: GitHub Private Vulnerability Reporting**
    * Go to the "Security" tab of the repository.
    * Click on "Report a vulnerability" to open a private report. This is the most secure way to reach us.

2.  **Alternative Method: GitHub Issues**
    * If you are unable to use private reporting, you can create a new issue on our [GitHub Issues page](https://github.com/kayipbaliknepo/StokGold/issues).
    * Please provide a clear title and a detailed description of the vulnerability. **Do not include sensitive information** like API keys or personal data in the issue description.

We will do our best to acknowledge your report within 48-72 hours and will keep you updated on our progress.

## Key Security Practices

### **API Key Management**

* The **Google Gemini API Key** required for the Smart Assistant is managed entirely by the user.
* The application loads the key from a local `.env` file that you create in the application's directory.
* **Crucially, the `.env` file is explicitly ignored by our version control system (`.gitignore`) and should never be shared or committed to the repository.**

### **Data Storage**

* StokGold is a desktop application. All your data, including inventory, transactions, and repair logs, is stored locally on your computer in a SQLite database file (`stokgold.db`).
* This data is stored in your local application data folder (`%LOCALAPPDATA%/StokGold`) and is **not** transmitted to any external servers.

### **Dependencies**

* The application relies on third-party packages listed in the `requirements.txt` file.
* We strive to use reputable libraries, but we encourage developers to be aware of the security of these dependencies. Regularly updating packages and using tools like `pip-audit` is recommended for a secure development environment.

### **Database Interactions**

* We use parameterized queries for all database interactions to prevent SQL injection vulnerabilities.

Thank you for helping keep StokGold secure.
=======
## Supported Versions


| Version | Supported          |
| ------- | ------------------ |
| 3.2.x   | :white_check_mark: |
| 3.0.x   | :x:                |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

>>>>>>> 1102d10bba4a702eb08293c54b1771a537faacc0
