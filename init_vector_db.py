import json
from app.database.vector_db import vector_db

# 初始化向量库，添加文档分块
def init_vector_db():
    """初始化向量库，添加文档分块"""
    print("开始初始化向量库...")
    
    # 加载文档分块
    chunks_file = "d:/code/beauty-system/document_chunks.json"
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"加载了 {len(chunks)} 个文档分块")
    
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
    
    # 添加到向量库
    vector_db.add_documents(documents, metadatas, ids)
    
    print(f"成功添加 {len(chunks)} 个文档分块到向量库")
    
    # 验证添加结果
    collection = vector_db.get_collection()
    count = collection.count()
    print(f"向量库中文档数量: {count}")
    
    print("\n向量库初始化完成！")

if __name__ == "__main__":
    init_vector_db()
