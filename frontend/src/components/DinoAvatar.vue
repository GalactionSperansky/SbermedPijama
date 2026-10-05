<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  user: { type: Object, default: null },
  assistant: Boolean,
  size: { type: String, default: 'medium' },
})

const dinoLoaded = ref(true)
const backgroundLoaded = ref(true)
const backgroundSrc = computed(() => props.user?.avatar_background_url || `/avatars/background_${props.user?.avatar_background || 1}.png`)
const dinoSrc = computed(() => props.assistant
  ? '/avatars/dino_in_pijama_with_statoscope_transparent.png'
  : (props.user?.avatar_dino_url || `/avatars/dino_${props.user?.avatar_dino || 1}.png`))

watch([backgroundSrc, dinoSrc], () => {
  dinoLoaded.value = true
  backgroundLoaded.value = true
})
</script>

<template>
  <span class="dino-avatar" :class="[`dino-avatar-${size}`, { assistant }]">
    <img v-if="backgroundLoaded && !assistant" class="avatar-background" :src="backgroundSrc" alt="" @error="backgroundLoaded = false" />
    <img v-if="dinoLoaded" class="avatar-dino" :src="dinoSrc" :alt="assistant ? 'Динозаврик' : 'Аватар пользователя'" @error="dinoLoaded = false" />
    <span v-if="!dinoLoaded" class="avatar-fallback">{{ assistant ? '🦖' : '🦕' }}</span>
  </span>
</template>

