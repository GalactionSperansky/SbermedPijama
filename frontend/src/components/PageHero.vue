<script setup>
defineProps({
  eyebrow: String,
  title: String,
  text: String,
})
</script>

<template>
  <section class="page-hero">
    <div class="ambient-orb orb-one"></div>
    <div class="ambient-orb orb-two"></div>
    <div class="container page-hero-content">
      <span class="eyebrow">{{ eyebrow }}</span>
      <h1>{{ title }}</h1>
      <p>{{ text }}</p>
    </div>
  </section>
</template>

