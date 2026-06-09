from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, date
from app.database.db import get_db

# 创建路由器
router = APIRouter()

# 响应模型
class UsageStats(BaseModel):
    total_queries: int
    average_response_time: float
    accuracy_rate: float
    daily_stats: List[Dict[str, Any]]

class HotQuery(BaseModel):
    query: str
    count: int

# 路由
@router.get("/usage", summary="获取使用统计")
def get_usage_stats(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """获取使用统计"""
    from app.models.query import QueryLog
    
    # 构建查询
    query = db.query(QueryLog)
    
    # 添加日期过滤
    if start_date:
        query = query.filter(QueryLog.created_at >= start_date)
    if end_date:
        # 添加一天，确保包含结束日期
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(QueryLog.created_at <= end_datetime)
    
    # 获取所有查询日志
    query_logs = query.all()
    
    # 计算统计数据
    total_queries = len(query_logs)
    average_response_time = 0.0
    accuracy_rate = 0.0
    
    if total_queries > 0:
        total_response_time = sum(log.response_time for log in query_logs)
        average_response_time = total_response_time / total_queries
        
        # 计算准确率（假设relevance_score >= 0.8为准确）
        accurate_queries = [log for log in query_logs if log.relevance_score and log.relevance_score >= 0.8]
        accuracy_rate = len(accurate_queries) / total_queries
    
    # 计算每日统计
    daily_stats = {}
    for log in query_logs:
        log_date = log.created_at.date()
        if log_date not in daily_stats:
            daily_stats[log_date] = {
                "date": log_date.isoformat(),
                "queries": 0,
                "response_time": 0
            }
        daily_stats[log_date]["queries"] += 1
        daily_stats[log_date]["response_time"] += log.response_time
    
    # 计算每日平均响应时间
    for stat in daily_stats.values():
        if stat["queries"] > 0:
            stat["response_time"] = stat["response_time"] / stat["queries"]
    
    return {
        "code": 200,
        "data": {
            "total_queries": total_queries,
            "average_response_time": average_response_time,
            "accuracy_rate": accuracy_rate,
            "daily_stats": list(daily_stats.values())
        },
        "msg": "success"
    }

@router.get("/hot-queries", summary="获取热门查询")
def get_hot_queries(
    limit: int = 10,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """获取热门查询"""
    try:
        from app.models.query import QueryLog
        
        # 构建查询，添加query_content不为空的过滤条件
        from sqlalchemy import desc
        
        # 给count函数结果起一个明确的别名
        count_alias = func.count(QueryLog.id).label("count_result")
        
        query = db.query(
            QueryLog.query_content,
            count_alias
        ).filter(QueryLog.query_content.isnot(None))
        
        # 添加日期过滤
        if start_date:
            query = query.filter(QueryLog.created_at >= start_date)
        if end_date:
            # 添加一天，确保包含结束日期
            end_datetime = datetime.combine(end_date, datetime.max.time())
            query = query.filter(QueryLog.created_at <= end_datetime)
        
        # 分组并排序，使用正确的desc语法
        hot_queries = query.group_by(QueryLog.query_content)
        hot_queries = hot_queries.order_by(desc(count_alias))
        hot_queries = hot_queries.limit(limit)
        hot_queries = hot_queries.all()
        
        # 转换为响应模型，确保query_content是字符串类型
        hot_queries_list = [
            HotQuery(query=str(q.query_content), count=q.count_result).dict()
            for q in hot_queries
        ]
        
        # 返回与其他接口一致的格式，包含code、data和msg字段
        return {
            "code": 200,
            "data": hot_queries_list,
            "msg": "success"
        }
    except Exception as e:
        print(f"获取热门查询失败: {e}")
        import traceback
        traceback.print_exc()
        # 返回与其他接口一致的错误格式
        return {
            "code": 500,
            "data": [],
            "msg": f"获取热门查询失败: {str(e)}"
        }
