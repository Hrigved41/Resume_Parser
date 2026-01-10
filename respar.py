import ollama
from pypdf import PdfReader
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
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
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
        "skills": ["Array of Strings"]
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
                data = parse(text)
                if data:
                    print("\n--- Extraction Result ---")
                    print(json.dumps(data, indent=4))
                    
                    # Ask if user wants to save
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

