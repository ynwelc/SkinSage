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
                  <img src="/beauty-ai-logo.svg?v=2" alt="AI" class="ai-avatar-img">
                  <span class="ai-label">AI</span>
                </div>
                <div class="message-bubble ai-bubble" v-html="renderMarkdown(message.content)"></div>
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
import gsap from 'gsap'

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
  fetchConversationHistory().then(() => {
    nextTick(() => {
      const mm = gsap.matchMedia()
      mm.add('(prefers-reduced-motion: no-preference)', () => {
        gsap.from('.session-item', {
          autoAlpha: 0,
          x: -10,
          duration: 0.6,
          stagger: 0.05,
          ease: 'power3.out',
          clearProps: 'all'
        })
        gsap.from('.selected-session', {
          autoAlpha: 0,
          scale: 0.98,
          duration: 0.7,
          ease: 'power3.out',
          clearProps: 'all'
        })
      })
    })
  })
})
</script>

<style scoped>
.history-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--bg);
}

h2 {
  margin-bottom: 1.5rem;
  color: var(--text);
  font-size: 1.5rem;
  font-weight: 600;
  font-family: var(--font-display);
}

.history-content {
  display: flex;
  flex: 1;
  gap: 1.5rem;
  overflow: hidden;
}

/* 历史会话列表 */
.history-list {
  width: 320px;
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-list-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-light);
  background-color: var(--surface-alt);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-list-header h3 {
  color: var(--primary-dark);
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  font-family: var(--font-display);
}

/* 排序控件样式 */
.sort-controls {
  display: flex;
  align-items: center;
}

.sort-select {
  background-color: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 0.4rem 1.5rem 0.4rem 0.75rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s var(--ease);
  appearance: none;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%238A7F79%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem top 50%;
  background-size: 0.55rem auto;
}

.sort-select:hover {
  border-color: var(--primary-light);
}

.sort-select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(196, 136, 122, 0.1);
}

.history-sessions {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
}

.session-item {
  background-color: var(--surface-alt);
  border-radius: var(--radius-md);
  margin-bottom: 0.75rem;
  padding: 1.125rem;
  cursor: pointer;
  transition: all 0.25s var(--ease);
  border: 1px solid transparent;
}

.session-item:hover {
  background-color: var(--surface);
  border-color: var(--primary-light);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.session-item.active {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(196, 136, 122, 0.25);
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
  font-weight: 500;
  font-size: 0.9rem;
  line-height: 1.5;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-item.active .session-question {
  color: #ffffff;
}

.session-answer {
  font-size: 0.8rem;
  line-height: 1.4;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.session-item.active .session-answer {
  color: rgba(255, 255, 255, 0.85);
}

.session-date {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: right;
  margin-top: 0.25rem;
}

.session-item.active .session-date {
  color: rgba(255, 255, 255, 0.7);
}

/* 选中会话的内容 */
.selected-session {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--text-muted);
  font-size: 1.125rem;
  background-color: var(--bg);
}

.empty-subtext {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

/* 选中会话内容区域 */
.selected-session-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 选中会话头部样式 */
.selected-session-header {
  padding: 1.25rem 2rem;
  border-bottom: 1px solid var(--border-light);
  background-color: var(--surface-alt);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-session-header h3 {
  color: var(--primary-dark);
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  font-family: var(--font-display);
}

/* 聊天历史 */
.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background-color: var(--bg);
  max-height: calc(100% - 140px);
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

/* 滚动条样式 */
.history-sessions::-webkit-scrollbar,
.chat-history::-webkit-scrollbar {
  width: 6px;
}

.history-sessions::-webkit-scrollbar-track,
.chat-history::-webkit-scrollbar-track {
  background: var(--bg);
}

.history-sessions::-webkit-scrollbar-thumb,
.chat-history::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}

.history-sessions::-webkit-scrollbar-thumb:hover,
.chat-history::-webkit-scrollbar-thumb:hover {
  background: var(--primary-light);
}

/* Markdown 样式 */
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

/* 响应式布局 */
@media (max-width: 1024px) {
  .history-content {
    flex-direction: column;
  }
  
  .history-list {
    width: 100%;
    max-height: 250px;
  }
}
</style>