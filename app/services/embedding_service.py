import requests
from typing import List, Optional
from app.config.config import settings

class EmbeddingService:
    """文本嵌入服务，用于将文本转换为向量表示"""
    
    def __init__(self):
        self.siliconflow_api_url = settings.SILICONFLOW_API_URL
        self.siliconflow_api_key = settings.SILICONFLOW_API_KEY
        self.embedding_model = settings.SILICONFLOW_EMBED_MODEL
    
    def get_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        获取文本列表的向量嵌入
        
        Args:
            texts: 要嵌入的文本列表
            
        Returns:
            向量嵌入列表，每个文本对应一个向量
        """
        if not texts:
            return []
        
        # 如果没有配置API密钥，返回默认嵌入（全零向量）
        if not self.siliconflow_api_key:
            print("硅基流动API密钥未配置，使用默认嵌入")
            # 返回全零向量，维度为1024
            default_embedding = [0.0] * 1024
            return [default_embedding for _ in texts]
        
        try:
            # 调用硅基流动API获取向量嵌入
            response = requests.post(
                self.siliconflow_api_url,
                headers={
                    "Authorization": f"Bearer {self.siliconflow_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.embedding_model,
                    "input": texts
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 处理响应结果
            embeddings = []
            for item in result.get("data", []):
                if isinstance(item, dict) and "embedding" in item:
                    embeddings.append(item["embedding"])
            
            return embeddings
        
        except requests.exceptions.RequestException as e:
            print(f"获取向量嵌入失败: {e}")
            # 返回默认嵌入，确保系统能继续运行
            default_embedding = [0.0] * 1024
            return [default_embedding for _ in texts]
    
    def get_embedding(self, text: str) -> List[float]:
        """
        获取单个文本的向量嵌入
        
        Args:
            text: 要嵌入的文本
            
        Returns:
            向量嵌入，确保返回列表格式
        """
        embeddings = self.get_embeddings([text])
        if embeddings and len(embeddings) > 0 and isinstance(embeddings[0], list):
            return embeddings[0]
        # 确保返回一个默认的全零向量列表
        return [0.0] * 1024

# 创建全局embedding服务实例
embedding_service = EmbeddingService()
