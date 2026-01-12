import ollama
import pdfplumber  
import json
import tkinter as tk
from tkinter import filedialog
import os

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
        "address": "String",
        "education": [{"degree": "String", "institution": "String", "year": "String"}],
        "skills": ["Array of Strings"],
        "experience": [
            {
                "job_title": "String",
                "company": "String",
                "duration": "String",
                "description": "String (Short summary)"
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


def main():
    while True:
        print("\n--- AI Resume Parser ---")
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
                print("Text extracted successfully. Analyzing...")
                data = parse(text)
                if data:
                    print("\n--- Extraction Result ---")
                    print(json.dumps(data, indent=4))
                    
                    save = input("\nWould you like to save this to a JSON file? (y/n): ")
                    if save.lower() == 'y':
                        output_name = os.path.basename(path).replace(".pdf", ".json")
                        with open(output_name, "w") as f:
                            json.dump(data, f, indent=4)
                        print(f"Saved as {output_name}")
            else:
                print("Could not extract text from the selected file.")
                
        elif choice == '2':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()


