<template>
  <div id="app">
    <div v-if="loading" class="loading-overlay">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <span>应用加载中...</span>
    </div>
    
    <div v-else-if="error" class="error-overlay">
      <el-alert type="error" title="应用加载失败" :description="error" show-icon />
    </div>
    
    <div v-else>
      <el-container>
        <el-header>
          <div class="header-content">
            <h1>
              <el-icon><Picture /></el-icon>
              CLIP 智能相册搜索
            </h1>
            <div class="header-actions">
              <el-button @click="refreshData" :loading="loading">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </el-header>
        
        <el-container>
          <el-aside width="200px">
            <el-menu
              :default-active="$route.path"
              router
              class="sidebar-menu"
            >
              <el-menu-item index="/random">
                <span>Random Walk</span>
              </el-menu-item>
              <el-menu-item index="/search">
                <el-icon><Search /></el-icon>
                <span>智能搜索</span>
              </el-menu-item>
              <el-menu-item index="/stats">
                <el-icon><DataAnalysis /></el-icon>
                <span>统计信息</span>
              </el-menu-item>
            </el-menu>
          </el-aside>
          
          <el-main>
            <router-view />
          </el-main>
        </el-container>
      </el-container>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const loading = ref(true)
const error = ref(null)

onMounted(() => {
  console.log('🔄 App组件已挂载')
  // 模拟加载过程
  setTimeout(() => {
    loading.value = false
    console.log('✅ App组件加载完成')
  }, 1000)
})

const refreshData = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 1000)
}
</script>

<style scoped>
.loading-overlay, .error-overlay {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  gap: 20px;
}

.loading-icon {
  font-size: 48px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

#app {
  font-family: 'Arial', sans-serif;
  height: 100vh;
}

.el-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.header-content h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.el-aside {
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
}

.sidebar-menu {
  border-right: none;
  height: 100%;
}

.el-main {
  padding: 20px;
  background-color: #f0f2f5;
}

:deep(.el-menu-item.is-active) {
  background-color: #ecf5ff;
  color: #409eff;
}

:deep(.el-menu-item:hover) {
  background-color: #f5f7fa;
}
</style>