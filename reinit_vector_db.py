import os
import json
import chromadb
from chromadb.config import Settings
from app.config.config import settings
from app.services.embedding_service import embedding_service

def reinit_vector_db():
    """重新初始化向量库，添加完整的文档分块"""
    print("=== 重新初始化向量库 ===\n")
    
    # 持久化路径
    persist_dir = settings.CHROMA_PERSIST_DIRECTORY
    print(f"1. 持久化路径: {persist_dir}")
    
    # 初始化ChromaDB客户端
    client = chromadb.PersistentClient(
        path=persist_dir,
        settings=Settings(
            anonymized_telemetry=False
        )
    )
    
    # 获取集合
    collection_name = settings.CHROMA_COLLECTION_NAME
    print(f"2. 集合名称: {collection_name}")
    
    # 检查集合是否存在
    collections = client.list_collections()
    collection_exists = any(coll.name == collection_name for coll in collections)
    
    if collection_exists:
        # 删除现有集合
        print(f"   ✓ 集合已存在，正在删除...")
        client.delete_collection(name=collection_name)
        print(f"   ✓ 集合删除成功")
    
    # 创建新集合
    print(f"   创建新集合...")
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "美容知识向量库"}
    )
    print(f"   ✓ 集合创建成功")
    
    # 加载文档分块
    chunks_file = "d:/code/beauty-system/document_chunks.json"
    print(f"\n3. 加载文档分块文件: {chunks_file}")
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"   ✓ 加载成功，包含 {len(chunks)} 个文档分块")
    
    # 准备数据
    print(f"\n4. 准备数据...")
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
    
    # 生成嵌入向量
    print(f"5. 生成 {len(chunks)} 个文档分块的嵌入向量...")
    embeddings = embedding_service.get_embeddings(documents)
    
    if embeddings and len(embeddings) == len(chunks):
        print(f"   ✓ 嵌入向量生成成功")
        
        # 添加到集合，直接传递嵌入向量
        print(f"6. 添加 {len(chunks)} 个文档分块到集合...")
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        
        print(f"   ✓ 添加完成")
        
        # 验证添加结果
        count = collection.count()
        print(f"   ✓ 验证结果: 集合中的文档数量 = {count}")
    else:
        print(f"   ✗ 嵌入向量生成失败，无法添加文档到集合")
    
    # 测试搜索功能
    print(f"\n6. 测试搜索功能")
    test_queries = [
        "斑点净化术的疗程安排是怎样的？",
        "敏肌急救术的注意事项有哪些？",
        "痘肌调理术的治疗时长是多久？"
    ]
    
    for query in test_queries:
        print(f"   查询: {query}")
        # 使用我们自己的嵌入服务生成查询向量
        query_embedding = embedding_service.get_embedding(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )
        
        if results and results["documents"] and results["documents"][0]:
            doc = results["documents"][0][0]
            distance = results["distances"][0][0]
            relevance = 1 - distance
            print(f"   ✓ 搜索成功，相关度: {relevance:.4f}")
            print(f"   文档内容: {doc[:100]}...")
        else:
            print(f"   ✗ 搜索失败")
    
    print(f"\n7. 查看目录结构:")
    for item in os.listdir(persist_dir):
        item_path = os.path.join(persist_dir, item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            print(f"   - 文件: {item} ({size} bytes)")
        else:
            print(f"   - 目录: {item}")
    
    print(f"\n=== 重新初始化完成 ===")
    print(f"向量库现在包含 {count} 个文档分块，持久化到了 {persist_dir} 目录")

if __name__ == "__main__":
    reinit_vector_db()
