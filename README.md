# AI Resume Parser (Local & Private)

An interactive Python tool that extracts specific information from resume PDFs into structured JSON format using Local LLMs.

## 🌟 Features
- **Local AI Processing**: Uses Ollama (Llama 3) to process resumes locally—no API keys or internet required.
- **Smart Extraction**: Extracts Name, Email, Phone, Address, Education, and Skills even with complex multi-line layouts.
- **Interactive CLI**: Easy-to-use file selection dialog for a seamless user experience.

## 🛠️ Tech Stack
- **Language**: Python 3.10+
- **AI Engine**: [Ollama](https://ollama.com/) (Model: Llama 3)
- **Library**: `pypdf`, `re`, `json`, `tkinter`

## 🚀 Getting Started

### 1. Install Ollama
Download and install Ollama from [ollama.com](https://ollama.com). Once installed, open your terminal and pull the Llama 3 model:
```bash
ollama pull llama3
