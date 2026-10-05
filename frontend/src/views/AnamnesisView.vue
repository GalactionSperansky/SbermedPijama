<script setup>
import { computed, nextTick, ref } from 'vue'
import { AlertTriangle, ArrowRight, CheckCircle2, RotateCcw, Send, ShieldCheck } from '@lucide/vue'
import PageHero from '../components/PageHero.vue'
import DinoAvatar from '../components/DinoAvatar.vue'
import { api } from '../services/api'

const initialMessage = 'Здравствуйте! Расскажите своими словами, что вас беспокоит. Я задам несколько уточняющих вопросов и помогу выбрать врача.'
const dialog = ref([{ from: 'assistant', text: initialMessage }])
const input = ref('')
const answersCount = ref(0)
const finished = ref(false)
const loading = ref(false)
const error = ref('')
const sessionId = ref(null)
const result = ref(null)
const chat = ref(null)
const progress = computed(() => finished.value ? 100 : Math.min(85, answersCount.value * 22))
const assistantStatus = computed(() => result.value?.source?.startsWith('mock') ? 'демо-режим' : 'ИИ-помощник')
const appointmentLink = computed(() => ({
  path: '/appointment',
  query: {
    ...(result.value?.specialty ? { specialty: result.value.specialty } : {}),
    ...(result.value?.recommended_doctor?.id ? { doctor: result.value.recommended_doctor.id } : {}),
  },
}))

async function scrollBottom() {
  await nextTick()
  if (chat.value) chat.value.scrollTop = chat.value.scrollHeight
}

async function send() {
  const text = input.value.trim()
  if (!text || finished.value || loading.value) return
  dialog.value.push({ from: 'user', text })
  input.value = ''
  error.value = ''
  loading.value = true
  answersCount.value += 1
  await scrollBottom()
  try {
    const data = await api('/anamnesis/chat/', {
      method: 'POST',
      body: JSON.stringify({ message: text, ...(sessionId.value ? { session_id: sessionId.value } : {}) }),
    })
    sessionId.value = data.session_id
    result.value = data
    dialog.value.push({ from: 'assistant', text: data.message })
    finished.value = data.anamnesis_complete
  } catch (requestError) {
    answersCount.value = Math.max(0, answersCount.value - 1)
    error.value = requestError.message
  } finally {
    loading.value = false
    scrollBottom()
  }
}

function restart() {
  dialog.value = [{ from: 'assistant', text: initialMessage }]
  input.value = ''
  answersCount.value = 0
  finished.value = false
  loading.value = false
  error.value = ''
  sessionId.value = null
  result.value = null
}
</script>

<template>
  <div>
    <PageHero eyebrow="Предварительный анамнез" title="Подготовимся к приёму вместе" text="Динозаврик задаст вопросы по ситуации и подготовит предварительный маршрут. Это не диагноз и не замена врачу." />
    <section class="section compact-section">
      <div class="container intake-layout">
        <div class="chat-card">
          <div class="chat-header">
            <div class="assistant-topline"><DinoAvatar assistant size="small" /><div><strong>Динозаврик</strong><span><i></i> {{ assistantStatus }}</span></div></div>
            <button class="icon-button" type="button" aria-label="Начать заново" @click="restart"><RotateCcw :size="19" /></button>
          </div>
          <div class="chat-progress"><span :style="{ width: `${progress}%` }"></span></div>
          <div ref="chat" class="chat-messages" aria-live="polite">
            <div v-for="(message, index) in dialog" :key="index" class="chat-row" :class="message.from">
              <DinoAvatar v-if="message.from === 'assistant'" assistant size="mini" />
              <div class="chat-bubble">{{ message.text }}</div>
            </div>
            <div v-if="loading" class="chat-row assistant">
              <DinoAvatar assistant size="mini" />
              <div class="chat-bubble chat-thinking"><span></span><span></span><span></span></div>
            </div>
            <p v-if="error" class="form-error">{{ error }}</p>
            <div v-if="finished && result" class="result-card" :class="{ urgent: result.urgency === 'urgent' }">
              <span class="result-icon"><AlertTriangle v-if="result.urgency === 'urgent'" :size="27" /><CheckCircle2 v-else :size="27" /></span>
              <div>
                <small>{{ result.urgency === 'urgent' ? 'Требуется срочная помощь' : 'Предварительный маршрут' }}</small>
                <h3>{{ result.specialty || (result.urgency === 'urgent' ? 'Экстренная помощь' : 'Консультация врача') }}</h3>
                <p>{{ result.summary }}</p>
                <div v-if="result.recommended_doctor" class="recommended-doctor">
                  <small>Рекомендуемый врач</small>
                  <strong>{{ result.recommended_doctor.full_name }}</strong>
                  <span>Стаж {{ result.recommended_doctor.experience_years }} лет</span>
                </div>
                <p v-if="result.urgency === 'urgent'" class="urgent-reminder">Сначала обратитесь за экстренной помощью: плановая запись не заменяет звонок 112 или 103.</p>
                <RouterLink :to="appointmentLink" class="button button-primary button-small">{{ result.urgency === 'urgent' ? 'Перейти к записи' : 'Выбрать время' }} <ArrowRight :size="16" /></RouterLink>
              </div>
            </div>
          </div>
          <form v-if="!finished" class="chat-input" @submit.prevent="send">
            <input v-model="input" :disabled="loading" aria-label="Ответ" placeholder="Напишите ответ…" autocomplete="off" />
            <button type="submit" :disabled="loading || !input.trim()" aria-label="Отправить"><Send :size="20" /></button>
          </form>
        </div>

        <aside class="intake-sidebar">
          <div class="info-card"><ShieldCheck :size="23" class="blue-icon" /><h3>Как используются ответы</h3><p>Контакты берутся из профиля. Модели передаются только медицински значимые сведения, а диалог сохраняется в сервисе.</p></div>
          <div class="info-card warning-card"><AlertTriangle :size="22" /><h3>При экстренной ситуации</h3><p>Если вам трудно дышать, есть сильное кровотечение, потеря сознания или внезапное нарушение речи — звоните 112 или 103.</p></div>
        </aside>
      </div>
    </section>
  </div>
</template>
