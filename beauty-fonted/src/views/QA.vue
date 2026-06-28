<template>
  <div class="qa-wrapper">
    <!-- 侧边栏：历史会话 -->
    <div class="qa-sidebar" :class="{ 'open': isSidebarOpen }">
      <div class="qa-sidebar-header">
        <h3 class="qa-sidebar-title">历史对话</h3>
        <button class="close-sidebar-btn" @click="toggleSidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="close-icon"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
      <div class="qa-sidebar-content">
        <div v-if="historyLoading" class="qa-sidebar-status">加载中...</div>
        <div v-else-if="sessions.length === 0" class="qa-sidebar-status">暂无历史对话</div>
        <div 
          v-else
          v-for="(session, index) in sessions"
          :key="index"
          class="qa-session-item"
          @click="loadSession(session)"
        >
          <div class="qa-session-title">{{ session.title }}</div>
          <div class="qa-session-time">{{ formatDate(session.created_at) }}</div>
        </div>
      </div>
    </div>
    
    <div class="qa-overlay" v-if="isSidebarOpen" @click="toggleSidebar"></div>

    <div class="chat-container">
      <div class="chat-header">
        <button class="open-history-btn" @click="toggleSidebar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="history-icon"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
          历史记录
        </button>
        <button class="new-chat-btn" @click="startNewChat">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="new-chat-icon"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          新对话
        </button>
      </div>
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
            <img src="/beauty-ai-logo.svg?v=2" alt="AI" class="ai-avatar-img">
            <span class="ai-label">SkinSage AI</span>
            <span v-if="message.isLoading" class="loading-indicator">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </span>
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
              <div class="related-docs-title">✧ 参考文档</div>
              <div class="related-docs-toggle">
                {{ message.isDocsExpanded ? '收起' : '展开' }}
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
            <span class="user-label">我</span>
            <div class="user-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 1rem; height: 1rem;"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            </div>
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
          placeholder="输入您的美容咨询问题..." 
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import { marked } from 'marked'
import gsap from 'gsap'
import axios from 'axios'

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
    content: '你好！我是您的私人美容顾问 SkinSage。有什么关于护肤、成分或护理流程的问题可以帮助您？',
    sender: 'ai'
  }
])

const inputMessage = ref('')
const relatedDocs = ref<RelatedDoc[]>([])
const loading = ref(false)
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

// 侧边栏及历史状态
const isSidebarOpen = ref(false)
const historyLoading = ref(false)
const sessions = ref<any[]>([])

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
  if (isSidebarOpen.value && sessions.value.length === 0) {
    fetchHistory()
  }
}

const fetchHistory = async () => {
  historyLoading.value = true
  try {
    const response = await axios.get('http://localhost:8000/api/qa/history', {
      params: { user_id: 1, page: 1, page_size: 100 }
    })
    if (response.data && response.data.code === 200) {
      let items = response.data.data.items
      items.sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      
      const grouped: any[] = []
      let currentGroup: any[] = []
      const TEN_MINUTES = 10 * 60 * 1000
      
      items.forEach((item: any) => {
        if (currentGroup.length === 0) {
          currentGroup.push(item)
        } else {
          const firstTime = new Date(currentGroup[0].created_at).getTime()
          const currTime = new Date(item.created_at).getTime()
          if (firstTime - currTime <= TEN_MINUTES) {
            currentGroup.push(item)
          } else {
            grouped.push(currentGroup)
            currentGroup = [item]
          }
        }
      })
      if (currentGroup.length > 0) grouped.push(currentGroup)
      
      sessions.value = grouped.map(group => {
        const sorted = [...group].sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
        const msgs: ChatMessage[] = []
        sorted.forEach((item: any, idx: number) => {
          msgs.push({ id: Number(`1${item.id}`), content: item.query, sender: 'user' })
          msgs.push({ id: Number(`2${item.id}`), content: item.response, sender: 'ai' })
        })
        return {
          id: group[0].id,
          title: group[group.length - 1].query || '新对话',
          created_at: group[0].created_at,
          messages: msgs
        }
      })
    }
  } catch (err) {
    console.error(err)
  } finally {
    historyLoading.value = false
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const loadSession = (session: any) => {
  messages.value = session.messages
  isSidebarOpen.value = false
  scrollToBottom()
}

const startNewChat = () => {
  messages.value = [{
    id: Date.now(),
    content: '你好！我是您的私人美容顾问 SkinSage。有什么关于护肤、成分或护理流程的问题可以帮助您？',
    sender: 'ai'
  }]
  scrollToBottom()
}

// GSAP进场动画
onMounted(() => {
  scrollToBottom()
  nextTick(() => {
    const mm = gsap.matchMedia()
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      gsap.from('.input-container', {
        autoAlpha: 0,
        y: 15,
        duration: 0.6,
        ease: 'power3.out',
        delay: 0.2,
        clearProps: 'transform'
      })
    })
  })
})

// Markdown渲染函数
const renderMarkdown = (content: string) => {
  if (!content) return ''
  let processedContent = content
    .replace(/\r\n/g, '\n')
    .replace(/\n\n/g, '\n\n')
  return marked(processedContent)
}

// 切换参考文档展开/折叠状态
const toggleDocs = (message: ChatMessage) => {
  message.isDocsExpanded = !message.isDocsExpanded
}

// 过滤参考文档
const filteredDocs = (docs: RelatedDoc[]) => {
  if (!docs) return []
  return docs.filter(doc => (doc.relevance_score * 100) >= 25)
}

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message) return

  messages.value.push({
    id: Date.now(),
    content: message,
    sender: 'user'
  })

  scrollToBottom()
  inputMessage.value = ''

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

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('No readable stream in response')
    }

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
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        
        for (const line of lines) {
          if (line.trim()) {
            try {
              const event = JSON.parse(line)
              switch (event.type) {
                case 'text_chunk':
                  if (event.content) {
                    fullResponse += event.content
                    const msgIndex = messages.value.findIndex(m => m.id === aiMessageId)
                    if (msgIndex !== -1 && messages.value[msgIndex]) {
                      messages.value[msgIndex].content = fullResponse
                    }
                    scrollToBottom()
                  }
                  break
                case 'complete':
                  if (event.data && event.data.related_docs) {
                    relatedDocsData = event.data.related_docs
                    const msgIndex = messages.value.findIndex(m => m.id === aiMessageId)
                    if (msgIndex !== -1 && messages.value[msgIndex]) {
                      messages.value[msgIndex].related_docs = relatedDocsData
                    }
                  }
                  break
                case 'error':
                  console.error('流式响应错误:', event.message)
                  const errIndex = messages.value.findIndex(m => m.id === aiMessageId)
                  if (errIndex !== -1 && messages.value[errIndex]) {
                    messages.value[errIndex].content = `抱歉，处理请求时发生错误：${event.message}`
                  }
                  break
              }
            } catch (e) {
              console.error('解析流式数据失败:', e)
            }
          }
        }
      }
    }
    
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

    const msgIndex = messages.value.findIndex(m => m.id === aiMessageId)
    if (msgIndex !== -1 && messages.value[msgIndex]) {
      messages.value[msgIndex].isLoading = false
    }
    
    if (relatedDocsData.length > 0) {
      relatedDocs.value = relatedDocsData
    }
  } catch (error) {
    console.error('Error sending message:', error)
    const msgIndex = messages.value.findIndex(m => m.id === aiMessageId)
    if (msgIndex !== -1) {
      messages.value[msgIndex].content = '抱歉，暂时无法回复您的问题，请稍后再试。'
      messages.value[msgIndex].isLoading = false
    }
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
/* 整体布局 */
.qa-wrapper {
  display: flex;
  height: 100%;
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  background-color: var(--bg);
}

/* 侧边栏：历史会话 */
.qa-sidebar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 300px;
  background-color: var(--surface);
  border-right: 1px solid var(--border-light);
  z-index: 100;
  transform: translateX(-100%);
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-lg);
}

.qa-sidebar.open {
  transform: translateX(0);
}

.qa-sidebar-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--surface-alt);
}

.qa-sidebar-title {
  margin: 0;
  font-size: 1.1rem;
  color: var(--primary-dark);
  font-weight: 600;
  font-family: var(--font-display);
}

.close-sidebar-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  transition: all 0.25s var(--ease);
  display: flex;
  align-items: center;
  justify-content: center;
}
.close-sidebar-btn:hover { 
  background-color: rgba(196, 136, 122, 0.1);
  color: var(--primary-dark); 
}
.close-icon { width: 1.25rem; height: 1.25rem; }

.qa-sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.qa-session-item {
  padding: 1rem 1.25rem;
  border-radius: var(--radius-md);
  margin-bottom: 0.75rem;
  cursor: pointer;
  background-color: var(--bg);
  border: 1px solid var(--border-light);
  transition: all 0.25s var(--ease);
}
.qa-session-item:hover {
  border-color: var(--primary-light);
  background-color: var(--surface-alt);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}
.qa-session-title {
  font-size: 0.9rem;
  color: var(--text);
  font-weight: 500;
  margin-bottom: 0.35rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.qa-session-time {
  font-size: 0.75rem;
  color: var(--text-muted);
}
.qa-sidebar-status {
  padding: 2.5rem 1rem;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.95rem;
}

.qa-overlay {
  position: absolute;
  inset: 0;
  background: rgba(196, 136, 122, 0.15);
  z-index: 90;
  backdrop-filter: blur(2px);
}

/* 聊天界面 */
.chat-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  height: 100%;
}

.chat-header {
  padding: 0.8rem 1.5rem;
  background-color: var(--surface);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.open-history-btn, .new-chat-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  padding: 0.5rem 1rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s var(--ease);
}
.open-history-btn:hover, .new-chat-btn:hover {
  background-color: rgba(196, 136, 122, 0.08);
  color: var(--primary-dark);
  border-color: var(--primary-light);
}
.history-icon, .new-chat-icon { width: 1rem; height: 1rem; }

/* 聊天历史 */
.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background-color: var(--bg);
  scroll-behavior: smooth;
}

/* 消息项 */
.message-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
  animation: fadeUp 0.3s var(--ease) forwards;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* AI消息 */
.ai-message {
  justify-content: flex-start;
  flex-direction: column;
  gap: 0.3rem;
}

.ai-message-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.25rem;
  margin-left: 0.25rem;
}

.ai-avatar-img {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background-color: var(--surface-alt);
  padding: 3px;
  border: 1px solid var(--border);
}

.ai-label {
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 500;
  font-family: var(--font-display);
  letter-spacing: 0.02em;
}

/* 加载动画 */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 3px;
  margin-left: 0.5rem;
}

.dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background-color: var(--primary-light);
  animation: pulse 1.5s infinite ease-in-out;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 100% { transform: scale(0.8); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 1; background-color: var(--primary); }
}

/* 相关文档样式 */
.related-docs {
  margin-top: 0.5rem;
  background-color: var(--surface-alt);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  width: 100%;
  max-width: 450px;
  align-self: flex-start;
  overflow: hidden;
}

/* 相关文档头部 */
.related-docs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.25rem;
  cursor: pointer;
  transition: all 0.25s var(--ease);
  background-color: rgba(196, 136, 122, 0.04);
}

.related-docs-header:hover {
  background-color: rgba(196, 136, 122, 0.08);
}

.related-docs-title {
  font-weight: 500;
  color: var(--primary-dark);
  font-size: 0.85rem;
  margin-bottom: 0;
}

.related-docs-toggle {
  color: var(--text-muted);
  font-size: 0.75rem;
  transition: color 0.2s;
}

.related-docs-header:hover .related-docs-toggle {
  color: var(--primary);
}

/* 相关文档列表 */
.related-docs-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background-color: var(--surface);
  border-top: 1px solid var(--border);
}

.related-doc-item {
  background-color: var(--bg);
  border-radius: var(--radius-sm);
  padding: 0.875rem;
  border: 1px solid var(--border-light);
  transition: all 0.2s var(--ease);
}

.related-doc-item:hover {
  border-color: var(--primary-light);
  background-color: var(--surface-alt);
}

.related-doc-title {
  font-weight: 500;
  color: var(--text);
  margin-bottom: 0.25rem;
  font-size: 0.85rem;
}

.related-doc-score {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* 用户消息 */
.user-message {
  justify-content: flex-end;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.3rem;
}

.user-message-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.25rem;
  margin-right: 0.25rem;
  flex-direction: row-reverse;
}

.user-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 500;
}

.user-label {
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 500;
}

/* 消息气泡 */
.message-bubble {
  max-width: 80%;
  padding: 1rem 1.25rem;
  border-radius: 1.25rem;
  font-size: 0.95rem;
  line-height: 1.6;
  word-wrap: break-word;
}

/* AI气泡 */
.ai-bubble {
  background-color: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-bottom-left-radius: 0.25rem;
  box-shadow: var(--shadow-sm);
  align-self: flex-start;
}

/* 用户气泡 */
.user-bubble {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: #ffffff;
  border-bottom-right-radius: 0.25rem;
  box-shadow: 0 4px 12px rgba(196, 136, 122, 0.2);
  align-self: flex-end;
}

/* Markdown 样式覆盖 */
:deep(.ai-bubble h1),
:deep(.ai-bubble h2),
:deep(.ai-bubble h3),
:deep(.ai-bubble h4) {
  color: var(--text);
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  font-family: var(--font-display);
}

:deep(.ai-bubble h3) {
  color: var(--primary-dark);
  font-size: 1.15rem;
}

:deep(.ai-bubble p) {
  margin-bottom: 0.875rem;
}

:deep(.ai-bubble p:last-child) {
  margin-bottom: 0;
}

:deep(.ai-bubble strong) {
  font-weight: 600;
  color: var(--primary-dark);
}

:deep(.ai-bubble ul),
:deep(.ai-bubble ol) {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

:deep(.ai-bubble li) {
  margin-bottom: 0.35rem;
}

:deep(.ai-bubble hr) {
  margin: 1.5rem 0;
  border: 0;
  border-top: 1px solid var(--border-light);
}

:deep(.ai-bubble blockquote) {
  border-left: 3px solid var(--primary-light);
  padding-left: 1.25rem;
  margin: 1rem 0;
  color: var(--text-secondary);
  font-style: italic;
  background-color: var(--bg);
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

:deep(.ai-bubble code) {
  background-color: rgba(196, 136, 122, 0.08);
  color: var(--primary-dark);
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
  font-family: var(--font-mono);
}

:deep(.ai-bubble pre) {
  background-color: var(--surface-alt);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1rem;
  overflow-x: auto;
  margin-bottom: 1rem;
}

:deep(.ai-bubble pre code) {
  background-color: transparent;
  padding: 0;
  color: var(--text);
}

/* 输入区域 */
.input-container {
  padding: 1.5rem 2rem;
  background-color: var(--surface);
  border-top: 1px solid var(--border-light);
  z-index: 10;
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  background-color: var(--bg);
  border-radius: var(--radius-pill);
  padding: 0.5rem 0.5rem 0.5rem 1.5rem;
  border: 1px solid var(--border);
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
  transition: all 0.3s var(--ease);
}

.input-wrapper:focus-within {
  border-color: var(--primary-light);
  box-shadow: 0 0 0 4px rgba(196, 136, 122, 0.08);
  background-color: var(--surface);
}

.input-field {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text);
  font-size: 0.95rem;
  font-family: var(--font-body);
}

.input-field::placeholder {
  color: var(--text-muted);
}

/* 发送按钮 */
.send-btn {
  padding: 0.6rem 1.5rem;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: #ffffff;
  border: none;
  border-radius: var(--radius-pill);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s var(--ease);
  box-shadow: 0 4px 10px rgba(196, 136, 122, 0.2);
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 14px rgba(196, 136, 122, 0.3);
}

.send-btn:disabled {
  background: var(--border);
  color: var(--text-muted);
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

/* 响应式布局 - 移动端 */
@media (max-width: 768px) {
  .chat-container {
    border-radius: 0;
    border: none;
  }
  .chat-history {
    padding: 1rem;
  }
  .message-bubble {
    max-width: 90%;
    padding: 0.875rem 1rem;
    font-size: 0.9rem;
  }
  .input-container {
    padding: 1rem;
  }
  .input-wrapper {
    padding: 0.4rem 0.4rem 0.4rem 1rem;
  }
}
</style>