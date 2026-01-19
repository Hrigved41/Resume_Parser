import json
import mysql.connector
import os
import getpass
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'empl_database'
}


def select_json_file():
    """Opens a file dialog to let the user select a JSON file."""
    root = tk.Tk()
    root.withdraw() 
    file_path = filedialog.askopenfilename(
        title="Select Resume JSON Data",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    root.destroy()
    return file_path

def convert_to_mysql_date(date_str):
    if not date_str: return None
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y", "%B %d, %Y", "%d %B %Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
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

def insert_single_resume(cursor, json_data):
    try:
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
        print(f"   -> Inserted Employee: {json_data.get('full_name')} (ID: {empl_cd})")


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

        return True

    except mysql.connector.Error as err:
        print(f"   [!] Database Error for {json_data.get('full_name')}: {err}")
        return False

def main():
    print("--- Import JSON to Database ---")
    

    try:
        db_config['password'] = getpass.getpass("Enter MySQL Root Password: ")
    except:
        db_config['password'] = input("Enter MySQL Root Password: ")

    print("\nPlease select the JSON file from the pop-up window...")
    
    
    json_filename = select_json_file()
    
    if not json_filename:
        print("No file selected. Exiting.")
        return

    
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        with open(json_filename, 'r') as f:
            data = json.load(f)

        print(f"\nProcessing '{os.path.basename(json_filename)}'...")

        if isinstance(data, list):
            count = 0
            for resume in data:
                if insert_single_resume(cursor, resume):
                    count += 1
            print(f"\nSuccessfully imported {count} resumes.")
        
        elif isinstance(data, dict):
            if insert_single_resume(cursor, data):
                print("\nSuccessfully imported 1 resume.")
        
        else:
            print("Error: JSON format not recognized.")

        conn.commit()

    except mysql.connector.Error as err:
        print(f"Connection Error: {err}")
    except json.JSONDecodeError:
        print("Error: The file is not valid JSON.")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
