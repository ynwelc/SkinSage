import json
from sqlalchemy.orm import Session
from app.database.db import SessionLocal, engine, Base
from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.models.product import Product
from app.database.vector_db import vector_db
from app.config.config import settings

# 创建数据库表Base.metadata.create_all(bind=engine)

# 初始化数据库
def init_database():
    """初始化数据库，导入初始数据"""
    db = SessionLocal()
    
    try:
        # 1. 检查是否已有管理员用户
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            # 创建默认管理员用户
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            admin_user = User(
                username="admin",
                password_hash=pwd_context.hash("admin123"),
                email="admin@example.com",
                role="manager",
                name="系统管理员"
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("创建了默认管理员用户")
        
        # 2. 检查是否已有示例产品
        product_count = db.query(Product).count()
        if product_count == 0:
            # 创建示例产品
            products = [
                Product(name="玻尿酸保湿精华", category="护肤品", description="深层保湿，提亮肤色", price=298.00),
                Product(name="瓷肌多肽修复套", category="修复产品", description="修复敏感肌，淡化痘印", price=598.00),
                Product(name="美白淡斑面膜", category="护肤品", description="美白淡斑，补水保湿", price=198.00)
            ]
            db.add_all(products)
            db.commit()
            print("创建了示例产品")
        
        # 3. 导入售后百问百答文档
        print("开始导入售后百问百答文档...")
        
        # 检查是否已有该文档
        document_title = "御可肤项目售后流程百问百答"
        existing_doc = db.query(Document).filter(Document.title == document_title).first()
        
        if not existing_doc:
            # 创建文档记录
            document = Document(
                title=document_title,
                filename="售后百问百答.md",
                file_path="d:/code/beauty-system/售后百问百答.md",
                file_size=os.path.getsize("d:/code/beauty-system/售后百问百答.md"),
                file_type="md",
                status="completed",
                created_by=admin_user.id
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            print(f"创建了文档记录：{document.title}")
        else:
            document = existing_doc
            print(f"文档已存在：{document.title}")
        
        # 4. 导入文档分块
        print("开始导入文档分块...")
        
        # 加载文档分块
        chunks_file = "d:/code/beauty-system/document_chunks.json"
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        # 检查是否已有文档分块
        existing_chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).count()
        if existing_chunks == 0:
            # 导入文档分块到数据库
            document_chunks = []
            vector_docs = []
            vector_metadatas = []
            vector_ids = []
            
            for i, chunk in enumerate(chunks):
                document_chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_content=chunk["chunk_content"],
                    chunk_index=i
                )
                document_chunks.append(document_chunk)
                
                # 准备向量库数据
                vector_docs.append(chunk["chunk_content"])
                vector_metadatas.append({
                    "category": chunk["category"],
                    "question": chunk["question"],
                    "chunk_index": i,
                    "start_index": chunk["start_index"],
                    "end_index": chunk["end_index"],
                    "document_id": document.id
                })
                vector_ids.append(f"chunk_{document.id}_{i}")
            
            # 批量添加到数据库
            db.add_all(document_chunks)
            db.commit()
            print(f"导入了 {len(document_chunks)} 个文档分块到数据库")
            
            # 添加到向量库
            vector_db.add_documents(vector_docs, vector_metadatas, vector_ids)
            print(f"导入了 {len(vector_docs)} 个文档分块到向量库")
        else:
            print(f"文档分块已存在，共 {existing_chunks} 个")
        
        print("数据库初始化完成！")
        
    except Exception as e:
        db.rollback()
        print(f"数据库初始化失败：{str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import os
    init_database()
