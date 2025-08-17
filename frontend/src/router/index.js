import { createRouter, createWebHistory } from 'vue-router'

// Views
import HomeView from '@/views/HomeView.vue'
import MaterialsView from '@/views/MaterialsView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/materials',
    name: 'materials',
    component: MaterialsView
  },
  {
    path: '/receiving',
    name: 'receiving',
    component: () => import('@/views/ReceivingView.vue')
  },
  {
    path: '/storage',
    name: 'storage',
    component: () => import('@/views/StorageView.vue')
  },
  {
    path: '/inspection',
    name: 'inspection',
    component: () => import('@/views/InspectionView.vue')
  },
  {
    path: '/reports',
    name: 'reports',
    component: () => import('@/views/ReportsView.vue')
  },
  {
    path: '/destructive-tests',
    name: 'destructive-tests',
    component: () => import('@/views/DestructiveTestsView.vue')
  },
  {
    path: '/non-destructive-tests',
    name: 'non-destructive-tests',
    component: () => import('@/views/NonDestructiveTestsView.vue')
  },
  {
    path: '/test-results',
    name: 'test-results',
    component: () => import('@/views/TestResultsView.vue')
  },
  {
    path: '/material-request',
    name: 'material-request',
    component: () => import('@/views/MaterialRequestView.vue')
  },
  {
    path: '/production-status',
    name: 'production-status',
    component: () => import('@/views/ProductionStatusView.vue')
  },
  {
    path: '/workflow-config',
    name: 'workflow-config',
    component: () => import('@/views/WorkflowConfigView.vue')
  },
  {
    path: '/users',
    name: 'users',
    component: () => import('@/views/UsersView.vue')
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/SettingsView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router