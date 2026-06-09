import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../views/LoginPage.vue'
import MainLayout from '../views/MainLayout.vue'
import QA from '../views/QA.vue'
import Docs from '../views/DocsPage.vue'
import Knowledge from '../views/KnowledgePage.vue'
import Analytics from '../views/AnalyticsPage.vue'
import Settings from '../views/SettingsPage.vue'
import History from '../views/HistoryPage.vue'

const routes = [
  {
    path: '/',
    name: 'login',
    component: LoginPage
  },
  {
    path: '/app',
    name: 'main',
    component: MainLayout,
    children: [
      {
        path: 'qa',
        name: 'qa',
        component: QA
      },
      {
        path: 'docs',
        name: 'docs',
        component: Docs
      },
      {
        path: 'knowledge',
        name: 'knowledge',
        component: Knowledge
      },
      {
        path: 'analytics',
        name: 'analytics',
        component: Analytics
      },
      {
        path: 'settings',
        name: 'settings',
        component: Settings
      },
      {
        path: 'history',
        name: 'history',
        component: History
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
