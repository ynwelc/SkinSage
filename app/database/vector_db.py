from chromadb import PersistentClient
from chromadb.config import Settings
from app.config.config import settings
from app.services.embedding_service import embedding_service

class VectorDB:
    """向量数据库管理类"""
    
    def __init__(self):
        """初始化向量数据库"""
        # 确保持久化目录存在
        import os
        os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        
        # 使用PersistentClient替代Client，确保数据持久化
        self.client = PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # 尝试获取集合，如果不存在则创建
        try:
            # get_collection方法不支持metadata参数
            self.collection = self.client.get_collection(
                name=settings.CHROMA_COLLECTION_NAME
            )
            print(f"成功获取集合: {settings.CHROMA_COLLECTION_NAME}")
            
            # 检查集合中文档数量
            count = self.collection.count()
            print(f"集合中文档数量: {count}")
            
        except Exception as e:
            print(f"获取集合失败: {e}")
            
            # 尝试创建集合，如果已存在则忽略
            try:
                self.collection = self.client.create_collection(
                    name=settings.CHROMA_COLLECTION_NAME,
                    metadata={"description": "美容知识向量库"}
                )
                print(f"成功创建集合: {settings.CHROMA_COLLECTION_NAME}")
            except Exception as e:
                # 如果集合已存在，再次尝试获取
                print(f"创建集合失败，再次尝试获取: {e}")
                self.collection = self.client.get_collection(
                    name=settings.CHROMA_COLLECTION_NAME
                )
                print(f"成功获取集合: {settings.CHROMA_COLLECTION_NAME}")
            
            # 检查集合中文档数量
            count = self.collection.count()
            print(f"集合中文档数量: {count}")
    
    def get_collection(self):
        """获取向量集合"""
        return self.collection
    
    def search_similar(self, query: str, n_results: int = 5):
        """搜索相似的文档分块"""
        # 生成查询向量
        query_vector = embedding_service.get_embedding(query)
        
        # 使用向量搜索相似文档
        return self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
    
    def add_documents(self, documents: list, metadatas: list, ids: list):
        """添加文档到向量库"""
        # 生成文档嵌入向量
        embeddings = embedding_service.get_embeddings(documents)
        
        # 添加文档和嵌入向量到向量库
        return self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )

# 创建向量数据库实例
vector_db = VectorDB()
