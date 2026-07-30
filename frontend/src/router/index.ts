import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/assessment/:id',
      name: 'Detail',
      component: () => import('../views/DetailView.vue')
    },
    {
      path: '/upload',
      name: 'Upload',
      component: () => import('../views/UploadView.vue')
    }
  ],
})

export default router
