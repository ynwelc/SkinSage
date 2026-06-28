# 智能美容咨询助手

![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi)
![Vue 3](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?style=flat-square&logo=typescript)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)
![ChromaDB](https://img.shields.io/badge/ChromaDB-1.3+-FF6B6B?style=flat-square)
![DeepSeek](https://img.shields.io/badge/DeepSeek-V3.2-6366F1?style=flat-square)
![RAG](https://img.shields.io/badge/RAG-Enabled-10B981?style=flat-square)

> **一句话硬核总结**：基于 RAG 技术的美业垂类智能问答系统，从 PDF 语义切分、向量精准召回，到前端 Vue3 打字机流式渲染，一个人搞定了全栈闭环。

[![Bilibili](https://img.shields.io/badge/Bilibili-%E8%A7%86%E9%A2%91%E6%BC%94%E7%A4%BA-blue?style=flat-square&logo=bilibili)](https://www.bilibili.com/video/BV1QuEz65EHQ/)

### 效果演示视频
![效果演示视频](./beauty-fonted/demo-video/demo.gif)

---

## 背景与痛点分析

**为什么做这个系统？**

市面上的通用 LLM（GPT、Claude 等）虽然能力强大，但在**专业美业私域**场景下存在致命缺陷：

- **幻觉严重**：对美容专业知识一知半解，容易给出错误建议
- **缺乏垂类知识**：不懂美业术语、产品成分、护理流程等专业知识
- **无法溯源**：回答无法关联到具体的知识库文档，用户不敢信任
- **多轮对话断层**：无法记住用户肤质、历史咨询等上下文信息

**我的解决方案**：构建一个完整的 RAG（检索增强生成）系统，让 AI 基于企业私有知识库回答问题，实现**精准、可溯源、多轮连贯**的专业咨询服务。

从 PDF/Word 文档解析、语义分块策略设计、向量嵌入与检索，到后端流式响应、前端打字机效果渲染，**全部由一个人从零到一完成**。

---

## 架构设计

![SkinSage 系统架构图](picture/SkinSage系统架构图.png)

---

## 核心功能与亮点

### 1. 完整的 RAG 问答闭环

```
用户提问 → 向量检索 → 上下文构建 → LLM 生成 → 流式输出
```

- **精准召回**：使用 BGE-M3 嵌入模型（1024 维向量），在 ChromaDB 中进行语义相似度检索
- **上下文增强**：自动将检索到的 Top-K 文档片段注入 Prompt，让 AI 基于真实知识回答
- **可溯源引用**：每条回答都附带参考文档及相关度评分，用户可追溯知识来源

### 2. 智能文档处理管道

支持 **PDF / Word / Markdown** 三种格式，核心处理流程：

- **语义分块**：500 字/块 + 50 字重叠，保证语义完整性，避免关键信息被截断
- **自动向量化**：上传即入库，文档内容自动转换为向量并持久化到 ChromaDB
- **元数据管理**：保留文档分类、来源等元信息，支持按类别过滤检索

### 3. 多轮对话记忆

基于 LangChain 实现的对话历史管理：

- **会话隔离**：每个用户独立的对话历史，互不干扰
- **滑动窗口**：保留最近 20 轮对话，平衡上下文长度与响应质量
- **上下文注入**：历史对话自动注入 LLM Prompt，实现连贯的多轮咨询

### 4. 流式响应 + 打字机效果

**后端**：FastAPI `StreamingResponse` + SSE 协议，逐 Token 推送

**前端**：Vue 3 + Fetch Streams API，实时渲染 Markdown，实现丝滑的打字机效果

```typescript
// 前端核心流式处理逻辑
const reader = response.body?.getReader()
const decoder = new TextDecoder()

while (!done) {
  const { value, done: doneReading } = await reader.read()
  buffer += decoder.decode(value, { stream: true })
  
  for (const line of lines) {
    const event = JSON.parse(line)
    if (event.type === 'text_chunk') {
      fullResponse += event.content
      // 实时更新 UI
      messages.value[msgIndex].content = fullResponse
    }
  }
}
```

### 5. 安全认证体系

- **JWT Token**：基于 HS256 算法的无状态认证，Token 有效期 30 分钟
- **Bcrypt 加密**：密码使用 bcrypt 算法（12 轮）加密存储，抗彩虹表攻击
- **权限控制**：基于角色的访问控制（RBAC），支持管理员/普通用户角色

---

## 全栈技术栈总览

**Backend:** FastAPI + Python 3.10+ | SQLAlchemy + MySQL | ChromaDB（向量存储）| LangChain（对话管理）

**Frontend:** Vue 3 + TypeScript + Vite | Pinia（状态管理）| Axios + Fetch Streams（流式请求）

**AI/LLM:** 硅基流动 API（DeepSeek-V3.2）| BGE-M3 嵌入模型（1024 维）

**Security:** JWT + Bcrypt | CORS 中间件 | SQL 注入防护（SQLAlchemy ORM）

**DevOps:** Docker 容器化 | Uvicorn ASGI 服务器

---

## 核心业务时序图

### RAG 智能问答流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant Frontend as Vue3 前端
    participant QA_Route as QA 路由
    participant Embedding as Embedding 服务
    participant VectorDB as ChromaDB
    participant ChatService as Chat 服务
    participant LLM as DeepSeek API

    User->>Frontend: 输入问题并发送
    Frontend->>QA_Route: POST /api/qa<br/>{"query": "敏感肌如何选护肤品?",<br/>"user_id": 1, "n_results": 5}
    
    rect rgb(240, 248, 255)
        Note over QA_Route,VectorDB: 向量检索阶段
        QA_Route->>Embedding: get_embedding(query)
        Embedding->>LLM: 调用 BGE-M3 API
        LLM-->>Embedding: 返回 1024 维向量
        Embedding-->>QA_Route: vector: List[float]
        
        QA_Route->>VectorDB: search_similar(vector, n_results=5)
        VectorDB-->>QA_Route: {"documents": [...],<br/>"metadatas": [...],<br/>"distances": [...]}
    end
    
    rect rgb(255, 250, 240)
        Note over QA_Route,LLM: 流式生成阶段
        QA_Route->>ChatService: generate_response(messages, stream=True)
        ChatService->>LLM: POST /v1/chat/completions<br/>{"model": "DeepSeek-V3.2",<br/>"messages": [...], "stream": true}
        
        loop SSE 流式响应
            LLM-->>ChatService: data: {"choices": [{"delta": {"content": "..."}}]}
            ChatService-->>QA_Route: content chunk
            QA_Route-->>Frontend: {"type": "text_chunk",<br/>"content": "..."}
            Frontend->>Frontend: 实时渲染 Markdown<br/>打字机效果
        end
    end
    
    LLM-->>QA_Route: [DONE] 信号
    QA_Route->>QA_Route: 更新对话历史
    QA_Route->>QA_Route: 记录查询日志 QueryLog
    QA_Route-->>Frontend: {"type": "complete",<br/>"data": {"response_time": 1234,<br/>"related_docs": [...]}}
    Frontend-->>User: 展示完整回答及参考文档
```

### 文档处理冷启动流程

```mermaid
sequenceDiagram
    participant Admin as 管理员
    participant Doc_Route as Documents 路由
    participant Parser as DocumentParser
    participant Embedding as Embedding 服务
    participant VectorDB as ChromaDB
    participant MySQL as MySQL 数据库

    Admin->>Doc_Route: POST /api/documents<br/>上传 PDF/Word/Markdown
    Doc_Route->>Doc_Route: 保存文件到 uploads/
    
    Doc_Route->>Parser: parse_document(file_path)
    
    alt PDF 格式
        Parser->>Parser: pypdf.PdfReader<br/>提取所有页面文本
    else Word 格式
        Parser->>Parser: python-docx.Document<br/>提取所有段落
    else Markdown 格式
        Parser->>Parser: 直接读取文件内容
    end
    
    Parser-->>Doc_Route: parsed_doc: {"title": "...",<br/>"categories": [...]}
    
    Doc_Route->>Parser: chunk_document(parsed_doc,<br/>chunk_size=500, overlap=50)
    Parser-->>Doc_Route: chunks: [{"chunk_content": "...",<br/>"category": "护肤知识", ...}]
    
    Doc_Route->>Embedding: get_embeddings(chunks)
    Embedding-->>Doc_Route: embeddings: List[List[float]]
    
    Doc_Route->>VectorDB: add_documents(documents, metadatas, ids, embeddings)
    VectorDB-->>Doc_Route: success
    
    Doc_Route->>MySQL: 创建 Document 记录
    Doc_Route->>MySQL: 创建 DocumentChunk 记录
    
    Doc_Route-->>Admin: {"code": 200, "document_id": 1}
```

---

## 快速本地运行

### 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis（可选，用于缓存）

### 1. 克隆项目

```bash
git clone https://github.com/your-username/beauty-system.git
cd beauty-system
```

### 2. 后端配置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（创建 .env 文件）
cat > .env << EOF
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/beauty_assistant
SILICONFLOW_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
EOF

# 初始化数据库
python init_database.py

# 启动后端服务
python main.py
```

后端服务运行在 `http://localhost:8000`，API 文档访问 `http://localhost:8000/docs`

### 3. 前端配置

```bash
cd beauty-fonted

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务运行在 `http://localhost:5173`

### 4. 初始化知识库

```bash
# 回到项目根目录
cd ..

# 初始化向量数据库
python init_vector_db.py
```

### 一键启动（Docker）

```bash
# 构建镜像
docker build -t beauty-assistant .

# 运行容器
docker run -d -p 8000:8000 -p 5173:5173 beauty-assistant
```

---

## 安全与性能指标

### 安全性

| 安全措施 | 实现细节 |
|---------|---------|
| 密码加密 | Bcrypt 算法，12 轮加密，抗彩虹表攻击 |
| 身份认证 | JWT Token（HS256），30 分钟有效期 |
| SQL 注入防护 | SQLAlchemy ORM 参数化查询 |
| CORS 配置 | 支持跨域，生产环境建议配置白名单 |
| 密码长度限制 | Bcrypt 72 字节限制，自动截断处理 |

### 性能优化

| 优化点 | 实现细节 |
|-------|---------|
| 流式响应 | SSE 协议，首字延迟 < 1s |
| 向量检索 | ChromaDB + HNSW 索引，检索延迟 < 500ms |
| 对话历史 | 滑动窗口（20 轮），避免 Prompt 过长 |
| 前端渲染 | Vue 3 响应式 + 虚拟滚动，流畅渲染长对话 |
| 向量维度 | BGE-M3（1024 维），平衡精度与存储 |

---

## 技术亮点总结

1. **RAG 全栈闭环**：从文档解析、向量入库、语义检索到流式生成，完整实现 RAG 架构
2. **智能分块策略**：500 字分块 + 50 字重叠，保证语义完整性，避免关键信息截断
3. **流式响应架构**：后端 SSE + 前端 Streams API，实现丝滑的打字机效果
4. **多轮对话记忆**：LangChain 管理对话历史，滑动窗口策略平衡上下文长度
5. **安全认证体系**：JWT + Bcrypt 完整的用户认证方案
6. **向量检索优化**：BGE-M3 嵌入模型 + ChromaDB，检索延迟 < 500ms

---

**如果这个项目对你有帮助，请给个支持的 Star！谢谢** ⭐️