<template>
  <div class="chat-container">
    <div class="chat-history" ref="chatHistoryRef">
      <!-- 消息列表 -->
      <div 
        v-for="(message, index) in messages" 
        :key="message.id || index"
        class="message-item" 
        :class="message.sender === 'ai' ? 'ai-message' : 'user-message'"
      >
        <!-- AI消息 -->
        <template v-if="message.sender === 'ai'">
          <div class="ai-message-header">
            <div class="ai-avatar">AI</div>
            <span class="ai-label">AI</span>
            <span v-if="message.isLoading" class="loading-indicator">⏳</span>
          </div>
          <div class="message-bubble ai-bubble" v-html="renderMarkdown(message.content)"></div>
          
          <!-- 显示相关文档 -->
          <div 
            v-if="message.related_docs && filteredDocs(message.related_docs).length > 0" 
            class="related-docs"
          >
            <div 
              class="related-docs-header"
              @click="toggleDocs(message)"
            >
              <div class="related-docs-title">📚 参考文档</div>
              <div class="related-docs-toggle">
                {{ message.isDocsExpanded ? '▼' : '▶' }}
              </div>
            </div>
            
            <div 
              v-if="message.isDocsExpanded" 
              class="related-docs-list"
            >
              <div 
                v-for="(doc, index) in filteredDocs(message.related_docs)" 
                :key="index"
                class="related-doc-item"
              >
                <div class="related-doc-title">{{ doc.title }}</div>
                <div class="related-doc-score">相关度: {{ (doc.relevance_score * 100).toFixed(1) }}%</div>
              </div>
            </div>
          </div>
        </template>
        
        <!-- 用户消息 -->
        <template v-else>
          <div class="user-message-header">
            <span class="user-label">U</span>
            <div class="user-avatar">U</div>
          </div>
          <div class="message-bubble user-bubble">{{ message.content }}</div>
        </template>
      </div>
      
      <!-- 滚动到底部的标记 -->
      <div ref="scrollToBottomMarker"></div>
    </div>
    
    <!-- 输入区域 -->
    <div class="input-container">
      <div class="input-wrapper">
        <input 
          type="text" 
          v-model="inputMessage" 
          @keyup.enter="sendMessage" 
          placeholder="请输入您的问题..." 
          :disabled="loading"
          class="input-field"
        >
        <button 
          class="send-btn" 
          @click="sendMessage" 
          :disabled="!inputMessage.trim() || loading"
        >
          <span v-if="loading">发送中...</span>
          <span v-else>发送</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { marked } from 'marked'

// 聊天消息类型
interface ChatMessage {
  id: number
  content: string
  sender: 'user' | 'ai'
  isLoading?: boolean
  related_docs?: RelatedDoc[]
  isDocsExpanded?: boolean
}

// 相关文档类型
interface RelatedDoc {
  document_id: number
  title: string
  relevance_score: number
}



const messages = ref<ChatMessage[]>([
  {
    id: 1,
    content: '你好！我是美容AI助手，有什么可以帮助你的吗？',
    sender: 'ai'
  }
])

const inputMessage = ref('')

// 相关文档
const relatedDocs = ref<RelatedDoc[]>([])

// 加载状态
const loading = ref(false)

// 滚动相关的ref
const scrollToBottomMarker = ref<HTMLElement | null>(null)

// 滚动到底部的函数
const scrollToBottom = () => {
  nextTick(() => {
    scrollToBottomMarker.value?.scrollIntoView({
      behavior: 'smooth',
      block: 'end'
    })
  })
}

// 监听消息变化，自动滚动到底部
watch(messages, () => {
  scrollToBottom()
}, { deep: true })

// 组件挂载时滚动到底部
onMounted(() => {
  scrollToBottom()
})

// Markdown渲染函数
const renderMarkdown = (content: string) => {
  if (!content) return ''
  // 处理特殊字符和格式
  let processedContent = content
    .replace(/\r\n/g, '\n') // 统一换行符
    .replace(/\n\n/g, '\n\n') // 确保段落分隔
  
  return marked(processedContent)
}

// 切换参考文档展开/折叠状态
const toggleDocs = (message: ChatMessage) => {
  message.isDocsExpanded = !message.isDocsExpanded
}

// 过滤参考文档，只显示相似度大于等于25%的文档
const filteredDocs = (docs: RelatedDoc[]) => {
  if (!docs) return []
  return docs.filter(doc => {
    const score = doc.relevance_score * 100
    return score >= 25
  })
}

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message) return

  // 添加用户消息
  messages.value.push({
    id: Date.now(),
    content: message,
    sender: 'user'
  })

  // 自动滚动到底部
  scrollToBottom()

  // 清空输入框
  inputMessage.value = ''

  // 创建AI回复消息（初始为空）
  const aiMessageId = Date.now() + 1
  const aiMessage: ChatMessage = {
    id: aiMessageId,
    content: '',
    sender: 'ai',
    isLoading: true,
    isDocsExpanded: false
  }
  messages.value.push(aiMessage)

  try {
    // 设置加载状态
    loading.value = true
    
    // 使用fetch API调用后端流式接口
    const response = await fetch('http://localhost:8000/api/qa', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: message,
        user_id: 1,
        n_results: 3
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    // 获取响应的可读流
    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('No readable stream in response')
    }

    // 解析流式数据
    const decoder = new TextDecoder()
    let done = false
    let fullResponse = ''
    let buffer = ''
    let relatedDocsData: RelatedDoc[] = []

    while (!done) {
      const { value, done: doneReading } = await reader.read()
      done = doneReading
      if (value) {
        buffer += decoder.decode(value, { stream: true })
        
        // 按行分割，处理每个JSON事件
        const lines = buffer.split('\n')
        // 保存最后一行（可能不完整），处理其余完整行
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.trim()) {
            try {
              // 解析单个JSON事件
              const event = JSON.parse(line)
              
              // 处理不同类型的事件
              switch (event.type) {
                case 'text_chunk':
                  // 添加文本片段到完整响应
                  if (event.content) {
                    fullResponse += event.content
                    // 更新AI消息的内容
                    const msgIndex = messages.value.findIndex(m => m.id === aiMessageId)
                    if (msgIndex !== -1 && messages.value[msgIndex]) {
                      messages.value[msgIndex].content = fullResponse
                    }
                    // 滚动到底部
                    scrollToBottom()
                  }
                  break
                
                case 'complete':
                  // 处理完成信号
                  if (event.data && event.data.related_docs) {
                    relatedDocsData = event.data.related_docs
                    // 更新AI消息的related_docs字段
                    const msgIndex = messages.value.findIndex(m => m.id === aiMessageId)
                    if (msgIndex !== -1 && messages.value[msgIndex]) {
                      messages.value[msgIndex].related_docs = relatedDocsData
                    }
                  }
                  // 可以在这里处理related_products和conversation_history
                  break
                
                case 'error':
                  // 处理错误信息
                  console.error('流式响应错误:', event.message)
                  // 更新AI消息为错误提示
                  const msgIndex = messages.value.findIndex(m => m.id === aiMessageId)
                  if (msgIndex !== -1 && messages.value[msgIndex]) {
                    messages.value[msgIndex].content = `抱歉，处理请求时发生错误：${event.message}`
                  }
                  break
                
                default:
                  console.warn('未知的流式事件类型:', event.type)
              }
            } catch (e) {
              console.error('解析流式数据失败:', e)
            }
          }
        }
      }
    }
    
    // 处理缓冲区中剩余的最后一行（如果有）
    if (buffer.trim()) {
      try {
        const event = JSON.parse(buffer)
        if (event.type === 'text_chunk' && event.content) {
          fullResponse += event.content
          const msgIndex = messages.value.findIndex(m => m.id === aiMessageId)
          if (msgIndex !== -1 && messages.value[msgIndex]) {
            messages.value[msgIndex].content = fullResponse
          }
          scrollToBottom()
        }
      } catch (e) {
        console.error('解析最后一行流式数据失败:', e)
      }
    }

    // 标记AI消息为加载完成
    const msgIndex = messages.value.findIndex(m => m.id === aiMessageId)
    if (msgIndex !== -1 && messages.value[msgIndex]) {
      messages.value[msgIndex].isLoading = false
    }
    
    // 更新推荐产品（如果有）
    if (relatedDocsData.length > 0) {
      relatedDocs.value = relatedDocsData
    }
  } catch (error) {
    console.error('Error sending message:', error)
    // 更新AI消息为错误提示
    const msgIndex = messages.value.findIndex(m => m.id === Date.now() + 1)
    if (msgIndex !== -1) {
      messages.value[msgIndex] = {
        id: Date.now() + 1,
        content: '抱歉，暂时无法回复您的问题，请稍后再试。',
        sender: 'ai',
        isLoading: false
      }
    } else {
      // 如果消息不存在，添加新消息
      messages.value.push({
        id: Date.now() + 1,
        content: '抱歉，暂时无法回复您的问题，请稍后再试。',
        sender: 'ai'
      })
    }
  } finally {
    // 清除加载状态
    loading.value = false
    // 滚动到底部
    scrollToBottom()
  }
}


</script>

<style scoped>
/* 对话界面 */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #e9eaeb;
  overflow: hidden;
}

/* 聊天历史 */
.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background-color: #111827;
}

/* 消息项 */
.message-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0;
}

/* AI消息 */
.ai-message {
  justify-content: flex-start;
  flex-direction: column;
  gap: 0.5rem;
}

.ai-message-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.ai-avatar {
  width: 24px;
  height: 24px;
  border-radius: 0.375rem;
  background-color: #6366f1;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.ai-label {
  color: #6366f1;
  font-size: 0.75rem;
  font-weight: 600;
}

.loading-indicator {
  margin-left: 0.5rem;
  animation: spin 1s linear infinite;
  font-size: 0.75rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 相关文档样式 */
.related-docs {
  margin-top: 0.75rem;
  background-color: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 0.75rem;
  width: 25%;
  align-self: flex-start;
  overflow: hidden;
}

/* 相关文档头部 */
.related-docs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: rgba(99, 102, 241, 0.15);
}

.related-docs-header:hover {
  background-color: rgba(99, 102, 241, 0.25);
}

.related-docs-title {
  font-weight: 600;
  color: #6366f1;
  font-size: 0.875rem;
  margin-bottom: 0;
}

.related-docs-toggle {
  color: #94a3b8;
  font-size: 0.75rem;
  transition: transform 0.2s ease;
}

/* 相关文档列表 */
.related-docs-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background-color: rgba(15, 23, 42, 0.3);
}

.related-doc-item {
  background-color: rgba(15, 23, 42, 0.5);
  border-radius: 0.5rem;
  padding: 0.75rem;
  border: 1px solid rgba(71, 85, 105, 0.5);
  transition: all 0.2s ease;
}

.related-doc-item:hover {
  background-color: rgba(15, 23, 42, 0.7);
  border-color: rgba(99, 102, 241, 0.5);
}

.related-doc-title {
  font-weight: 500;
  color: #cbd5e1;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
}

.related-doc-score {
  font-size: 0.75rem;
  color: #94a3b8;
}

/* 用户消息 */
.user-message {
  justify-content: flex-end;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.user-message-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.user-avatar {
  width: 24px;
  height: 24px;
  border-radius: 0.375rem;
  background-color: #8b5cf6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.user-label {
  color: #8b5cf6;
  font-size: 0.75rem;
  font-weight: 600;
}

/* 消息气泡 */
.message-bubble {
  max-width: 75%;
  padding: 0.875rem 1.125rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  line-height: 1.5;
  word-wrap: break-word;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

/* 消息气泡 */
.ai-bubble {
  background-color: #1f2937;
  color: #e5e7eb;
  border: 1px solid #374151;
  border-radius: 0.75rem;
  align-self: flex-start;
}

/* Markdown 样式 */
.ai-bubble h1,
.ai-bubble h2,
.ai-bubble h3,
.ai-bubble h4,
.ai-bubble h5,
.ai-bubble h6 {
  color: #e5e7eb;
  margin-top: 1.25rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  line-height: 1.25;
}

.ai-bubble h1 {
  font-size: 1.875rem;
}

.ai-bubble h2 {
  font-size: 1.5rem;
}

.ai-bubble h3 {
  font-size: 1.25rem;
  color: #6366f1;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.ai-bubble p {
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

.ai-bubble strong {
  font-weight: 600;
  color: #6366f1;
}

.ai-bubble ul,
.ai-bubble ol {
  margin-left: 1.5rem;
  margin-bottom: 0.75rem;
}

.ai-bubble li {
  margin-bottom: 0.25rem;
  line-height: 1.6;
}

.ai-bubble hr {
  margin: 1.5rem 0;
  border: 0;
  border-top: 1px solid #374151;
}

.ai-bubble blockquote {
  border-left: 3px solid #6366f1;
  padding-left: 1rem;
  margin: 0.75rem 0;
  color: #9ca3af;
  font-style: italic;
}

.ai-bubble code {
  background-color: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.ai-bubble pre {
  background-color: rgba(30, 41, 59, 0.8);
  border: 1px solid #374151;
  border-radius: 0.5rem;
  padding: 0.75rem;
  overflow-x: auto;
  margin-bottom: 0.75rem;
}

.ai-bubble pre code {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
  display: block;
  white-space: pre;
}

/* 用户气泡 */
.user-bubble {
  background-color: #8b5cf6;
  color: #ffffff;
  border-radius: 0.75rem;
  align-self: flex-end;
}

/* 输入区域 */
.input-container {
  padding: 1.5rem 2rem;
  background-color: #111827;
  border-top: 1px solid #374151;
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  background-color: #1f2937;
  border-radius: 0.75rem;
  padding: 0.75rem 1rem;
  border: 1px solid #374151;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.input-field {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #e5e7eb;
  font-size: 0.875rem;
  padding: 0.5rem 0;
}

.input-field::placeholder {
  color: #9ca3af;
}

/* 发送按钮 */
.send-btn {
  padding: 0.625rem 1.25rem;
  background-color: #6366f1;
  color: #ffffff;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px 0 rgba(99, 102, 241, 0.3);
}

.send-btn:hover:not(:disabled) {
  background-color: #4f46e5;
  box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.4);
  transform: translateY(-1px);
}

.send-btn:disabled {
  background-color: #4b5563;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

/* 滚动条样式 */
.chat-history::-webkit-scrollbar {
  width: 8px;
}

.chat-history::-webkit-scrollbar-track {
  background: #111827;
}

.chat-history::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 4px;
}

.chat-history::-webkit-scrollbar-thumb:hover {
  background: #4b5563;
}

/* 响应式布局 - 移动端 */
@media (max-width: 768px) {
  .chat-history {
    padding: 1rem;
    gap: 1rem;
  }

  .message-bubble {
    max-width: 85%;
    padding: 0.75rem;
    font-size: 0.8125rem;
  }

  .input-container {
    padding: 1rem;
  }

  .input-wrapper {
    padding: 0.625rem 0.875rem;
  }

  .send-btn {
    padding: 0.5rem 1rem;
    font-size: 0.8125rem;
  }
}
</style>