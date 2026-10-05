<script setup>
import { ref } from 'vue'
import { CheckCircle2, Clock3, Mail, MapPin, MessageCircle, Phone } from '@lucide/vue'
import PageHero from '../components/PageHero.vue'
import DinoAvatar from '../components/DinoAvatar.vue'
import { authStore } from '../stores/auth'
import { api } from '../services/api'

const sent = ref(false)
const form = ref({ message: '' })
const error = ref('')

async function submit() {
  error.value = ''
  try {
    await api('/support/', { method: 'POST', body: JSON.stringify(form.value) })
    sent.value = true
  } catch (err) {
    error.value = err.message
  }
}
</script>

<template>
  <div>
    <PageHero eyebrow="Мы рядом" title="Контакты и поддержка" text="Поможем с записью, личным кабинетом и работой сервиса." />
    <section class="section compact-section">
      <div class="container support-layout">
        <div class="support-contacts">
          <article class="contact-card"><span><Phone /></span><div><small>Позвонить</small><h3>+7 (987) 654-32-10</h3><p>Ежедневно, 08:00–21:00</p></div></article>
          <article class="contact-card"><span><Mail /></span><div><small>Написать</small><h3>diinozavr@health.ru</h3><p>Ответим в течение рабочего дня</p></div></article>
          <article class="contact-card"><span><MapPin /></span><div><small>Клиника</small><h3>Мезозойский проспект, дом 67</h3><p>Москва</p></div></article>
          <div class="support-hours"><Clock3 :size="22" /><div><strong>Служба поддержки</strong><p>Пн–Вс · 08:00–21:00</p></div></div>
        </div>

        <form v-if="!sent" class="form-card support-form" @submit.prevent="submit">
          <span class="service-icon blue"><MessageCircle :size="24" /></span><h2>Напишите нам</h2><p>Опишите вопрос — мы свяжемся с вами.</p>
          <div class="patient-inline"><DinoAvatar :user="authStore.state.user" size="small" /><div><strong>{{ authStore.state.user?.full_name }}</strong><p>Ответ придёт на {{ authStore.state.user?.email }}</p></div></div>
          <label class="field"><span>Сообщение</span><textarea v-model="form.message" required rows="5" placeholder="Чем можем помочь?"></textarea></label>
          <p v-if="error" class="form-error">{{ error }}</p>
          <button class="button button-primary full-width" type="submit">Отправить сообщение</button>
        </form>
        <div v-else class="form-card success-state"><span class="success-illustration"><CheckCircle2 :size="45" /></span><h2>Сообщение отправлено</h2><p>Мы ответим на {{ authStore.state.user?.email }} в течение рабочего дня.</p><button class="button button-secondary" @click="sent = false">Отправить ещё</button></div>
      </div>
    </section>
  </div>
</template>
