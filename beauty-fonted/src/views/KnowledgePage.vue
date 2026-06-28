<template>
  <div class="knowledge-page">
    <div class="page-header mb-4">
      <h2 class="page-title">知识库管理</h2>
      <p class="page-subtitle text-muted">系统共有 {{ totalChunks }} 个知识分块可供查询</p>
    </div>

    <!-- 统计卡片区 -->
    <div class="stats-grid mb-4">
      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-content">
          <div class="stat-value">{{ documentCount }}</div>
          <div class="stat-label">文档总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🧩</div>
        <div class="stat-content">
          <div class="stat-value">{{ totalChunks }}</div>
          <div class="stat-label">知识分块总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🔍</div>
        <div class="stat-content">
          <div class="stat-value">{{ searchCount }}</div>
          <div class="stat-label">今日查询次数</div>
        </div>
      </div>
    </div>

    <!-- 搜索和过滤区 -->
    <div class="card mb-4 search-card">
      <div class="flex gap-3 items-center w-full">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜索知识库内容..." 
            class="input search-input"
            @keyup.enter="searchKnowledge"
          >
        </div>
        <div class="filter-box">
          <select class="input select-input" v-model="filterDocId">
            <option value="">所有文档</option>
            <option v-for="doc in documents" :key="doc.id" :value="doc.id">
              {{ doc.title || doc.filename }}
            </option>
          </select>
        </div>
        <button class="btn btn-primary" @click="searchKnowledge">搜索</button>
      </div>
    </div>

    <!-- 知识列表区 -->
    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th width="10%">文档ID</th>
            <th width="15%">分块索引</th>
            <th width="60%">内容摘要</th>
            <th width="15%">更新时间</th>
          </tr>
        </thead>
        <tbody class="table-body">
          <tr v-for="chunk in knowledgeChunks" :key="chunk.id" class="table-row">
            <td>
              <span class="badge-type">DOC-{{ chunk.document_id }}</span>
            </td>
            <td>
              <span class="chunk-index">分块 {{ chunk.chunk_index + 1 }}</span>
            </td>
            <td>
              <div class="content-preview">{{ truncateText(chunk.chunk_content, 100) }}</div>
            </td>
            <td class="text-muted">{{ formatDate(chunk.created_at) }}</td>
          </tr>
          <tr v-if="knowledgeChunks.length === 0 && !isLoading">
            <td colspan="4" class="text-center empty-state">
              <span v-if="searchQuery">没有找到匹配"{{ searchQuery }}"的知识分块</span>
              <span v-else>暂无知识分块，请先上传文档</span>
            </td>
          </tr>
          <tr v-if="isLoading">
            <td colspan="4" class="text-center empty-state">
              加载中，请稍候...
            </td>
          </tr>
        </tbody>
      </table>

      <!-- 分页控件 -->
      <div class="pagination-container" v-if="totalPages > 1">
        <button 
          class="btn btn-secondary btn-sm" 
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >上一页</button>
        <div class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</div>
        <button 
          class="btn btn-secondary btn-sm" 
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
        >下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import gsap from 'gsap'

// 接口定义
interface Document {
  id: number
  title: string
  filename: string
}

interface KnowledgeChunk {
  id: number
  document_id: number
  chunk_content: string
  chunk_index: number
  created_at: string
}

// 状态
const documentCount = ref(0)
const totalChunks = ref(0)
const searchCount = ref(128) // 模拟数据
const documents = ref<Document[]>([])
const knowledgeChunks = ref<KnowledgeChunk[]>([])
const isLoading = ref(false)
const searchQuery = ref('')
const filterDocId = ref('')

// 分页
const currentPage = ref(1)
const totalPages = ref(1)
const limit = 10

// 动画函数
const animateEntrance = () => {
  nextTick(() => {
    const mm = gsap.matchMedia()
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      // 卡片交错动画
      gsap.from('.stat-card', {
        autoAlpha: 0,
        y: 10,
        duration: 0.6,
        stagger: 0.08,
        ease: 'power3.out',
        clearProps: 'all'
      })
      
      // 搜索区域动画
      gsap.from('.search-card', {
        autoAlpha: 0,
        y: 8,
        duration: 0.6,
        delay: 0.1,
        ease: 'power3.out',
        clearProps: 'all'
      })
    })
  })
}

const animateTableRows = () => {
  nextTick(() => {
    const mm = gsap.matchMedia()
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      gsap.from('.table-row', {
        autoAlpha: 0,
        y: 10,
        duration: 0.4,
        stagger: 0.05,
        ease: 'power2.out',
        clearProps: 'all'
      })
    })
  })
}

// 工具函数
const truncateText = (text: string, length: number): string => {
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 获取数据
const fetchStats = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/documents')
    if (response.ok) {
      const data = await response.json()
      documents.value = data
      documentCount.value = data.length
      
      // 真实项目中应该有一个专门的统计接口，这里只是模拟获取总分块数
      if (data.length > 0) {
        // 先获取第一页知识块来获取总数信息
        await fetchKnowledgeChunks()
      }
    }
  } catch (error) {
    console.error('获取统计数据出错:', error)
  }
}

const fetchKnowledgeChunks = async () => {
  isLoading.value = true
  try {
    // 这里应该是带有分页和搜索的API
    // 假设API支持类似 ?skip=0&limit=10&query=xxx&doc_id=1 的查询
    let url = `http://localhost:8000/api/documents/chunks?skip=${(currentPage.value - 1) * limit}&limit=${limit}`
    
    // 因为后端当前没有这个API，我们这里模拟行为
    // 如果是真实的后端，你需要对应修改
    
    // 这里为了演示，我们先获取所有文档，然后合并它们的分块，然后在前端分页
    if (documents.value.length > 0) {
      let allChunks: KnowledgeChunk[] = []
      
      for (const doc of documents.value) {
        if (filterDocId.value && parseInt(filterDocId.value) !== doc.id) continue
        
        try {
          const res = await fetch(`http://localhost:8000/api/documents/${doc.id}/chunks`)
          if (res.ok) {
            const chunks = await res.json()
            allChunks = [...allChunks, ...chunks]
          }
        } catch (e) {
          // ignore
        }
      }
      
      // 搜索过滤
      if (searchQuery.value) {
        allChunks = allChunks.filter(chunk => 
          chunk.chunk_content.toLowerCase().includes(searchQuery.value.toLowerCase())
        )
      }
      
      totalChunks.value = allChunks.length
      totalPages.value = Math.ceil(totalChunks.value / limit) || 1
      
      // 修正当前页码
      if (currentPage.value > totalPages.value) {
        currentPage.value = totalPages.value
      }
      
      // 前端分页
      const startIndex = (currentPage.value - 1) * limit
      const endIndex = startIndex + limit
      knowledgeChunks.value = allChunks.slice(startIndex, endIndex)
      
      animateTableRows()
    }
  } catch (error) {
    console.error('获取知识块出错:', error)
  } finally {
    isLoading.value = false
  }
}

// 事件处理
const searchKnowledge = () => {
  currentPage.value = 1
  fetchKnowledgeChunks()
}

const changePage = (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchKnowledgeChunks()
}

onMounted(() => {
  fetchStats().then(() => {
    animateEntrance()
  })
})
</script>

<style scoped>
.knowledge-page {
  padding: 0;
}

.page-title {
  font-family: var(--font-display);
  font-size: 1.5rem;
  color: var(--text);
  font-weight: 600;
  margin: 0 0 0.25rem 0;
}

.page-subtitle {
  font-size: 0.9rem;
  margin: 0;
}

.flex { display: flex; }
.items-center { align-items: center; }
.mb-4 { margin-bottom: 1.5rem; }
.gap-3 { gap: 0.75rem; }
.w-full { width: 100%; }
.text-muted { color: var(--text-muted); }

/* 统计卡片区 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.stat-card {
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  transition: all 0.3s var(--ease);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-light);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: rgba(196, 136, 122, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: var(--primary);
}

.stat-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 搜索区 */
.search-card {
  padding: 1rem 1.5rem;
  background-color: var(--surface);
  border: 1px solid var(--border-light);
}

.search-box {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: var(--text-muted);
}

.search-input {
  padding-left: 2.5rem;
  width: 100%;
}

.filter-box {
  width: 200px;
}

.select-input {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%238A7F79%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem top 50%;
  background-size: 0.65rem auto;
}

/* 表格区 */
.table-container {
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  overflow: hidden;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 1rem 1.5rem;
  text-align: left;
  border-bottom: 1px solid var(--border-light);
}

.table th {
  background-color: var(--surface-alt);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.85rem;
  letter-spacing: 0.02em;
}

.table tbody tr {
  transition: background-color 0.2s var(--ease);
}

.table tbody tr:hover {
  background-color: var(--bg);
}

.badge-type {
  background-color: var(--bg);
  padding: 0.2rem 0.5rem;
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-family: var(--font-mono);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.chunk-index {
  font-weight: 500;
  color: var(--primary);
  font-size: 0.85rem;
  background-color: rgba(196, 136, 122, 0.08);
  padding: 0.2rem 0.6rem;
  border-radius: var(--radius-sm);
}

.content-preview {
  color: var(--text);
  font-size: 0.9rem;
  line-height: 1.5;
}

.text-center { text-align: center; }

.empty-state {
  padding: 4rem 2rem;
  color: var(--text-muted);
  font-style: italic;
}

/* 分页控件 */
.pagination-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  background-color: var(--surface);
  border-top: 1px solid var(--border-light);
}

.page-info {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
}

/* 响应式 */
@media (max-width: 992px) {
  .stats-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; }
  .search-card .flex { flex-direction: column; }
  .filter-box { width: 100%; }
}
</style>