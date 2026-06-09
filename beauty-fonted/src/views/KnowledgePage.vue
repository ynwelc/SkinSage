<template>
  <div class="knowledge-page">
    <div class="flex justify-between items-center mb-4">
      <h2>知识库管理</h2>
      <div class="flex gap-2">
        <button class="btn btn-primary">
          <span>➕</span>
          <span>添加知识</span>
        </button>
        <div class="search-box">
          <span>🔍</span>
          <input type="text" placeholder="搜索知识..." v-model="searchQuery">
        </div>
      </div>
    </div>

    <!-- 知识库统计卡片 -->
    <div class="stats-container mb-6">
      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-content">
          <div class="stat-label">文档总数</div>
          <div class="stat-value">{{ isLoading ? '加载中...' : knowledgeStats?.total_documents || 0 }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📝</div>
        <div class="stat-content">
          <div class="stat-label">分块总数</div>
          <div class="stat-value">{{ isLoading ? '加载中...' : knowledgeStats?.total_chunks || 0 }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">❓</div>
        <div class="stat-content">
          <div class="stat-label">查询总数</div>
          <div class="stat-value">{{ isLoading ? '加载中...' : knowledgeStats?.total_queries || 0 }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⏱️</div>
        <div class="stat-content">
            <div class="stat-label">平均响应时间</div>
            <div class="stat-value">{{ isLoading ? '加载中...' : (knowledgeStats?.average_response_time ? knowledgeStats.average_response_time.toFixed(2) : '0') + 'ms' }}</div>
          </div>
      </div>
    </div>
    
    <!-- 文档分块表格 -->
    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>文档ID</th>
            <th>分块索引</th>
            <th>分块内容</th>
            <th>创建时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="chunk in documentChunks" :key="chunk.id">
            <td>{{ chunk.id }}</td>
            <td>{{ chunk.document_id }}</td>
            <td>{{ chunk.chunk_index }}</td>
            <td class="chunk-content-cell">{{ chunk.chunk_content }}</td>
            <td>{{ new Date(chunk.created_at).toLocaleString('zh-CN') }}</td>
          </tr>
          <tr v-if="documentChunks.length === 0 && !isLoading">
            <td colspan="5" class="text-center">暂无文档分块</td>
          </tr>
          <tr v-if="isLoading">
            <td colspan="5" class="text-center">加载中...</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页控件 -->
    <div class="pagination-container">
      <div class="pagination-info">
        显示 {{ (page - 1) * pageSize + 1 }} - {{ Math.min(page * pageSize, totalChunks) }} 条，共 {{ totalChunks }} 条
      </div>
      <div class="pagination-controls">
        <div class="dropdown">
          <select v-model="pageSize" class="input" @change="handlePageSizeChange">
            <option value="10">10条/页</option>
            <option value="20">20条/页</option>
            <option value="50">50条/页</option>
            <option value="100">100条/页</option>
          </select>
        </div>
        <button class="btn btn-secondary btn-sm" @click="handlePageChange(page - 1)" :disabled="page === 1 || isLoading">
          上一页
        </button>
        <span class="page-info">{{ page }} / {{ totalPages }}</span>
        <button class="btn btn-secondary btn-sm" @click="handlePageChange(page + 1)" :disabled="page === totalPages || isLoading">
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// 知识库统计类型
interface KnowledgeStats {
  total_documents: number
  total_chunks: number
  total_queries: number
  average_response_time: number
}

// 文档分块类型
interface DocumentChunk {
  id: number
  document_id: number
  chunk_content: string
  chunk_index: number
  created_at: string
}

// 分页参数
const page = ref(1)
const pageSize = ref(10)
const totalChunks = ref(0)

const searchQuery = ref('')
const knowledgeStats = ref<KnowledgeStats | null>(null)
const documentChunks = ref<DocumentChunk[]>([])
const isLoading = ref(false)

// 获取知识库统计数据
const fetchKnowledgeStats = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/knowledge-base/stats')
    if (response.ok) {
      const data = await response.json()
      // 检查数据格式，支持直接返回统计数据的情况
      if (data.code === 200 && data.data) {
        // 后端返回格式: { code: 200, data: { ...stats } }
        knowledgeStats.value = data.data
        totalChunks.value = data.data.total_chunks
      } else {
        // 后端直接返回统计数据: { ...stats }
        knowledgeStats.value = data
        totalChunks.value = data.total_chunks
      }
    } else {
      console.error('获取知识库统计失败')
    }
  } catch (error) {
    console.error('获取知识库统计出错:', error)
  }
}

// 获取文档分块数据
const fetchDocumentChunks = async () => {
  isLoading.value = true
  try {
    // 尝试使用不同的API路径，适配后端路由配置
    // 先获取所有文档，然后获取每个文档的分块
    const documentsResponse = await fetch('http://localhost:8000/api/documents')
    if (documentsResponse.ok) {
      const documents = await documentsResponse.json()
      let allChunks: DocumentChunk[] = []
      
      // 获取所有文档的分块
      for (const doc of documents) {
        const chunksResponse = await fetch(`http://localhost:8000/api/documents/${doc.id}/chunks`)
        if (chunksResponse.ok) {
          const chunks = await chunksResponse.json()
          allChunks = [...allChunks, ...chunks]
        }
      }
      
      // 手动分页
      const startIndex = (page.value - 1) * pageSize.value
      const endIndex = startIndex + pageSize.value
      documentChunks.value = allChunks.slice(startIndex, endIndex)
      totalChunks.value = allChunks.length
    } else {
      console.error('获取文档列表失败')
    }
  } catch (error) {
    console.error('获取文档分块出错:', error)
  } finally {
    isLoading.value = false
  }
}

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(totalChunks.value / pageSize.value)
})

// 页面变化处理
const handlePageChange = (newPage: number) => {
  if (newPage >= 1 && newPage <= totalPages.value) {
    page.value = newPage
    fetchDocumentChunks()
  }
}

// 每页条数变化处理
const handlePageSizeChange = () => {
  // 重置到第一页
  page.value = 1
  fetchDocumentChunks()
}

// 刷新数据
const refreshData = () => {
  fetchKnowledgeStats()
  fetchDocumentChunks()
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.knowledge-page {
  padding: 0;
}

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.items-center {
  align-items: center;
}

.mb-4 {
  margin-bottom: 1rem;
}

.gap-2 {
  gap: 0.5rem;
}

/* 搜索框 */
.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #0f172a;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #475569;
  transition: all 0.3s ease;
}

.search-box:focus-within {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.search-box input {
  background: transparent;
  border: none;
  outline: none;
  color: #f8fafc;
  font-size: 0.875rem;
}

.search-box input::placeholder {
  color: #94a3b8;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
  background-color: #1e293b;
  border-radius: 0.75rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border: 1px solid #475569;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #475569;
}

.table th {
  background-color: #334155;
  font-weight: 600;
  color: #f8fafc;
}

.table tbody tr {
  transition: all 0.3s ease;
}

.table tbody tr:hover {
  background-color: #334155;
}

.table tbody tr:last-child td {
  border-bottom: none;
}

/* 按钮组 */
.btn-group {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
}

/* 统计卡片样式 */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background-color: #1e293b;
  border: 1px solid #475569;
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border-color: #6366f1;
}

.stat-icon {
  font-size: 2rem;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(99, 102, 241, 0.1);
  border-radius: 0.5rem;
  color: #6366f1;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #94a3b8;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #f8fafc;
  line-height: 1.2;
}

/* 分块内容单元格样式 */
.chunk-content-cell {
  max-width: 400px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chunk-content-cell:hover {
  overflow: visible;
  white-space: normal;
  z-index: 10;
  position: relative;
  background-color: #334155;
  padding: 0.5rem;
  border-radius: 0.375rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

/* 分页样式 */
.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: #1e293b;
  border: 1px solid #475569;
  border-radius: 0.5rem;
  position: relative;
  z-index: 100;
  width: 100%;
  overflow: visible;
}

.pagination-info {
  color: #94a3b8;
  font-size: 0.875rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* 下拉框样式 */
.dropdown select {
  background-color: #0f172a;
  color: #e5e7eb;
  border: 1px solid #475569;
  border-radius: 0.375rem;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dropdown select:hover {
  border-color: #6366f1;
}

.dropdown select:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.page-info {
  color: #cbd5e1;
  font-weight: 600;
  min-width: 60px;
  text-align: center;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .stats-container {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .stat-card {
    padding: 1rem;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .pagination-container {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .chunk-content-cell {
    max-width: 200px;
  }
}
</style>