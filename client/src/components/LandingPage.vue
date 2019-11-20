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

      <v-tab v-for="i in tabs" :key="i">{{tab_vals[i - 1]}}</v-tab>

      <v-tab-item v-for="i in tabs" :key="i">
        <v-card flat tile>
          <v-card-text>
            <h1 v-if="i==1">{{i}}</h1>

            <v-container v-if="i==2">
              <v-card flat class="mx-auto ma-auto mt-12" width="500px">
                <v-select :items="brands" v-model="selectedBrand" label="Standard"></v-select>

                <v-text-field v-model="priceRange" label="Enter price "></v-text-field>

                <v-btn color="orange" tile @click="carListSearch()">Check for cars</v-btn>
              </v-card>

              <v-card>
                  <v-card-subtitle v-for="(obj,i) in estimateCarResult" :key="i">
                    {{obj[1]}} {{obj[0]}}, {{obj[2]}} model
                  </v-card-subtitle>

              </v-card>
            </v-container>

            <h1 v-if="i==3">{{i}}</h1>
            <h1 v-if="i==4">{{i}}</h1>
          </v-card-text>
        </v-card>
      </v-tab-item>
    </v-tabs>
  </div>
</template>


<script>
import axios from 'axios';
export default {
  data() {
    return {
      estimateCarResult: '',
      priceRange: '',
      selectedBrand : '',
      price: 0,
      tab: null,
      tabs: 4,
      tab_vals: [
        "Estimate car price",
        "Estimate Budget",
        "Some visual info",
        "API analytics"
      ],
      brands: [
        "Audi",
        "Jeep",
        "Volkswagen",
        "Skoda",
        "BMW",
        "Peugeot",
        "Mazda",
        "Nissan",
        "Renault",
        "Ford",
        "Mercedes-Benz",
        "Seat",
        "Citroen",
        "Honda",
        "Fiat",
        "Mini",
        "Smart",
        "Hyundai",
        "Subaru",
        "Volvo",
        "Mitsubishi",
        "Kia",
        "Toyota",
        "Chevrolet",
        "Suzuki",
        "Daihatsu",
        "Chrysler",
        "Jaguar",
        "Rover",
        "Porsche",
        "Saab",
        "LANDROVER"
      ]
    };
  },
  created() {
    //console.log("checking");
  },
  methods: {
    carListSearch() {
      console.log(this.priceRange, this.selectedBrand)
      axios.get(`http://localhost:9000/estimateCar/${this.priceRange}/${this.selectedBrand}`).then(response => {
        console.log("resp is", response)
        this.estimateCarResult = response.data.data;
      });
    }
  }
};
</script>
<style scoped>
</style>