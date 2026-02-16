import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import HomeView from '../core/views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { guestOnly: true }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../features/dashboard/views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/schedule',
    name: 'schedule',
    component: () => import('../features/schedule/views/ScheduleView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../features/admin/views/AdminDashboardView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'admin-users',
    component: () => import('../features/admin/views/UsersManagementView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/logs',
    name: 'admin-logs',
    component: () => import('../features/admin/views/SystemLogsView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/groups',
    name: 'admin-groups',
    component: () => import('../features/admin/views/GroupsView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/auditoriums',
    name: 'admin-auditoriums',
    component: () => import('../features/admin/views/AuditoriumsView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Навигационный гард
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated
  const userRole = authStore.user?.role?.toLowerCase()

  // 1. Проверка авторизации
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'home' })
  }

  // 2. Проверка прав администратора
  if (to.meta.requiresAdmin && userRole !== 'admin') {
    return next({ name: 'dashboard' })
  }

  // 3. Запрет входа на страницу логина для авторизованных
  if (to.meta.guestOnly && isAuthenticated) {
    return next({ name: 'dashboard' })
  }

  next()
})

export default router
