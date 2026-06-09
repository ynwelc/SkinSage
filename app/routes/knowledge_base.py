from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
from app.database.db import get_db

# 创建路由器
router = APIRouter()

# 响应模型
class KnowledgeBaseStats(BaseModel):
    total_documents: int
    total_chunks: int
    total_queries: int
    average_response_time: float

# 路由
@router.get("/stats", response_model=KnowledgeBaseStats, summary="获取知识库统计")
def get_knowledge_base_stats(db: Session = Depends(get_db)):
    """获取知识库统计信息"""
    from app.models.document import Document, DocumentChunk
    from app.models.query import QueryLog
    
    # 获取统计数据
    total_documents = db.query(Document).count()
    total_chunks = db.query(DocumentChunk).count()
    
    # 获取查询日志统计
    query_stats = db.query(
        QueryLog.id,
        QueryLog.response_time
    ).all()
    
    total_queries = len(query_stats)
    average_response_time = 0.0
    
    if total_queries > 0:
        total_response_time = sum(q.response_time for q in query_stats)
        average_response_time = total_response_time / total_queries
    
    return KnowledgeBaseStats(
        total_documents=total_documents,
        total_chunks=total_chunks,
        total_queries=total_queries,
        average_response_time=average_response_time
    )
