import os
import chromadb
from chromadb.config import Settings
from app.config.config import settings
import json

def diagnose_chromadb():
    """诊断ChromaDB向量库"""
    print("=== ChromaDB 向量库诊断工具 ===\n")
    
    # 检查持久化路径
    persist_dir = settings.CHROMA_PERSIST_DIRECTORY
    print(f"1. 检查持久化路径: {persist_dir}")
    
    if os.path.exists(persist_dir):
        print(f"   ✓ 路径存在")
        print(f"   路径内容:")
        for root, dirs, files in os.walk(persist_dir):
            level = root.replace(persist_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            print(f"   {indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                print(f"   {subindent}{file}")
    else:
        print(f"   ✗ 路径不存在")
        print(f"   正在创建路径...")
        os.makedirs(persist_dir, exist_ok=True)
        print(f"   ✓ 路径创建成功")
    
    # 检查文档分块文件
    chunks_file = "d:/code/beauty-system/document_chunks.json"
    print(f"\n2. 检查文档分块文件: {chunks_file}")
    
    if os.path.exists(chunks_file):
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        print(f"   ✓ 文件存在")
        print(f"   包含 {len(chunks)} 个文档分块")
    else:
        print(f"   ✗ 文件不存在")
        return
    
    # 初始化ChromaDB客户端，使用PersistentClient确保持久化
    print(f"\n3. 初始化ChromaDB客户端")
    client = chromadb.PersistentClient(
        path=persist_dir,
        settings=Settings(
            anonymized_telemetry=False
        )
    )
    
    # 获取所有集合
    print(f"\n4. 获取所有集合")
    collections = client.list_collections()
    print(f"   集合数量: {len(collections)}")
    
    for coll in collections:
        print(f"   - {coll.name}")
    
    # 检查指定集合
    collection_name = settings.CHROMA_COLLECTION_NAME
    print(f"\n5. 检查指定集合: {collection_name}")
    
    # 获取或创建集合
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
    
    # 查看集合中的文档数量
    count = collection.count()
    print(f"   集合中的文档数量: {count}")
    
    # 如果集合为空，尝试重新添加数据
    if count == 0:
        print(f"\n6. 集合为空，尝试重新添加数据")
        
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
        print(f"   添加 {len(chunks)} 个文档分块到集合...")
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"   ✓ 添加完成")
        
        # 验证添加结果
        new_count = collection.count()
        print(f"   ✓ 验证结果: 集合中的文档数量 = {new_count}")
    
    # 测试搜索功能
    print(f"\n7. 测试搜索功能")
    test_query = "斑点净化术的疗程安排是怎样的？"
    print(f"   查询: {test_query}")
    
    search_results = collection.query(
        query_texts=[test_query],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )
    
    if search_results and search_results["documents"] and search_results["documents"][0]:
        print(f"   ✓ 搜索成功，找到 {len(search_results['documents'][0])} 个结果")
        print(f"   第一个结果:")
        print(f"   文档内容: {search_results['documents'][0][0]}")
        print(f"   相关度: {1 - search_results['distances'][0][0]:.4f}")
    else:
        print(f"   ✗ 搜索失败，未找到结果")
    
    print("\n=== 诊断完成 ===")
    print("\n建议:")
    print("1. 确保所有脚本都使用相同的配置和工作目录")
    print("2. 确保ChromaDB客户端的持久化路径正确")
    print("3. 如仍有问题，请尝试删除持久化目录并重新初始化向量库")

if __name__ == "__main__":
    diagnose_chromadb()
