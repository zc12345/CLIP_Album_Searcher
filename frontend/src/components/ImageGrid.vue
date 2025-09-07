<template>
  <div class="image-grid">
    <ImageCard
      v-for="(image, index) in images"
      :key="index"
      :image="image"
      :show-score="showScores"
      :searching="isSearching(image)"
      @search-similar="emit('search-similar', $event)"
      @open-folder="emit('open-folder', $event)"
      @preview="emit('preview', $event)"
    />
  </div>
</template>

<script setup>
import ImageCard from './ImageCard.vue'

const props = defineProps({
  images: {
    type: Array,
    default: () => []
  },
  showScores: {
    type: Boolean,
    default: false
  },
  searchingImage: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['search-similar', 'open-folder', 'preview'])

const isSearching = (image) => {
  return props.searchingImage === image.path
}
</script>

<style scoped>
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
</style>