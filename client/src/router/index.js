import Vue from 'vue';
import VueRouter from 'vue-router';
import HomePage from '../components/home_page.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/landing',
    name: 'home',
    component: HomePage,
  },
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});

export default router;