import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CreateModelView from '../views/CreateModelView.vue'

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
      component: () => import('../views/ModelView.vue'),
      // Add props: true to pass route params as component props
      props: true
    },
    {
      path: '/scene',
      name: 'scene',
      // Lazy-loaded component
      component: () => import('../views/SceneView.vue')
    },
    {
      path: '/create',
      name: 'create-model',
      component: CreateModelView
    }
  ]
})

export default router
