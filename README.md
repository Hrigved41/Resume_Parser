# AI Resume Parser & Database Archiver

A robust, privacy-focused Python application that extracts structured data from PDF resumes using Local AI (Llama 3) and archives it directly into a MySQL database.

## 🌟 Key Features
- **Local AI Processing**: Uses **Ollama** (Llama 3) to parse resumes entirely offline. No data leaves your machine.
- **Smart Text Extraction**: Utilizes `pdfplumber` with layout awareness to correctly read complex multi-column resumes.
- **Database Integration**: Automatically stores candidates in a **MySQL** database.
- **Interactive UI**: Native file selection dialog for easy PDF picking.

---

## 🛠️ Prerequisites

Before running the tool, ensure you have the following installed:

1.  **Python 3.10+**
2.  **MySQL Server** (8.0 or higher)
3.  **Ollama**: [Download here](https://ollama.com)
    * Pull the model: `ollama pull llama3`

---

## 📦 Installation

1.  **Clone the Repository** (or download the files)
    ```bash
    git clone [https://github.com/yourusername/resume-parser.git](https://github.com/yourusername/resume-parser.git)
    cd resume-parser
    ```

2.  **Install Python Libraries**
    ```bash
    pip install ollama pdfplumber mysql-connector-python tkinter
    ```

---

## 🗄️ Database Setup

You must create the database and tables before running the Python script.

1.  **Log in to MySQL** (via Command Prompt or Workbench).
2.  **Create the Database**:
    ```sql
    CREATE DATABASE empl_database;
    ```
3.  **Import the Schema**:
    Save the provided SQL code into a file named `tablestr.sql` and import it:
    ```bash
    mysql -u root -p empl_database < tablestr.sql
    ```

---

## 🚀 Usage

1.  **Run the Application**:
    ```bash
    python main.py
    ```

2.  **Enter Password**:
    The script will securely ask for your MySQL root password.
    ```text
    Enter your MySQL Root Password:  [Hidden Input]
    ```

3.  **Select a Resume**:
    A file window will pop up. Select any PDF resume.

4.  **Review & Save**:
    * The AI will print the extracted JSON data to the console.
    * You will be asked: `Store in Database? (y/n):`
    * Type `y` to save the candidate to MySQL.

---

## 📂 Project Structure

* `main.py`: The core application code.
* `tablestr.sql`: The SQL script to create the database tables.
* `README.md`: Project documentation.
* `requirements.txt`: List of dependencies.

## ⚠️ Troubleshooting

* **Error: `Access denied for user 'root'@'localhost'`**: You entered the wrong MySQL password at the start. Restart the script.
* **Error: `1045 (28000)`**: Same as above, invalid password.
* **Error reading PDF**: Ensure the file is a valid PDF and not an image-based scan (OCR is not currently supported).
* **Dates saving as NULL**: If the AI cannot find a date or the date format is extremely unusual, the script defaults to `NULL` to prevent database errors.

## 🛡️ Privacy Note
This tool uses **Local LLMs** via Ollama. No resume data is sent to OpenAI, Google, or any cloud API. Your data remains 100% private on your local machine.
