# 🧪 Adsorption Material AI Resolution System (A-MARS)

A-MARS is an intelligent adsorption material analysis system based on MOF (Metal-Organic Framework) material databases and the DeepSeek large language model.  
It supports gas adsorption performance queries, MOF material screening, expert knowledge Q&A, and provides both **Command Line Interface (CLI)** and **Web Interface (Gradio)** interaction methods.

---

## ✨ Key Features

- 🔍 **Query Mode**  
  - Query by gas name (e.g., HCHO, C7H16FO2P)  
  - Filter by structural/performance fields (e.g., LCD > 30, VSA < 1000)  
  - Support for compound conditions (AND)  
  - Automatic statistical summaries (average lgN, max diffusivity, etc.)

- 🧠 **Expert Mode**  
  - Intelligent Q&A based on DeepSeek API  
  - Built-in FAQ knowledge base  
  - Bilingual support (Chinese/English)

- 🌐 **Web Interface (Gradio)**  
  - Visual operation panel  
  - Quick selection of preset questions  
  - Chinese/English interface switching

- 📁 **Local Database Support**  
  - Supports multiple gas Excel files  
  - Automatic gas alias recognition

---

## 🗂️ Project Structure
