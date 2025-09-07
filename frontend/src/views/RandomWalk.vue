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

    <div v-else-if="images.length > 0" class="content">
      <ImageGrid
        :images="images"
        :searching-image="searchingImage"
        @search-similar="searchSimilar"
        @open-folder="openFolder"
      />
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
      <div v-else-if="searchResults.length > 0" class="search-content">
        <ImageGrid
          :images="searchResults"
          :show-scores="true"
          @search-similar="searchSimilarFromResults"
          @open-folder="openFolder"
        />
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
import ImageGrid from '@/components/ImageGrid.vue'

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
    const response = await fetch(image.image_data)
    const blob = await response.blob()
    const file = new File([blob], image.filename, { type: 'image/jpeg' })
    
    const searchResponse = await searchService.imageSearch(file, 12, 0.0)
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

// 从搜索结果中再次搜索相似图片
const searchSimilarFromResults = async (image) => {
  searching.value = true
  
  try {
    const response = await fetch(image.image_data)
    const blob = await response.blob()
    const file = new File([blob], image.filename, { type: 'image/jpeg' })
    
    const searchResponse = await searchService.imageSearch(file, 12, 0.0)
    if (searchResponse.success) {
      searchResults.value = searchResponse.data
      ElMessage.success('重新搜索完成')
    } else {
      ElMessage.error('搜索失败')
    }
  } catch (error) {
    console.error('Error searching similar images:', error)
    ElMessage.error('搜索失败')
  } finally {
    searching.value = false
  }
}

// 打开文件夹
const openFolder = async (image) => {
  try {
    const response = await fetch('/api/images/open-folder', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ path: image.path })
    })
    
    const data = await response.json()
    
    if (data.success) {
      ElMessage.success(data.message)
    } else {
      const folderPath = image.path.replace(/[^/]*$/, '')
      ElMessage.info(`自动打开失败，请手动打开: ${folderPath}`)
    }
  } catch (error) {
    const folderPath = image.path.replace(/[^/]*$/, '')
    ElMessage.info(`网络错误，请手动打开: ${folderPath}`)
    console.error('打开文件夹错误:', error)
  }
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
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
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
  flex-wrap: wrap;
}

.loading-container {
  padding: 20px;
}

.content {
  margin-top: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px;
}

.search-loading {
  padding: 20px;
}

.search-content {
  margin-top: 10px;
}

.no-results {
  text-align: center;
  padding: 40px;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
    margin-top: 10px;
  }
}
</style>