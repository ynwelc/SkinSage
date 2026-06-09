<template>
  <div class="analytics-page">
    <h2>统计分析</h2>
    
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-title">总查询数</div>
        <div class="stat-value">{{ isLoading ? '加载中...' : usageStats?.total_queries.toLocaleString() || 0 }}</div>
        <div class="stat-change positive">+12% 较上周</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">平均响应时间</div>
        <div class="stat-value">{{ isLoading ? '加载中...' : ((usageStats?.average_response_time || 0) / 1000).toFixed(1) + 's' }}</div>
        <div class="stat-change negative">-5% 较上周</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">准确率</div>
        <div class="stat-value">{{ isLoading ? '加载中...' : ((usageStats?.accuracy_rate || 0) * 100).toFixed(0) + '%' || '0%' }}</div>
        <div class="stat-change positive">+3% 较上周</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">用户满意度</div>
        <div class="stat-value">4.8/5</div>
        <div class="stat-change positive">+0.2 较上周</div>
      </div>
    </div>
    
    <!-- 图表和数据 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="card">
        <h3>热门查询</h3>
        <div class="mt-3">
          <div v-if="isLoading" class="loading-text">加载中...</div>
          <div v-else-if="popularQueries.length === 0" class="empty-text">暂无热门查询数据</div>
          <div v-else>
            <div class="flex justify-between items-center py-2 border-b border-gray-700" v-for="(query, index) in popularQueries" :key="index">
              <span>{{ index + 1 }}. {{ query.text }}</span>
              <span class="text-muted">{{ query.count }}次</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card">
        <h3>知识库统计</h3>
        <div class="mt-3">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <div class="text-muted">总文档数</div>
              <div class="text-2xl font-bold">{{ isLoading ? '加载中...' : knowledgeBaseStats?.total_documents || 0 }}</div>
            </div>
            <div>
              <div class="text-muted">总分块数</div>
              <div class="text-2xl font-bold">{{ isLoading ? '加载中...' : knowledgeBaseStats?.total_chunks || 0 }}</div>
            </div>
            <div>
              <div class="text-muted">分块大小</div>
              <div class="text-2xl font-bold">{{ isLoading ? '加载中...' : knowledgeBaseStats?.chunk_size + '字' || '0字' }}</div>
            </div>
            <div>
              <div class="text-muted">重叠字数</div>
              <div class="text-2xl font-bold">{{ isLoading ? '加载中...' : knowledgeBaseStats?.overlap_size + '字' || '0字' }}</div>
            </div>
          </div>
          
          <div class="mt-4">
            <h4>文档类型分布</h4>
            <div class="mt-2">
              <div v-if="isLoading" class="loading-text">加载中...</div>
              <div v-else-if="Object.keys(documentTypeStats).length === 0" class="empty-text">暂无文档类型数据</div>
              <div v-else>
                <div class="chart-container">
                  <div class="bar-chart">
                    <div 
                      v-for="(count, type) in documentTypeStats" 
                      :key="type" 
                      class="bar-item"
                    >
                      <div class="bar-label">{{ type }}</div>
                      <div class="bar-wrapper">
                        <div 
                          class="bar" 
                          :style="{ width: `${(count / Math.max(...Object.values(documentTypeStats))) * 100}%` }"
                        ></div>
                        <div class="bar-count">{{ count }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// 热门查询类型
interface PopularQuery {
  text: string
  count: number
}

// 使用统计类型
interface UsageStats {
  total_queries: number
  average_response_time: number
  accuracy_rate: number
  daily_stats: Array<{
    date: string
    queries: number
    response_time: number
  }>
}

// 知识库统计类型
interface KnowledgeBaseStats {
  total_documents: number
  total_chunks: number
  chunk_size: number
  overlap_size: number
}

// 文档类型
interface Document {
  id: number
  title: string
  filename: string
  file_size: number
  file_type: string
  status: string
  created_by: number
  created_at: string
}

const popularQueries = ref<PopularQuery[]>([])
const usageStats = ref<UsageStats | null>(null)
const knowledgeBaseStats = ref<KnowledgeBaseStats | null>(null)
const isLoading = ref(false)
const documents = ref<Document[]>([])
const documentTypeStats = ref<Record<string, number>>({})

// 获取使用统计数据
const fetchUsageStats = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/analytics/usage')
    if (response.ok) {
      const data = await response.json()
      if (data.code === 200 && data.data) {
        usageStats.value = data.data
      }
    }
  } catch (error) {
    console.error('获取使用统计失败:', error)
  }
}

// 获取热门查询数据
const fetchPopularQueries = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/analytics/hot-queries')
    if (response.ok) {
      const data = await response.json()
      if (data.code === 200 && data.data) {
        popularQueries.value = data.data.map((item: any) => ({
          text: item.query,
          count: item.count
        }))
      }
    }
  } catch (error) {
    console.error('获取热门查询失败:', error)
  }
}

// 获取知识库统计数据
const fetchKnowledgeBaseStats = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/knowledge-base/stats')
    if (response.ok) {
      const data = await response.json()
      if (data.code === 200 && data.data) {
        knowledgeBaseStats.value = {
          total_documents: data.data.total_documents,
          total_chunks: data.data.total_chunks,
          chunk_size: 500, // 固定值，可从后端获取
          overlap_size: 50 // 固定值，可从后端获取
        }
      } else if (data.total_documents) {
        // 直接返回数据的情况
        knowledgeBaseStats.value = {
          total_documents: data.total_documents,
          total_chunks: data.total_chunks,
          chunk_size: 500,
          overlap_size: 50
        }
      }
    }
  } catch (error) {
    console.error('获取知识库统计失败:', error)
  }
}

// 获取文档列表
const fetchDocuments = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/documents')
    if (response.ok) {
      const data = await response.json()
      documents.value = data
      calculateDocumentTypeStats()
    }
  } catch (error) {
    console.error('获取文档列表失败:', error)
  }
}

// 统计文档类型分布
const calculateDocumentTypeStats = () => {
  const stats: Record<string, number> = {};
  documents.value.forEach(doc => {
    const fileType = doc.file_type.toUpperCase();
    stats[fileType] = (stats[fileType] || 0) + 1;
  });
  documentTypeStats.value = stats;
}

const fetchAnalytics = async () => {
  isLoading.value = true
  try {
    await Promise.all([
      fetchUsageStats(),
      fetchPopularQueries(),
      fetchKnowledgeBaseStats(),
      fetchDocuments()
    ])
  } catch (error) {
    console.error('获取统计数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchAnalytics()
})
</script>

<style scoped>
.analytics-page {
  padding: 0;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background-color: #1e293b;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border: 1px solid #475569;
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  transform: translateY(-2px);
}

.stat-title {
  color: #cbd5e1;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-change {
  font-size: 0.75rem;
  font-weight: 600;
}

.stat-change.positive {
  color: #10b981;
}

.stat-change.negative {
  color: #ef4444;
}

/* 网格布局 */
.grid {
  display: grid;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.md\:grid-cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.gap-4 {
  gap: 1rem;
}

/* 卡片样式 */
.card {
  background-color: #1e293b;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border: 1px solid #475569;
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  transform: translateY(-2px);
}

/* 弹性布局 */
.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.items-center {
  align-items: center;
}

.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.border-b {
  border-bottom: 1px solid #475569;
}

.mt-3 {
  margin-top: 1rem;
}

.mt-4 {
  margin-top: 1.5rem;
}

/* 文本样式 */
.text-muted {
  color: #94a3b8;
}

.text-2xl {
  font-size: 1.5rem;
}

.font-bold {
  font-weight: 700;
}

/* 加载和空数据状态 */
.loading-text {
  color: #94a3b8;
  text-align: center;
  padding: 1rem;
  font-style: italic;
}

.empty-text {
  color: #94a3b8;
  text-align: center;
  padding: 1rem;
  font-style: italic;
}

/* 图表容器 */
.chart-container {
  background-color: #334155;
  border-radius: 0.75rem;
  padding: 1.5rem;
  height: 300px;
  border: 1px solid #475569;
}

/* 柱状图 */
.bar-chart {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1rem;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.bar-label {
  width: 60px;
  font-weight: 600;
  color: #cbd5e1;
  text-align: right;
}

.bar-wrapper {
  flex: 1;
  height: 30px;
  background-color: #475569;
  border-radius: 0.25rem;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  padding: 0 10px;
}

.bar {
  height: 20px;
  background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 0.25rem;
  transition: width 0.5s ease;
}

.bar-count {
  position: absolute;
  right: 10px;
  font-weight: 600;
  color: #cbd5e1;
  font-size: 0.875rem;
}

/* 图表占位符 */
.chart-placeholder {
  background-color: #334155;
  border-radius: 0.75rem;
  padding: 2rem;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 1.125rem;
  border: 2px dashed #475569;
  transition: all 0.3s ease;
}

.chart-placeholder:hover {
  border-color: #6366f1;
  color: #cbd5e1;
}
</style>