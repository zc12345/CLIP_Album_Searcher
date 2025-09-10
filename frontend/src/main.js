import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

// 正确导入 Element Plus 图标
import {
  Menu,
  Picture,
  Refresh,
  Search,
  DataAnalysis,
  FolderOpened,
  Upload,
  Setting,
  CircleCheck,
  CircleClose,
  DataBoard,
  Histogram,
  Document,
} from '@element-plus/icons-vue'

console.log('🚀 Vue应用开始初始化...')

const app = createApp(App)
const pinia = createPinia()

// 手动注册需要的图标组件
const icons = {
  Menu,
  Picture,
  Refresh,
  Search,
  DataAnalysis,
  FolderOpened,
  Upload,
  Setting,
  CircleCheck,
  CircleClose,
  DataBoard,
  Histogram,
  Document,
}

// 注册图标组件
Object.entries(icons).forEach(([name, component]) => {
  app.component(name, component)
  console.log(`✅ 注册图标: ${name}`)
})

app.use(pinia)
app.use(router)
app.use(ElementPlus)

console.log('✅ 所有插件已注册')

try {
  app.mount('#app')
  console.log('🎉 Vue应用挂载成功')
} catch (error) {
  console.error('❌ Vue应用挂载失败:', error)
}