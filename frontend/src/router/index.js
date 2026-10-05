import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AppointmentView from '../views/AppointmentView.vue'
import ProfileView from '../views/ProfileView.vue'
import AnamnesisView from '../views/AnamnesisView.vue'
import MedicationTrackerView from '../views/MedicationTrackerView.vue'
import SupportView from '../views/SupportView.vue'
import AuthView from '../views/AuthView.vue'
import AdminView from '../views/AdminView.vue'
import { authStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    { path: '/', component: HomeView, name: 'home' },
    { path: '/auth', component: AuthView, name: 'auth' },
    { path: '/appointment', component: AppointmentView, name: 'appointment', meta: { requiresAuth: true } },
    { path: '/profile', component: ProfileView, name: 'profile', meta: { requiresAuth: true } },
    { path: '/anamnesis', component: AnamnesisView, name: 'anamnesis', meta: { requiresAuth: true } },
    { path: '/tracker', component: MedicationTrackerView, name: 'tracker', meta: { requiresAuth: true } },
    { path: '/support', component: SupportView, name: 'support', meta: { requiresAuth: true } },
    { path: '/admin/dashboard', component: AdminView, name: 'admin', meta: { requiresAuth: true, admin: true } },
  ],
})

router.beforeEach(async (to) => {
  await authStore.initialize()
  if (to.meta.requiresAuth && !authStore.state.user) {
    return { name: 'auth', query: { redirect: to.fullPath } }
  }
  if (to.meta.admin && authStore.state.user?.role !== 'admin') return { name: 'profile' }
  if (to.name === 'auth' && authStore.state.user) {
    return { name: authStore.state.user.role === 'admin' ? 'admin' : 'profile' }
  }
})

export default router
