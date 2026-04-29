import os
import re
import pandas as pd
import requests
import json
from typing import Optional, Dict, List

class MOFExpertSystem:
    from faq_config import FAQ_DICT as DEFAULT_FAQ  
    TRANSLATIONS = {
        'zh': {
            'welcome': "MOF专家系统已启动",
            'mode_select': "请选择模式：",
            'mode_selection_prompt': "请选择模式(1/2):",
            'query_mode': "查询模式",
            'expert_mode': "专家解答模式",
            'exit_prompt': "输入'退出'结束程序",
            'back_prompt': "输入'返回'切换模式",
            'invalid_mode': "无效的模式选择,请输入1或2",
            'query_prompt': "请输入查询条件",
            'expert_prompt': "请输入您的问题",
            'invalid_input': "请输入有效的输入",
            'entering_query_mode': "已进入查询模式",
            'entering_expert_mode': "已进入专家解答模式",
            'query_mode_selected_prompt': "已选择查询模式",
            'expert_mode_selected_prompt': "已选择专家解答模式",
            'gas_query_result_title': "气体查询结果",
            'unknown_gas': "未知气体",
            'found_records': "找到",
            'matching_records': "条匹配记录",
            'statistical_summary': "统计摘要",
            'average_lgN': "平均lgN值",
            'unknown': "未知",
            'max_diffusivity': "最大扩散系数",
            'top_recommendations': "推荐的前3条记录",
            'input_detail_prompt': "输入'详细",
            'to_view_all_matches': "查看全部匹配记录",
            'numeric_query_result_title': "数值查询结果",
            'unknown_field': "未知字段",
            'knowledge_qa': "知识问答",
            'debug_response_type': "[DEBUG] 响应类型",
            'debug_response_status': "[DEBUG] 响应状态",
            'section_divider': "分隔线",
            'section_end': "="*20 + " 结束 " + "="*20,
            'api_prepare_call': "准备调用DeepSeek API，prompt长度",
            'api_key_invalid': "API密钥无效或太短",
            'api_try_endpoint': "尝试调用API端点",
            'api_received_response': "收到响应，状态码",
            'api_html_response': "服务暂时不可用,请稍后再试或检查API状态",
            'api_success_response': "成功获取API响应",
            'api_empty_response': "API返回空响应",
            'api_exception': "API调用异常",
            'api_fallback': "无法连接到AI服务",
            'api_source': "DeepSeek API",
            'preset_knowledge_source': "预设知识库",
            'system_source': "系统"
        },
        'en': {
            'welcome': "MOF Expert System Started",
            'mode_select': "Please select mode:",
            'mode_selection_prompt': "Please select mode (1/2):",
            'query_mode': "Query Mode",
            'expert_mode': "Expert Answer Mode", 
            'exit_prompt': "Enter 'exit' to quit",
            'back_prompt': "Enter 'back' to switch mode",
            'invalid_mode': "Invalid mode selection, please enter 1 or 2",
            'query_prompt': "Please enter query condition",
            'expert_prompt': "Please enter your question",
            'invalid_input': "Please enter valid input",
            'entering_query_mode': "Entered query mode",
            'entering_expert_mode': "Entered expert answer mode",
            'query_mode_selected_prompt': "Query mode selected",
            'expert_mode_selected_prompt': "Expert answer mode selected",
            'gas_query_result_title': "Gas query results",
            'unknown_gas': "Unknown gas",
            'found_records': "Found",
            'matching_records': "matching records",
            'statistical_summary': "Statistical summary",
            'average_lgN': "Average lgN value",
            'unknown': "Unknown",
            'max_diffusivity': "Maximum diffusivity",
            'top_recommendations': "Top 3 recommendations",
            'input_detail_prompt': "Enter 'detail",
            'to_view_all_matches': "to view all matching records",
            'numeric_query_result_title': "Numeric query results",
            'unknown_field': "Unknown field",
            'knowledge_qa': "Knowledge Q&A",
            'debug_response_type': "[DEBUG] Response type",
            'debug_response_status': "[DEBUG] Response status",
            'section_divider': "Divider",
            'section_end': "="*20 + " End " + "="*20,
            'api_prepare_call': "Preparing to call DeepSeek API, prompt length",
            'api_key_invalid': "API key is invalid or too short",
            'api_try_endpoint': "Trying API endpoint",
            'api_received_response': "Received response, status code",
            'api_html_response': "Service temporarily unavailable, please try again later or check API status",
            'api_success_response': "Successfully received API response",
            'api_empty_response': "API returned empty response",
            'api_exception': "API call exception",
            'api_fallback': "Unable to connect to AI service",
            'api_source': "DeepSeek API",
            'preset_knowledge_source': "Preset Knowledge Base", 
            'system_source': "System"
        }
    }

    def __init__(self, database_path: str, deepseek_api_key: str, language: str = 'zh', faq_file: str = None, base_url: str = "https://api.deepseek.com"):
        from openai import OpenAI
        
        if not os.path.exists(database_path):
            raise ValueError(f"数据库路径不存在: {database_path}")
            
        self.client = OpenAI(
            api_key=deepseek_api_key,
            base_url=base_url
        )
            
        if not os.path.isdir(database_path):
            raise ValueError("数据库路径必须是文件夹")
            
        if not any(fname.endswith('.xlsx') for fname in os.listdir(database_path)):
            raise ValueError("数据库文件夹中未找到Excel文件")
            
        self.database_path = database_path
        self.database = pd.DataFrame()
        self.deepseek_api_key = deepseek_api_key
        self.manual_operation_url = "https://bohrium.dp.tech/apps/predict"
        self.base_url = base_url.rstrip('/')
        self.language = language
        self.translations = self.TRANSLATIONS
        self.faq_file = faq_file
        self.gas_adsorption_faq = self._load_faq(faq_file) if faq_file else self.DEFAULT_FAQ.copy()

    def _load_and_preprocess_data(self, path: str) -> pd.DataFrame:
        try:
            gas_name = os.path.basename(path).split('.')[0].upper()
            
            if not os.path.exists(path):
                raise ValueError(f"数据文件 {gas_name}.xlsx 不存在")
                
            if os.path.getsize(path) == 0:
                raise ValueError(f"数据文件 {gas_name}.xlsx 为空")
            
            try:
                df = pd.read_excel(path)
            except Exception as e:
                raise ValueError(f"无法读取 {gas_name}.xlsx - 文件可能已损坏: {str(e)}")
                
            if df.empty:
                raise ValueError(f"Excel文件 {gas_name}.xlsx 为空或格式不正确")
            
            if 'Gas' not in df.columns:
                df['Gas'] = gas_name
            else:
                df['Gas'] = df['Gas'].fillna(gas_name).str.upper()
            
            if 'CSD' not in df.columns:
                raise ValueError(f"Excel文件 {gas_name}.xlsx 缺少必需的CSD列")
            
            df = df.dropna(subset=['CSD'])
            
            numeric_cols = ['lgN', 'LCD', 'PLD', 'VSA', 'Density', 'φ']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except ValueError as ve:
            raise ValueError(f"加载数据库失败: {str(ve)}")
        except Exception as e:
            raise ValueError(f"加载 {os.path.basename(path)} 失败: {str(e)}")

    def _load_faq(self, faq_file: str) -> Dict[str, str]:
        try:
            with open(faq_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载预设问题文件失败: {str(e)}")
            return {}

    def _parse_condition(self, condition_str: str) -> tuple:
        condition_str = condition_str.strip()
        field = None
        operator = None
        value = None
        
        if condition_str.startswith('筛选'):
            parts = condition_str[2:].strip().split()
            if len(parts) >= 3:
                field = parts[0].upper()
                operator = parts[1]
                try:
                    value = float(parts[2])
                except ValueError:
                    pass
                return (field, operator, value)
        
        field_candidates = ['LCD', 'PLD', 'φ', 'Density', 'VSA']
        for candidate in field_candidates:
            if candidate.lower() in condition_str.lower():
                field = candidate
                break
                
        if not field:
            return (None, None, None)
        
        operator_map = {
            '>': ['>', '大于'],
            '<': ['<', '小于'], 
            '=': ['=', '等于']
        }
        
        for op_symbol, op_forms in operator_map.items():
            for op_form in op_forms:
                if op_form in condition_str:
                    operator = op_symbol
                    value_part = condition_str.split(op_form)[-1].strip()
                    value_str = ''.join(c for c in value_part if c.isdigit() or c == '.')
                    try:
                        value = float(value_str) if value_str else None
                    except ValueError:
                        value = None
                    break
            if operator:
                break
        
        return (field, operator, value)

    GAS_NAME_MAPPING = {
        'HCHO': ['HCHO', '甲醛', 'FORMALDEHYDE'],
        'C2H5OH': ['C2H5OH', 'C2H6O', '乙醇', 'ETHANOL', '酒精'],
        'C3H8': ['C3H8', '丙烷', 'PROPANE'],
        'C3H9O3P': ['C3H9O3P', '磷酸三甲酯', 'TRIMETHYL PHOSPHATE'],
        'C4H8CL2S': ['C4H8CL2S', 'C4H8Cl2S', '二氯乙硫醚', 'MUSTARD GAS'],
        'C4H9CLS': ['C4H9CLS', 'C4H9ClS', '氯乙硫醚', 'CHLOROETHYL SULFIDE'],
        'C7H16FO2P': ['C7H16FO2P', 'C7H16FO2P',
            '沙林', 'SARIN', 'GB', 
            '甲基氟膦酸异丙酯',
            'Isopropyl methylphosphonofluoridate'
        ],
        'C8H10': ['C8H10', '二甲苯', 'XYLENE'],
        'n-C4H10': ['n-C4H10', 'nC4H10', '正丁烷', 'n-BUTANE'],
        'n-C5H12': ['n-C5H12', 'nC5H12', '正戊烷', 'n-PENTANE'],
        'n-C6H14': ['n-C6H14', 'nC6H14', '正己烷', 'n-HEXANE']
    }

    def _get_gas_data_file(self, gas_name: str) -> str:
        if not hasattr(self, 'database_path'):
            return None
            
        gas_name = gas_name.upper()
        for file in os.listdir(self.database_path):
            file_upper = file.upper()
            if file_upper == f"{gas_name}.XLSX":
                return os.path.join(self.database_path, file)
        
        for file in os.listdir(self.database_path):
            if file.upper().startswith(gas_name) and file.lower().endswith('.xlsx'):
                return os.path.join(self.database_path, file)
        return None

    def _load_gas_data(self, gas_name: str) -> None:
        data_file = self._get_gas_data_file(gas_name)
        if data_file:
            self.database = self._load_and_preprocess_data(data_file)
        else:
            available_gases = [f.split('.')[0] for f in os.listdir(self.database_path) 
                             if f.lower().endswith('.xlsx')]
            raise ValueError(
                f"找不到{gas_name}对应的数据文件\n"
                f"可用气体: {', '.join(available_gases)}"
            )

    def process_query_request(self, query: str, previous_results: pd.DataFrame = None) -> Dict:
        try:
            if hasattr(self, 'database_path') and self.database is None:
                gas_files = [f for f in os.listdir(self.database_path) 
                           if f.lower().endswith('.xlsx')]
                
                query_upper = query.upper()
                for gas_file in gas_files:
                    gas_name = gas_file.split('.')[0].upper()
                    if query_upper == gas_name or query_upper in self.GAS_NAME_MAPPING.get(gas_name, []):
                        self._load_gas_data(gas_name)
                        break
            if query.startswith('筛选'):
                if previous_results is None:
                    return {
                        'type': 'query_error',
                        'message': "没有可筛选的先前结果",
                        'suggestion': "请先执行初始查询"
                    }
                
                condition_str = query[2:].strip()
                field, operator, value = self._parse_condition(condition_str)
                
                if not all([field, operator, value is not None]):
                    return {
                        'type': 'query_error',
                        'message': "无效的筛选条件格式",
                        'details': "请使用: 筛选 [字段] [操作符] [值]",
                        'suggestion': "示例: 筛选 VSA > 1000"
                    }

                if operator == '>':
                    results = previous_results[previous_results[field] > value]
                elif operator == '<':
                    results = previous_results[previous_results[field] < value]
                else:
                    results = previous_results[previous_results[field] == value]
                
                if len(results) > 0:
                    return {
                        'type': 'filter_query',
                        'field': field,
                        'operator': operator,
                        'value': value,
                        'count': len(results),
                        'mof_recommendations': results.nlargest(3, 'lgN').to_dict('records'),
                        'full_results': results
                    }
                else:
                    return {
                        'type': 'query_error',
                        'message': "没有找到匹配的记录",
                        'suggestion': "尝试放宽筛选条件"
                    }

            query_lower = query.lower()
            
            if '最大的' in query_lower or 'max' in query_lower or '最小的' in query_lower or 'min' in query_lower:
                field = None
                field_candidates = ['LCD', 'PLD', 'φ', 'lgN', 'Density', 'VSA']
                for candidate in field_candidates:
                    if candidate.lower() in query_lower:
                        field = candidate
                        break
                
                if field:
                    if '最小的' in query_lower or 'min' in query_lower:
                        mof = self.database.loc[self.database[field].idxmin()]
                        query_type = 'min_value_query'
                    else:
                        mof = self.database.loc[self.database[field].idxmax()]
                        query_type = 'max_value_query'
                    
                    return {
                        'type': query_type,
                        'field': field,
                        'value': mof[field],
                        'mof': {
                            'CSD': mof['CSD'],
                            'No.': mof['No.'],
                            'Gas': mof['Gas'],
                            'lgN': mof['lgN']
                        }
                    }
            
            if '且' in query_lower or '和' in query_lower or '并且' in query_lower:
                conditions = []
                valid = True
                
                parts = re.split('且|和|并且', query_lower)
                for part in parts:
                    part = part.strip()
                    field, operator, value = self._parse_condition(part)
                    if field and operator and value is not None:
                        conditions.append((field, operator, value))
                    else:
                        valid = False
                        break
                
                if valid and len(conditions) >= 2:
                    results = self.database.copy()
                    for field, operator, value in conditions:
                        if operator == '>':
                            results = results[results[field] > value]
                        elif operator == '<':
                            results = results[results[field] < value]
                        else:
                            results = results[results[field] == value]
                    
                    if len(results) > 0:
                        response = {
                            'type': 'compound_query',
                            'conditions': conditions,
                            'count': len(results),
                            'mof_recommendations': results.nlargest(10, 'lgN').to_dict('records'),
                            'mofs': results.nlargest(10, 'lgN').to_dict('records'),
                            'full_results': results
                        }

                        if len(results) > 3:
                            response['suggestion'] = "找到多条记录，输入'筛选 [字段] [条件]'进行进一步筛选"
                        
                        return response

            comparison_phrases = ['大于', '小于', '等于', '>', '<', '=']
            if any(phrase in query_lower for phrase in comparison_phrases):
                field, operator, value = self._parse_condition(query_lower)
                if field and operator and value is not None:
                    if operator == '>':
                        results = self.database[self.database[field] > value]
                    elif operator == '<':
                        results = self.database[self.database[field] < value]
                    else:
                        results = self.database[self.database[field] == value]
                        
                    if len(results) > 0:
                        return {
                            'type': 'numeric_query',
                            'field': field,
                            'operator': operator,
                            'value': value,
                            'count': len(results),
                            'mof_recommendations': results.nlargest(10, 'lgN').to_dict('records'),
                            'mofs': results.nlargest(10, 'lgN').to_dict('records')
                        }

            gas_query = query.strip().upper()

            known_gas = None
            for gas_code, names in self.GAS_NAME_MAPPING.items():
                if gas_query == gas_code:
                    known_gas = gas_code
                    break
                if gas_query in names:
                    known_gas = gas_code 
                    break
                if f"查询{gas_code}" in gas_query or \
                   any(f"查询{name}" in gas_query for name in names):
                    known_gas = gas_code
                    break
                if f"{gas_code}的MOF" in gas_query or \
                   any(f"{name}的MOF" in gas_query for name in names):
                    known_gas = gas_code
                    break
            
            if known_gas:
                if not hasattr(self, 'database') or self.database.empty or \
                   self.database.iloc[0]['Gas'].upper() != known_gas:
                    self._load_gas_data(known_gas)
                
                gas_data = self.database[self.database['Gas'].str.upper() == known_gas]
                
                if len(gas_data) == 0:
                    return {
                        'type': 'query_error',
                        'message': f"数据库中未找到 {known_gas} 的相关数据",
                        'suggestion': "请检查数据库文件内容"
                    }
                
                stats = {
                    'average_lgN': round(gas_data['lgN'].mean(), 3),
                    'max_diffusivity': round(gas_data['Diffusivity'].max(), 3) if 'Diffusivity' in gas_data.columns else None,
                    'average_LCD': round(gas_data['LCD'].mean(), 3) if 'LCD' in gas_data.columns else None,
                    'average_PLD': round(gas_data['PLD'].mean(), 3) if 'PLD' in gas_data.columns else None,
                    'average_VSA': round(gas_data['VSA'].mean(), 3) if 'VSA' in gas_data.columns else None
                }

                top_mofs = []
                for _, row in gas_data.nlargest(3, 'lgN').iterrows():
                    gas_name = row.get('Gas', '未知')
                    standard_name = next(
                        (k for k, v in self.GAS_NAME_MAPPING.items() 
                         if gas_name.upper() in v or gas_name.upper() == k),
                        gas_name
                    )
                    mof = {
                        'CSD': row.get('CSD', '未知'),
                        'No.': row.get('No.', '未知'),
                        'Gas': standard_name,
                        'GasAliases': self.GAS_NAME_MAPPING.get(standard_name, []),
                        'lgN': round(row.get('lgN', 0), 3),
                        'LCD': round(row.get('LCD', 0), 3) if 'LCD' in gas_data.columns else None,
                        'PLD': round(row.get('PLD', 0), 3) if 'PLD' in gas_data.columns else None,
                        'VSA': round(row.get('VSA', 0), 3) if 'VSA' in gas_data.columns else None,
                        'Density': round(row.get('Density', 0), 3) if 'Density' in gas_data.columns else None,
                        'φ': round(row.get('φ', 0), 3) if 'φ' in gas_data.columns else None
                    }
                    top_mofs.append(mof)
                
                return {
                    'type': 'gas_query_summary',
                    'gas': known_gas,
                    'match_count': len(gas_data),
                    'statistical_summary': stats,
                    'top_mofs': top_mofs
                }

            supported_fields = ['LCD', 'PLD', 'φ', 'lgN', 'Density', 'VSA']
            return {
                'type': 'query_error',
                'message': "无法解析查询条件",
                'details': f"请尝试以下格式之一:\n1. '字段最大的MOF'\n2. '字段最小的MOF'\n3. '字段>值'\n4. '气体名称'\n\n支持字段: {', '.join(supported_fields)}",
                'suggestion': "或切换到专家模式获取更详细的帮助"
            }
            
        except Exception as e:
            return {
                'type': 'error',
                'message': f"查询处理失败: {str(e)}",
                'suggestion': "请检查查询格式或稍后再试"
            }

    def _call_deepseek_api(self, prompt: str, max_tokens: int = None, image_url: str = None) -> Optional[str]:
        print(f"[Step 2] {self._t('api_prepare_call')}: {len(prompt)}")
        
        if not self.deepseek_api_key or len(self.deepseek_api_key) < 30:
            print(f"[ERROR] {self._t('api_key_invalid')}")
            return None
            
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        if image_url:
            payload = {
                "model": "deepseek-v4-flash",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }],
                "stream": True,
                "response_format": {"type": "text"}
            }
        else:
            payload = {
                "model": "deepseek-v4-flash",
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
                "response_format": {"type": "text"}
            }

        endpoints = [
                     "https://api.deepseek.com/v1/chat/completions"
                     ]
        
        last_error = None
        endpoint_errors = []
        
        for endpoint in endpoints:
            print(f"[Step 3] {self._t('api_try_endpoint')}: {endpoint}")
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=60,
                    stream=True
                )
                
                if response.status_code == 200:
                    full_response = ""
                    for chunk in response.iter_lines():
                        if chunk:
                            decoded_chunk = chunk.decode('utf-8')
                            if decoded_chunk.startswith('data:'):
                                try:
                                    data = json.loads(decoded_chunk[5:])
                                    if 'choices' in data and len(data['choices']) > 0:
                                        delta = data['choices'][0].get('delta', {})
                                        if 'content' in delta:
                                            full_response += delta['content']
                                except json.JSONDecodeError:
                                    continue
                    return full_response if full_response else None
                
                print(f"[Step 4] {self._t('api_received_response')}: {response.status_code}")

                if 'text/html' in response.headers.get('Content-Type', ''):
                    return self._t('api_html_response')
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if 'choices' in result and len(result['choices']) > 0:
                            return result['choices'][0]['message']['content']
                        elif 'error' in result:
                            return {
                                'type': 'api_error',
                                'message': result['error'].get('message', self._t('api_error_generic')),
                                'suggestion': self._t('api_check_config')
                            }
                        else:
                            return {
                                'type': 'api_error',
                                'message': self._t('api_response_format_error'),
                                'suggestion': self._t('api_contact_support')
                            }
                    except json.JSONDecodeError:
                        return {
                            'type': 'api_error',
                            'message': self._t('api_invalid_response_format'),
                            'suggestion': self._t('api_try_again')
                        }
                elif response.status_code == 404:
                    return {
                        'type': 'api_error',
                        'message': self._t('api_endpoint_not_found'),
                        'suggestion': self._t('api_check_endpoint')
                    }
                else:
                    return {
                        'type': 'api_error',
                        'message': f"{self._t('api_service_error')}: {response.status_code}",
                        'suggestion': self._t('api_try_again')
                    }
                
            except requests.exceptions.RequestException as e:
                if hasattr(e, 'response') and e.response is not None and e.response.status_code == 429:
                    wait_time = 2
                    print(f"[INFO] {self._t('api_rate_limit')}, {self._t('api_waiting')} {wait_time} {self._t('api_seconds_retry')}...")
                    import time
                    time.sleep(wait_time)
                    continue
                
                error_msg = f"{self._t('api_request_exception')}: {str(e)}"
                endpoint_errors.append(f"{endpoint}: {error_msg}")
                print(f"[ERROR] {error_msg}")
                return {
                    'type': 'api_error',
                    'message': 'API请求失败',
                    'details': str(e),
                    'suggestion': '请检查网络连接后重试'
                }
            except Exception as e:
                error_msg = f"{self._t('api_unknown_exception')}: {str(e)}"
                endpoint_errors.append(f"{endpoint}: {error_msg}")
                print(f"[ERROR] {error_msg}")
                return {
                    'type': 'api_error',
                    'message': '系统内部错误',
                    'details': str(e),
                    'suggestion': '请联系技术支持'
                }
                
        print(f"[WARNING] {self._t('api_fallback')}")
        return {
            'type': 'api_error',
            'message': "暂时无法获取AI解答",
            'suggestion': "请尝试使用更具体的问题或稍后再试",
            'fallback_suggestion': "您可以访问以下链接获取帮助: " + self.manual_operation_url
        }

    def query_mof_by_gas(self, gas: str) -> Dict:
        try:
            if not isinstance(gas, str) or not gas.strip():
                return {
                    'status': 'error',
                    'message': "无效的气体名称",
                    'details': "输入必须是非空字符串"
                }
            
            gas_upper = gas.upper().strip()

            try:
                self._load_gas_data(gas_upper)
            except ValueError as e:
                if self.language == 'zh':
                    return {
                        'status': 'not_found',
                        'message': f"数据库中未找到 {gas} 的相关数据",
                        'details': str(e),
                        'suggestion': "请尝试其他气体查询或访问以下链接手动操作:",
                        'manual_url': self.manual_operation_url
                    }
                else:
                    return {
                        'status': 'not_found',
                        'message': f"No relevant data found for {gas}",
                        'details': str(e),
                        'suggestion': "Please try other gas queries or visit:",
                        'manual_url': self.manual_operation_url,
                        'manual_prompt': "Manual operation link:"
                    }

            results = self.database[self.database['Gas'] == gas_upper]
            
            if len(results) == 0:
                return {
                    'status': 'not_found',
                    'message': f"数据库中未找到 {gas} 的相关数据",
                    'suggestion': "请尝试其他气体查询或访问以下链接手动操作:",
                    'manual_url': self.manual_operation_url
                }

            top_mofs = results.sort_values(by='lgN', ascending=False).head(3)

            max_lgN = top_mofs['lgN'].iloc[0] if len(top_mofs) > 0 else results['lgN'].max()
            
            summary_stats = {
                'average_lgN': results['lgN'].mean(),
                'max_lgN': max_lgN,
                'max_diffusivity': results['Diffusion_Coefficient'].max() if 'Diffusion_Coefficient' in results.columns else None,
                'count': len(results)
            }
            
            return {
                'status': 'success',
                'gas': gas,
                'top_mofs': top_mofs.to_dict('records'),
                'summary_stats': summary_stats
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': "查询过程中发生错误",
                'details': str(e),
                'suggestion': "请检查数据库格式或联系管理员"
            }

    def add_faq(self, question: str, answer: str) -> bool:
        if question and answer:
            self.gas_adsorption_faq[question] = answer
            return True
        return False

    def remove_faq(self, question: str) -> bool:
        if question in self.gas_adsorption_faq:
            del self.gas_adsorption_faq[question]
            return True
        return False

    def save_faq(self, faq_file: str = None) -> bool:
        file_path = faq_file or self.faq_file
        if not file_path:
            return False
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.gas_adsorption_faq, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存预设问题文件失败: {str(e)}")
            return False

    def _parse_numeric_query(self, query: str) -> Optional[Dict]:
        import re
        max_min_pattern = '(最大|最小)(LCD|lgN|Density|VSA|PLD|φ|K|Q_st\^0|ρ)|(LCD|lgN|Density|VSA|PLD|φ|K|Q_st\^0|ρ)(最大|最小)'
        max_min_match = re.search(max_min_pattern, query)
        if max_min_match:
            return {
                'field': max_min_match.group(2),
                'operator': 'max' if max_min_match.group(1) == '最大' else 'min',
                'value': None
            }

        patterns = [
            ('(LCD|lgN|Density|VSA|PLD|φ|K|Q_st\^0|ρ)\s*大于\s*([\d\.]+)', '>'),
            ('(LCD|lgN|Density|VSA|PLD|φ|K|Q_st\^0|ρ)\s*小于\s*([\d\.]+)', '<'), 
            ('(LCD|lgN|Density|VSA|PLD|φ|K|Q_st\^0|ρ)\s*等于\s*([\d\.]+)', '=='),
            ('(LCD|lgN|Density|VSA|PLD|φ|K|Q_st\^0|ρ)\s*=\s*([\d\.]+)', '=='),
            ('(LCD|lgN|Density|VSA|PLD|φ|K|Q_st\^0|ρ)\s*>\s*([\d\.]+)', '>'),
            ('(LCD|lgN|Density|VSA|PLD|φ|K|Q_st\^0|ρ)\s*<\s*([\d\.]+)', '<'),
        ]
        
        for pattern, operator in patterns:
            match = re.search(pattern, query)
            if match:
                return {
                    'field': match.group(1),
                    'operator': operator,
                    'value': float(match.group(2))
                }
        return None

    def query_by_numeric(self, field: str, operator: str, value: float = None) -> Dict:
        try:
            results = pd.DataFrame()
            
            if operator in ['>', '<', '==']:
                if operator == '>':
                    results = self.database[self.database[field] > value]
                elif operator == '<':
                    results = self.database[self.database[field] < value]
                elif operator == '==':
                    results = self.database[self.database[field] == value]
            elif operator == 'max':
                results = self.database.sort_values(by=field, ascending=False)
            elif operator == 'min':
                results = self.database.sort_values(by=field, ascending=True)
            else:
                return {
                    'status': 'error',
                    'message': f"不支持的比较运算符: {operator}"
                }

            if operator in ['max', 'min']:
                results = results.head(3)

            if results is None:
                results = pd.DataFrame()
            
            if len(results) == 0:
                return {
                    'status': 'not_found',
                    'message': f"未找到{field}{operator}{value}的材料",
                    'suggestion': "请尝试其他查询条件"
                }

            if results is not None and not results.empty:
                numeric_cols = results.select_dtypes(include=['float64', 'int64']).columns
                if len(numeric_cols) > 0:
                    results = results.copy()
                    results[numeric_cols] = results[numeric_cols].round(3)
            
            return {
                'status': 'success',
                'field': field,
                'operator': operator,
                'value': value,
                'results': results.to_dict('records'),
                'count': len(results)
            }
            
        except KeyError:
            return {
                'status': 'error',
                'message': f"数据库中不存在字段: {field}",
                'available_fields': list(self.database.columns)
            }

    def process_user_request(self, user_input: str) -> Dict:
        if user_input.strip() in ['1', '查询']:
            print(f"\n{expert._t('query_mode_selected_prompt')}")
            new_input = input("> ").strip()
            if not new_input:
                return {
                    'type': 'error',
                    'message': "请输入有效的查询条件"
                }
            user_input = new_input
        elif user_input.strip() in ['2', '专家解答']:
            print(f"\n{expert._t('expert_mode_selected_prompt')}")
            new_input = input("> ").strip()
            if not new_input:
                return {
                    'type': 'error', 
                    'message': "请输入有效的问题"
                }
            return self.answer_question(new_input)

        if user_input.strip() == "详细":
            return {
                'type': 'error',
                'status': 'error',
                'message': "请先执行气体查询后再使用详细查询",
                'details': "详细查询需要先执行气体查询获取结果",
                'source': '系统'
            }

        if user_input in self.gas_adsorption_faq:
            return self.answer_question(user_input)

        query = user_input.strip().upper()
        
        gas_patterns = {
            'HCHO': '(HCHO|甲醛|FORMALDEHYDE)',
            'C2H5OH': '(C2H5OH|乙醇|ETHANOL|酒精)',
            'C3H8': '(C3H8|丙烷|PROPANE)',
            'C3H9O3P': '(C3H9O3P|磷酸三甲酯|TRIMETHYL PHOSPHATE)',
            'C4H8CL2S': '(C4H8CL2S|二氯乙硫醚|MUSTARD GAS)',
            'C4H9CLS': '(C4H9CLS|氯乙硫醚|CHLOROETHYL SULFIDE)',
            'C7H16FO2P': '(C7H16FO2P|沙林|SARIN)',
            'C8H10': '(C8H10|二甲苯|XYLENE)',
            'n-C4H10': '(n-C4H10|正丁烷|N-BUTANE)',
            'n-C5H12': '(n-C5H12|正戊烷|N-PENTANE)',
            'n-C6H14': '(n-C6H14|正己烷|N-HEXANE)',
            'NH3': '(NH3|氨气|AMMONIA)',
            'CO2': '(CO2|二氧化碳|CARBON DIOXIDE)',
            'CH4': '(CH4|甲烷|METHANE)',
            'H2': '(H2|氢气|HYDROGEN)',
            'N2': '(N2|氮气|NITROGEN)',
            'O2': '(O2|氧气|OXYGEN)',
        }
        
        detected_gases = []
        for gas_code, pattern in gas_patterns.items():
            if re.search(pattern, user_input, re.IGNORECASE):
                detected_gases.append(gas_code)
        
        if detected_gases:
            primary_gas = detected_gases[0]
            try:
                query_result = self.query_mof_by_gas(primary_gas)
            except Exception as e:
                return {
                    'type': 'query_error',
                    'message': "气体查询过程中发生错误",
                    'details': str(e),
                    'suggestion': "请检查输入或联系管理员",
                    'source': '系统'
                }
                
            if not query_result:
                return {
                    'type': 'query_error',
                    'message': "查询失败: 未获得有效响应",
                    'details': "查询函数返回None",
                    'suggestion': "请检查数据库连接或联系管理员",
                    'source': '系统'
                }
            
            if 'status' not in query_result:
                return {
                    'type': 'query_error',
                    'message': "查询结果格式错误",
                    'details': "响应缺少必要的status字段",
                    'suggestion': "请检查数据库格式或联系管理员",
                    'source': '系统'
                }
            
            if query_result.get('status') == 'error':
                return {
                    'type': 'query_error',
                    'message': "查询过程中发生错误",
                    'details': query_result.get('details', '未知错误'),
                    'suggestion': query_result.get('suggestion', '请重试或联系管理员'),
                    'source': '系统'
                }
            
            if query_result['status'] == 'not_found':
                if self.language == 'zh':
                    return {
                        'type': 'gas_not_found',
                        'message': query_result.get('message', '未找到相关数据'),
                        'suggestion': query_result.get('suggestion', '请尝试其他查询'),
                        'manual_url': query_result.get('manual_url', self.manual_operation_url),
                        'manual_prompt': query_result.get('manual_prompt', 'Manual operation link:')
                    }
                else:
                    return {
                        'type': 'gas_not_found',
                        'message': query_result.get('message', 'No relevant data found'),
                        'suggestion': query_result.get('suggestion', 'Please try other queries'),
                        'manual_url': query_result.get('manual_url', self.manual_operation_url)
                    }

            return {
                'type': 'gas_query_summary',
                'gas': primary_gas,
                'match_count': len(self.database[self.database['Gas'] == primary_gas.upper()]),
                'statistical_summary': query_result['summary_stats'],
                'top_mofs': query_result['top_mofs']
            }

        if any(keyword in user_input for keyword in ['大于', '小于', '等于', '>', '<', '=']):
            numeric_query = self._parse_numeric_query(user_input)
            if numeric_query:
                query_result = self.query_by_numeric(
                    numeric_query['field'],
                    numeric_query['operator'],
                    numeric_query['value']
                )
                
                if query_result['status'] == 'success':
                    return {
                        'type': 'numeric_query',
                        'field': query_result['field'],
                        'operator': query_result['operator'],
                        'value': query_result['value'],
                        'mof_recommendations': query_result['results'],
                        'count': query_result['count']
                    }
                else:
                    return query_result

        if self.language == 'zh':
            return {
                'type': 'query_error',
                'message': "无法识别的查询格式",
                'details': "请输入有效的查询条件或切换至专家模式",
                'source': '系统'
            }
        else:
            return {
                'type': 'query_error',
                'message': "Unrecognized query format",
                'details': "Please enter valid query conditions or switch to expert mode",
                'source': 'system'
            }

    API_PROMPT_TEMPLATES = {
        'zh': """你是一个资深MOF材料专家,请用专业且易于理解的中文回答以下问题,
问题: {question}
请按照以下框架构建回答：

【概念解析】
首先建立基础概念框架，确保本科生也能理解核心原理

【深度分析】
从以下层面进行专业分析：
• 分子层面：电子结构、相互作用机理（配位键、氢键、范德华力等）
• 结构层面：孔道几何、拓扑特征、晶体学参数
• 性能层面：热力学驱动力、动力学限制、结构-性能关系

【实例验证】
提供1-2个具体MOF案例，每个案例包含：
- 具体MOF名称和结构特征
- 关键性能数据（比表面积、吸附容量、选择性等）
- 实验或计算证据支持

【实用指导】
针对问题性质提供：
- 如涉及气体吸附：分析该气体的物性参数与MOF设计策略的关联
- 如涉及材料选择：系统评估吸附容量、选择性、稳定性的平衡方案
- 如涉及应用场景：给出从实验室到产业化的技术路径

【对比总结】
与传统材料或其他MOF的对比分析，用文字描述关键差异

【研究展望】
指出当前技术瓶颈和未来发展方向

回答要求：
1. 使用纯文本格式，避免任何Markdown符号
2. 专业深度与教学表达并重，复杂概念要用贴切比喻
3. 每个论点都要有具体数据或文献依据
4. 结构清晰，层次分明，逻辑连贯
5. 避免使用*、#、-等特殊符号，用文字分段""",
        'en': """You are a chief MOF materials scientist, please answer the following question in professional yet accessible English:
Question: {question}
Please structure your response using this framework:

[Conceptual Foundation]
Firstly, establish a basic conceptual framework to ensure that undergraduate students can also understand the core principles

[In-depth Analysis]
Provide professional analysis from these perspectives:
• Molecular level: Electronic structure, interaction mechanisms (coordination bonds, hydrogen bonding, van der Waals forces, etc.)
• Structural level: Pore geometry, topological features, crystallographic parameters  
• Performance level: Thermodynamic drivers, kinetic limitations, structure-property relationships

[Evidence and Examples]
Provide 1-2 specific MOF case studies, each including:
- Specific MOF name and structural characteristics
- Key performance data (surface area, adsorption capacity, selectivity, etc.)
- Experimental or computational evidence support

[Practical Guidance]
Offer actionable insights based on question context:
- For gas adsorption: Analyze correlations between gas properties and MOF design strategies
- For material selection: Systematically evaluate trade-offs between adsorption capacity, selectivity, and stability
- For applications: Outline technical pathways from laboratory to industrialization

[Comparative Analysis]
Compare with traditional materials or other MOFs, describing key differences in text

[Research Outlook]
Identify current technological bottlenecks and future development directions

Response Requirements:
1. Use plain text format only, avoid all Markdown symbols
2. Balance professional depth with pedagogical expression, using appropriate analogies for complex concepts
3. Support each argument with specific data or literature evidence
4. Maintain clear structure, logical hierarchy, and coherent flow
5. Avoid using *, #, - symbols, use text-based paragraph separation"""
    }

    ERROR_MESSAGES = {
        'zh': "无法获取解答，请尝试更具体的问题或稍后再试。",
        'en': "Unable to get answer, please try a more specific question or try again later."
    }

    def answer_question(self, question: str) -> Dict:
        prompt = self.API_PROMPT_TEMPLATES[self.language].format(question=question)
        error_msg = self.ERROR_MESSAGES[self.language]


        if question in self.gas_adsorption_faq:
            return {
                'type': 'faq',
                'answer': self.gas_adsorption_faq[question],
                'source': self._t('preset_knowledge_source'),
                'source_label': self._t('source_label')
            }

        import difflib

        processed_question = question.lower().strip()
        for char in '?!.,':
            processed_question = processed_question.replace(char, '')

        faq_questions = [
            q.lower().strip().replace('?', '').replace('!', '').replace('.', '').replace(',', '')
            for q in self.gas_adsorption_faq.keys()
        ]

        matches = difflib.get_close_matches(processed_question, faq_questions, n=1, cutoff=0.7)
        if matches:
            matched_question = matches[0]
            original_question = next(
                q for q in self.gas_adsorption_faq.keys()
                if q.lower().strip().replace('?', '').replace('!', '').replace('.', '').replace(',', '') == matched_question
            )
            return {
                    'type': 'faq',
                    'answer': self.gas_adsorption_faq[original_question],
                    'source': self._t('preset_knowledge_source'),
                    'source_label': self._t('source_label')
                }

        if self.language == 'zh':
            print(f"[Step 1] 正在调用DeepSeek API获取问题答案: {question}")
        else:
            print(f"[Step 1] Calling DeepSeek API for question: {question}")
        try:
            api_response = self._call_deepseek_api(prompt)
            if api_response:
                if self.language == 'zh':
                    print(f"[Respond] 成功获取API响应")
                else:
                    print(f"[Respond] Successfully received API response")
                return {
                    'type': 'expert_answer',
                    'answer': api_response,
                    'source': self._t('api_source')
                }
            else:
                if self.language == 'zh':
                    print(f"[Respond] API返回空响应")
                else:
                    print(f"[Respond] API returned empty response")
        except Exception as e:
            if self.language == 'zh':
                print(f"[Respond] API调用异常: {str(e)}")
            else:
                print(f"[Respond] API call exception: {str(e)}")
        
        print(f"[Result] 无法获取API解答,返回错误信息")
        return {
            'type': 'error',
            'answer': error_msg,
            'source': self._t('system_source'),
            'source_label': self._t('source_label')
        }

    def _t(self, key: str) -> str:
        return self.translations.get(self.language, {}).get(key, key)

if __name__ == "__main__":
    CONFIG = {
        "database_path": "D:/all/database",
        "deepseek_api_key": "DEFAULT_API_KEY"  # Your API Key Here
    }

    print("\n请选择语言/Please select language:")
    print("1. Chinese")
    print("2. English")
    lang_choice = input("选择/Choice (1/2): ").strip()
    language = 'zh' if lang_choice == '1' else 'en'
    
    try:
        expert = MOFExpertSystem(CONFIG["database_path"], CONFIG["deepseek_api_key"], language)
        print(expert._t('welcome'))
        current_mode = None
        
        while True:
            if current_mode is None:
                print(f"\n{expert._t('mode_select')}")
                print(f"1. {expert._t('query_mode')}")
                print(f"2. {expert._t('expert_mode')}")
                print(expert._t('exit_prompt'))
                
                mode = input(expert._t('mode_selection_prompt')).strip()
                if mode.lower() in ['退出', 'exit']:
                    break
                    
                if mode == '1':
                    current_mode = 'query'
                    print(f"\n{expert._t('entering_query_mode')}")
                elif mode == '2':
                    current_mode = 'expert'
                    print(f"\n{expert._t('entering_expert_mode')}")
                else:
                    print(expert._t('invalid_mode'))
                    continue
            
            if current_mode == 'query':
                print(f"\n{expert._t('query_prompt')}({expert._t('back_prompt')}):")
                query = input("> ").strip()
                if not query:
                    print(expert._t('invalid_input'))
                    continue
                if query.lower() in ['返回', 'back', 'exit']:
                    current_mode = None
                    continue
                if query.lower() == '退出':
                    break

                if any(keyword in query.lower() for keyword in ['如何', '为什么', '是什么', '解释', '说明']):
                    print("\n提示: 您的问题更适合在专家解答模式下回答")
                    print(f"建议: 输入'返回'切换模式，或输入'退出'结束程序")
                    continue

                response = expert.process_query_request(query, getattr(expert, '_last_results', None))

                if response and response.get('full_results') is not None:
                    expert._last_results = response['full_results']
            elif current_mode == 'expert':
                print(f"\n{expert._t('expert_prompt')}({expert._t('back_prompt')}):")
                question = input("> ").strip()
                if not question:
                    print(expert._t('invalid_input'))
                    continue
                if question.lower() in ['返回', 'back', 'exit']:
                    current_mode = None
                    continue
                if question.lower() == '退出':
                    break
                response = expert.answer_question(question)

            if response.get('type') == 'api_error':
                print(f"\n{response.get('message', '服务暂时不可用')}")
                print(f"建议: {response.get('suggestion', '请稍后再试')}")
                if 'fallback_suggestion' in response:
                    print(response['fallback_suggestion'])
                continue
            elif response.get('type') == 'gas_query_summary':
                title = f"{expert._t('gas_query_result_title')} - {response.get('gas', expert._t('unknown_gas'))}"
                divider = f"{'='*30} {expert._t('section_divider')} {'='*30}"
                count_info = f"{expert._t('found_records')} {response.get('match_count', 0)} {expert._t('matching_records')}"
                
                print(f"\n{title}")
                print(divider)
                print(count_info)
                print(f"\n{expert._t('statistical_summary')}:")
                stats = response.get('statistical_summary', {})
                print(f"{expert._t('average_lgN')}: {round(stats.get('average_lgN', expert._t('unknown')), 3)}")
                max_diff = stats.get('max_diffusivity', None)
                if max_diff is not None:
                    print(f"{expert._t('max_diffusivity')}: {max_diff:.2e} cm²/s")
                else:
                    print(f"{expert._t('max_diffusivity')}: {expert._t('unknown')}")

                print(f"\n{expert._t('top_recommendations')}:")
                for i, mof in enumerate(response.get('top_mofs', []), 1):
                    print(f"{i}. CSD: {mof.get('CSD', '未知')} (No. {mof.get('No.', '未知')})")
                    print(f"   lgN: {round(mof.get('lgN', '未知'), 3)} mol/kg")
                    print(f"   φ: {round(mof.get('φ', '未知'), 3)}")
                    print(f"   PLD: {round(mof.get('PLD', '未知'), 3)} Å")
                    print(f"   LCD: {round(mof.get('LCD', '未知'), 3)} Å")
                    print(f"   Density: {round(mof.get('Density', '未知'), 3)} g/cm³")
                    print(f"   VSA: {round(mof.get('VSA', '未知'), 3)} m²/g")
                    print("-"*20)

                print(f"\n{expert._t('input_detail_prompt')} {response.get('gas', '')}' {expert._t('to_view_all_matches')}")
            
            elif response.get('type') == 'numeric_query':
                print(f"\n{expert._t('numeric_query_result_title')} - {response.get('field', expert._t('unknown_field'))}{response.get('operator', '')}{response.get('value', '')}:")
                print("="*30 + " Divider " + "="*30)
                print(f"找到 {response.get('count', 0)} 条匹配记录:")
                for i, mof in enumerate(response.get('mof_recommendations', []), 1):
                    print(f"{i}. {mof.get('CSD', '未知')}")
                    print(f"   {response.get('field', '字段')}: {round(mof.get(response.get('field', ''), '未知'), 3)}")
                    print(f"   lgN: {round(mof.get('lgN', '未知'), 3)} mol/kg")
                    print(f"   φ: {round(mof.get('φ', '未知'), 3)}")
                    print(f"   PLD: {round(mof.get('PLD', '未知'), 3)} Å")
                    print(f"   LCD: {round(mof.get('LCD', '未知'), 3)} Å")
                    print(f"   Density: {round(mof.get('Density', '未知'), 3)} g/cm³")
                    print(f"   VSA: {round(mof.get('VSA', '未知'), 3)} m²/g")
                    print(f"   气体: {mof.get('Gas', '未知')}")
                    print("-"*20)
            
            elif response.get('type') == 'compound_query':
                conditions = response.get('conditions', [])
                print(f"\n复合条件查询结果:")
                print("="*30 + " 分隔线 " + "="*30)
                for i, (field, operator, value) in enumerate(conditions, 1):
                    print(f"条件{i}: {field}{operator}{value}")
                print(f"\n找到 {response.get('count', 0)} 条匹配记录:")
                
                for i, mof in enumerate(response.get('mof_recommendations', []), 1):
                    print(f"{i}. CSD: {mof.get('CSD', '未知')}")
                    print(f"   lgN: {round(mof.get('lgN', '未知'), 3)} mol/kg")
                    print(f"   φ: {round(mof.get('φ', '未知'), 3)}")
                    print(f"   PLD: {round(mof.get('PLD', '未知'), 3)} Å")
                    print(f"   LCD: {round(mof.get('LCD', '未知'), 3)} Å")
                    print(f"   Density: {round(mof.get('Density', '未知'), 3)} g/cm³")
                    print(f"   VSA: {round(mof.get('VSA', '未知'), 3)} m²/g")
                    print(f"   Gas: {mof.get('Gas', '未知')}")
                    print("-"*20)

                if 'suggestion' in response:
                    print(f"\n{response['suggestion']}")
                    print("可用字段: LCD, PLD, φ, Density, VSA")
                    print("示例: 筛选 LCD > 30")
            
            elif response.get('type') in ['max_value_query', 'min_value_query']:
                field = response.get('field')
                value = response.get('value')
                mof = response.get('mof')
                query_type = "最大" if response['type'] == 'max_value_query' else "最小"
                print(f"\n{field}{query_type}的MOF材料:")
                print("="*30 + " 分隔线 " + "="*30)
                print(f"CSD: {mof.get('CSD', '未知')}")
                print(f"No: {mof.get('No.', '未知')}")
                print(f"Gas: {mof.get('Gas', '未知')}")
                print(f"{field}: {value}")
                print(f"lgN: {mof.get('lgN', '未知')} mol/kg")
            
            elif response.get('type') in ['faq', 'expert_answer']:
                print(f"\n{expert._t('knowledge_qa')}:")
                print("="*30 + " 分隔线 " + "="*30)
                print(response.get('answer', '暂无回答'))
                print(f"\nFrom: {response.get('source', '未知')}")
            
            elif response.get('type') == 'gas_not_found':
                if expert.language == 'zh':
                    print(f"\n提示: {response.get('message', '未找到相关数据')}")
                    print(f"建议: {response.get('suggestion', '请尝试其他查询')}")
                    print(f"手动操作链接: {response.get('manual_url', expert.manual_operation_url)}")
                else:
                    print(f"\nPrompt: {response.get('message', 'No relevant data found')}")
                    print(f"Suggestion: {response.get('suggestion', 'Please try other queries')}")
                    print(f"Manual operation link: {response.get('manual_url', expert.manual_operation_url)}")
            
            elif response.get('status') == 'not_found':
                print(f"\n提示: {response.get('message', '未找到相关数据')}")
                if 'suggestion' in response:
                    print(f"建议: {response.get('suggestion', '')}")
            
            elif response.get('status') == 'error':
                print(f"\n错误: {response.get('message', '未知错误')}")
                if 'available_fields' in response:
                    print("可用字段:", ", ".join(response.get('available_fields', [])))
            
            else:
                print("\n系统错误: 无法识别的响应格式")
                print(f"[DEBUG] 完整响应: {response}")
            
            end_divider = f"\n{'='*20} {expert._t('End')} {'='*20}" if language == 'en' else f"\n{'='*20} 结束 {'='*20}"
            print(end_divider)
            
    except Exception as e:
        if language == 'zh':
            print(f"系统初始化失败: {str(e)}")
        else:
            print(f"System initialization failed: {str(e)}")
