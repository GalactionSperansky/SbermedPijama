<script setup>
import { computed, onMounted, ref } from 'vue'
import { CalendarDays, ChevronRight, ClipboardList, FileCheck2, FlaskConical, Microscope, Pill, ScrollText, Stethoscope } from '@lucide/vue'
import PageHero from '../components/PageHero.vue'
import DinoAvatar from '../components/DinoAvatar.vue'
import { authStore } from '../stores/auth'
import { api } from '../services/api'

const activeCategory = ref('all')
const records = ref([])
const editing = ref(false)
const saveError = ref('')
const profileForm = ref({ first_name: '', last_name: '', middle_name: '', phone: '', birth_date: '', policy_number: '' })
const demoRecords = [
  { id: 'd1', category: 'visit_protocol', category_label: 'Протокол приёма', title: 'Консультация оториноларинголога', summary: 'Рекомендации и план наблюдения после первичного осмотра.', occurred_at: '2026-10-02T15:30:00Z', doctor_name: 'Анна Сергеевна Лебедева' },
  { id: 'd2', category: 'lab_result', category_label: 'Результат анализа', title: 'Общий анализ крови', summary: 'Результат загружен в медицинскую карту.', occurred_at: '2026-09-28T08:20:00Z', doctor_name: '' },
  { id: 'd3', category: 'study', category_label: 'Исследование', title: 'Аудиометрия', summary: 'Тональная пороговая аудиометрия.', occurred_at: '2026-09-21T11:10:00Z', doctor_name: 'Михаил Олегович Воронов' },
  { id: 'd4', category: 'certificate', category_label: 'Справка', title: 'Справка о посещении врача', summary: 'Электронный документ готов к просмотру.', occurred_at: '2026-09-21T12:00:00Z', doctor_name: '' },
  { id: 'd5', category: 'event', category_label: 'Событие', title: 'Создан план лечения', summary: 'Назначения добавлены в трекер лекарств.', occurred_at: '2026-09-20T17:40:00Z', doctor_name: '' },
]

const categories = [
  ['all', 'Все записи'], ['event', 'События'], ['certificate', 'Справки'],
  ['lab_result', 'Анализы'], ['study', 'Исследования'], ['visit_protocol', 'Заключения'],
]
const iconMap = { event: CalendarDays, certificate: FileCheck2, lab_result: FlaskConical, study: Microscope, visit_protocol: ScrollText }
const visibleRecords = computed(() => {
  const source = records.value.length ? records.value : demoRecords
  return activeCategory.value === 'all' ? source : source.filter((item) => item.category === activeCategory.value)
})
const user = computed(() => authStore.state.user)

onMounted(async () => {
  try { records.value = await api('/medical-records/') } catch { records.value = [] }
})

function startEditing() {
  profileForm.value = {
    first_name: user.value?.first_name || '',
    last_name: user.value?.last_name || '',
    middle_name: user.value?.middle_name || '',
    phone: user.value?.phone || '',
    birth_date: user.value?.birth_date || '',
    policy_number: user.value?.policy_number || '',
  }
  saveError.value = ''
  editing.value = true
}

async function saveProfile() {
  saveError.value = ''
  try {
    await authStore.updateProfile(profileForm.value)
    editing.value = false
  } catch (error) {
    saveError.value = error.message
  }
}

function formatDate(value) {
  return new Intl.DateTimeFormat('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(value))
}
</script>

<template>
  <div>
    <PageHero eyebrow="Личный кабинет" :title="`Добрый день, ${user?.first_name || 'пациент'}`" text="Записи, документы и план лечения всегда под рукой." />
    <section class="section compact-section">
      <div class="container dashboard-grid">
        <div class="profile-card dino-profile-card">
          <DinoAvatar :user="user" size="profile" />
          <div><h2>{{ user?.full_name }}</h2><p>Профиль пациента DИИnozavr</p></div>
          <button v-if="!editing" class="ghost-button" type="button" @click="startEditing">Редактировать</button>
          <form v-if="editing" class="profile-edit-form" @submit.prevent="saveProfile">
            <div class="form-grid two-columns">
              <label class="field"><span>Имя</span><input v-model="profileForm.first_name" required /></label>
              <label class="field"><span>Фамилия</span><input v-model="profileForm.last_name" /></label>
              <label class="field"><span>Отчество</span><input v-model="profileForm.middle_name" /></label>
            </div>
            <label class="field"><span>Телефон</span><input v-model="profileForm.phone" type="tel" required /></label>
            <div class="form-grid two-columns">
              <label class="field"><span>Дата рождения</span><input v-model="profileForm.birth_date" type="date" /></label>
              <label class="field"><span>Полис</span><input v-model="profileForm.policy_number" /></label>
            </div>
            <p v-if="saveError" class="form-error">{{ saveError }}</p>
            <div class="profile-edit-actions"><button class="button button-primary button-small" type="submit">Сохранить</button><button class="ghost-button" type="button" @click="editing = false">Отмена</button></div>
          </form>
          <dl v-else>
            <div><dt>Email</dt><dd>{{ user?.email }}</dd></div>
            <div><dt>Телефон</dt><dd>{{ user?.phone || 'Не указан' }}</dd></div>
            <div><dt>Дата рождения</dt><dd>{{ user?.birth_date || 'Не указана' }}</dd></div>
            <div><dt>Полис</dt><dd>{{ user?.policy_number || 'Не указан' }}</dd></div>
          </dl>
          <small class="avatar-lock-note">Ваш динозавр создан при регистрации и остаётся с вами.</small>
        </div>

        <div class="dashboard-main">
          <article class="next-visit-card">
            <div class="visit-date"><strong>18</strong><span>окт</span></div>
            <div class="visit-details"><span class="eyebrow light">Ближайший приём</span><h2>Оториноларинголог</h2><p>Анна Сергеевна Лебедева · 17:30</p></div>
            <RouterLink to="/appointment" class="button button-white button-small">Подробнее</RouterLink>
          </article>

          <div class="dashboard-actions">
            <RouterLink to="/anamnesis" class="dashboard-action"><span><ClipboardList /></span><div><h3>Анамнез</h3><p>Продолжить опрос</p></div><ChevronRight /></RouterLink>
            <RouterLink to="/tracker" class="dashboard-action"><span><Pill /></span><div><h3>Лекарства</h3><p>Открыть план лечения</p></div><ChevronRight /></RouterLink>
            <RouterLink to="/appointment" class="dashboard-action"><span><Stethoscope /></span><div><h3>Новая запись</h3><p>Выбрать врача</p></div><ChevronRight /></RouterLink>
            <RouterLink to="/support" class="dashboard-action"><span><FileCheck2 /></span><div><h3>Получить помощь</h3><p>Связаться с клиникой</p></div><ChevronRight /></RouterLink>
          </div>

          <div class="history-card medical-card">
            <div class="card-header"><div><span class="eyebrow">Медицинская карта</span><h2>Документы и последние события</h2></div><ScrollText class="blue-icon" /></div>
            <div class="record-filters"><button v-for="category in categories" :key="category[0]" :class="{ active: activeCategory === category[0] }" @click="activeCategory = category[0]">{{ category[1] }}</button></div>
            <div v-if="visibleRecords.length" class="medical-records">
              <article v-for="record in visibleRecords" :key="record.id" class="medical-record-row">
                <span class="record-icon"><component :is="iconMap[record.category] || CalendarDays" /></span>
                <div><small>{{ record.category_label }} · {{ formatDate(record.occurred_at) }}</small><h3>{{ record.title }}</h3><p>{{ record.summary }}</p><strong v-if="record.doctor_name">{{ record.doctor_name }}</strong></div>
                <ChevronRight />
              </article>
            </div>
            <p v-else class="empty-state">В этой категории пока нет записей.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
