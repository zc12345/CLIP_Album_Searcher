<template>
  <div class="search">
    <el-card class="page-header">
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><Search /></el-icon>
            智能搜索
          </h2>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="文本搜索" name="text">
          <div class="search-form">
            <el-form :model="textForm" label-width="80px">
              <el-form-item label="搜索内容">
                <el-input
                  v-model="textForm.query"
                  placeholder="输入文本描述，例如：一只可爱的小猫、蓝天白云、美丽的风景..."
                  type="textarea"
                  :rows="3"
                />
              </el-form-item>
              <el-form-item label="返回数量">
                <el-input-number
                  v-model="textForm.k"
                  :min="1"
                  :max="50"
                  :step="1"
                />
              </el-form-item>
              <el-form-item label="相似度阈值">
                <el-slider
                  v-model="textForm.threshold"
                  :min="0"
                  :max="1"
                  :step="0.05"
                  :format-tooltip="formatTooltip"
                />
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  @click="performTextSearch"
                  :loading="searching"
                >
                  <el-icon><Search /></el-icon>
                  开始搜索
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="图像搜索" name="image">
          <div class="search-form">
            <el-form :model="imageForm" label-width="80px">
              <el-form-item label="上传图片">
                <el-upload
                  class="image-uploader"
                  :auto-upload="false"
                  :show-file-list="false"
                  accept="image/*"
                  :on-change="handleImageChange"
                >
                  <el-image
                    v-if="imageForm.image"
                    :src="imageForm.imageUrl"
                    class="uploaded-image"
                    fit="cover"
                  />
                  <el-button v-else type="primary">
                    <el-icon><Upload /></el-icon>
                    选择图片
                  </el-button>
                </el-upload>
              </el-form-item>
              <el-form-item label="返回数量">
                <el-input-number
                  v-model="imageForm.k"
                  :min="1"
                  :max="50"
                  :step="1"
                />
              </el-form-item>
              <el-form-item label="相似度阈值">
                <el-slider
                  v-model="imageForm.threshold"
                  :min="0"
                  :max="1"
                  :step="0.05"
                  :format-tooltip="formatTooltip"
                />
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  @click="performImageSearch"
                  :loading="searching"
                  :disabled="!imageForm.image"
                >
                  <el-icon><Search /></el-icon>
                  开始搜索
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 搜索结果 -->
    <div v-if="searchResults.length > 0" class="search-results">
      <div class="results-header">
        <h3>
          <el-icon><Picture /></el-icon>
          搜索结果 ({{ searchResults.length }} 张图片)
        </h3>
        <el-tag type="success">搜索完成</el-tag>
      </div>
      
      <div class="results-grid">
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
    </div>

    <!-- 无结果提示 -->
    <div v-else-if="hasSearched" class="no-results">
      <el-empty description="未找到符合条件的图片">
        <el-button type="primary" @click="resetSearch">重新搜索</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { searchService } from '@/services/searchService'

const activeTab = ref('text')
const searching = ref(false)
const hasSearched = ref(false)
const searchResults = ref([])

const textForm = reactive({
  query: '',
  k: 20,
  threshold: 0.3
})

const imageForm = reactive({
  image: null,
  imageUrl: '',
  k: 20,
  threshold: 0.3
})

const formatTooltip = (value) => {
  return `${(value * 100).toFixed(0)}%`
}

const handleTabClick = () => {
  // 切换标签页时重置搜索结果
  searchResults.value = []
  hasSearched.value = false
}

const handleImageChange = (file) => {
  if (file && file.raw) {
    imageForm.image = file.raw
    imageForm.imageUrl = URL.createObjectURL(file.raw)
  }
}

const performTextSearch = async () => {
  if (!textForm.query.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }

  searching.value = true
  hasSearched.value = false
  
  try {
    const response = await searchService.textSearch(
      textForm.query,
      textForm.k,
      textForm.threshold
    )
    
    if (response.success) {
      searchResults.value = response.data
      hasSearched.value = true
      
      if (response.data.length === 0) {
        ElMessage.info('未找到符合条件的图片，请尝试降低相似度阈值或修改搜索词')
      } else {
        ElMessage.success(`找到 ${response.data.length} 张相似图片`)
      }
    } else {
      ElMessage.error('搜索失败')
    }
  } catch (error) {
    console.error('Text search error:', error)
    ElMessage.error('搜索失败')
  } finally {
    searching.value = false
  }
}

const performImageSearch = async () => {
  if (!imageForm.image) {
    ElMessage.warning('请先上传图片')
    return
  }

  searching.value = true
  hasSearched.value = false
  
  try {
    const response = await searchService.imageSearch(
      imageForm.image,
      imageForm.k,
      imageForm.threshold
    )
    
    if (response.success) {
      searchResults.value = response.data
      hasSearched.value = true
      
      if (response.data.length === 0) {
        ElMessage.info('未找到符合条件的图片，请尝试降低相似度阈值')
      } else {
        ElMessage.success(`找到 ${response.data.length} 张相似图片`)
      }
    } else {
      ElMessage.error('搜索失败')
    }
  } catch (error) {
    console.error('Image search error:', error)
    ElMessage.error('搜索失败')
  } finally {
    searching.value = false
  }
}

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

const resetSearch = () => {
  searchResults.value = []
  hasSearched.value = false
  textForm.query = ''
  imageForm.image = null
  imageForm.imageUrl = ''
}
</script>

<style scoped>
.search {
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

.search-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px 0;
}

.image-uploader {
  text-align: center;
}

.uploaded-image {
  width: 300px;
  height: 200px;
  border-radius: 8px;
  border: 2px dashed #d9d9d9;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.results-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #333;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.result-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.result-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.result-image {
  width: 100%;
  height: 200px;
}

.result-info {
  padding: 15px;
}

.result-score {
  margin-bottom: 10px;
}

.result-filename {
  margin-bottom: 10px;
}

.result-actions {
  display: flex;
  justify-content: center;
}

.no-results {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>