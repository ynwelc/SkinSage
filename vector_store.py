import chromadb
import json
import os
from typing import List, Dict, Any
from chromadb.config import Settings

class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """初始化向量存储"""
        self.persist_directory = persist_directory
        
        # 确保持久化目录存在
        import os
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # 初始化ChromaDB客户端，使用PersistentClient确保持久化
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # 创建或获取集合
        self.collection_name = "beauty_knowledge_base"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "美容知识向量库"}
        )
    
    def load_chunks(self, chunks_file: str) -> List[Dict[str, Any]]:
        """加载文档分块"""
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        return chunks
    
    def add_chunks_to_collection(self, chunks: List[Dict[str, Any]]):
        """将文档分块添加到向量库"""
        # 准备数据
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        documents = [chunk["chunk_content"] for chunk in chunks]
        
        # 准备元数据
        metadatas = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "category": chunk["category"],
                "question": chunk["question"],
                "chunk_index": i,
                "start_index": chunk["start_index"],
                "end_index": chunk["end_index"]
            }
            metadatas.append(metadata)
        
        # 添加到集合
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"成功添加 {len(chunks)} 个文档分块到向量库")
    
    def search_similar_chunks(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """搜索相似的文档分块"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        # 格式化结果
        formatted_results = []
        for i in range(n_results):
            result = {
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "relevance_score": 1 - results["distances"][0][i]  # 将距离转换为相关度分数
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        stats = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": stats
        }
    
    def run(self, chunks_file: str):
        """执行完整的向量存储流程"""
        print(f"开始处理向量存储...")
        
        # 加载文档分块
        chunks = self.load_chunks(chunks_file)
        print(f"加载了 {len(chunks)} 个文档分块")
        
        # 添加到向量库
        self.add_chunks_to_collection(chunks)
        
        # 获取统计信息
        stats = self.get_collection_stats()
        print(f"向量库统计信息：{stats}")
        
        # 测试检索功能
        print("\n测试检索功能：")
        test_query = "斑点净化术的疗程安排是怎样的？"
        results = self.search_similar_chunks(test_query, n_results=3)
        
        print(f"查询：{test_query}")
        print("检索结果：")
        for i, result in enumerate(results):
            print(f"\n结果 {i+1} (相关度: {result['relevance_score']:.4f}):")
            print(f"文档: {result['document']}")
            print(f"分类: {result['metadata']['category']}")
            print(f"问题: {result['metadata']['question']}")

if __name__ == "__main__":
    vector_store = VectorStore()
    vector_store.run("d:/code/beauty-system/document_chunks.json")
