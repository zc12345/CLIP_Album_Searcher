<template>
  <div class="stats">
    <el-card class="page-header">
      <template #header>
        <div class="card-header">
          <h2>
            <el-icon><DataAnalysis /></el-icon>
            相册统计信息
          </h2>
          <div class="header-actions">
            <el-button
              @click="loadStats"
              :loading="loading"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button
              type="primary"
              @click="scanAlbum"
              :loading="scanning"
            >
              <el-icon><FolderOpened /></el-icon>
              扫描相册
            </el-button>
          </div>
        </div>
      </template>
    </el-card>

    <!-- 统计卡片 -->
    <div v-if="stats" class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon images">
            <el-icon><Picture /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_images }}</div>
            <div class="stat-label">总图片数</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon features">
            <el-icon><DataBoard /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.feature_count }}</div>
            <div class="stat-label">特征向量</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon dimensions">
            <el-icon><Histogram /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.feature_dim }}</div>
            <div class="stat-label">特征维度</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon size">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_size_gb }} GB</div>
            <div class="stat-label">总大小</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 系统信息 -->
    <el-card class="system-info">
      <template #header>
        <div class="card-header">
          <h3>
            <el-icon><Setting /></el-icon>
            系统信息
          </h3>
        </div>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="系统状态">
          <el-tag type="success" v-if="systemStatus === 'healthy'">
            <el-icon><CircleCheck /></el-icon>
            正常运行
          </el-tag>
          <el-tag type="danger" v-else>
            <el-icon><CircleClose /></el-icon>
            异常
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="API版本">
          <el-tag>1.0.0</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="图片目录">
          <el-text>{{ config?.root_path || 'N/A' }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="数据库路径">
          <el-text>{{ config?.dump_path || 'N/A' }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="最大返回结果">
          <el-tag type="info">{{ config?.max_results || 50 }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="默认阈值">
          <el-tag type="info">{{ (config?.default_threshold || 0.3) * 100 }}%</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 操作日志 -->
    <el-card class="operation-log">
      <template #header>
        <div class="card-header">
          <h3>
            <el-icon><Document /></el-icon>
            操作日志
          </h3>
        </div>
      </template>
      
      <el-timeline>
        <el-timeline-item
          v-for="(log, index) in operationLogs"
          :key="index"
          :type="log.type"
          :timestamp="log.timestamp"
        >
          {{ log.message }}
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <!-- 性能测试对话框 -->
    <el-dialog
      v-model="showBenchmarkDialog"
      title="性能测试与多线程设置"
      width="600px"
    >
      <div class="benchmark-content">
        <div class="benchmark-section">
          <h4>工作线程设置</h4>
          <div class="worker-control">
            <el-input-number
              v-model="workerCount"
              :min="1"
              :max="16"
              :step="1"
              size="small"
            />
            <el-button
              type="primary"
              size="small"
              @click="updateWorkerCount"
              :loading="benchmarkLoading"
            >
              设置线程数
            </el-button>
          </div>
          <div class="current-info">
            当前线程数: {{ stats?.max_workers || 4 }}
          </div>
        </div>

        <div class="benchmark-section">
          <h4>性能基准测试</h4>
          <el-button
            type="primary"
            @click="runBenchmark"
            :loading="benchmarkLoading"
          >
            <el-icon><DataAnalysis /></el-icon>
            运行性能测试
          </el-button>
          
          <div v-if="benchmarkResults" class="benchmark-results">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="单线程耗时">
                {{ benchmarkResults.single_thread_time.toFixed(2) }}s
              </el-descriptions-item>
              <el-descriptions-item label="多线程耗时">
                {{ benchmarkResults.multi_thread_time.toFixed(2) }}s
              </el-descriptions-item>
              <el-descriptions-item label="加速比">
                <el-tag type="success">
                  {{ benchmarkResults.speedup.toFixed(2) }}x
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="测试样本数">
                {{ benchmarkResults.sample_size }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>

        <div class="benchmark-section">
          <h4>多线程说明</h4>
          <div class="info-text">
            <p>• 多线程可以显著提高大量图片的特征提取速度</p>
            <p>• 建议根据CPU核心数设置线程数（通常4-8个线程）</p>
            <p>• 线程数过多可能导致内存占用过高</p>
            <p>• 系统会自动根据图片数量选择最优处理方式</p>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  DataAnalysis, 
  Refresh, 
  FolderOpened, 
  Picture, 
  DataBoard, 
  Histogram, 
  Document, 
  Setting,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'
import { searchService } from '@/services/searchService'

const loading = ref(false)
const scanning = ref(false)
const stats = ref(null)
const config = ref(null)
const systemStatus = ref('healthy')
const operationLogs = ref([])
const showBenchmarkDialog = ref(false)
const benchmarkLoading = ref(false)
const benchmarkResults = ref(null)
const workerCount = ref(4)

// 加载统计信息
const loadStats = async () => {
  loading.value = true
  try {
    const [statsResponse, configResponse] = await Promise.all([
      searchService.getStats(),
      searchService.getConfig()
    ])
    
    if (statsResponse.success) {
      stats.value = statsResponse.data
    } else {
      ElMessage.error('获取统计信息失败')
    }
    
    if (configResponse.success) {
      config.value = configResponse.data
    }
    
    // 添加操作日志
    addOperationLog('success', '统计信息已刷新')
  } catch (error) {
    console.error('Error loading stats:', error)
    ElMessage.error('获取统计信息失败')
    addOperationLog('error', '统计信息刷新失败')
  } finally {
    loading.value = false
  }
}

// 扫描相册
const scanAlbum = async () => {
  scanning.value = true
  try {
    const response = await searchService.scanAlbum()
    if (response.success) {
      ElMessage.success('相册扫描完成')
      addOperationLog('success', '相册扫描完成')
      // 重新加载统计信息
      await loadStats()
    } else {
      ElMessage.error('相册扫描失败')
      addOperationLog('error', '相册扫描失败')
    }
  } catch (error) {
    console.error('Error scanning album:', error)
    ElMessage.error('相册扫描失败')
    addOperationLog('error', '相册扫描失败')
  } finally {
    scanning.value = false
  }
}

// 添加操作日志
const addOperationLog = (type, message) => {
  const now = new Date()
  const timestamp = now.toLocaleString('zh-CN')
  
  operationLogs.value.unshift({
    type,
    message,
    timestamp
  })
  
  // 保持最多10条日志
  if (operationLogs.value.length > 10) {
    operationLogs.value = operationLogs.value.slice(0, 10)
  }
}

// 性能测试
const runBenchmark = async () => {
  benchmarkLoading.value = true
  try {
    const response = await searchService.benchmark(30)
    if (response.success) {
      benchmarkResults.value = response.data
      ElMessage.success('性能测试完成')
      addOperationLog('success', `性能测试完成，加速比: ${response.data.speedup.toFixed(2)}x`)
    } else {
      ElMessage.error('性能测试失败')
    }
  } catch (error) {
    console.error('Benchmark error:', error)
    ElMessage.error('性能测试失败')
    addOperationLog('error', '性能测试失败')
  } finally {
    benchmarkLoading.value = false
  }
}

// 设置工作线程数
const updateWorkerCount = async () => {
  try {
    const response = await searchService.setWorkers(workerCount.value)
    if (response.success) {
      ElMessage.success(`工作线程数已设置为 ${workerCount.value}`)
      addOperationLog('success', `工作线程数设置为 ${workerCount.value}`)
      // 重新加载统计信息
      await loadStats()
    } else {
      ElMessage.error('设置工作线程数失败')
    }
  } catch (error) {
    console.error('Set workers error:', error)
    ElMessage.error('设置工作线程数失败')
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadStats()
  addOperationLog('info', '统计页面已加载')
})
</script>

<style scoped>
.stats {
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

.card-header h2,
.card-header h3 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  overflow: hidden;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.images {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.features {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.dimensions {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.size {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.system-info,
.operation-log {
  margin-bottom: 20px;
}

.operation-log {
  min-height: 200px;
}
</style>