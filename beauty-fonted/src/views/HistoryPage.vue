<template>
  <div class="history-container">
    <h2>对话历史</h2>
    
    <div class="history-content">
      <!-- 历史对话列表 -->
      <div class="history-list">
        <div class="history-list-header">
          <h3>历史会话</h3>
          <div class="sort-controls">
            <select v-model="sortOrder" @change="sortSessions" class="sort-select">
              <option value="desc">最新会话</option>
              <option value="asc">最早会话</option>
            </select>
          </div>
        </div>
        <div class="history-sessions">
          <div 
            v-for="(session, index) in sessions" 
            :key="index"
            class="session-item"
            :class="{ active: selectedSession === index }"
            @click="selectSession(index)"
          >
            <div class="session-preview">
              <div class="session-messages">
                <div class="session-question">{{ session.messages.find(m => m.role === 'user')?.content || '无对话内容' }}</div>
                <div class="session-answer">{{ session.messages.find(m => m.role === 'assistant')?.content.substring(0, 50) || '' }}...</div>
              </div>
              <div class="session-date">{{ formatDate(session.created_at) }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 选中会话的对话内容 -->
      <div class="selected-session">
        <div v-if="!selectedSessionMessages.length" class="empty-state">
          <div>📝 请选择一个历史会话</div>
          <div class="empty-subtext">选择后可以查看完整对话历史并继续交流</div>
        </div>
        
        <div v-else class="selected-session-content">
          <!-- 对话内容标题和下拉框 -->
          <div class="selected-session-header">
            <h3>对话内容</h3>
            <div class="sort-controls">
              <select v-model="sortOrder" @change="sortSessions" class="sort-select">
                <option value="desc">最新会话</option>
                <option value="asc">最早会话</option>
              </select>
            </div>
          </div>
          
          <!-- 聊天历史 -->
          <div class="chat-history" ref="chatHistoryRef">
            <!-- 消息列表 -->
            <div 
              v-for="(message, index) in selectedSessionMessages" 
              :key="index"
              class="message-item" 
              :class="message.role === 'assistant' ? 'ai-message' : 'user-message'"
            >
              <!-- AI消息 -->
              <template v-if="message.role === 'assistant'">
                <div class="ai-message-header">
                  <div class="ai-avatar">AI</div>
                  <span class="ai-label">AI</span>
                </div>
                <div class="message-bubble ai-bubble" v-html="renderMarkdown(message.content)"></div>
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
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import { marked } from 'marked'

// 聊天消息类型
interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

// 会话类型
interface Session {
  id: number
  user_id: number
  messages: ChatMessage[]
  created_at: string
}

// 状态
const loading = ref(false)
const sessions = ref<Session[]>([])
const selectedSession = ref<number>(-1)
const selectedSessionMessages = ref<ChatMessage[]>([])
const inputMessage = ref('')
// 排序状态
const sortOrder = ref<'asc' | 'desc'>('desc') // 默认倒序，最新会话显示在最上面

// 滚动相关
const scrollToBottomMarker = ref<HTMLElement | null>(null)

// API返回的问答历史项类型
interface QAHIstoryItem {
  id: number;
  user_id: number;
  query: string;
  response: string;
  response_time: number;
  session_id: string;
  created_at: string;
}

// 获取会话历史
const fetchConversationHistory = async () => {
  try {
    loading.value = true
    // 假设当前用户ID为1，实际应从认证系统获取
    const user_id = 1
    const response = await axios.get('http://localhost:8000/api/qa/history', {
      params: {
        user_id,
        page: 1,
        page_size: 100
      }
    })
    
    if (response.data && response.data.code === 200 && response.data.data) {
      let qaHistoryItems: QAHIstoryItem[] = response.data.data.items
      
      // 1. 首先按时间倒序排序问答项，确保最新的问答项在前面
      qaHistoryItems.sort((a, b) => {
        const timeA = new Date(a.created_at).getTime()
        const timeB = new Date(b.created_at).getTime()
        // 倒序排序，时间大的在前
        return timeB - timeA
      })
      
      // 将消息分组为会话，10分钟内的对话为一个会话
      const newSessions: Session[] = []
      const TEN_MINUTES = 10 * 60 * 1000 // 10分钟毫秒数
      
      // 2. 将问答项按10分钟分组
      const groupedQAIitems: QAHIstoryItem[][] = []
      let currentGroup: QAHIstoryItem[] = []
      
      qaHistoryItems.forEach((item, index) => {
        if (currentGroup.length === 0) {
          // 第一个项，创建新组
          currentGroup.push(item)
        } else {
          // 添加空值检查
          if (currentGroup[0]) {
            const firstItemTime = new Date(currentGroup[0].created_at).getTime()
            const currentItemTime = new Date(item.created_at).getTime()
            
            // 检查当前项是否与组内第一个项相差在10分钟内
            // 注意：因为qaHistoryItems是倒序排序的，所以currentItemTime <= firstItemTime
            if (firstItemTime - currentItemTime <= TEN_MINUTES) {
              // 在10分钟内，加入当前组
              currentGroup.push(item)
            } else {
              // 超过10分钟，保存当前组并创建新组
              groupedQAIitems.push(currentGroup)
              currentGroup = [item]
            }
          } else {
            // 异常情况，重置当前组
            currentGroup = [item]
          }
        }
        
        // 处理最后一个项
        if (index === qaHistoryItems.length - 1) {
          groupedQAIitems.push(currentGroup)
        }
      })
      
      // 3. 将分组后的问答项转换为会话
      groupedQAIitems.forEach((group, groupIndex) => {
        const sessionMessages: ChatMessage[] = []
        
        // 按时间正序处理组内的问答项，确保对话顺序正确
        const sortedGroup = [...group].sort((a, b) => {
          const timeA = new Date(a.created_at).getTime()
          const timeB = new Date(b.created_at).getTime()
          // 正序排序，时间小的在前
          return timeA - timeB
        })
        
        sortedGroup.forEach(item => {
          // 添加用户查询消息
          sessionMessages.push({
            role: 'user',
            content: item.query
          })
          // 添加AI回复消息
          sessionMessages.push({
            role: 'assistant',
            content: item.response
          })
        })
        
        // 获取会话创建时间，使用组内第一个消息的时间
        const createdAt = group[0] ? group[0].created_at : new Date().toISOString()
        
        newSessions.push({
          id: groupIndex + 1,
          user_id: 1,
          messages: sessionMessages,
          created_at: createdAt // 使用组内第一个消息的时间作为会话创建时间
        })
      })
      
      // 4. 将会话按创建时间倒序排序，确保最新的会话在最前面
      sessions.value = [...newSessions]
      sortSessions()
      
      // 默认选择第一个会话
      if (newSessions.length > 0) {
        selectSession(0)
      }
    }
  } catch (error) {
    console.error('获取会话历史失败:', error)
  } finally {
    loading.value = false
  }
}

// 选择会话
const selectSession = (index: number) => {
  if (sessions.value[index]) {
    selectedSession.value = index
    selectedSessionMessages.value = [...sessions.value[index].messages]
    scrollToBottom()
  }
}

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || selectedSession.value === -1) return

  const sessionIndex = selectedSession.value
  if (!sessions.value[sessionIndex]) return

  // 添加用户消息到当前会话
  const userMessage: ChatMessage = {
    role: 'user',
    content: message
  }
  selectedSessionMessages.value.push(userMessage)
  
  // 更新会话列表中的消息
  sessions.value[sessionIndex].messages.push(userMessage)
  
  // 清空输入框
  inputMessage.value = ''
  
  // 滚动到底部
  scrollToBottom()

  try {
    // 设置加载状态
    loading.value = true
    
    // 调用后端API获取回复
    const response = await axios.post('http://localhost:8000/api/qa', {
      query: message,
      user_id: 1,
      n_results: 3
    })

    // 添加AI回复
    const aiMessage: ChatMessage = {
      role: 'assistant',
      content: response.data.response
    }
    selectedSessionMessages.value.push(aiMessage)
    
    // 更新会话列表中的消息
    if (sessions.value[sessionIndex]) {
      sessions.value[sessionIndex].messages.push(aiMessage)
    }
    
  } catch (error) {
    console.error('Error sending message:', error)
    // 添加错误提示
    const errorMessage: ChatMessage = {
      role: 'assistant',
      content: '抱歉，暂时无法回复您的问题，请稍后再试。'
    }
    selectedSessionMessages.value.push(errorMessage)
    if (sessions.value[sessionIndex]) {
      sessions.value[sessionIndex].messages.push(errorMessage)
    }
  } finally {
    // 清除加载状态
    loading.value = false
    // 滚动到底部
    scrollToBottom()
  }
}

// 滚动到底部的函数
const scrollToBottom = () => {
  nextTick(() => {
    scrollToBottomMarker.value?.scrollIntoView({
      behavior: 'smooth',
      block: 'end'
    })
  })
}

// 会话排序函数
const sortSessions = () => {
  sessions.value.sort((a, b) => {
    const timeA = new Date(a.created_at).getTime()
    const timeB = new Date(b.created_at).getTime()
    
    if (sortOrder.value === 'desc') {
      // 倒序：时间大的在前（最新会话）
      return timeB - timeA
    } else {
      // 正序：时间小的在前（最早会话）
      return timeA - timeB
    }
  })
  
  // 如果当前选中的会话存在，重新选择它以保持选中状态
  if (selectedSession.value !== -1 && sessions.value.length > 0) {
    // 这里简化处理，重新选择第一个会话
    selectSession(0)
  }
}

// 监听消息变化，自动滚动到底部
watch(selectedSessionMessages, () => {
  scrollToBottom()
}, { deep: true })

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Markdown渲染函数
const renderMarkdown = (content: string) => {
  if (!content) return ''
  // 处理特殊字符和格式
  let processedContent = content
    .replace(/\r\n/g, '\n') // 统一换行符
    .replace(/\n\n/g, '\n\n') // 确保段落分隔
  
  return marked(processedContent)
}

// 组件挂载时获取会话历史
onMounted(() => {
  fetchConversationHistory()
})
</script>

<style scoped>
.history-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #111827;
}

h2 {
  margin-bottom: 1.5rem;
  color: #e2e8f0;
  font-size: 1.5rem;
  font-weight: 700;
}

.history-content {
  display: flex;
  flex: 1;
  gap: 1.5rem;
  overflow: hidden;
}

/* 历史会话列表 */
.history-list {
  width: 300px;
  background-color: #1e293b;
  border-radius: 0.75rem;
  border: 1px solid #334155;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-list-header {
  padding: 1.5rem;
  border-bottom: 1px solid #334155;
  background-color: #1e293b;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-list-header h3 {
  color: #e2e8f0;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}

/* 排序控件样式 */
.sort-controls {
  display: flex;
  align-items: center;
}

.sort-select {
  background-color: #334155;
  color: #e2e8f0;
  border: 1px solid #475569;
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sort-select:hover {
  background-color: #475569;
  border-color: #6366f1;
}

.sort-select:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.history-sessions {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.session-item {
  background-color: #334155;
  border-radius: 0.5rem;
  margin-bottom: 0.75rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.session-item:hover {
  background-color: #475569;
  border-color: #6366f1;
}

.session-item.active {
  background-color: #6366f1;
  border-color: #6366f1;
  color: #ffffff;
}

.session-preview {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.session-messages {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.session-question {
  font-weight: 600;
  font-size: 0.875rem;
  line-height: 1.5;
  color: #cbd5e1;
}

.session-item.active .session-question {
  color: #ffffff;
}

.session-answer {
  font-size: 0.75rem;
  line-height: 1.4;
  color: #94a3b8;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.session-item.active .session-answer {
  color: #e2e8f0;
  opacity: 0.8;
}

.session-date {
  font-size: 0.75rem;
  color: #64748b;
  text-align: right;
}

.session-item.active .session-date {
  color: #ffffff;
  opacity: 0.7;
}

/* 选中会话的内容 */
.selected-session {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #1e293b;
  border-radius: 0.75rem;
  border: 1px solid #334155;
  overflow: hidden;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #94a3b8;
  font-size: 1.125rem;
}

.empty-subtext {
  font-size: 0.875rem;
  color: #64748b;
}

/* 选中会话内容区域 */
.selected-session-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #1e293b;
}

/* 选中会话头部样式 */
.selected-session-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #334155;
  background-color: #1e293b;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-session-header h3 {
  color: #e2e8f0;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}

/* 聊天历史 */
.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background-color: #1e293b;
  max-height: calc(100% - 140px); /* 确保聊天区域可以滚动 */
}

/* 确保选中会话区域使用flex布局 */
.selected-session {
  display: flex;
  flex-direction: column;
  background-color: #1e293b;
  border-radius: 0.75rem;
  border: 1px solid #334155;
  overflow: hidden;
}

.selected-session > div {
  display: flex;
  flex-direction: column;
  height: 100%;
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

/* AI气泡 */
.ai-bubble {
  background-color: #1f2937;
  color: #e5e7eb;
  border: 1px solid #374151;
  border-radius: 0.75rem;
  align-self: flex-start;
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
  background-color: #1e293b;
  border-top: 1px solid #334155;
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
.history-sessions::-webkit-scrollbar,
.chat-history::-webkit-scrollbar {
  width: 8px;
}

.history-sessions::-webkit-scrollbar-track,
.chat-history::-webkit-scrollbar-track {
  background: #1e293b;
  border-radius: 4px;
}

.history-sessions::-webkit-scrollbar-thumb,
.chat-history::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}

.history-sessions::-webkit-scrollbar-thumb:hover,
.chat-history::-webkit-scrollbar-thumb:hover {
  background: #64748b;
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

/* 响应式布局 */
@media (max-width: 1024px) {
  .history-content {
    flex-direction: column;
  }
  
  .history-list {
    width: 100%;
    max-height: 200px;
  }
}
</style>