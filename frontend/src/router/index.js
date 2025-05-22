import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/model/:id',
      name: 'model',
      // Lazy-loaded component
      component: () => import('../views/ModelView.vue')
    }
  ]
})

export default router
