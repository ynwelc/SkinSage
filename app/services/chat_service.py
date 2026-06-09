import requests
import json
from typing import List, Dict, Optional, Generator
from app.config.config import settings

class ChatService:
    """聊天服务，用于调用硅基流动API生成智能回答"""
    
    def __init__(self):
        self.siliconflow_api_url = settings.SILICONFLOW_CHAT_API_URL
        self.siliconflow_api_key = settings.SILICONFLOW_API_KEY
        self.siliconflow_model = settings.SILICONFLOW_CHAT_MODEL
    
    def _read_system_prompt(self) -> str:
        """
        从外部文件读取系统提示词
        
        Returns:
            系统提示词内容
        """
        try:
            # 使用项目根目录下的prompt文件夹
            with open('prompt/system_prompt.txt', 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"读取系统提示词文件失败: {e}")
            # 返回默认提示词作为 fallback
            return "你是一位专业的美容顾问，擅长解答各种美容相关的问题。请根据提供的上下文信息，给出专业、准确、友好的回答。"
    
    def generate_response(self, messages: List[Dict[str, str]], stream: bool = False) -> Optional[str | Generator[str, None, None]]:
        """
        调用硅基流动API生成智能回答
        
        Args:
            messages: 消息列表，格式为[{"role": "user", "content": "问题"}, ...]
            stream: 是否流式返回
            
        Returns:
            生成的回答文本或流式生成器
        """
        if not self.siliconflow_api_key:
            print("硅基流动API Key未配置")
            return None
        
        try:
            # 构建请求体，使用OpenAI风格的格式
            payload = {
                "model": self.siliconflow_model,
                "messages": messages,
                "stream": stream,
                "temperature": 0.7,
                "max_tokens": 4096,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            # 从外部文件读取系统提示
            system_message = {
                "role": "system",
                "content": self._read_system_prompt()
            }
            payload["messages"].insert(0, system_message)
            
            # 调用硅基流动API
            response = requests.post(
                self.siliconflow_api_url,
                headers={
                    "Authorization": f"Bearer {self.siliconflow_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json" if not stream else "text/event-stream"
                },
                json=payload,
                stream=stream,
                timeout=60
            )
            
            response.raise_for_status()
            
            if not stream:
                # 非流式响应处理
                result = response.json()
                
                # 处理响应结果，使用OpenAI风格的格式
                # 使用try-except处理可能的编码问题
                try:
                    print(f"硅基流动API响应: {result}")
                except UnicodeEncodeError:
                    # 如果遇到编码问题，只打印响应的键
                    print(f"硅基流动API响应（简化）: {list(result.keys())}")
                
                # 根据OpenAI风格的格式提取回答
                if result and "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"]
                
                return None
            else:
                # 流式响应处理
                print("调试：开始处理流式响应")
                
                # 逐行处理流式响应
                for line in response.iter_lines():
                    if line:
                        # 解码字节并去除前导空格
                        line = line.decode('utf-8').strip()
                        print(f"调试：流式响应行: {line}")
                        
                        # 跳过非data行
                        if not line.startswith('data: '):
                            continue
                        
                        # 提取data内容
                        data_str = line[6:]
                        
                        # 检查是否结束
                        if data_str == '[DONE]':
                            break
                        
                        # 解析JSON
                        try:
                            data = json.loads(data_str)
                            
                            # 提取文本片段
                            if data and "choices" in data and len(data["choices"]) > 0:
                                choice = data["choices"][0]
                                if "delta" in choice and "content" in choice["delta"]:
                                    content = choice["delta"]["content"]
                                    if content:
                                        yield content
                        except json.JSONDecodeError as e:
                            print(f"调试：JSON解析错误: {e}")
                            continue
                
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"调用硅基流动API失败: {e}")
            # 打印完整的错误信息，包括响应内容
            if hasattr(e, 'response'):
                print(f"API响应内容: {e.response.text}")
            return None
    
    def generate_answer(self, query: str, context: Optional[str] = None) -> Optional[str]:
        """
        生成智能回答，结合上下文信息
        
        Args:
            query: 用户查询
            context: 上下文信息，用于增强回答的准确性
            
        Returns:
            生成的回答文本
        """
        messages = []
        
        # 添加上下文信息（如果有）
        if context:
            messages.append({
                "role": "system",
                "content": f"上下文信息：\n{context}"
            })
        
        # 添加用户查询
        messages.append({
            "role": "user",
            "content": query
        })
        
        return self.generate_response(messages)

# 创建全局聊天服务实例
chat_service = ChatService()
