import Vue from 'vue';
import VueRouter from 'vue-router';
import Login from '../components/Login.vue';
import Register from '../components/Register.vue';
import LandingPage from '../components/LandingPage.vue';


Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'login',
    component: Login,
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
  },
  {
    path: '/landing',
    name: 'landing',
    component: LandingPage,
  },

];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});

export default router;
