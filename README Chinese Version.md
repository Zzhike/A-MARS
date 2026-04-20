# 🧪 吸附材料智能分析系统 (A-MARS)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-API-purple.svg)](https://deepseek.com/)

A-MARS 是一个基于 MOF（金属有机框架）材料数据库和 DeepSeek 大语言模型的智能吸附材料分析系统。支持气体吸附性能查询、MOF 材料筛选、专家知识问答等功能，并提供**命令行界面（CLI）**和**Web 界面（Gradio）**两种交互方式。

## 📋 目录
- [主要功能](#-主要功能)
- [项目结构](#-项目结构)
- [安装与配置](#-安装与配置)
- [使用方法](#-使用方法)
- [示例查询](#-示例查询)
- [支持的气体](#-支持的气体)
- [扩展与定制](#-扩展与定制)
- [常见问题](#-常见问题)
- [许可证](#-许可证)

---

## ✨ 主要功能

### 🔍 查询模式
- **气体查询**：按气体名称查询（如 HCHO、C7H16FO2P）
- **条件查询**：按结构/性能字段筛选（如 LCD > 30、VSA < 1000）
- **复合查询**：支持多条件 AND 逻辑组合
- **统计分析**：自动计算平均 lgN、最大扩散系数等
- **智能推荐**：基于吸附容量推荐前 3-10 个 MOF 材料

### 🧠 专家模式
- **AI 智能问答**：基于 DeepSeek API 的智能响应
- **内置 FAQ**：预设常见问题知识库
- **双语支持**：支持中英文混合提问
- **相似度匹配**：对 FAQ 问题进行模糊匹配

### 🌐 Web 界面（Gradio）
- **可视化操作**：用户友好的面板，支持标签页和按钮
- **快速选择**：预设问题和气体选项
- **语言切换**：中英文界面实时切换
- **示例查询**：点击即可尝试的示例

### 📁 本地数据库支持
- **多气体支持**：不同气体使用独立的 Excel 文件
- **自动识别**：自动识别气体别名
- **灵活架构**：必需列（CSD、lgN）+ 可选列（LCD、PLD、VSA、Density、φ、Diffusivity）

---

## 🗂️ 项目结构

```
A-MARS/
├── MARS.py               # MOF专家系统核心逻辑
├── llms.py               # Gradio Web界面启动文件
├── faq_config.py         # 预设FAQ知识库（可选）
├── database/             # 气体数据文件夹（用户提供）
│   ├── HCHO.xlsx
│   ├── C2H5OH.xlsx
│   ├── C3H8.xlsx
│   ├── C7H16FO2P.xlsx
│   ├── n-C4H10.xlsx
│   ├── n-C5H12.xlsx
│   ├── n-C6H14.xlsx
│   └── ...
└── README.md             # 项目说明文档
```

---

## ⚙️ 安装与配置

### 1. 系统要求
- **Python**：3.8 或更高版本
- **操作系统**：Windows / Linux / macOS
- **内存**：最低 4GB（推荐 8GB）
- **存储**：依赖包 500MB + 数据库大小

### 2. 安装依赖包

```bash
pip install pandas openai requests gradio openpyxl
```

或创建 `requirements.txt`：

```txt
pandas>=2.0.0
openai>=1.0.0
requests>=2.31.0
gradio>=4.0.0
openpyxl>=3.1.0
```

然后安装：
```bash
pip install -r requirements.txt
```

### 3. 配置 DeepSeek API Key

**方式 A**：在 `MARS.py` 中硬编码
```python
CONFIG = {
    "deepseek_api_key": "your-api-key-here"
}
```

**方式 B**：环境变量
```bash
export DEEPSEEK_API_KEY="your-api-key-here"  # Linux/Mac
set DEEPSEEK_API_KEY="your-api-key-here"     # Windows
```

**方式 C**：在 Web 界面中动态输入

> **获取 API Key**：[DeepSeek 平台](https://platform.deepseek.com/)

### 4. 准备数据库文件夹

1. 创建文件夹 `D:/all/database`（或在代码中修改路径）
2. 放置 Excel 文件，命名格式：`GASNAME.xlsx`（如 `HCHO.xlsx`）
3. 确保包含必需列：

| 列名 | 必需 | 说明 |
|------|------|------|
| CSD | ✅ 是 | 晶体结构标识符 |
| lgN | ✅ 是 | 吸附容量的对数 (mol/kg) |
| LCD | ✅ 是 | 最大空腔直径 (Å) |
| PLD | ✅ 是 | 孔道极限直径 (Å) |
| VSA | ✅ 是 | 孔隙表面积 (m²/g) |
| Density | ✅ 是 | 材料密度 (g/cm³) |
| φ | ✅ 是 | 孔隙率 |
| Diffusivity | ✅ 是 | 扩散系数 (cm²/s) |
| No. | ✅ 是 | 材料序号 |

---

## 🚀 使用方法

### Web 界面（Gradio）

```bash
python llms.py
```

**访问地址：**
- 本地访问：`http://127.0.0.1:7860`
- 网络访问：`http://你的IP:7860`

**Web 界面功能：**
- **语言切换**：中英文实时切换
- **模式选择**：查询模式 / 专家模式
- **气体数据库**：下拉选择可用气体
- **API Key 输入**：可选的 DeepSeek API 密钥字段
- **预设问题**：FAQ 下拉快速访问
- **示例查询**：点击即试的示例

---

## 📖 示例查询

### 查询模式示例

| 输入 | 说明 | 预期输出 |
|------|------|----------|
| `HCHO` | 查询甲醛吸附数据 | 前3个MOF及其lgN值 |
| `LCD > 30` | 孔径大于30Å | 大孔MOF材料 |
| `VSA < 1000` | 比表面积小于1000 m²/g | 低表面积MOF |
| `lgN 最大` | 最高吸附容量 | 最大lgN的MOF |
| `Density 最小` | 最低密度 | 最轻的MOF材料 |
| `LCD > 20 且 VSA > 500` | 复合条件 | 同时满足两个条件的MOF |
| `筛选 VSA > 800` | 筛选先前结果 | 精炼的结果集 |

### 专家模式示例

| 输入 | 类型 | 说明 |
|------|------|------|
| `什么是MOF？` | 中文 | 基本概念解释 |
| `如何选择用于气体吸附的MOF？` | 中文 | 选择标准和策略 |
| `What is breakthrough curve?` | 英文 | 突破曲线解释 |
| `MOF相比传统吸附剂的优势` | 中文 | 对比分析 |
| `如何提高MOF的稳定性？` | 中文 | 设计策略 |

### 高级查询示例

```python
# 气体别名查询
"HCHO"           # 标准名称
"甲醛"           # 中文名称
"ETHANOL"        # 英文别名
"酒精"           # 常用名称

# 数值查询
"φ > 0.5"        # 孔隙率大于0.5
"PLD 在5到10之间"  # 范围查询

# 极值查询
"最大lgN"        # 最大吸附容量
"最小Density"    # 最小密度
```

---

## 🧪 支持的气体

系统目前支持以下气体及其别名：

| 气体代码 | 别名 |
|----------|------|
| **HCHO** | 甲醛、Formaldehyde |
| **C2H5OH** | 乙醇、Ethanol、C2H6O、酒精 |
| **C3H8** | 丙烷、Propane |
| **C3H9O3P** | 磷酸三甲酯、Trimethyl phosphate |
| **C4H8Cl2S** | 二氯乙硫醚、芥子气、Mustard Gas |
| **C4H9ClS** | 氯乙硫醚、Chloroethyl sulfide |
| **C7H16FO2P** | 沙林、Sarin、GB、甲基氟膦酸异丙酯 |
| **C8H10** | 二甲苯、Xylene |
| **n-C4H10** | 正丁烷、n-Butane |
| **n-C5H12** | 正戊烷、n-Pentane |
| **n-C6H14** | 正己烷、n-Hexane |
| **NH3** | 氨气、Ammonia |
| **CO2** | 二氧化碳、Carbon dioxide |
| **CH4** | 甲烷、Methane |
| **H2** | 氢气、Hydrogen |
| **N2** | 氮气、Nitrogen |
| **O2** | 氧气、Oxygen |

> **注意**：要添加新气体，只需将 Excel 文件放入 `database/` 文件夹，并在 `MARS.py` 的 `GAS_NAME_MAPPING` 字典中添加别名即可。

---

## 🛠️ 扩展与定制

### 添加新气体

1. **准备 Excel 文件**，包含必需列（CSD、lgN）
2. **保存到数据库文件夹**：`database/NEWGAS.xlsx`
3. **更新 GAS_NAME_MAPPING**（在 `MARS.py` 中）：

```python
GAS_NAME_MAPPING = {
    # ... 现有气体 ...
    'NEWGAS': ['NEWGAS', '别名1', '别名2', '中文名'],
}
```

### 修改 FAQ

**方式一**：编辑 `faq_config.py`

```python
FAQ_DICT = {
    "什么是MOF？": "MOF是金属有机框架材料...",
    "你的新问题": "你的答案..."
}
```

**方式二**：在代码中动态添加

```python
expert = MOFExpertSystem(database_path, api_key)
expert.add_faq("问题文本", "答案文本")
expert.save_faq("faq_config.py")
```

### 更改 API 端点

```python
expert = MOFExpertSystem(
    database_path=path,
    deepseek_api_key=key,
    base_url="https://你的自定义端点.com"
)
```

### 自定义数据库路径

```python
# 在 MARS.py 或 llms.py 中
database_path = "你的/自定义/路径/database"
```

---

## ❓ 常见问题

### 1. 错误："数据库路径不存在"

**解决方法**：
- 确认数据库文件夹存在于 `D:/all/database`
- 在 `MARS.py` 或 `llms.py` 中修改路径以匹配你的系统
- 确保文件夹中至少有一个 `.xlsx` 文件

### 2. 错误："找不到气体数据文件"

**解决方法**：
- 检查文件命名：必须为 `GASNAME.xlsx`（大写）
- 确认文件在正确的数据库文件夹中
- 确保气体名称与 `GAS_NAME_MAPPING` 中的条目匹配

### 3. DeepSeek API 调用失败

**解决方法**：
- 验证 API Key 是否有效且有足够额度
- 检查网络是否能访问 `api.deepseek.com`
- 在 Web 界面中尝试手动输入 API Key
- API 失败时系统会自动降级到 FAQ

### 4. Excel 文件读取错误

**解决方法**：
- 确保文件未被其他程序打开
- 检查文件是否损坏（尝试重新保存）
- 确认列名与要求的格式完全匹配
- 运行 `pip install openpyxl --upgrade`

### 5. 查询返回空结果

**解决方法**：
- 检查字段名是否与 Excel 列名匹配（区分大小写）
- 确认筛选值在数据范围内
- 先尝试宽松条件，再逐步缩小范围
- 使用 `筛选` 命令对先前结果进行筛选

### 6. Gradio 界面无法启动

**解决方法**：
- 检查端口 7860 是否被占用：`netstat -ano | findstr :7860`
- 尝试不同端口：`demo.launch(server_port=7861)`
- 使用共享模式运行：`demo.launch(share=True)`

### 7. 大数据库内存错误

**解决方法**：
- 增加 RAM 分配
- 将大的 Excel 文件拆分成多个小文件
- 使用筛选功能减少加载的数据量

---

## 📊 性能说明

- **数据库加载**：首次查询某气体会将其整个 Excel 文件加载到内存
- **查询速度**：大多数查询在 1 秒内完成（不含 API 调用）
- **API 响应**：DeepSeek API 通常在 2-5 秒内响应
- **并发用户**：Gradio 界面支持多用户但可能会排队请求

---

## 🔧 调试命令

```bash
# 检查 Python 版本
python --version

# 验证已安装的包
pip list | findstr "pandas openai gradio"


# 使用调试输出运行
python llms.py --debug
```

---

## 📄 许可证

本项目仅供**学习和研究使用**。  
DeepSeek API 的使用须遵守其[服务条款](https://deepseek.com/terms)。  

---

## 📧 联系与支持

- **问题反馈**：请在 GitHub 上提交 Issue
- **使用疑问**：参考 FAQ 或开启讨论
- **功能建议**：通过 Pull Request 或 Issue 提交

---

## 🙏 致谢

- **DeepSeek** 提供的大语言模型 API
- **Gradio** 提供的 Web 界面框架

---


## ⭐ 给我们点个星

如果您觉得这个项目有用，请在 GitHub 上给我们点个星！
