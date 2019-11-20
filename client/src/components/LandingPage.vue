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
          <v-card-text>
            <h1 v-if="i==1"> {{i}}</h1>
            
            <v-container v-if="i==2"> 
              <v-card flat class="mx-auto ma-auto mt-12" width="500px">
               
                          <v-text-field
                        v-model="pricerange"
                        label="Enter price "
                        ></v-text-field>


                        <v-btn color="orange" tile @click="carlistsearch()"> Check for cars </v-btn>
                </v-card>
            </v-container>
                
            <h1 v-if="i==3"> {{i}}</h1>
            <h1 v-if="i==4"> {{i}}</h1>
          </v-card-text>
        </v-card>
      </v-tab-item>
    </v-tabs>
  </div>
</template>


<script>
export default {
  data() {
    return {
        price: 0,
        tab: null,
        tabs: 4,
        tab_vals : ['Estimate car price', 'Estimate Budget', 'Some visual info', 'API analytics' ]
    }
  },
  created() {
    console.log("checking");
    
  },
  methods: {
    carlistsearch() {

    }
  }


};
</script>
<style scoped>

</style>