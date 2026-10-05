<script setup>
import { onMounted, ref } from 'vue'
import { CalendarDays, Headphones, Stethoscope, UsersRound } from '@lucide/vue'
import PageHero from '../components/PageHero.vue'
import { api } from '../services/api'

const stats = ref({ patients: 0, doctors: 0, appointments: 0, support_open: 0 })
onMounted(async () => {
  try { stats.value = await api('/admin/summary/') } catch { /* status cards stay at zero */ }
})
const cards = [
  ['patients', 'Пациенты', UsersRound],
  ['doctors', 'Врачи', Stethoscope],
  ['appointments', 'Записи', CalendarDays],
  ['support_open', 'Поддержка', Headphones],
]
</script>

<template>
  <div>
    <PageHero eyebrow="Панель администратора" title="Управление DИИnozavr" text="Основные показатели клиники и быстрый переход к управлению данными." />
    <section class="section compact-section"><div class="container admin-grid"><article v-for="card in cards" :key="card[0]" class="admin-stat"><span><component :is="card[2]" /></span><div><strong>{{ stats[card[0]] }}</strong><p>{{ card[1] }}</p></div></article></div><div class="container admin-note"><h2>Управление данными</h2><p>Врачи, расписание, медкарты и обращения редактируются в защищённой Django Admin.</p><a class="button button-primary" href="http://localhost:8000/admin/" target="_blank" rel="noreferrer">Открыть Django Admin</a></div></section>
  </div>
</template>

