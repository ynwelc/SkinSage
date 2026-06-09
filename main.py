from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 导入路由
from app.routes import auth, documents, qa, knowledge_base, analytics

# 创建FastAPI应用
app = FastAPI(
    title="智能美容咨询助手API",
    description="基于RAG技术的智能美容咨询助手后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应配置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(documents.router, prefix="/api/documents", tags=["文档管理"])
app.include_router(qa.router, prefix="/api/qa", tags=["问答服务"])
app.include_router(knowledge_base.router, prefix="/api/knowledge-base", tags=["知识库管理"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["统计分析"])

# 根路径
@app.get("/")
def root():
    return {
        "message": "智能美容咨询助手API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
