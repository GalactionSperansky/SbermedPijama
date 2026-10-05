<script setup>
import {
  ArrowRight,
  CalendarDays,
  Check,
  ClipboardList,
  Clock3,
  Headphones,
  HeartHandshake,
  MessageCircleHeart,
  Pill,
  ShieldCheck,
  Sparkles,
  UserRound,
} from '@lucide/vue'
import DinoAvatar from '../components/DinoAvatar.vue'

const services = [
  {
    icon: CalendarDays,
    title: 'Запись к врачу',
    text: 'Найдите нужного специалиста и удобное время без звонков.',
    to: '/appointment',
    accent: 'cyan',
  },
  {
    icon: MessageCircleHeart,
    title: 'Сбор анамнеза',
    text: 'Ответьте на несколько понятных вопросов до визита.',
    to: '/anamnesis',
    accent: 'blue',
  },
  {
    icon: Pill,
    title: 'Трекер лекарств',
    text: 'Следуйте назначениям и отмечайте каждый приём.',
    to: '/tracker',
    accent: 'violet',
  },
  {
    icon: Headphones,
    title: 'Поддержка',
    text: 'Мы рядом, если нужна помощь с сервисом или записью.',
    to: '/support',
    accent: 'mint',
  },
]

const steps = [
  ['01', 'Опишите самочувствие', 'Можно обычными словами — помощник уточнит важное.'],
  ['02', 'Получите маршрут', 'Сервис подскажет специальность и срочность обращения.'],
  ['03', 'Запишитесь и следуйте плану', 'Результат опроса попадёт врачу, а назначения — в трекер.'],
]
</script>

<template>
  <div>
    <section class="hero">
      <div class="hero-mesh"></div>
      <div class="ambient-orb hero-orb-one"></div>
      <div class="ambient-orb hero-orb-two"></div>
      <div class="container hero-grid">
        <div class="hero-copy">
          <div class="eyebrow"><Sparkles :size="15" /> Забота начинается до приёма</div>
          <h1>Путь к врачу<br /><span>без лишних шагов</span></h1>
          <p class="hero-lead">
            Запись, предварительный анамнез и сопровождение лечения — в одном понятном сервисе.
          </p>
          <div class="hero-actions">
            <RouterLink to="/anamnesis" class="button button-primary">
              Рассказать о симптомах <ArrowRight :size="18" />
            </RouterLink>
            <RouterLink to="/appointment" class="button button-secondary">Записаться к врачу</RouterLink>
          </div>
          <div class="trust-row">
            <span><ShieldCheck :size="18" /> Бережно к данным</span>
            <span><Clock3 :size="18" /> Опрос за 3–5 минут</span>
          </div>
        </div>

        <div class="hero-visual" aria-label="Пример интерфейса медицинского помощника">
          <div class="glass-panel assistant-card">
            <div class="assistant-topline">
              <DinoAvatar assistant size="small" />
              <div>
                <strong>Динозаврик</strong>
                <span><i></i> на связи</span>
              </div>
            </div>
            <div class="message message-assistant">
              Расскажите, что вас беспокоит. Я задам несколько вопросов и помогу выбрать врача.
            </div>
            <div class="message message-user">Заложило ухо после бассейна и стало хуже слышно.</div>
            <div class="assistant-question">
              <span>Следующий вопрос</span>
              Есть ли боль или выделения из уха?
            </div>
            <div class="progress-line"><span></span></div>
            <small>Шаг 2 из 4</small>
          </div>
          <div class="floating-card floating-doctor">
            <span class="floating-icon"><UserRound :size="21" /></span>
            <div><small>Подходящий специалист</small><strong>Оториноларинголог</strong></div>
          </div>
          <div class="floating-card floating-ready">
            <span class="success-dot"><Check :size="15" /></span>
            <div><small>Ближайшее время</small><strong>Сегодня, 17:30</strong></div>
          </div>
        </div>
      </div>
    </section>

    <section class="section services-section">
      <div class="container">
        <div class="section-heading centered">
          <span class="eyebrow">Всё необходимое рядом</span>
          <h2>Здоровье — понятным языком</h2>
          <p>Начните с того шага, который нужен вам сейчас.</p>
        </div>
        <div class="service-grid">
          <RouterLink v-for="service in services" :key="service.title" :to="service.to" class="service-card">
            <span class="service-icon" :class="service.accent"><component :is="service.icon" :size="25" /></span>
            <h3>{{ service.title }}</h3>
            <p>{{ service.text }}</p>
            <span class="card-link">Перейти <ArrowRight :size="17" /></span>
          </RouterLink>
        </div>
      </div>
    </section>

    <section class="section flow-section">
      <div class="container flow-grid">
        <div class="flow-intro">
          <span class="eyebrow">Как это работает</span>
          <h2>От первого сообщения до понятного плана</h2>
          <p>Ассистент собирает нужную информацию, но решения о лечении всегда остаются за врачом.</p>
          <RouterLink to="/anamnesis" class="text-link">Попробовать демо <ArrowRight :size="17" /></RouterLink>
        </div>
        <div class="steps-list">
          <article v-for="step in steps" :key="step[0]" class="step-card">
            <span class="step-number">{{ step[0] }}</span>
            <div><h3>{{ step[1] }}</h3><p>{{ step[2] }}</p></div>
          </article>
        </div>
      </div>
    </section>

    <section class="section cta-section">
      <div class="container">
        <div class="cta-panel">
          <div class="cta-icon"><ClipboardList :size="32" /></div>
          <div>
              <span class="eyebrow light">DИИnozavr рядом</span>
            <h2>Подготовьтесь к приёму уже сейчас</h2>
            <p>Ответьте на вопросы, получите маршрут и выберите удобное время.</p>
          </div>
          <RouterLink to="/anamnesis" class="button button-white">Начать <ArrowRight :size="18" /></RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>
