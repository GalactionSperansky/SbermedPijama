import { reactive, readonly } from 'vue'
import { api } from '../services/api'

const state = reactive({
  user: null,
  loading: false,
  initialized: false,
})

async function initialize() {
  if (state.initialized) return
  const token = localStorage.getItem('diinozavr_token')
  if (token) {
    try {
      state.user = await api('/auth/me/')
    } catch {
      localStorage.removeItem('diinozavr_token')
    }
  }
  state.initialized = true
}

async function login(payload) {
  state.loading = true
  try {
    const data = await api('/auth/login/', { method: 'POST', body: JSON.stringify(payload) })
    localStorage.setItem('diinozavr_token', data.token)
    state.user = data.user
    state.initialized = true
    return data.user
  } finally {
    state.loading = false
  }
}

async function register(payload) {
  state.loading = true
  try {
    const data = await api('/auth/register/', { method: 'POST', body: JSON.stringify(payload) })
    localStorage.setItem('diinozavr_token', data.token)
    state.user = data.user
    state.initialized = true
    return data.user
  } finally {
    state.loading = false
  }
}

async function logout() {
  try {
    if (state.user) await api('/auth/logout/', { method: 'POST' })
  } finally {
    localStorage.removeItem('diinozavr_token')
    state.user = null
  }
}

async function updateProfile(payload) {
  state.loading = true
  try {
    state.user = await api('/auth/me/', { method: 'PATCH', body: JSON.stringify(payload) })
    return state.user
  } finally {
    state.loading = false
  }
}

export const authStore = {
  state: readonly(state),
  initialize,
  login,
  register,
  updateProfile,
  logout,
}
