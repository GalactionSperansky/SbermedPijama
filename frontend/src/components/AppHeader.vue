<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { LogIn, LogOut, Menu, X } from '@lucide/vue'
import DinoAvatar from './DinoAvatar.vue'
import { authStore } from '../stores/auth'

const isOpen = ref(false)
const router = useRouter()
const links = [
  { to: '/appointment', label: 'Запись' },
  { to: '/anamnesis', label: 'Анамнез' },
  { to: '/tracker', label: 'Трекер' },
  { to: '/support', label: 'Поддержка' },
]

async function signOut() {
  await authStore.logout()
  isOpen.value = false
  router.push('/')
}
</script>

<template>
  <header class="site-header">
    <div class="container header-inner">
      <RouterLink to="/" class="brand" @click="isOpen = false">
        <span class="brand-mark"><img src="/branding/dino_in_pijames_with_statescope.png" alt="" /></span>
        <span>D<span class="brand-ai">ИИ</span>nozavr</span>
      </RouterLink>

      <nav class="desktop-nav" aria-label="Основная навигация">
        <RouterLink v-for="link in links" :key="link.to" :to="link.to">{{ link.label }}</RouterLink>
      </nav>

      <RouterLink v-if="!authStore.state.user" to="/auth" class="button button-small desktop-account"><LogIn :size="16" /> Войти</RouterLink>
      <div v-else class="account-menu desktop-account">
        <RouterLink :to="authStore.state.user.role === 'admin' ? '/admin/dashboard' : '/profile'" class="account-link"><DinoAvatar :user="authStore.state.user" size="mini" /><span>{{ authStore.state.user.first_name || 'Профиль' }}</span></RouterLink>
        <button type="button" aria-label="Выйти" @click="signOut"><LogOut :size="16" /></button>
      </div>

      <button class="mobile-menu-button" type="button" aria-label="Открыть меню" @click="isOpen = !isOpen">
        <X v-if="isOpen" />
        <Menu v-else />
      </button>
    </div>

    <Transition name="menu">
      <nav v-if="isOpen" class="mobile-nav" aria-label="Мобильная навигация">
        <RouterLink v-for="link in links" :key="link.to" :to="link.to" @click="isOpen = false">{{ link.label }}</RouterLink>
        <RouterLink v-if="!authStore.state.user" to="/auth" @click="isOpen = false">Войти или зарегистрироваться</RouterLink>
        <template v-else>
          <RouterLink :to="authStore.state.user.role === 'admin' ? '/admin/dashboard' : '/profile'" @click="isOpen = false">{{ authStore.state.user.role === 'admin' ? 'Панель администратора' : 'Личный кабинет' }}</RouterLink>
          <button class="mobile-logout" type="button" @click="signOut">Выйти</button>
        </template>
      </nav>
    </Transition>
  </header>
</template>
