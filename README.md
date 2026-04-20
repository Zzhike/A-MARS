# 🧪 Adsorption Material AI Resolution System (A-MARS)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-API-purple.svg)](https://deepseek.com/)

A-MARS is an intelligent adsorption material analysis system based on MOF (Metal-Organic Framework) material databases and the DeepSeek large language model. It supports gas adsorption performance queries, MOF material screening, expert knowledge Q&A, and provides both **Command Line Interface (CLI)** and **Web Interface (Gradio)** interaction methods.

## 📋 Table of Contents
- [Key Features](#-key-features)
- [Project Structure](#-project-structure)
- [Installation & Configuration](#-installation--configuration)
- [Usage](#-usage)
- [Example Queries](#-example-queries)
- [Supported Gases](#-supported-gases)
- [Extension & Customization](#-extension--customization)
- [FAQ](#-frequently-asked-questions)
- [License](#-license)

---

## ✨ Key Features

### 🔍 Query Mode
- **Gas Query**: Query by gas name (e.g., HCHO, C7H16FO2P)
- **Conditional Query**: Filter by structural/performance fields (e.g., LCD > 30, VSA < 1000)
- **Compound Query**: Support for multiple conditions with AND logic
- **Statistical Analysis**: Automatic calculation of average lgN, max diffusivity, etc.
- **Top Recommendations**: Display top 3-10 MOF materials based on adsorption capacity

### 🧠 Expert Mode
- **AI-Powered Q&A**: Intelligent responses based on DeepSeek API
- **Built-in FAQ**: Preset knowledge base for common questions
- **Bilingual Support**: Both Chinese and English queries supported
- **Similarity Matching**: Fuzzy matching for FAQ questions

### 🌐 Web Interface (Gradio)
- **Visual Operation**: User-friendly panel with tabs and buttons
- **Quick Selection**: Preset questions and gas options
- **Language Toggle**: Switch between Chinese and English interfaces
- **Example Queries**: Click-to-try examples for new users

### 📁 Local Database Support
- **Multi-Gas Support**: Separate Excel files for different gases
- **Auto-Detection**: Automatic gas alias recognition
- **Flexible Schema**: Required columns (CSD, lgN, LCD, PLD, VSA, Density, φ, Diffusivity, No.)

---

## 🗂️ Project Structure

```
A-MARS/
├── MARS.py               # MOF Expert System core logic
├── llms.py               # Gradio Web interface launcher
├── faq_config.py         # Preset FAQ knowledge base (optional)
├── database/             # Gas data folder (user-provided)
│   ├── HCHO.xlsx
│   ├── C2H5OH.xlsx
│   ├── C3H8.xlsx
│   ├── C7H16FO2P.xlsx
│   ├── n-C4H10.xlsx
│   ├── n-C5H12.xlsx
│   ├── n-C6H14.xlsx
│   └── ...
└── README.md             # Project documentation
```

---

## ⚙️ Installation & Configuration

### 1. System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows / Linux / macOS
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 500MB for dependencies + database size

### 2. Install Dependencies

```bash
pip install pandas openai requests gradio openpyxl
```

Or create a `requirements.txt`:

```txt
pandas>=2.0.0
openai>=1.0.0
requests>=2.31.0
gradio>=4.0.0
openpyxl>=3.1.0
```

Then install with:
```bash
pip install -r requirements.txt
```

### 3. Configure DeepSeek API Key

**Option A**: Hardcode in `MARS.py`
```python
CONFIG = {
    "deepseek_api_key": "your-api-key-here"
}
```

**Option B**: Environment variable
```bash
export DEEPSEEK_API_KEY="your-api-key-here"  # Linux/Mac
set DEEPSEEK_API_KEY="your-api-key-here"     # Windows
```

**Option C**: Enter in Web interface (dynamic input field)

> **Get your API key**: [DeepSeek Platform](https://platform.deepseek.com/)

### 4. Prepare Database Folder

1. Create folder `D:/all/database` (or modify path in code)
2. Place Excel files with naming format: `GASNAME.xlsx` (e.g., `HCHO.xlsx`)
3. Ensure required columns exist:

| Column | Required | Description |
|--------|----------|-------------|
| CSD | ✅ Yes | Crystal structure identifier |
| lgN | ✅ Yes | Log of adsorption capacity (mol/kg) |
| LCD | ✅ Yes | Largest cavity diameter (Å) |
| PLD | ✅ Yes | Pore limiting diameter (Å) |
| VSA | ✅ Yes | Void surface area (m²/g) |
| Density | ✅ Yes | Material density (g/cm³) |
| φ | ✅ Yes | Porosity |
| Diffusivity | ✅ Yes | Diffusion coefficient (cm²/s) |
| No. | ✅ Yes | Material serial number |

---

## 🚀 Usage

### Web Interface (Gradio)

```bash
python llms.py
```

**Access:**
- Local access: `http://127.0.0.1:7860`
- Network access: `http://your-ip:7860`

**Web Interface Features:**
- **Language Toggle**: Switch between Chinese/English
- **Mode Selection**: Query Mode / Expert Mode
- **Gas Database**: Dropdown selection of available gases
- **API Key Input**: Optional DeepSeek API key field
- **Preset Questions**: FAQ dropdown for quick access
- **Example Queries**: Click-to-try examples

---

## 📖 Example Queries

### Query Mode Examples

| Input | Description | Expected Output |
|-------|-------------|-----------------|
| `HCHO` | Query formaldehyde adsorption | Top 3 MOFs with lgN values |
| `LCD > 30` | Pore size > 30Å | MOFs with large pores |
| `VSA < 1000` | Surface area < 1000 m²/g | Low surface area MOFs |
| `lgN max` | Highest adsorption capacity | MOF with maximum lgN |
| `Density min` | Lowest density | Lightest MOF materials |
| `LCD > 20 AND VSA > 500` | Compound condition | MOFs meeting both criteria |
| `Filter VSA > 800` | Filter previous results | Refined result set |

### Expert Mode Examples

| Input | Type | Description |
|-------|------|-------------|
| `What is MOF?` | English | Basic concept explanation |
| `How to select MOF for gas adsorption?` | English | Selection criteria and strategies |
| `什么是突破曲线？` | Chinese | Breakthrough curve explanation |
| `MOF vs Traditional adsorbents advantages` | Chinese | Comparative analysis |
| `How to improve MOF stability?` | English | Design strategies |

### Advanced Query Examples

```python
# Gas queries with aliases
"HCHO"           # Standard name
"Formaldehyde"   # English name
"甲醛"           # Chinese name
"ETHANOL"        # English alias

# Numerical queries
"φ > 0.5"        # Porosity greater than 0.5
"PLD between 5 and 10"  # Range query

# Extreme value queries
"max lgN"        # Maximum adsorption capacity
"min Density"    # Minimum density
```

---

## 🧪 Supported Gases

The system currently supports the following gases with their aliases:

| Gas Code | Aliases |
|----------|---------|
| **HCHO** | Formaldehyde, 甲醛 |
| **C2H5OH** | Ethanol, C2H6O, 乙醇, 酒精 |
| **C3H8** | Propane, 丙烷 |
| **C3H9O3P** | Trimethyl phosphate, 磷酸三甲酯 |
| **C4H8Cl2S** | Dichlorothiophene, Mustard Gas, 二氯乙硫醚 |
| **C4H9ClS** | Chlorothiophene, Chloroethyl sulfide, 氯乙硫醚 |
| **C7H16FO2P** | Sarin, GB, 沙林, Methylphosphonofluoridic acid |
| **C8H10** | Xylene, 二甲苯 |
| **n-C4H10** | n-Butane, 正丁烷 |
| **n-C5H12** | n-Pentane, 正戊烷 |
| **n-C6H14** | n-Hexane, 正己烷 |
| **NH3** | Ammonia, 氨气 |
| **CO2** | Carbon dioxide, 二氧化碳 |
| **CH4** | Methane, 甲烷 |
| **H2** | Hydrogen, 氢气 |
| **N2** | Nitrogen, 氮气 |
| **O2** | Oxygen, 氧气 |

> **Note**: To add new gases, simply place an Excel file in the `database/` folder and add aliases to the `GAS_NAME_MAPPING` dictionary in `MARS.py`.

---

## 🛠️ Extension & Customization

### Adding a New Gas

1. **Prepare Excel file** with required columns (CSD, lgN, LCD, PLD, VSA, Density, φ, Diffusivity, No.)
2. **Save to database folder**: `database/NEWGAS.xlsx`
3. **Update GAS_NAME_MAPPING** in `MARS.py`:

```python
GAS_NAME_MAPPING = {
    # ... existing gases ...
    'NEWGAS': ['NEWGAS', 'Alias1', 'Alias2', '中文名'],
}
```

### Modifying FAQ

**Option 1**: Edit `faq_config.py`

```python
FAQ_DICT = {
    "What is MOF?": "MOF stands for Metal-Organic Framework...",
    "Your new question": "Your answer here..."
}
```

**Option 2**: Dynamic addition in code

```python
expert = MOFExpertSystem(database_path, api_key)
expert.add_faq("Question text", "Answer text")
expert.save_faq("faq_config.py")
```

### Changing API Endpoint

```python
expert = MOFExpertSystem(
    database_path=path,
    deepseek_api_key=key,
    base_url="https://your-custom-endpoint.com"
)
```

### Customizing Database Path

```python
# In MARS.py or llms.py
database_path = "your/custom/path/to/database"
```

---

## ❓ Frequently Asked Questions

### 1. Error: "Database path does not exist"

**Solution**: 
- Verify the database folder exists at `D:/all/database`
- Modify the path in `MARS.py` or `llms.py` to match your system
- Ensure the folder contains at least one `.xlsx` file

### 2. Error: "Gas data file not found"

**Solution**:
- Check file naming: must be `GASNAME.xlsx` (uppercase)
- Verify the file is in the correct database folder
- Ensure the gas name matches an entry in `GAS_NAME_MAPPING`

### 3. DeepSeek API call fails

**Solutions**:
- Verify API key is valid and has sufficient credits
- Check internet connection to `api.deepseek.com`
- Try the Web interface and enter API key manually
- The system will fall back to FAQ if API fails

### 4. Excel file reading errors

**Solutions**:
- Ensure the file is not open in another program
- Check for corrupted file (try re-saving)
- Verify column names exactly match required format
- Run `pip install openpyxl --upgrade`

### 5. Query returns empty results

**Solutions**:
- Check field names match Excel column names (case-sensitive)
- Verify filter values are within data range
- Try broader conditions first, then narrow down
- Use `Filter` command to filter previous results

### 6. Gradio interface doesn't launch

**Solutions**:
- Check port 7860 is not occupied: `netstat -ano | findstr :7860`
- Try different port: `demo.launch(server_port=7861)`
- Run with sharing enabled: `demo.launch(share=True)`

### 7. Memory errors with large databases

**Solutions**:
- Increase RAM allocation
- Split large Excel files into smaller ones
- Use filtering to reduce loaded data

---

## 📊 Performance Notes

- **Database Loading**: First query for a gas loads its entire Excel file into memory
- **Query Speed**: Most queries complete in <1 second (excluding API calls)
- **API Response**: DeepSeek API typically responds in 2-5 seconds
- **Concurrent Users**: Gradio interface supports multiple users but may queue requests

---

## 🔧 Debugging Commands

```bash
# Check Python version
python --version

# Verify installed packages
pip list | findstr "pandas openai gradio"

# Run with debug output
python llms.py --debug
```

---

## 📄 License

This project is for **learning and research purposes only**.  
Usage of the DeepSeek API is subject to its [Terms of Service](https://deepseek.com/terms).

---

## 📧 Contact & Support

- **Issues**: Please open an issue on GitHub
- **Questions**: Refer to FAQ or open a discussion
- **Feature Requests**: Submit via pull request or issue

---

## 🙏 Acknowledgments

- **DeepSeek** for providing the LLM API
- **Gradio** for the web interface framework

---

## ⭐ Star Us

If you find this project useful, please give it a star on GitHub!

```

This updated English README reflects all the changes you made to the Chinese version, including:
- Changed all columns to required (✅ Yes) in the database preparation table
- Removed the CLI usage section (keeping only Web Interface)
- Removed the test database folder command from debugging section
- Updated the acknowledgments section
- Maintained consistent formatting and structure throughout
