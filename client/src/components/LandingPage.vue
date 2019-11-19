<template>
  <div>
    <v-tabs
      v-model="tab"
      background-color="deep-purple accent-4"
      class="elevation-2"
      dark
      :grow="true"
    >
      <v-tabs-slider></v-tabs-slider>

      <v-tab
        v-for="i in tabs"
        :key="i"
      >
        {{tab_vals[i - 1]}}
      </v-tab>

      <v-tab-item
        v-for="i in tabs"
        :key="i"
      >
        <v-card
          flat
          tile
        >
          <v-card-text></v-card-text>
        </v-card>
      </v-tab-item>
    </v-tabs>
  </div>
</template>


<script>
export default {
  data() {
    return {
       
        tab: null,
        tabs: 4,
        tab_vals : ['Estimate car price', 'Estimate Budget', 'Some visual info', 'API analytics' ]
    }
  },
  created() {
    console.log("checking");
    
  },


};
</script>
<style scoped>

</style>