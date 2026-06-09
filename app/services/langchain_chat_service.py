from typing import List, Dict, Optional
from app.config.config import settings
from app.database.vector_db import vector_db

class LangChainChatService:
    """基于LangChain的多轮对话服务"""
    
    def __init__(self):
        # 使用现有的ChatService进行LLM调用
        from app.services.chat_service import chat_service
        self.chat_service = chat_service
        self.vector_db = vector_db
        
        # 初始化对话历史存储，使用字典存储不同用户的对话历史
        self.conversation_history: Dict[int, List[Dict[str, str]]] = {}
    
    def get_or_create_conversation(self, user_id: int) -> List[Dict[str, str]]:
        """获取或创建用户的对话历史"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        return self.conversation_history[user_id]
    
    def add_message_to_history(self, user_id: int, role: str, content: str):
        """添加消息到对话历史"""
        history = self.get_or_create_conversation(user_id)
        history.append({"role": role, "content": content})
        # 限制对话历史长度，避免内存占用过大
        if len(history) > 20:  # 保留最近20条消息
            self.conversation_history[user_id] = history[-20:]
    
    def clear_conversation_history(self, user_id: int):
        """清空对话历史"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
    
    def generate_response(self, query: str, user_id: int = 0, n_results: int = 5) -> Optional[str]:
        """
        生成多轮对话响应
        
        Args:
            query: 用户当前查询
            user_id: 用户ID，用于区分不同用户的对话历史
            n_results: 向量检索的结果数量
            
        Returns:
            生成的回答文本
        """
        # 1. 获取用户对话历史
        history = self.get_or_create_conversation(user_id)
        
        # 2. 执行向量检索，获取相关文档
        print(f"调试：执行向量检索，查询：{query}")
        results = self.vector_db.search_similar(query, n_results=n_results)
        
        # 3. 构建上下文信息
        context = ""
        if results and results["documents"] and results["documents"][0]:
            print(f"调试：找到 {len(results['documents'][0])} 个相关文档分块")
            for i, doc in enumerate(results["documents"][0]):
                context += f"{doc}\n\n"
        
        # 4. 构建包含历史对话的完整消息列表
        messages = []
        
        # 添加上下文信息
        if context:
            messages.append({
                "role": "system",
                "content": f"上下文信息：\n{context}"
            })
        
        # 添加历史对话
        for msg in history:
            messages.append(msg)
        
        # 添加当前查询
        messages.append({
            "role": "user",
            "content": query
        })
        
        # 5. 调用LLM生成响应
        response = self.chat_service.generate_response(messages)
        
        # 6. 更新对话历史
        if response:
            self.add_message_to_history(user_id, "user", query)
            self.add_message_to_history(user_id, "assistant", response)
        
        return response
    
    def get_conversation_history(self, user_id: int) -> List[Dict[str, str]]:
        """获取用户的对话历史"""
        return self.get_or_create_conversation(user_id)

# 创建全局LangChain聊天服务实例
langchain_chat_service = LangChainChatService()
