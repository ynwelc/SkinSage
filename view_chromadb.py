import chromadb
from chromadb.config import Settings
from app.config.config import settings

def view_chromadb():
    """查看ChromaDB中的向量数据"""
    print("=== ChromaDB 向量库查看工具 ===\n")
    
    # 初始化ChromaDB客户端，使用PersistentClient确保持久化
    print(f"1. 连接到ChromaDB，持久化路径: {settings.CHROMA_PERSIST_DIRECTORY}")
    client = chromadb.PersistentClient(
        path=settings.CHROMA_PERSIST_DIRECTORY,
        settings=Settings(
            anonymized_telemetry=False
        )
    )
    
    # 获取或创建集合
    collection_name = settings.CHROMA_COLLECTION_NAME
    print(f"2. 获取或创建集合: {collection_name}")
    try:
        collection = client.get_collection(name=collection_name)
        print(f"   ✓ 集合已存在")
    except Exception as e:
        print(f"   ✗ 集合不存在，正在创建...")
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "美容知识向量库"}
        )
        print(f"   ✓ 集合创建成功")
    
    # 查看集合统计信息
    count = collection.count()
    print(f"3. 集合中的文档数量: {count}\n")
    
    if count == 0:
        print("集合中没有数据！")
        return
    
    # 查看集合中的一些示例数据
    print("4. 查看集合中的示例数据（前3个）:")
    results = collection.get(limit=3)
    
    for i in range(min(3, count)):
        doc_id = results['ids'][i]
        document = results['documents'][i]
        metadata = results['metadatas'][i]
        
        print(f"\n示例 {i+1} (ID: {doc_id}):")
        print(f"文档内容: {document}")
        print(f"元数据: {metadata}")
    
    # 测试向量搜索
    print("\n5. 测试向量搜索:")
    test_query = "斑点净化术的疗程安排是怎样的？"
    print(f"查询: {test_query}")
    
    search_results = collection.query(
        query_texts=[test_query],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )
    
    if search_results and search_results["documents"] and search_results["documents"][0]:
        print("搜索结果:")
        for i, (doc, dist, metadata) in enumerate(zip(
            search_results["documents"][0],
            search_results["distances"][0],
            search_results["metadatas"][0]
        )):
            relevance_score = 1 - dist
            print(f"\n结果 {i+1} (相关度: {relevance_score:.4f}):")
            print(f"文档内容: {doc}")
            print(f"分类: {metadata.get('category', '未知')}")
            print(f"问题: {metadata.get('question', '未知')}")
    else:
        print("未找到相关结果")
    
    print("\n=== 查看完成 ===")

if __name__ == "__main__":
    view_chromadb()
