<template>
  <div class="image-card">
    <el-image
      :src="image.image_data"
      :alt="image.filename"
      fit="cover"
      :preview-src-list="previewSrcList"
      :preview-teleported="true"
      class="image-item"
      @click="handleImageClick"
    >
      <template #placeholder>
        <div class="image-placeholder">
          <el-icon><Picture /></el-icon>
        </div>
      </template>
    </el-image>
    
    <div class="image-actions">
      <el-button
        type="primary"
        size="small"
        @click="handleSearchSimilar"
        :loading="searching"
      >
        <el-icon><Search /></el-icon>
        搜索相似图片
      </el-button>
      <el-button
        size="small"
        @click="openFolder"
      >
        <el-icon><FolderOpened /></el-icon>
        打开文件夹
      </el-button>
    </div>
    
    <div class="image-info">
      <el-text size="small" truncated>{{ image.filename }}</el-text>
      <el-tag v-if="showScore" type="success" size="small" class="score-tag">
        相似度: {{ (image.score * 100).toFixed(1) }}%
      </el-tag>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  image: {
    type: Object,
    required: true
  },
  showScore: {
    type: Boolean,
    default: false
  },
  searching: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['search-similar', 'open-folder', 'preview'])

const previewSrcList = computed(() => {
  return [`/api/images/original?path=${encodeURIComponent(props.image.path)}`]
})

const handleSearchSimilar = () => {
  emit('search-similar', props.image)
}

const openFolder = async () => {
  try {
    const response = await fetch('/api/images/open-folder', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ path: props.image.path })
    })
    
    const data = await response.json()
    
    if (data.success) {
      ElMessage.success(data.message)
    } else {
      const folderPath = props.image.path.replace(/[^/]*$/, '')
      ElMessage.info(`自动打开失败，请手动打开: ${folderPath}`)
    }
  } catch (error) {
    const folderPath = props.image.path.replace(/[^/]*$/, '')
    ElMessage.info(`网络错误，请手动打开: ${folderPath}`)
    console.error('打开文件夹错误:', error)
  }
}

const handleImageClick = () => {
  emit('preview', props.image)
}
</script>

<style scoped>
.image-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.image-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.image-item {
  width: 100%;
  height: 200px;
  cursor: pointer;
}

.image-placeholder {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #909399;
  font-size: 24px;
}

.image-actions {
  padding: 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.image-info {
  padding: 0 10px 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.score-tag {
  flex-shrink: 0;
}
</style>