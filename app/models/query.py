from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.database.db import Base

class QueryLog(Base):
    """查询日志模型"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query_content = Column(Text, nullable=False)
    response_content = Column(Text, nullable=False)
    response_time = Column(Integer, nullable=False, comment="响应时间（毫秒）")
    relevance_score = Column(Float, nullable=True, comment="相关度评分")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
