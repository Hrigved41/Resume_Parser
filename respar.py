import ollama
import pdfplumber
import json
import tkinter as tk
from tkinter import filedialog
import os
import mysql.connector
from datetime import datetime
import getpass  


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  
    'database': 'empl_database'
}

def select_file():
    root = tk.Tk()
    root.withdraw() 
    file_path = filedialog.askopenfilename(
        title="Select a Resume PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    root.destroy()
    return file_path

def extract_text_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                extracted = page.extract_text(layout=True)
                if extracted:
                    text += extracted + "\n"
            return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def parse(resume_text):
    system_prompt = """
    You are an expert Resume Parser. 
    Extract the following information and return it ONLY as a valid JSON object.
    
    Schema:
    {
        "full_name": "String",
        "email": "String",
        "phone": "String",
        "date_of_birth": "String (Extract exactly as written in resume)",
        "address": "String",
        "pincode": "String",
        "education": [{"degree": "String", "institution": "String", "year": "String"}],
        "skills": ["Array of Strings"],
        "experience": [
            {
                "job_title": "String",
                "company": "String",
                "duration": "String",
                "description": "String"
            }
        ]
    }
    """
    try:
        response = ollama.chat(
            model='llama3', 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": resume_text}
            ],
            format='json', 
        )
        return json.loads(response['message']['content'])
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def convert_to_mysql_date(date_str):
    
    if not date_str: return None
    formats_to_try = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y", "%B %d, %Y", "%d %B %Y"]
    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    print(f"Warning: Could not parse date '{date_str}'. Saving as NULL.")
    return None

def get_next_employee_id(cursor):
    
    try:
        cursor.execute("SELECT MAX(CAST(empl_cd AS UNSIGNED)) FROM employee")
        result = cursor.fetchone()
        if result and result[0] is not None:
            return str(result[0] + 1)
        else:
            return "1"
    except Exception as e:
        print(f"Error generating ID: {e}")
        return "1"

def insert_resume_to_db(json_data):
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        empl_cd = get_next_employee_id(cursor)
        formatted_dob = convert_to_mysql_date(json_data.get("date_of_birth"))
        
        
        emp_values = (
            empl_cd,
            json_data.get("full_name", ""),
            formatted_dob,
            json_data.get("email", ""),
            json_data.get("phone", ""),
            json_data.get("address", ""),
            json_data.get("pincode", "")
        )
        sql_employee = "INSERT INTO employee (empl_cd, name, b_date, email, mobile, res_addr1, res_pin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql_employee, emp_values)
        print(f"Inserted Employee: {json_data.get('full_name')} (ID: {empl_cd})")

        
        education_list = json_data.get("education", [])
        if education_list:
            sql_edu = "INSERT INTO edu_dtl (empl_cd, degree, university, pass_yr) VALUES (%s, %s, %s, %s)"
            edu_values = [(empl_cd, e.get("degree", ""), e.get("institution", ""), e.get("year", "")) for e in education_list]
            cursor.executemany(sql_edu, edu_values)

        
        experience_list = json_data.get("experience", [])
        if experience_list:
            sql_exp = "INSERT INTO exp_dtl (empl_cd, company, experience, fr_dt, to_dt) VALUES (%s, %s, %s, %s, %s)"
            exp_values = [(empl_cd, x.get("company", ""), x.get("duration", ""), '0000-00-00', '0000-00-00') for x in experience_list]
            cursor.executemany(sql_exp, exp_values)

        conn.commit()
        print("--- Saved to Database Successfully ---")

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        if conn: conn.rollback()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def main():
    print("--- AI Resume Parser ---")
    
    
    try:
        user_password = getpass.getpass("Enter your MySQL Root Password: ")
        db_config['password'] = user_password
    except Exception as e:
        
        user_password = input("Enter your MySQL Root Password: ")
        db_config['password'] = user_password

    while True:
        print("\n--- Menu ---")
        print("1. Select a PDF to Parse")
        print("2. Exit")
        
        choice = input("Enter your choice (1/2): ")
        
        if choice == '1':
            path = select_file()
            if not path:
                print("No file selected.")
                continue
                
            print(f"\nProcessing: {os.path.basename(path)}...")
            text = extract_text_from_pdf(path)
            
            if text:
                print("Text extracted. Analyzing...")
                data = parse(text)
                if data:
                    print("\n--- Extraction Result ---")
                    print(json.dumps(data, indent=4))
                    
                    save_db = input("\nStore in Database? (y/n): ")
                    if save_db.lower() == 'y':
                        insert_resume_to_db(data)
            else:
                print("Could not extract text.")
                
        elif choice == '2':
            print("Exiting...")
            break

if __name__ == "__main__":
    main()
