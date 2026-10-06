# 🍔 McDonald's India AI Nutrition Assistant

An AI chatbot built with Python, Gradio, and Ngrok. It helps users analyze the McDonald's India menu dataset using hybrid RAG (ChromaDB) and SQL query tools.

## ✨ Cool Features
* **Isolated Chat Sessions:** Separate user chat histories for multi-user connections.
* **Smart Hybrid Routing:** The AI decides whether to search via text vector (RAG) or query via SQL tables.
* **Local Scope Guardrails:** Blocks general questions (like asking for the CEO) using 0 API tokens.
* **Mobile Ready:** Accessible anywhere using a secure Ngrok HTTPS tunnel link.

## 🛠️ Project Setup

1. **Activate Virtual Environment:**
   ```powershell
   (Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
   & .\Nutri\Scripts\Activate.ps1
   ```

2. **Install Libraries:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Set Up Data & Databases:**
   ```powershell
   python data_pipeline/clean_dataset.py
   python data_pipeline/load_to_databases.py
   ```

4. **Launch Application:**
   ```powershell
   python main_UI.py
   ```

## 📄 License
This project is licensed under the MIT License.

# 🧠 AI Agent Core Architecture

This document explains the backend cognitive logic loops running inside the `core/` package folder.

## 🔄 Step-by-Step Execution Pipeline

1. **Input Sanitization (`main_UI.py`)**
   * Drops empty browser inputs.
   * Intercepts "bye/goodbye" keywords before hitting database queries.

2. **Intent Barrier Guardrail (`core/orchestrator.py`)**
   * Screens raw messages using dataset keyword strings.
   * Blocks out-of-scope prompts immediately to save Groq API tokens.

3. **Pronoun Memory Resolver (`core/memory.py`)**
   * Scans user text for pronouns (e.g., "it", "its").
   * Automatically references the last 2 isolated conversation history steps to rewrite the prompt.

4. **Keyword Classification Router (`core/router.py`)**
   * Checks query against specialized text matching keywords.
   * Decides to route execution to **SQL**, **RAG**, or **BOTH**.

5. **Tool Orchestration Execution**
   * **SQL Tool:** Generates and executes database queries via a self-healing 3-attempt retry loop.
   * **RAG Tool:** Queries ChromaDB embedding vectors for 2 top-context narrative blocks.

6. **Isolated Logger Engine**
   * Generates a completely unique session hash ID string per device stream (`gr.State`).
   * Saves metrics and conversation turns to unique individual JSON logs.

