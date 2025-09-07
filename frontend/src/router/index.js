import { createRouter, createWebHistory } from 'vue-router'
import RandomWalk from '@/views/RandomWalk.vue'
import Search from '@/views/Search.vue'
import Stats from '@/views/Stats.vue'

const routes = [
  {
    path: '/',
    redirect: '/random'
  },
  {
    path: '/random',
    name: 'RandomWalk',
    component: RandomWalk,
    meta: { title: 'Random Walk' }
  },
  {
    path: '/search',
    name: 'Search',
    component: Search,
    meta: { title: '智能搜索' }
  },
  {
    path: '/stats',
    name: 'Stats',
    component: Stats,
    meta: { title: '统计信息' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由标题设置
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - CLIP 智能相册搜索` : 'CLIP 智能相册搜索'
  next()
})

export default router