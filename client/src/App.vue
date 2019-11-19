<template>
<v-app>
<v-content>
<router-view> </router-view>
</v-content>


</v-app>
</template>

<script>
import Login from './components/Login.vue';


export default {
  name: 'App',

  components: {
    Login,

    
  },

  data: () => ({
    //
  }),
};
</script>
