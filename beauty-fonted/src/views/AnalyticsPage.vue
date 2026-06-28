<template>
  <div class="analytics-page">
    <div class="page-header mb-4">
      <h2 class="page-title">系统使用统计</h2>
      <p class="page-subtitle text-muted">监控系统对话质量与知识库覆盖率</p>
    </div>

    <!-- 核心指标区 -->
    <div class="stats-grid mb-5">
      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-title">总对话次数</div>
          <div class="stat-icon-small">💬</div>
        </div>
        <div class="stat-value">{{ formatNumber(summary.total_conversations) }}</div>
        <div class="stat-change" :class="getChangeClass(summary.conversations_trend)">
          <span class="trend-icon">{{ summary.conversations_trend >= 0 ? '↑' : '↓' }}</span>
          {{ Math.abs(summary.conversations_trend) }}% 较上周
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-title">平均对话轮数</div>
          <div class="stat-icon-small">🔄</div>
        </div>
        <div class="stat-value">{{ summary.avg_turns.toFixed(1) }}</div>
        <div class="stat-change" :class="getChangeClass(summary.turns_trend)">
          <span class="trend-icon">{{ summary.turns_trend >= 0 ? '↑' : '↓' }}</span>
          {{ Math.abs(summary.turns_trend) }}% 较上周
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-title">知识库命中率</div>
          <div class="stat-icon-small">🎯</div>
        </div>
        <div class="stat-value">{{ summary.hit_rate }}%</div>
        <div class="stat-change" :class="getChangeClass(summary.hit_rate_trend)">
          <span class="trend-icon">{{ summary.hit_rate_trend >= 0 ? '↑' : '↓' }}</span>
          {{ Math.abs(summary.hit_rate_trend) }}% 较上周
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-header">
          <div class="stat-title">用户满意度</div>
          <div class="stat-icon-small">⭐</div>
        </div>
        <div class="stat-value">{{ summary.satisfaction_score.toFixed(1) }}</div>
        <div class="stat-change text-muted">满分 5.0</div>
      </div>
    </div>

    <div class="charts-grid">
      <!-- 每日对话趋势图 -->
      <div class="card chart-card">
        <h3 class="chart-title">每日对话趋势 (最近7天)</h3>
        <div class="chart-container">
          <div class="mock-bar-chart" v-if="!isLoading">
            <div class="y-axis">
              <span>500</span>
              <span>400</span>
              <span>300</span>
              <span>200</span>
              <span>100</span>
              <span>0</span>
            </div>
            <div class="bars-area">
              <div class="bar-group" v-for="(item, index) in trendData" :key="index">
                <div class="bar-bg">
                  <div class="bar-fill" :style="`height: ${(item.count / 500) * 100}%`">
                    <span class="bar-tooltip">{{ item.count }}</span>
                  </div>
                </div>
                <div class="x-label">{{ formatDateShort(item.date) }}</div>
              </div>
            </div>
          </div>
          <div v-else class="loading-state">加载数据中...</div>
        </div>
      </div>

      <!-- 热门话题 -->
      <div class="card chart-card">
        <h3 class="chart-title">热门咨询话题</h3>
        <div class="topics-list" v-if="!isLoading">
          <div class="topic-item" v-for="(topic, index) in topTopics" :key="index">
            <div class="topic-info">
              <span class="topic-rank" :class="`rank-${index + 1}`">{{ index + 1 }}</span>
              <span class="topic-name">{{ topic.name }}</span>
            </div>
            <div class="topic-progress-container">
              <div class="topic-progress-bar" :style="`width: ${topic.percentage}%`"></div>
              <span class="topic-percent">{{ topic.percentage }}%</span>
            </div>
          </div>
        </div>
        <div v-else class="loading-state">加载数据中...</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import gsap from 'gsap'

// 模拟数据接口
interface SummaryStats {
  total_conversations: number
  conversations_trend: number
  avg_turns: number
  turns_trend: number
  hit_rate: number
  hit_rate_trend: number
  satisfaction_score: number
}

interface TrendData {
  date: string
  count: number
}

interface TopicData {
  name: string
  percentage: number
}

const isLoading = ref(true)

const summary = ref<SummaryStats>({
  total_conversations: 12580,
  conversations_trend: 12.5,
  avg_turns: 4.2,
  turns_trend: -2.1,
  hit_rate: 87.5,
  hit_rate_trend: 3.2,
  satisfaction_score: 4.8
})

const trendData = ref<TrendData[]>([])
const topTopics = ref<TopicData[]>([
  { name: '敏感肌护肤步骤', percentage: 28 },
  { name: '抗老精华成分对比', percentage: 22 },
  { name: '光电医美后修复', percentage: 18 },
  { name: '防晒霜选择推荐', percentage: 15 },
  { name: '美白淡斑方案', percentage: 10 },
  { name: '换季过敏应对', percentage: 7 }
])

const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getChangeClass = (trend: number) => {
  if (trend > 0) return 'text-success'
  if (trend < 0) return 'text-error'
  return 'text-muted'
}

const formatDateShort = (dateStr: string) => {
  const parts = dateStr.split('-')
  return `${parts[1]}/${parts[2]}`
}

const generateMockTrend = () => {
  const data: TrendData[] = []
  const today = new Date()
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().split('T')[0]
    data.push({
      date: dateStr,
      count: Math.floor(Math.random() * 200) + 200 // 200-400 random
    })
  }
  trendData.value = data
}

const animateElements = () => {
  nextTick(() => {
    const mm = gsap.matchMedia()
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      gsap.from('.stat-card', {
        autoAlpha: 0,
        y: 10,
        duration: 0.6,
        stagger: 0.08,
        ease: 'power3.out',
        clearProps: 'all'
      })
      gsap.from('.chart-card', {
        autoAlpha: 0,
        y: 15,
        duration: 0.7,
        stagger: 0.1,
        ease: 'power3.out',
        clearProps: 'all'
      })
    })
  })
}

onMounted(() => {
  generateMockTrend()
  isLoading.value = false
  animateElements()
})
</script>

<style scoped>
.analytics-page {
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

.mb-4 { margin-bottom: 1.5rem; }
.mb-5 { margin-bottom: 2rem; }

/* 核心指标卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.stat-card {
  background-color: var(--surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  transition: all 0.3s var(--ease);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--border);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stat-title {
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-icon-small {
  font-size: 1.25rem;
  opacity: 0.8;
}

.stat-value {
  font-size: 2rem;
  font-family: var(--font-display);
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

.stat-change {
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 500;
}

.trend-icon {
  font-weight: bold;
}

.text-success { color: var(--success); }
.text-error { color: var(--error); }
.text-muted { color: var(--text-muted); }

/* 图表区 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.chart-card {
  display: flex;
  flex-direction: column;
}

.chart-title {
  font-size: 1.1rem;
  color: var(--text);
  margin: 0 0 1.5rem 0;
  font-weight: 600;
  font-family: var(--font-display);
}

.chart-container {
  flex: 1;
  min-height: 250px;
  position: relative;
}

.loading-state {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-style: italic;
  background-color: rgba(251, 248, 245, 0.5);
}

/* 模拟柱状图 */
.mock-bar-chart {
  display: flex;
  height: 100%;
  padding-bottom: 1.5rem;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-right: 1rem;
  border-right: 1px dashed var(--border);
  color: var(--text-muted);
  font-size: 0.75rem;
  font-family: var(--font-mono);
  text-align: right;
  width: 40px;
}

.bars-area {
  flex: 1;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  padding-left: 1rem;
  position: relative;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  height: 100%;
  width: 30px;
}

.bar-bg {
  flex: 1;
  width: 100%;
  background-color: var(--border-light);
  border-radius: var(--radius-sm);
  position: relative;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.bar-fill {
  width: 100%;
  background: linear-gradient(to top, var(--primary), var(--primary-light));
  border-radius: var(--radius-sm);
  position: relative;
  transition: height 1s var(--ease);
  cursor: pointer;
}

.bar-fill:hover {
  background: linear-gradient(to top, var(--primary-dark), var(--primary));
}

.bar-tooltip {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--text);
  color: #fff;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
  font-family: var(--font-mono);
}

.bar-fill:hover .bar-tooltip {
  opacity: 1;
}

.x-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

/* 热门话题列表 */
.topics-list {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.topic-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.topic-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 140px;
}

.topic-rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--surface-alt);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: var(--font-mono);
}

.rank-1 { background-color: rgba(196, 136, 122, 0.2); color: var(--primary-dark); }
.rank-2 { background-color: rgba(196, 136, 122, 0.15); color: var(--primary); }
.rank-3 { background-color: rgba(196, 136, 122, 0.1); color: var(--primary-light); }

.topic-name {
  font-size: 0.9rem;
  color: var(--text);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.topic-progress-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.topic-progress-bar {
  height: 6px;
  background-color: var(--primary-light);
  border-radius: var(--radius-pill);
  transition: width 1s var(--ease);
}

.topic-percent {
  font-size: 0.8rem;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  width: 35px;
  text-align: right;
}

@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .charts-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr; }
}
</style>