import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Topology',
    component: () => import('@/views/TopologyView.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue')
  },
  {
    path: '/detection',
    name: 'Detection',
    component: () => import('@/views/DetectionView.vue')
  },
  {
    path: '/execution',
    name: 'Execution',
    component: () => import('@/views/ExecutionView.vue')
  },
  {
    path: '/report',
    name: 'Report',
    component: () => import('@/views/ReportView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
