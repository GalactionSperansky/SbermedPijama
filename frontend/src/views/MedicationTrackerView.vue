<script setup>
import { computed, ref } from 'vue'
import { Bell, Check, CirclePlus, Clock3, Pill, Plus, Trash2, X } from '@lucide/vue'
import PageHero from '../components/PageHero.vue'

const medicines = ref([
  { id: 1, title: 'Назальный спрей', dosage: '1 впрыскивание', time: '09:00', taken: true },
  { id: 2, title: 'Антигистаминный препарат', dosage: '1 таблетка', time: '14:00', taken: false },
  { id: 3, title: 'Промывание носа', dosage: 'По назначению', time: '21:00', taken: false },
])
const modalOpen = ref(false)
const draft = ref({ title: '', dosage: '', time: '' })
const completed = computed(() => medicines.value.filter((item) => item.taken).length)
const percent = computed(() => medicines.value.length ? Math.round((completed.value / medicines.value.length) * 100) : 0)

function addMedicine() {
  medicines.value.push({ id: Date.now(), ...draft.value, taken: false })
  draft.value = { title: '', dosage: '', time: '' }
  modalOpen.value = false
}

function removeMedicine(id) {
  medicines.value = medicines.value.filter((item) => item.id !== id)
}
</script>

<template>
  <div>
    <PageHero eyebrow="План лечения" title="Принимайте лекарства вовремя" text="Все назначения и отметки о приёме собраны в одном месте." />
    <section class="section compact-section">
      <div class="container tracker-layout">
        <div>
          <div class="tracker-summary">
            <div class="progress-ring" :style="{ '--progress': `${percent * 3.6}deg` }"><span>{{ percent }}%</span></div>
            <div><span class="eyebrow">Сегодня</span><h2>{{ completed }} из {{ medicines.length }} выполнено</h2><p>Продолжайте следовать плану врача.</p></div>
            <button class="button button-primary" type="button" @click="modalOpen = true"><Plus :size="18" /> Добавить</button>
          </div>

          <div class="medicine-list">
            <article v-for="medicine in medicines" :key="medicine.id" class="medicine-card" :class="{ completed: medicine.taken }">
              <button class="check-button" type="button" :aria-label="medicine.taken ? 'Отменить отметку' : 'Отметить прием'" @click="medicine.taken = !medicine.taken"><Check v-if="medicine.taken" :size="18" /></button>
              <span class="medicine-icon"><Pill :size="22" /></span>
              <div class="medicine-copy"><h3>{{ medicine.title }}</h3><p>{{ medicine.dosage }}</p></div>
              <span class="medicine-time"><Clock3 :size="17" /> {{ medicine.time }}</span>
              <button class="delete-button" type="button" aria-label="Удалить" @click="removeMedicine(medicine.id)"><Trash2 :size="17" /></button>
            </article>
          </div>
        </div>
        <aside class="tracker-sidebar">
          <div class="info-card gradient-card"><Bell :size="24" /><h3>Напоминания включены</h3><p>Мы напомним за 10 минут до следующего приёма.</p></div>
          <div class="info-card"><h3>Важное правило</h3><p>Добавляйте лекарства только из назначения врача. Не меняйте дозировку самостоятельно.</p></div>
        </aside>
      </div>
    </section>

    <Transition name="fade">
      <div v-if="modalOpen" class="modal-backdrop" @click.self="modalOpen = false">
        <form class="modal-card" @submit.prevent="addMedicine">
          <button class="modal-close" type="button" @click="modalOpen = false"><X /></button>
          <span class="service-icon blue"><CirclePlus :size="25" /></span>
          <h2>Добавить назначение</h2>
          <p>Перенесите данные из рекомендации врача.</p>
          <label class="field"><span>Название</span><input v-model="draft.title" required placeholder="Название препарата" /></label>
          <label class="field"><span>Дозировка</span><input v-model="draft.dosage" required placeholder="Например: 1 таблетка" /></label>
          <label class="field"><span>Время</span><input v-model="draft.time" required type="time" /></label>
          <button class="button button-primary full-width" type="submit">Добавить в расписание</button>
        </form>
      </div>
    </Transition>
  </div>
</template>
