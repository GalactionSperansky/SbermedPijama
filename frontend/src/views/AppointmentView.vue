<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { CalendarCheck, CheckCircle2, ChevronLeft, ChevronRight, Clock3, MapPin, Stethoscope } from '@lucide/vue'
import PageHero from '../components/PageHero.vue'
import DinoAvatar from '../components/DinoAvatar.vue'
import { authStore } from '../stores/auth'
import { api } from '../services/api'

const route = useRoute()
const doctorOptions = ref([
  { id: 1, full_name: 'Анна Сергеевна Лебедева', specialty_name: 'Оториноларинголог', experience_years: 12, bio: 'Взрослый ЛОР-врач. Специализируется на заболеваниях носа и околоносовых пазух.' },
  { id: 2, full_name: 'Михаил Олегович Воронов', specialty_name: 'Оториноларинголог', experience_years: 8, bio: 'ЛОР-врач для взрослых и детей от 7 лет.' },
  { id: 3, full_name: 'Елена Викторовна Миронова', specialty_name: 'Терапевт', experience_years: 15, bio: 'Терапевт широкого профиля и первичная маршрутизация.' },
  { id: 4, full_name: 'Дарья Андреевна Соколова', specialty_name: 'Аллерголог', experience_years: 9, bio: 'Респираторная аллергия, поллиноз и аллергические реакции.' },
  { id: 5, full_name: 'Мария Игоревна Белова', specialty_name: 'Педиатр', experience_years: 11, bio: 'Принимает детей с рождения.' },
])
const form = ref({ specialty: '', doctor: '', date: '', time: '', complaint: '' })
const submitted = ref(false)
const error = ref('')
const slotError = ref('')
const loadingSlots = ref(false)
const availabilityDays = ref([])
const weekOffset = ref(0)
const specialties = computed(() => [...new Set(doctorOptions.value.map((doctor) => doctor.specialty_name))])
const availableDoctors = computed(() => doctorOptions.value.filter((doctor) => doctor.specialty_name === form.value.specialty))
const selectedDoctor = computed(() => doctorOptions.value.find((doctor) => doctor.id === Number(form.value.doctor)))
const selectedDay = computed(() => availabilityDays.value.find((day) => day.date === form.value.date))
const selectedSlot = computed(() => selectedDay.value?.slots.find((slot) => slot.time === form.value.time))
const today = new Date()
today.setHours(0, 0, 0, 0)

function toLocalDate(value) {
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function weekStartDate() {
  const date = new Date(today)
  date.setDate(date.getDate() + weekOffset.value * 7)
  return date
}

const weekLabel = computed(() => {
  const first = weekStartDate()
  const last = new Date(first)
  last.setDate(last.getDate() + 6)
  const formatter = new Intl.DateTimeFormat('ru-RU', { day: 'numeric', month: 'short' })
  return `${formatter.format(first)} — ${formatter.format(last)}`
})

onMounted(async () => {
  try { doctorOptions.value = await api('/doctors/') } catch { /* use demo catalog */ }
  const querySpecialty = Array.isArray(route.query.specialty) ? route.query.specialty[0] : route.query.specialty
  const queryDoctor = Number(Array.isArray(route.query.doctor) ? route.query.doctor[0] : route.query.doctor)
  const routedDoctor = doctorOptions.value.find((doctor) => doctor.id === queryDoctor)
  if (routedDoctor) {
    form.value.specialty = routedDoctor.specialty_name
    form.value.doctor = routedDoctor.id
    await loadAvailability()
  } else {
    form.value.specialty = specialties.value.includes(querySpecialty) ? querySpecialty : (specialties.value[0] || '')
  }
})

async function loadAvailability() {
  if (!form.value.doctor) {
    availabilityDays.value = []
    return
  }
  loadingSlots.value = true
  slotError.value = ''
  form.value.time = ''
  try {
    const start = toLocalDate(weekStartDate())
    const data = await api(`/availability/?doctor=${form.value.doctor}&from=${start}&days=7`)
    availabilityDays.value = data.days
    if (!data.days.some((day) => day.date === form.value.date)) {
      form.value.date = data.days.find((day) => day.slots.some((slot) => slot.available))?.date || data.days[0]?.date || ''
    }
  } catch (err) {
    availabilityDays.value = []
    slotError.value = err.message
  } finally {
    loadingSlots.value = false
  }
}

function changeDoctor() {
  weekOffset.value = 0
  form.value.date = ''
  loadAvailability()
}

function changeSpecialty() {
  form.value.doctor = ''
  form.value.date = ''
  form.value.time = ''
  availabilityDays.value = []
}

function changeWeek(delta) {
  const next = weekOffset.value + delta
  if (next < 0 || next > 7) return
  weekOffset.value = next
  form.value.date = ''
  loadAvailability()
}

function selectDay(day) {
  form.value.date = day.date
  form.value.time = ''
}

function dayParts(value) {
  const date = new Date(`${value}T12:00:00`)
  return {
    weekday: new Intl.DateTimeFormat('ru-RU', { weekday: 'short' }).format(date).replace('.', ''),
    number: date.getDate(),
    month: new Intl.DateTimeFormat('ru-RU', { month: 'short' }).format(date).replace('.', ''),
  }
}

async function submit() {
  error.value = ''
  try {
    await api('/appointments/', {
      method: 'POST',
      body: JSON.stringify({
        slot: selectedSlot.value?.id,
        complaint: form.value.complaint,
      }),
    })
    submitted.value = true
    window.scrollTo({ top: 240, behavior: 'smooth' })
  } catch (err) {
    error.value = err.message
  }
}
</script>

<template>
  <div>
    <PageHero eyebrow="Запись онлайн" title="Выберите врача и удобное время" text="Несколько шагов — и данные записи появятся в личном кабинете." />
    <section class="section compact-section">
      <div class="container booking-layout">
        <form v-if="!submitted" class="form-card" @submit.prevent="submit">
          <div class="form-section-title"><span>1</span><div><h2>Специалист</h2><p>Выберите направление и врача</p></div></div>
          <div class="form-grid two-columns">
            <label class="field"><span>Специальность</span><select v-model="form.specialty" required @change="changeSpecialty"><option value="" disabled>Выберите направление</option><option v-for="item in specialties" :key="item">{{ item }}</option></select></label>
            <label class="field"><span>Врач</span><select v-model="form.doctor" required @change="changeDoctor"><option value="" disabled>Выберите врача</option><option v-for="item in availableDoctors" :key="item.id" :value="item.id">{{ item.full_name }}</option></select></label>
          </div>
          <div v-if="selectedDoctor" class="doctor-detail-card">
            <div class="doctor-detail-heading">
              <span><Stethoscope :size="21" /></span>
              <div><small>{{ selectedDoctor.specialty_name }}</small><h3>{{ selectedDoctor.full_name }}</h3></div>
            </div>
            <p>{{ selectedDoctor.bio || 'Врач клиники DИИnozavr. Проводит первичные и повторные консультации.' }}</p>
            <strong>Стаж: {{ selectedDoctor.experience_years }} {{ selectedDoctor.experience_years === 1 ? 'год' : selectedDoctor.experience_years < 5 ? 'года' : 'лет' }}</strong>
          </div>
          <div class="form-divider"></div>
          <div class="form-section-title"><span>2</span><div><h2>Дата и время</h2><p>Листайте недели и выбирайте только свободные слоты</p></div></div>
          <div v-if="!form.doctor" class="calendar-placeholder"><CalendarCheck /><p>Сначала выберите врача — покажем его актуальное расписание.</p></div>
          <div v-else class="appointment-calendar">
            <div class="calendar-toolbar"><button type="button" aria-label="Предыдущая неделя" :disabled="weekOffset === 0" @click="changeWeek(-1)"><ChevronLeft /></button><strong>{{ weekLabel }}</strong><button type="button" aria-label="Следующая неделя" :disabled="weekOffset === 7" @click="changeWeek(1)"><ChevronRight /></button></div>
            <div v-if="loadingSlots" class="calendar-loading">Обновляем расписание…</div>
            <template v-else>
              <div class="calendar-days">
                <button v-for="day in availabilityDays" :key="day.date" type="button" :class="{ selected: form.date === day.date, unavailable: !day.slots.some((slot) => slot.available) }" :disabled="!day.slots.some((slot) => slot.available)" @click="selectDay(day)">
                  <span>{{ dayParts(day.date).weekday }}</span><strong>{{ dayParts(day.date).number }}</strong><small>{{ dayParts(day.date).month }}</small>
                </button>
              </div>
              <div v-if="selectedDay" class="field slot-field"><span>Выберите время</span><div class="time-grid"><button v-for="slot in selectedDay.slots" :key="slot.time" type="button" :disabled="!slot.available" :class="{ selected: form.time === slot.time, unavailable: !slot.available }" @click="form.time = slot.time"><strong>{{ slot.time }}</strong></button></div></div>
            </template>
            <p v-if="slotError" class="form-error">{{ slotError }}</p>
          </div>
          <div class="form-divider"></div>
          <div class="form-section-title"><span>3</span><div><h2>Подтверждение</h2><p>Контакты автоматически взяты из профиля</p></div></div>
          <div class="patient-inline"><DinoAvatar :user="authStore.state.user" size="small" /><div><strong>{{ authStore.state.user?.full_name }}</strong><p>{{ authStore.state.user?.phone }} · {{ authStore.state.user?.email }}</p></div></div>
          <label class="field"><span>Кратко опишите жалобу</span><textarea v-model="form.complaint" rows="3" placeholder="Например: заложило ухо после бассейна"></textarea></label>
          <p v-if="error" class="form-error">{{ error }}</p>
          <button class="button button-primary full-width" type="submit" :disabled="!form.time">Подтвердить запись <CalendarCheck :size="19" /></button>
        </form>

        <div v-else class="form-card success-state">
          <span class="success-illustration"><CheckCircle2 :size="45" /></span>
          <span class="eyebrow">Запись создана</span>
          <h2>{{ authStore.state.user?.first_name }}, ждём вас на приёме</h2>
          <div class="appointment-ticket">
            <p><Stethoscope :size="19" /><span><small>{{ form.specialty }}</small><strong>{{ selectedDoctor?.full_name }}</strong></span></p>
            <p><CalendarCheck :size="19" /><span><small>Дата и время</small><strong>{{ form.date }}, {{ form.time }}</strong></span></p>
            <p><MapPin :size="19" /><span><small>Адрес</small><strong>Мезозойский проспект, дом 67</strong></span></p>
          </div>
          <RouterLink to="/profile" class="button button-primary">Перейти в личный кабинет</RouterLink>
        </div>

        <aside class="booking-sidebar">
          <div class="info-card gradient-card"><Clock3 :size="24" /><h3>Не знаете, кого выбрать?</h3><p>Пройдите короткий опрос — помощник предложит подходящее направление.</p><RouterLink to="/anamnesis">Начать опрос →</RouterLink></div>
          <div class="info-card"><h3>Приём в клинике</h3><p><MapPin :size="18" /> Мезозойский проспект, дом 67</p><p><Clock3 :size="18" /> Ежедневно, 08:00–21:00</p></div>
        </aside>
      </div>
    </section>
  </div>
</template>
