<template>
  <div class="random-walk">
    <el-card class="page-header">
      <template #header>
        <div class="card-header">
          <h2>
            Random Walk - 随机探索你的相册
          </h2>
          <div class="header-actions">
            <el-input-number
              v-model="imageCount"
              :min="6"
              :max="50"
              :step="6"
              size="small"
              @change="loadRandomImages"
            />
            <el-button
              type="primary"
              @click="loadRandomImages"
              :loading="loading"
            >
              <el-icon><Refresh /></el-icon>
              换一批
            </el-button>
          </div>
        </div>
      </template>
      <p>点击任意图片下方的"搜索相似图片"按钮，自动查找相似的图片！</p>
    </el-card>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="6" animated />
    </div>

    <div v-else-if="images.length > 0" class="image-grid">
      <div
        v-for="(image, index) in images"
        :key="index"
        class="image-card"
      >
        <el-image
          :src="image.image_data"
          :alt="image.filename"
          fit="cover"
          :preview-src-list="[`/api/images/original?path=${encodeURIComponent(image.path)}`]"
          :preview-teleported="true"
          class="image-item"
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
            @click="searchSimilar(image)"
            :loading="searchingImage === image.path"
          >
            <el-icon><Search /></el-icon>
            搜索相似图片
          </el-button>
          <el-button
            size="small"
            @click="openFolder(image.path)"
          >
            <el-icon><FolderOpened /></el-icon>
            打开文件夹
          </el-button>
        </div>
        
        <div class="image-info">
          <el-text size="small" truncated>{{ image.filename }}</el-text>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <el-empty description="暂无图片，请检查相册目录设置">
        <el-button type="primary" @click="loadRandomImages">重新加载</el-button>
      </el-empty>
    </div>

    <!-- 搜索结果对话框 -->
    <el-dialog
      v-model="searchDialogVisible"
      title="相似图片搜索结果"
      width="80%"
      :before-close="handleSearchDialogClose"
    >
      <div v-if="searching" class="search-loading">
        <el-skeleton :rows="4" animated />
      </div>
      <div v-else-if="searchResults.length > 0" class="search-results">
        <div
          v-for="(result, index) in searchResults"
          :key="index"
          class="result-card"
        >
          <el-image
            :src="result.image_data"
            :alt="result.filename"
            fit="cover"
            :preview-src-list="[`/api/images/original?path=${encodeURIComponent(result.path)}`]"
            :preview-teleported="true"
            class="result-image"
          />
          <div class="result-info">
            <div class="result-score">
              <el-tag type="success" size="small">
                相似度: {{ (result.score * 100).toFixed(1) }}%
              </el-tag>
            </div>
            <div class="result-filename">
              <el-text size="small" truncated>{{ result.filename }}</el-text>
            </div>
            <div class="result-actions">
              <el-button
                size="small"
                @click="openFolder(result.path)"
              >
                <el-icon><FolderOpened /></el-icon>
                打开文件夹
              </el-button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="no-results">
        <el-empty description="未找到相似的图片" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { searchService } from '@/services/searchService'

const loading = ref(false)
const searching = ref(false)
const searchingImage = ref(null)
const images = ref([])
const imageCount = ref(12)
const searchDialogVisible = ref(false)
const searchResults = ref([])

// 加载随机图片
const loadRandomImages = async () => {
  loading.value = true
  try {
    const response = await searchService.getRandomImages(imageCount.value)
    if (response.success) {
      images.value = response.data
    } else {
      ElMessage.error('加载随机图片失败')
    }
  } catch (error) {
    console.error('Error loading random images:', error)
    ElMessage.error('加载随机图片失败')
  } finally {
    loading.value = false
  }
}

// 搜索相似图片
const searchSimilar = async (image) => {
  searchingImage.value = image.path
  searching.value = true
  searchDialogVisible.value = true
  
  try {
    // 这里需要将图片转换为文件进行搜索
    // 由于我们已经有图片路径，可以直接使用路径搜索
    const response = await fetch(image.image_data)
    const blob = await response.blob()
    const file = new File([blob], image.filename, { type: 'image/jpeg' })
    
    const searchResponse = await searchService.imageSearch(file, 8, 0.0)
    if (searchResponse.success) {
      searchResults.value = searchResponse.data
    } else {
      ElMessage.error('搜索失败')
    }
  } catch (error) {
    console.error('Error searching similar images:', error)
    ElMessage.error('搜索失败')
  } finally {
    searching.value = false
    searchingImage.value = null
  }
}

// 打开文件夹
const openFolder = async (path) => {
  try {
    const response = await fetch('/api/images/open-folder', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ path })
    });
    
    const data = await response.json();
    
    if (data.success) {
      ElMessage.success(data.message);
    } else {
      // 如果后端打开失败，显示手动提示
      const folderPath = path.replace(/[^/]*$/, '');
      ElMessage.info(`自动打开失败，请手动打开: ${folderPath}`);
    }
  } catch (error) {
    // 网络错误时显示手动提示
    const folderPath = path.replace(/[^/]*$/, '');
    ElMessage.info(`网络错误，请手动打开: ${folderPath}`);
    console.error('打开文件夹错误:', error);
  }
};

const getOriginalImageUrl = (imagePath) => {
  return `/api/images/original?path=${encodeURIComponent(imagePath)}`
}

// 处理搜索对话框关闭
const handleSearchDialogClose = () => {
  searchDialogVisible.value = false
  searchResults.value = []
}

// 组件挂载时加载数据
onMounted(() => {
  loadRandomImages()
})
</script>

<style scoped>
.random-walk {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.loading-container {
  padding: 20px;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 10px;
}

.image-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.image-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.image-item {
  width: 100%;
  height: 200px;
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
}

.image-info {
  padding: 0 10px 10px;
}

.empty-state {
  text-align: center;
  padding: 40px;
}

.search-loading {
  padding: 20px;
}

.search-results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.result-card {
  background: #f9f9f9;
  border-radius: 8px;
  overflow: hidden;
}

.result-image {
  width: 100%;
  height: 150px;
}

.result-info {
  padding: 10px;
}

.result-score {
  margin-bottom: 8px;
}

.result-filename {
  margin-bottom: 8px;
}

.result-actions {
  display: flex;
  justify-content: center;
}

.no-results {
  text-align: center;
  padding: 40px;
}
</style>