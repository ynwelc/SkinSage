from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from pydantic import BaseModel
import os
import shutil
import tempfile
from app.database.db import get_db
from app.models.document import Document, DocumentChunk
from app.models.user import User

# 尝试导入DocumentParser，如果失败则标记为None
DocumentParser: Optional[Any] = None
try:
    from parse_document import DocumentParser
    print("✅ DocumentParser 导入成功")
except ImportError as e:
    print(f"⚠️ DocumentParser 导入失败: {e}")
    print("⚠️ 文档上传功能将无法使用")

# 创建路由器
router = APIRouter()

# 响应模型
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    title: str
    filename: str
    file_size: int
    file_type: str
    status: str
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_content: str
    chunk_index: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 请求模型
class DocumentCreate(BaseModel):
    title: str
    filename: str
    file_path: str
    file_size: int
    file_type: str
    status: str

# 路由
@router.get("", response_model=List[DocumentResponse], summary="获取文档列表")
def get_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取文档列表"""
    documents = db.query(Document).offset(skip).limit(limit).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse, summary="获取文档详情")
def get_document(document_id: int, db: Session = Depends(get_db)):
    """获取文档详情"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    return document

@router.get("/{document_id}/chunks", response_model=List[DocumentChunkResponse], summary="获取文档分块")
def get_document_chunks(document_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取文档分块"""
    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).offset(skip).limit(limit).all()
    return chunks

@router.post("", summary="上传文档")
def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    category: str = Form(None),
    db: Session = Depends(get_db)
):
    """上传文档，支持PDF、Word、Markdown格式"""
    try:
        # 检查DocumentParser是否可用
        if DocumentParser is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="文档解析服务不可用，请联系管理员"
            )
        
        # 创建上传目录
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_ext = os.path.splitext(file.filename)[1].lower()
        temp_path = os.path.join(tempfile.gettempdir(), file.filename)
        final_path = os.path.join(upload_dir, file.filename)
        
        # 保存文件到临时路径
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 移动到最终路径
        shutil.move(temp_path, final_path)
        
        # 解析文档
        parser = DocumentParser()
        output_file = os.path.join(upload_dir, f"{os.path.splitext(file.filename)[0]}_chunks.json")
        parser.run(final_path, output_file)
        
        # 获取文件信息
        file_size = os.path.getsize(final_path)
        file_type = file_ext[1:]  # 去除点号
        document_title = title or file.filename
        
        # 创建文档记录
        document = Document(
            title=document_title,
            filename=file.filename,
            file_path=final_path,
            file_size=file_size,
            file_type=file_type,
            status="completed",
            created_by=1  # 默认用户ID，实际应从认证中获取
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # 读取分块结果并保存到数据库
        import json
        with open(output_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        
        for i, chunk in enumerate(chunks):
            doc_chunk = DocumentChunk(
                document_id=document.id,
                chunk_content=chunk["chunk_content"],
                chunk_index=i
            )
            db.add(doc_chunk)
        
        db.commit()
        
        # 清理临时文件
        os.remove(output_file)
        
        return {
            "code": 200,
            "data": {
                "document_id": document.id,
                "title": document.title,
                "filename": document.filename,
                "status": document.status
            },
            "msg": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"文档上传错误: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档上传失败: {str(e)}"
        )

@router.post("/create", response_model=DocumentResponse, summary="创建文档记录")
def create_document(document: DocumentCreate, db: Session = Depends(get_db)):
    """创建文档记录"""
    db_document = Document(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.get("/chunks", response_model=List[DocumentChunkResponse], summary="获取所有文档分块")
def get_all_chunks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取数据库中所有文档的分块，支持分页"""
    chunks = db.query(DocumentChunk).offset(skip).limit(limit).all()
    return chunks

@router.delete("/{document_id}", summary="删除文档")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """删除文档"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    
    # 删除文件
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # 删除关联的文档分块
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
    
    # 删除文档
    db.delete(document)
    db.commit()
    
    return {"message": "文档删除成功"}
