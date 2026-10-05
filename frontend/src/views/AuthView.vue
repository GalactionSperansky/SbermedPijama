<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight, LockKeyhole, Mail, Phone, ShieldCheck, UserRound } from '@lucide/vue'
import DinoAvatar from '../components/DinoAvatar.vue'
import { authStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const mode = ref(route.query.mode === 'register' ? 'register' : 'login')
const error = ref('')
const form = ref({ first_name: '', last_name: '', middle_name: '', email: '', phone: '', password: '' })
const title = computed(() => mode.value === 'login' ? 'С возвращением' : 'Создайте профиль пациента')

async function submit() {
  error.value = ''
  try {
    const user = mode.value === 'login'
      ? await authStore.login({ email: form.value.email, password: form.value.password })
      : await authStore.register(form.value)
    const target = route.query.redirect || (user.role === 'admin' ? '/admin/dashboard' : '/profile')
    router.push(target)
  } catch (err) {
    error.value = err.message
  }
}
</script>

<template>
  <section class="auth-page">
    <div class="auth-glow"></div>
    <div class="container auth-layout">
      <div class="auth-intro">
        <DinoAvatar assistant size="hero" />
        <span class="eyebrow light">DИИnozavr рядом</span>
        <h1>О здоровье заботиться проще вместе</h1>
        <p>Записывайтесь к врачу, храните медкарту и следуйте назначениям в одном личном кабинете.</p>
        <div class="auth-benefits"><span><ShieldCheck /> Медицинские данные защищены</span><span><UserRound /> Один профиль для всех сервисов</span></div>
      </div>

      <form class="auth-card" @submit.prevent="submit">
        <div class="auth-switch"><button type="button" :class="{ active: mode === 'login' }" @click="mode = 'login'; error = ''">Вход</button><button type="button" :class="{ active: mode === 'register' }" @click="mode = 'register'; error = ''">Регистрация</button></div>
        <h2>{{ title }}</h2>
        <p>{{ mode === 'login' ? 'Войдите как пациент или администратор.' : 'Аватар с динозавром создастся автоматически.' }}</p>
        <div v-if="mode === 'register'" class="form-grid two-columns">
          <label class="field"><span>Имя</span><div class="input-icon"><UserRound /><input v-model="form.first_name" required placeholder="Имя" /></div></label>
          <label class="field"><span>Фамилия</span><input v-model="form.last_name" placeholder="Фамилия" /></label>
          <label class="field"><span>Отчество</span><input v-model="form.middle_name" placeholder="Отчество" /></label>
        </div>
        <label class="field"><span>Email</span><div class="input-icon"><Mail /><input v-model="form.email" required type="email" placeholder="name@example.ru" /></div></label>
        <label v-if="mode === 'register'" class="field"><span>Телефон</span><div class="input-icon"><Phone /><input v-model="form.phone" required type="tel" placeholder="+7 999 000-00-00" /></div></label>
        <label class="field"><span>Пароль</span><div class="input-icon"><LockKeyhole /><input v-model="form.password" required type="password" minlength="8" placeholder="Не менее 8 символов" /></div></label>
        <p v-if="error" class="form-error">{{ error }}</p>
        <button class="button button-primary full-width" :disabled="authStore.state.loading">{{ authStore.state.loading ? 'Подождите…' : (mode === 'login' ? 'Войти' : 'Создать профиль') }} <ArrowRight :size="18" /></button>
        <small class="auth-note">Администраторы входят через ту же форму. Учётную запись администратора создаёт владелец системы.</small>
      </form>
    </div>
  </section>
</template>
