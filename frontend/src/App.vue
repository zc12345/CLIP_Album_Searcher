<template>
  <div id="app">
    <!-- 其他代码保持不变 -->
    
    <el-container>
      <el-header>
        <!-- 头部内容 -->
        <div class="header-content">
          <h1 @click="toggleSidebar" class="mobile-menu-trigger">
            <el-icon><Menu /></el-icon>
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
        <!-- 响应式侧边栏 -->
        <el-aside :width="sidebarWidth" class="sidebar" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
          <div class="sidebar-header">
            <span>导航菜单</span>
            <el-button link @click="toggleSidebar" class="collapse-btn">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
          <el-menu
            :default-active="$route.path"
            router
            class="sidebar-menu"
          >
            <el-menu-item index="/random">
              <el-icon><Refresh /></el-icon>
              <span>随机探索</span>
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
        
        <el-main :class="{ 'main-full': isSidebarCollapsed }">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(true)
const error = ref(null)
const isSidebarCollapsed = ref(false)
const isMobile = ref(false)

// 检测屏幕宽度
const checkScreenSize = () => {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) {
    isSidebarCollapsed.value = true
  }
}

// 响应式侧边栏宽度
const sidebarWidth = computed(() => {
  if (isSidebarCollapsed.value) return '0px'
  return isMobile.value ? '80%' : '200px'
})

const toggleSidebar = () => {
  if (isMobile.value) {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
  }
}

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  
  setTimeout(() => {
    loading.value = false
  }, 1000)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

const refreshData = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('刷新成功')
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
  position: relative;
  z-index: 1000;
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
  font-size: 1.2rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.mobile-menu-trigger {
  cursor: pointer;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* 侧边栏样式 */
.sidebar {
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  transition: all 0.3s ease;
  overflow: hidden;
}

.sidebar-collapsed {
  transform: translateX(-100%);
  opacity: 0;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #fff;
}

.sidebar-header span {
  font-weight: 600;
  color: #303133;
}

.collapse-btn {
  font-size: 16px;
}

.sidebar-menu {
  border-right: none;
  height: calc(100% - 60px);
}

.el-main {
  padding: 20px;
  background-color: #f0f2f5;
  transition: all 0.3s ease;
}

.main-full {
  margin-left: 0 !important;
}

/* 移动端样式 */
@media screen and (max-width: 768px) {
  .header-content h1 {
    font-size: 1rem;
  }
  
  .header-actions .el-button {
    padding: 8px 12px;
  }
  
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 999;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  }
  
  .sidebar:not(.sidebar-collapsed) {
    width: 80% !important;
  }
  
  /* 侧边栏展开时的遮罩 */
  .sidebar:not(.sidebar-collapsed)::before {
    content: '';
    position: fixed;
    top: 0;
    right: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    z-index: -1;
  }
}

/* 平板样式 */
@media screen and (min-width: 769px) and (max-width: 1024px) {
  .sidebar {
    width: 180px !important;
  }
  
  .header-content h1 {
    font-size: 1.3rem;
  }
}

:deep(.el-menu-item) {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-menu-item.is-active) {
  background-color: #ecf5ff;
  color: #409eff;
}

:deep(.el-menu-item:hover) {
  background-color: #f5f7fa;
}
</style>