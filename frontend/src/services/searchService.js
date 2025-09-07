import api from '@/utils/api'

export const searchService = {
  // 获取随机图片
  getRandomImages(count = 12) {
    return api.get(`/images/random?count=${count}`)
  },

  // 文本搜索
  textSearch(query, k = 20, threshold = 0.) {
    return api.post('/images/search/text', {
      query,
      k,
      threshold
    })
  },

  // 图像搜索
  imageSearch(imageFile, k = 20, threshold = 0.) {
    const formData = new FormData()
    formData.append('image', imageFile)
    formData.append('k', k)
    formData.append('threshold', threshold)
    
    return api.post('/images/search/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取统计信息
  getStats() {
    return api.get('/images/stats')
  },

  // 扫描相册
  scanAlbum() {
    return api.post('/album/scan')
  },

  // 获取配置
  getConfig() {
    return api.get('/config')
  },

  // 健康检查
  healthCheck() {
    return api.get('/health')
  },

  // 性能基准测试
  benchmark(sampleSize = 50) {
    return api.post('/album/benchmark', {
      sample_size: sampleSize
    })
  },

  // 设置工作线程数
  setWorkers(maxWorkers) {
    return api.post('/album/workers', {
      max_workers: maxWorkers
    })
  },

  // 扫描相册（支持多线程）
  scanAlbum(useMultithreading = true) {
    return api.post('/album/scan', {
      use_multithreading: useMultithreading
    })
  }
}