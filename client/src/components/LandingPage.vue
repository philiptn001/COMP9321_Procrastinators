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
            <v-container v-if="i==1">
              <v-card flat class="mx-auto ma-auto mt-12" relative>
                <v-row>
                  <v-select class="mr-12" :items="brandsML" v-model="selectedBrandML" label="Brand"></v-select>

                  <v-select class="mr-12" :items="models" v-model="selectedModelML" label="Model"></v-select>
                  <v-select class="mr-12" :items="types" v-model="selectedTypeML" label="Type"></v-select>

                  <v-select class="mr-12" :items="gear" v-model="selectedGearML" label="Gear"></v-select>

                  <v-text-field class="mr-12" v-model="year" label="Enter year  "></v-text-field>
                  <v-text-field class="mr-12" v-model="power" label="Enter power in PS  "></v-text-field>
                  <v-text-field class="mr-10" v-model="km" label="Enter kilometres"></v-text-field>
                  <v-select class="mr-12" :items="fuel" v-model="selectedFuelML" label="Fuel Type"></v-select>
                  <v-select
                    :items="repairedDamage"
                    v-model="repairedDamageML"
                    label="Damage repaired or not repaired"
                  ></v-select>
                </v-row>

                <v-btn tile color="orange" @click="estimatePrice()">Find Estimate Price</v-btn>
              </v-card>

              <v-card>
                <v-card-title
                  v-if="result"
                >The estimated price for the car you searched for is: {{estimateCarPrice}}</v-card-title>
              </v-card>
            </v-container>

            <v-container v-if="i==2">
              <v-card flat class="mx-auto ma-auto mt-12" width="500px">
                <v-select :items="brands" v-model="selectedBrand" label="Brand"></v-select>

                <v-text-field v-model="priceRange" label="Enter price "></v-text-field>

                <v-btn color="orange" tile @click="carListSearch()">Check for cars</v-btn>
              </v-card>

              <v-card>
                <v-card-subtitle
                  v-for="(obj,i) in estimateCarResult"
                  :key="i"
                >{{obj.brand}} {{obj.model}}, {{obj.yearOfRegistration}} model</v-card-subtitle>
              </v-card>
            </v-container>

            <v-container v-if="i==3">
            <v-btn tile color="orange" @click="reliability()"> Top 10 most reliable cars </v-btn>

            </v-container>
            <h1 v-if="i==4">{{i}}</h1>
          </v-card-text>
        </v-card>
      </v-tab-item>
    </v-tabs>
  </div>
</template>


<script>
import axios from "axios";
export default {
  data() {
    return {
      selectedBrandML: "",
      year: "",
      power: null,
      km: null,
      selectedTypeML: "",
      estimateCarResult: "",
      estimateCarPrice: "",
      selectedModelML: "",
      selectedGearML: "",
      priceRange: "",
      selectedBrand: "",
      selectedFuelML: "",
      repairedDamageML: "",
      models: [],
      reliableCars: [],
      result: false,
      price: 0,
      tab: null,
      tabs: 4,
      tab_vals: [
        "Estimate car price",
        "Find cars",
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
      ],
      brandsML: ["Audi", "BMW", "Mercedes_Benz", "Volkswagen"],
      types: [
        "coupe",
        "suv",
        "small car",
        "limousine",
        "cabrio",
        "station wagon",
        "bus"
      ],
      gear: ["manually", "automatic"],
      fuel: ["diesel", "petrol", "other", "lpg", "hybrid", "cng", "electro"],
      repairedDamage: ["Yes", "No", "unknown"],
      Audi: ["a8", "a4", "a6", "a3", "a2", "a5", "a1"],
      BMW: ["3er", "5er", "1er", "7er", "6er", "i3"],
      Mercedes_Benz: [
        "a_klasse",
        "e_klasse",
        "b_klasse",
        "c_klasse",
        "m_klasse",
        "s_klasse",
        "v_klasse",
        "g_klasse"
      ],
      Volkswagen: [
        "golf",
        "passat",
        "jetta",
        "polo",
        "tiguan",
        "beetle",
        "touareg"
      ]
    };
  },
  created() {
    //console.log("checking");
  },

  watch: {
    selectedBrandML: function(newVal) {
      switch (newVal) {
        case "Audi":
          this.models = this.Audi;
          break;
        case "BMW":
          this.models = this.BMW;
          break;
        case "Mercedes_Benz":
          this.models = this.Mercedes_Benz;
          break;
        case "Volkswagen":
          this.models = this.Volkswagen;
          break;
        default:
          this.models = [];
      }
    }
  },
  methods: {
    carListSearch() {
      // console.log(this.priceRange, this.selectedBrand);
      axios
        .get(
          `http://localhost:9000/estimateCar/${this.priceRange}/${this.selectedBrand}`
        )
        .then(response => {
          console.log("resp is", response);
          this.estimateCarResult = response.data;
        });
    },

    estimatePrice() {
      axios
        .get("http://localhost:9000/estimatePrice", {
          params: {
            brand: this.selectedBrandML,
            model: this.selectedModelML,
            vehicleType: this.selectedTypeML,
            yearOfRegistration: this.year,
            gearbox: this.selectedGearML,
            powerPS: this.power,
            kilometer: this.km,
            fuelType: this.selectedFuelML,
            notRepairedDamage: this.repairedDamageML
          }
        })
        .then(response => {
          this.estimateCarPrice = response.data.Predicted_Price;
          this.result = true;
        });
    },

    reliability() {
            axios
        .get(
          `http://localhost:9000/reliability`
        )
        .then(response => {
          console.log("resp is", response);
          //this.reliableCars = response.data;
          //console.log(this.reliableCars)
        });

    }
  }
};
</script>
<style scoped>
</style>