from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Generator, Optional
import time
import json
from app.database.db import get_db
from app.database.vector_db import vector_db
from app.services.chat_service import chat_service
from app.services.langchain_chat_service import langchain_chat_service
from app.models.query import QueryLog

# 创建路由器
router = APIRouter()

# 请求模型
class QARequest(BaseModel):
    query: str
    user_id: int | None = None
    n_results: int = 5

class ClearHistoryRequest(BaseModel):
    user_id: int

# 响应模型
class RelatedDocument(BaseModel):
    document_id: int
    title: str
    relevance_score: float

class RelatedProduct(BaseModel):
    id: int
    name: str
    price: float

class Message(BaseModel):
    role: str
    content: str

class QAResponse(BaseModel):
    response: str
    response_time: int
    related_docs: List[dict]
    related_products: List[dict]
    conversation_history: List[Dict[str, str]]

# 路由
@router.post("/", summary="智能问答")
def qa(request: QARequest, db: Session = Depends(get_db)):
    """智能问答服务，支持流式输出"""
    
    def generate_stream() -> Generator[str, None, None]:
        """生成流式响应的内容"""
        start_time = time.time()
        user_id = request.user_id or 0
        full_response = ""
        
        try:
            # 1. 执行向量检索
            results = vector_db.search_similar(request.query, n_results=request.n_results)
            
            # 构建相关文档
            related_docs = []
            if results and results["metadatas"] and results["metadatas"][0]:
                for i, metadata in enumerate(results["metadatas"][0]):
                    related_docs.append({
                        "document_id": i + 1,
                        "title": metadata.get("category", "未知分类"),
                        "relevance_score": 1 - results["distances"][0][i] if results["distances"] and results["distances"][0] else 0
                    })
            
            # 构建上下文信息
            context = ""
            if results and results["documents"] and results["documents"][0]:
                for doc in results["documents"][0]:
                    context += f"{doc}\n\n"
            
            # 2. 构建消息列表
            messages = []
            if context:
                messages.append({
                    "role": "system",
                    "content": f"上下文信息：\n{context}"
                })
            
            # 添加历史对话
            history = langchain_chat_service.get_or_create_conversation(user_id)
            for msg in history:
                messages.append(msg)
            
            # 添加当前查询
            messages.append({
                "role": "user",
                "content": request.query
            })
            
            # 3. 调用ChatService生成智能回答（流式）
            response_generator = chat_service.generate_response(messages, stream=True)
            
            if isinstance(response_generator, Generator):
                # 流式生成回答
                for content in response_generator:
                    full_response += content
                    # 封装成前端需要的格式，只需要提取content字段
                    yield json.dumps({
                        "content": content,
                        "type": "text_chunk"
                    }) + "\n"
            else:
                # 非流式回退
                if not response_generator:
                    response_generator = "抱歉，我暂时无法回答这个问题，请联系客服。"
                full_response = response_generator
                yield json.dumps({
                    "content": full_response,
                    "type": "text_chunk"
                }) + "\n"
            
            # 4. 更新对话历史
            langchain_chat_service.add_message_to_history(user_id, "user", request.query)
            langchain_chat_service.add_message_to_history(user_id, "assistant", full_response)
            
            # 5. 记录查询日志
            response_time = int((time.time() - start_time) * 1000)
            query_log = QueryLog(
                user_id=request.user_id,
                query_content=request.query,
                response_content=full_response,
                response_time=response_time
            )
            db.add(query_log)
            db.commit()
            
            # 6. 输出相关文档和产品信息（可选，前端可以选择使用）
            related_products = [
                {"id": 1, "name": "玻尿酸保湿精华", "price": 298.00},
                {"id": 2, "name": "瓷肌多肽修复套", "price": 598.00}
            ]
            
            # 获取对话历史
            conversation_history = langchain_chat_service.get_conversation_history(user_id)
            
            # 7. 结束信号
            yield json.dumps({
                "type": "complete",
                "data": {
                    "response_time": response_time,
                    "related_docs": related_docs,
                    "related_products": related_products,
                    "conversation_history": conversation_history
                },
                "code": 200
            }) + "\n"
            
        except Exception as e:
            # 流式输出错误信息
            yield json.dumps({
                "type": "error",
                "message": f"问答服务异常: {str(e)}",
                "code": 500
            }) + "\n"
    
    # 返回流式响应
    return StreamingResponse(
        generate_stream(),
        media_type="application/json",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@router.post("/clear-history", summary="清空对话历史")
def clear_history(request: ClearHistoryRequest):
    """清空指定用户的对话历史"""
    try:
        langchain_chat_service.clear_conversation_history(request.user_id)
        return {"message": "对话历史已清空"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清空对话历史失败: {str(e)}"
        )

@router.get("/history/{user_id}", summary="获取对话历史")
def get_history(user_id: int):
    """获取指定用户的对话历史"""
    try:
        history = langchain_chat_service.get_conversation_history(user_id)
        return {"conversation_history": history}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取对话历史失败: {str(e)}"
        )

@router.get("/history", summary="获取问答历史记录")
def get_qa_history(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
):
    """获取系统问答历史记录，支持分页和过滤"""
    try:
        # 构建查询
        query = db.query(QueryLog)
        
        # 过滤用户ID
        if user_id is not None:
            query = query.filter(QueryLog.user_id == user_id)
        
        # 注意：当前QueryLog模型中没有session_id字段，所以忽略该过滤条件
        if session_id is not None:
            print(f"警告：查询参数session_id已提供，但QueryLog模型中没有该字段，将忽略该过滤条件")
        
        # 过滤日期范围
        if start_date is not None:
            from datetime import datetime
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(QueryLog.created_at >= start_datetime)
        
        if end_date is not None:
            from datetime import datetime, timedelta
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(QueryLog.created_at < end_datetime)
        
        # 按创建时间倒序
        query = query.order_by(QueryLog.created_at.desc())
        
        # 计算总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        items = query.all()
        
        # 格式化结果
        formatted_items = []
        for item in items:
            formatted_items.append({
                "id": item.id,
                "user_id": item.user_id,
                "query": item.query_content,
                "response": item.response_content,
                "response_time": item.response_time,
                "session_id": "",  # 由于模型中没有该字段，返回空字符串
                "created_at": item.created_at.isoformat()
            })
        
        # 构建返回结果
        return {
            "code": 200,
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": formatted_items
            },
            "msg": "success"
        }
        
    except ValueError as e:
        # 日期格式错误
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"参数错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取问答历史记录失败: {str(e)}"
        )
