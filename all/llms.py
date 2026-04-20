import gradio as gr
from MARS import MOFExpertSystem
import os
import math
from faq_config import FAQ_DICT

def init_system(api_key=None):
    database_path = os.path.join(os.path.dirname(__file__), "D:/all/database")
    deepseek_api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "DEFAULT_API_KEY")#Your API Key Here
    
    try:
        return MOFExpertSystem(
            database_path=database_path,
            deepseek_api_key=deepseek_api_key
        )
    except Exception as e:
        print(f"系统初始化失败: {str(e)}")
        raise

def process_query(query, mode, language, gas_type, api_key=None):
    print(f"[DEBUG] 处理查询 - 模式: {mode}, 语言: {language}, 气体: {gas_type}, 查询: {query[:50]}...")
    
    lang_map = {"Chinese": "zh", "English": "en"}
    try:
        system = init_system(api_key)
        system.language = lang_map.get(language, "zh")
        system._load_gas_data(gas_type)
        
        is_query_mode = mode.startswith("查询模式") or mode.startswith("Query Mode")
        
        if is_query_mode:
            print("[DEBUG] 进入查询模式处理流程")
            response = system.process_user_request(query)
            if isinstance(response, dict) and response.get('type') == 'numeric_query' and len(response.get('mofs', [])) > 10:
                response['mofs'] = sorted(response['mofs'], key=lambda x: x['lgN_value'], reverse=True)[:10]
                response['count'] = len(response['mofs'])
            return response
        else:
            print("[DEBUG] 进入专家模式处理流程")
            response = system.answer_question(query)
            
            if isinstance(response, dict) and 'answer' in response:
                answer = response['answer']
                if isinstance(answer, str):
                    answer = answer.replace('\\n', '\n').replace('\\n\\n', '\n\n')
                return answer
            else:
                    answer = str(response) if response else ""
                    answer = answer.replace('\\n', '\n').replace('\\n\\n', '\n\n')
                    return answer
            
    except Exception as e:
        error_msg = f"错误: {str(e)}" if language == "Chinese" else f"Error: {str(e)}"
        suggestion = "请重试或切换模式" if language == "Chinese" else "Please try again or switch mode"
        
        return f"❌ {error_msg}\n💡 {suggestion}"

def format_lgN(lgN_value):
    if math.isnan(lgN_value):
        return "NAN"
    N = pow(10, lgN_value)
    N1 = float(N)
    N2 = format(N1, '.2E')
    N3 = N2.split('E')
    if (N3[1])[0] == "-":
        return N3[0] + " x 10^" + N3[1].lstrip('0')
    else:
        return N3[0] + " x 10^" + (N3[1])[1:].lstrip('0')

def format_faq_structure(faq_data, language):
    try:
        title = faq_data.get('title', '')
        sections = faq_data.get('sections', [])
        
        result_lines = []
        
        if language == "Chinese":
            result_lines.append("✨" + "="*50 + "✨")
            result_lines.append(f"    📚 {title}")
            result_lines.append("✨" + "="*50 + "✨")
        else:
            result_lines.append("✨" + "="*50 + "✨")
            result_lines.append(f"    📚 {title}")
            result_lines.append("✨" + "="*50 + "✨")
        
        result_lines.append("")
        
        for i, section in enumerate(sections):
            section_title = section.get('title', f'第{i+1}部分' if language == "Chinese" else f'Part {i+1}')
            
            if language == "Chinese":
                result_lines.append(f"🔹 【{section_title}】")
            else:
                result_lines.append(f"🔹 【{section_title}】")
            
            result_lines.append("")  
            
            if 'content' in section:
                content = section['content']
                content = content.replace('\\n', '\n').replace('\\n\\n', '\n\n')
                content = content.replace('\n', '\n    ')
                result_lines.append(f"    {content}")
                result_lines.append("")  
            
            if 'items' in section:
                items = section['items']
                for j, item in enumerate(items):
                    item_text = str(item).replace('\\n', '\n').replace('\\n\\n', '\n\n')
                    if language == "Chinese":
                        result_lines.append(f"    📌 {j+1}. {item_text}")
                    else:
                        result_lines.append(f"    📌 {j+1}. {item_text}")
                result_lines.append("")  
        
        result_lines.append("✨" + "="*50 + "✨")
        
        result = "\n".join(result_lines)

        result = result.replace('\\n', '\n').replace('\\n\\n', '\n\n')
        
        return result
        
    except Exception as e:
        print(f"[ERROR] 格式化FAQ结构时出错: {str(e)}")
        return str(faq_data)

def format_response(response, language):

    if isinstance(response, dict) and 'title' in response and 'sections' in response:
            print(f"[DEBUG] 处理结构化FAQ数据")
            return format_faq_structure(response, language)
        
    if isinstance(response, dict) and response.get('type') == 'faq_answer':
        answer = response.get('answer', '')
        answer = answer.replace('\\n', '\n').replace('\\n\\n', '\n\n')
        return answer

    if not isinstance(response, dict):
        content = str(response)
        content = content.replace('\\n\\n', '\n\n')
        content = content.replace('\\n', '\n')
        content = content.replace('\\n1', '\n1')
        content = content.replace('- ', '  - ')
        content = content.replace('{', '').replace('}', '')
        return content.strip()
    
    message = response.get('message', '未知错误').replace('/n', '\n').replace('/n1', '\n1')
    suggestion = response.get('suggestion', '请重试或联系管理员').replace('/n', '\n').replace('/n1', '\n1')
    
    if response.get('type') == 'error':
        error_msg = f"❌ {message}\n💡 {suggestion}"
        return error_msg.replace('/n', '\n').replace('/n1', '\n1')
    elif response.get('type') == 'gas_not_found':
        if language == "Chinese":
            return (
                f"⚠️ 数据库中未找到 {response.get('gas', '该气体')} 的相关数据\n"
                f"💡 请尝试查询其他气体或访问: https://bohrium.dp.tech/apps/predict"
            )
        else:
            return (
                f"⚠️ No relevant data found for {response.get('gas', 'this gas')}\n"
                f"💡 Please try other gas queries or visit: https://bohrium.dp.tech/apps/predict"
            )
    
    if language == "Chinese":
        if response.get('type') == 'numeric_query':
            mofs_to_display = response.get('mof_recommendations', [])[:10]
            mofs = "\n\n".join(
                f"{i+1}. CSD: {mof.get('CSD', '未知')} (No. {mof.get('No.', '未知')})\n"
                f"   N: {format_lgN(mof.get('lgN', 0))} mol/kg\n"
                f"   φ: {round(mof.get('φ', 0), 3)}\n"
                f"   PLD: {round(mof.get('PLD', 0), 3)} Å\n"
                f"   LCD: {round(mof.get('LCD', 0), 3)} Å\n"
                f"   Density: {round(mof.get('Density', 0), 3)} g/cm³\n"
                f"   VSA: {round(mof.get('VSA', 0), 3)} m²/g"
                for i, mof in enumerate(mofs_to_display)
            )
            return f"找到 {len(mofs_to_display)} 条匹配记录(基于常温常压):\n\n{mofs}"
        elif response.get('type') == 'gas_query_summary':
            mofs = "\n\n".join(
                f"{i+1}. CSD: {mof.get('CSD', '未知')} (No. {mof.get('No.', '未知')})\n"
                f"   N: {format_lgN(mof.get('lgN', 0))} mol/kg\n"
                f"   φ: {round(mof.get('φ', 0), 3)}\n"
                f"   PLD: {round(mof.get('PLD', 0), 3)} Å\n"
                f"   LCD: {round(mof.get('LCD', 0), 3)} Å\n"
                f"   Density: {round(mof.get('Density', 0), 3)} g/cm³\n"
                f"   VSA: {round(mof.get('VSA', 0), 3)} m²/g"
                for i, mof in enumerate(response.get('top_mofs', []))
            )
            stats = response.get('statistical_summary', {})
            avg_lgN = stats.get('average_lgN', 0)
            max_lgN = stats.get('max_lgN', avg_lgN)
            return (
                f"气体: {response.get('gas', '未知')}\n"
                f"匹配数量: {response.get('match_count', 0)}\n"
                f"平均N: {format_lgN(avg_lgN)} mol/kg\n"
                f"（数据库实验数据基于常温常压）\n\n"
                f"推荐MOF材料:\n{mofs}"
            )
    else:
        if response.get('type') == 'numeric_query':
            mofs_to_display = response.get('mof_recommendations', [])[:10]
            mofs = "\n\n".join(
                f"{i+1}. CSD: {mof.get('CSD', 'Unknown')} (No. {mof.get('No.', 'Unknown')})\n"
                f"   N: {format_lgN(mof.get('lgN', 0))} mol/kg\n"
                f"   φ: {round(mof.get('φ', 0), 3)}\n"
                f"   PLD: {round(mof.get('PLD', 0), 3)} Å\n"
                f"   LCD: {round(mof.get('LCD', 0), 3)} Å\n"
                f"   Density: {round(mof.get('Density', 0), 3)} g/cm³\n"
                f"   VSA: {round(mof.get('VSA', 0), 3)} m²/g"
                for i, mof in enumerate(mofs_to_display)
            )
            return f"Found {len(mofs_to_display)} matching records（Based on standard temperature and pressure）:\n\n{mofs}"
        elif response.get('type') == 'gas_query_summary':
            mofs = "\n\n".join(
                f"{i+1}. CSD: {mof.get('CSD', 'Unknown')} (No. {mof.get('No.', 'Unknown')})\n"
                f"   N: {format_lgN(mof.get('lgN', 0))} mol/kg\n"
                f"   φ: {round(mof.get('φ', 0), 3)}\n"
                f"   PLD: {round(mof.get('PLD', 0), 3)} Å\n"
                f"   LCD: {round(mof.get('LCD', 0), 3)} Å\n"
                f"   Density: {round(mof.get('Density', 0), 3)} g/cm³\n"
                f"   VSA: {round(mof.get('VSA', 0), 3)} m²/g"
                for i, mof in enumerate(response.get('top_mofs', []))
            )
            return (
                f"Gas: {response.get('gas', 'Unknown')}\n"
                f"Match count: {response.get('match_count', 0)}\n"
                f"Average N: {format_lgN(response.get('statistical_summary', {}).get('average_lgN', 0))}mol/kg\n"
                f"(Database experimental data based on standard temperature and pressure)\n\n"
                f"Recommended MOFs:\n{mofs}"
            )
    
        elif response.get('type') == 'faq':
            answer = response.get('answer', '')
            if not answer:
                return "❌ 无回答内容" if language == "Chinese" else "❌ No answer content"
            return answer
            
        elif response.get('type') == 'expert_answer':
            answer = response.get('answer', '')
            if not answer:
                return "❌ 无回答内容" if language == "Chinese" else "❌ No answer content"
            return answer
    
    return str(response)

with gr.Blocks(
    title="吸附材料智能分析系统/Adsorption Material AI Resolution System",
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="teal",
        font=["Noto Sans SC", "sans-serif"]
    )
) as demo:
    with gr.Row():
        with gr.Column(scale=4):
            gr.Markdown("""
            # 🧪Adsorption Material AI Resolution System(A-MARS)
            """)
        with gr.Column(scale=1):
            gr.Image("D:/all/logo.jpg", height=70, interactive=False, show_label=False, show_download_button=False, show_share_button=False)
    
    with gr.Tab("Query System"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ 系统设置/System Settings")
                with gr.Group():
                    query_language = gr.Radio(
                    choices=[("Chinese"), ("English")],
                    label="🌐 语言/Language",
                    value="English"
                )
                
                mode = gr.Radio(
                    choices=["查询模式/Query Mode", "专家模式/Expert Mode"],
                    label="🔧 模式/Mode",
                    value="查询模式/Query Mode"
                )
                
                api_key = gr.Textbox(
                    label="🔑 DeepSeek API密钥 (可选)/DeepSeek API Key (optional)",
                    type="password",
                    placeholder="留空则使用默认密钥/Leave blank to use default key"
                )
                
                gas_options = {
                    "Chinese": [
                        ("HCHO - 甲醛", "HCHO"),
                        ("C2H5OH - 乙醇", "C2H5OH"), 
                        ("C3H8 - 丙烷", "C3H8"),
                        ("C3H9O3P - 磷酸三甲酯", "C3H9O3P"),
                        ("C4H8Cl2S - 二氯代噻吩", "C4H8Cl2S"),
                        ("C4H9ClS - 氯代噻吩", "C4H9ClS"),
                        ("C7H16FO2P - 氟代磷酸酯", "C7H16FO2P"),
                        ("C8H10 - 二甲苯", "C8H10"),
                        ("n-C4H10 - 正丁烷", "n-C4H10"),
                        ("n-C5H12 - 正戊烷", "n-C5H12"),
                        ("n-C6H14 - 正己烷", "n-C6H14")
                    ],
                    "English": [
                        ("HCHO - Formaldehyde", "HCHO"),
                        ("C2H5OH - Ethanol", "C2H5OH"),
                        ("C3H8 - Propane", "C3H8"),
                        ("C3H9O3P - Trimethyl phosphate", "C3H9O3P"),
                        ("C4H8Cl2S - Dichlorothiophene", "C4H8Cl2S"),
                        ("C4H9ClS - Chlorothiophene", "C4H9ClS"),
                        ("C7H16FO2P - Fluoro phosphate ester", "C7H16FO2P"),
                        ("C8H10 - Xylene", "C8H10"),
                        ("n-C4H10 - n-Butane", "n-C4H10"),
                        ("n-C5H12 - n-Pentane", "n-C5H12"),
                        ("n-C6H14 - n-Hexane", "n-C6H14")
                    ]
                }
                
                def update_gas_options(lang_choice):
                    print(f"[查询语言切换] 语言选择: {lang_choice}")
                    
                    if lang_choice not in ["Chinese", "English"]:
                        print(f"[警告] 无效的语言选择: {lang_choice}")
                        lang_choice = "English" 
                    
                    if lang_choice == "Chinese":
                        return gr.update(choices=gas_options["Chinese"], label="选择气体数据库")
                    else:
                        return gr.update(choices=gas_options["English"], label="Select Gas Database")
                
                gas_type = gr.Radio(
                    choices=gas_options["English"],
                    label="Select Gas Database",
                    value="HCHO"
                )
                
                query_language.change(
                    fn=update_gas_options,
                    inputs=[query_language],
                    outputs=[gas_type]
                )

                faq_questions = {
                    "Chinese": [
                        "什么是MOF?",
                        "如何选择MOF?",
                        "常见吸附气体有哪些?",
                        "MOF的吸附原理是什么?",
                        "如何提高MOF的吸附性能?",
                        "MOF材料如何再生?",
                        "MOF的稳定性如何?",
                        "什么是突破曲线？",
                        "什么是化工吸附材料?",
                        "MOF相比传统吸附剂的优势是什么?",
                        "哪些气体被定义为化学战剂（CWAs）和挥发性有机化合物（VOCs）？",
                        "什么是材料指纹（分子指纹）？在MOFs材料中如何表征和提取这些指纹信息？",
                        "MOFs材料在吸附微量有毒气体方面有哪些独特优势？",
                        "针对吸附不同沸点区的ppm级毒气要如何设计MOFs材料？"
                    ],
                    "English": [
                        "What is MOF?",
                        "How to select MOF?",
                        "Common adsorbed gases?",
                        "MOF adsorption mechanism?",
                        "How to improve MOF adsorption?",
                        "How to regenerate MOF?",
                        "MOF stability?",
                        "What is the breakthrough curve?",
                        "What is chemical adsorbent material? ",
                        "What are the advantages of MOF compared to traditional adsorbents?",
                        "Which gases are defined as Chemical Warfare Agents (CWAs) and Volatile Organic Compounds (VOCs)?",
                        "What is a material fingerprint (molecular fingerprint)? How to characterize and extract this fingerprint information in MOFs materials?",
                        "What are the unique advantages of MOFs materials in adsorbing trace toxic gases?",
                        "How to design MOF materials for adsorbing ppm-level toxic gases across different boiling point ranges?"
                    ]
                }
                faq_type = gr.Dropdown(
                    choices=faq_questions["English"],
                    label="📋 预设问题/FAQ Questions",
                    value="What is MOF?"
                )
                
                def update_faq_type(lang):
                    print(f"[FAQ语言切换] 语言: {lang}")
                    return gr.Dropdown(choices=faq_questions[lang])
                
                query_language.change(
                    fn=update_faq_type,
                    inputs=query_language,
                    outputs=faq_type
                )
                
                def select_gas(gas, language):
                    print(f"[DEBUG] 选择气体: {gas}, 当前语言: {language}")
                    return "查询模式/Query Mode"
                
                gas_type.change(
                    fn=select_gas,
                    inputs=[gas_type, query_language],
                    outputs=mode
                )
                
            with gr.Column(scale=2):
                query = gr.Textbox(
                    label="📝 输入查询条件/Enter Query",
                    placeholder="输入气体名称或查询条件.../Enter gas name or query conditions..."
                )
                
                gr.Markdown("### 💡 示例查询/Example Queries")
                with gr.Row():
                    gr.Examples(
                        examples=[
                            ["HCHO", "查询模式/Query Mode", "English"],
                            ["LCD > 30", "查询模式/Query Mode", "Chinese"],
                            ["什么是MOF?", "专家模式/Expert Mode", "Chinese"],
                            ["What is chemical adsorbent material?", "专家模式/Expert Mode", "English"]
                        ],
                        inputs=[query, mode, query_language],
                        label="点击尝试示例/Click to try examples"
                    )
                with gr.Row():
                    submit = gr.Button("🚀 提交查询/Submit Query", variant="primary")
                    clear = gr.Button("🧹 清空/Clear")
                
                output = gr.Textbox(
                    label="📊 查询结果/Query Results",
                    interactive=False,
                    lines=10,
                    max_lines=20
                )
                gr.Markdown("""
                **提示/Tips**:
                - 查询模式支持气体名称(如HCHO)或条件查询(如LCD>30)/Query mode supports gas names (e.g. HCHO) or conditional queries (e.g. LCD>30)
                - 专家模式可回答MOF相关问题/Expert mode can answer MOF-related questions
                """)
                
                def select_faq(question, language):
                    return question, "专家模式/Expert Mode"
                
                faq_type.change(
                    fn=select_faq,
                    inputs=[faq_type, query_language],
                    outputs=[query, mode]
                )
    with gr.Tab("Help Documentation"):
        gr.Markdown("""
        ## 📚 系统使用指南/User Guide
        
        ### 查询模式/Query Mode
        - **气体查询/Gas Query**: 输入气体名称如 `HCHO`, `C7H16FO2P`/Enter gas names like `HCHO`, `C7H16FO2P`
        - **条件查询/Conditional Query**: 
            - `LCD > 30` (孔径大于30Å/pore size greater than 30Å)
            - `VSA < 1000` (比表面积小于1000m²/g/surface area less than 1000m²/g)
        
        ### 专家模式/Expert Mode
        - 回答关于MOF材料的各种问题/Answer various questions about MOF materials
        - 支持中英文提问/Supports questions in Chinese and English
        
        ### 常见问题/FAQ
        - 数据库目前包含HCHO、C4H8Cl2S、C3H9O3P等数据，详细请参考使用手册/The database currently contains data such as HCHO, C4H8Cl2S, C3H9O3P, etc. Please refer to the user manual for details
        - 查询其他气体时会提示数据限制/Querying other gases will show data limitation notice
        """)

    def run_query(query, mode, language, gas_type, api_key=None):
        if api_key and len(api_key.strip()) < 10:
            return "❌ API密钥无效 (至少需要10个字符)"
        
        progress = gr.Progress()
        progress(0, desc="处理中.../Processing...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = process_query(query, mode, language, gas_type, api_key)
                progress(1.0, desc="完成/Completed")
                return format_response(response, language)
            except ConnectionResetError:
                if attempt < max_retries - 1:
                    progress(0.5, desc=f"连接中断，正在重试({attempt+1}/{max_retries})...")
                    continue
                return "❌ 网络连接中断，请稍后重试/Network connection lost, please try again later"
            except Exception as e:
                return f"❌ 系统错误/System Error: {str(e)}\n💡 请检查输入或联系管理员/Please check input or contact admin"
        
        return "❌ 请求失败，请稍后重试/Request failed, please try again later"

    submit.click(
        fn=run_query,
        inputs=[query, mode, query_language, gas_type, api_key],
        outputs=output
    )
    clear.click(lambda: ("", ""), outputs=[query, output])

if __name__ == "__main__":
    demo.launch(show_error=True)
