<template>
  <div>
    <v-row>
      <v-btn
        tile
        outlined
        style="position: fixed; right: 0;top:0;"
        color="orange"
        class="mt-1 mr-1"
        @click="logOut()"
      >logout</v-btn>
    </v-row>

    <v-tabs
      v-model="tab"
      background-color="deep-purple accent-4"
      class="elevation-2 mt-12"
      dark
      :grow="true"
    >
      <v-tabs-slider></v-tabs-slider>

      <v-tab v-for="i in tabs" :key="i">{{tab_vals[i - 1]}}</v-tab>

      <v-tab-item v-for="i in tabs" :key="i">
        <v-card flat tile>
          <v-card-text>
            <v-container v-if="i==1">
              <h2>Gives user a recommended price to sell the car</h2>
              <v-card flat class="mx-auto ma-auto mt-12" relative>
                <v-row>
                  <v-select class="mr-12" :items="brandsML" v-model="selectedBrandML" label="Brand"></v-select>

                  <v-select class="mr-12" :items="models" v-model="selectedModelML" label="Model"></v-select>
                  <v-select class="mr-12" :items="types" v-model="selectedTypeML" label="Type"></v-select>

                  <v-select class="mr-12" :items="gear" v-model="selectedGearML" label="Gear"></v-select>

                  <v-text-field class="mr-12" v-model="year" label="Enter year"></v-text-field>
                  <v-text-field class="mr-12" v-model="power" label="Enter power in PS"></v-text-field>
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
              <h2>Gives user a recommended car [list] for a given budget [range of +/- 50 euros]</h2>
              <v-card flat class="mx-auto ma-auto mt-12" width="500px">
                <v-select :items="brands" v-model="selectedBrand" label="Brand"></v-select>

                <v-text-field v-model="priceRange" label="Enter price (in Euros)"></v-text-field>

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
              <h2 class="mb-5">Displays a graph of car brands with their reliability indices</h2>
              <v-btn tile color="orange" @click="reliability()">Reliability Index Chart</v-btn>
              <img v-if="pic_load" :src="src" />
            </v-container>
            <v-container v-if="i==4">
              <h2 class="mb-5">Gives user the amount he needs to pay every month for loan payment</h2>
              <v-text-field v-model="principal" label="Enter principal (in Euros)"></v-text-field>
              <v-text-field v-model="term" label="Enter term (in months) "></v-text-field>
              <v-text-field v-model="interest" label="Enter interest (in %) "></v-text-field>

              <v-btn tile color="orange" @click="loanAmount()">Calculate</v-btn>
              <v-card>
                <v-card-title v-if="loan">Monthly amount to be repaid: {{ monthly }} euros</v-card-title>
              </v-card>
            </v-container>

            <v-container v-if="i==5">
              <h2
                class="mb-5"
              >Compares 3 brands on reliability index and average repair cost and generates a graph</h2>
              <v-select
                :items="brandscomparison"
                v-model="selectedBrandComparison1"
                label="Brand 1"
              ></v-select>
              <v-select
                :items="brandscomparison"
                v-model="selectedBrandComparison2"
                label="Brand 2"
              ></v-select>
              <v-select
                :items="brandscomparison"
                v-model="selectedBrandComparison3"
                label="Brand 3"
              ></v-select>

              <v-btn tile color="orange" @click="compare()">Compare</v-btn>

              <v-card>
                <v-card-title v-if="compare_load">
                  <v-card class="mr-8">
                    <v-card-title class="indigo--text">{{selectedBrandComparison1}}</v-card-title>
                    <h3 class="font-weight-light title ml-4 mr-4">
                      Reliability index: {{brand1_rel}}
                      <br />
                      Average repair cost: {{brand1_avgrep}} euros
                    </h3>
                  </v-card>
                  <v-card class="mr-8">
                    <v-card-title class="indigo--text">{{selectedBrandComparison2}}</v-card-title>
                    <h3 class="font-weight-light title ml-4 mr-4">
                      Reliability index: {{brand2_rel}}
                      <br />
                      Average repair cost: {{brand2_avgrep}} euros
                    </h3>
                  </v-card>
                  <v-card>
                    <v-card-title class="indigo--text">{{selectedBrandComparison3}}</v-card-title>
                    <h3 class="font-weight-light title ml-4 mr-4">
                      Reliability index: {{brand3_rel}}
                      <br />
                      Average repair cost: {{brand3_avgrep}} euros
                    </h3>
                  </v-card>
                </v-card-title>
                <v-card-subtitle
                  v-if="compare_load"
                  class="red--text mt-7"
                >The Average of all cars is 100 which means that if the figure for the car you are looking at has a higher than average index it indicates that that car is less reliable than the average, if however there is a lower than average index the reliability is better.</v-card-subtitle>
              </v-card>
              <v-card>
                <img v-if="compare_load" :src="cmp_src" height="500px" />
              </v-card>
            </v-container>
          </v-card-text>
        </v-card>
      </v-tab-item>
    </v-tabs>
  </div>
</template>


<script>
import axios from "axios";

const props = {
  token: String
};
export default {
  props: props,
  data() {
    return {
      imageLoad: false,
      principal: null,
      term: null,
      interest: null,
      selectedBrandML: "",
      year: "",
      pic_load: false,
      power: null,
      monthly: null,
      loan: false,
      brand1_rel: "",
      brand1_avgrep: "",
      brand2_rel: "",
      brand2_avgrep: "",
      km: null,
      src: "",
      b64Response: "",
      final: "",
      image: "",
      selectedTypeML: "",
      selectedBrandComparison: "",
      estimateCarResult: "",
      estimateCarPrice: "",
      selectedModelML: "",
      comparison: false,
      result_compare: [],
      selectedGearML: "",
      priceRange: "",
      selectedBrand: "",
      selectedFuelML: "",
      repairedDamageML: "",
      selectedBrandComparison1: "",
      selectedBrandComparison2: "",
      selectedBrandComparison3: "",
      models: [],
      reliableCars: [],
      result: false,
      price: 0,
      tab: null,
      compare_load: false,
      cmp_src: "",
      tabs: 5,
      token_login: "random token",
      tab_vals: [
        "Estimate car price",
        "Find cars",
        "Some visual info",
        "Monthly Loan Repayment",
        "Brand Comparison"
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
      brandscomparison: [
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
    this.token_login = this.$route.params.token;
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
    logOut() {
      this.token_login = "";
      window.location.href = "/";
    },
    carListSearch() {
      axios
        .get(
          `http://localhost:9000/cars/${this.priceRange}/${this.selectedBrand}`,
          {
            headers: {
              "AUTH-TOKEN": this.token_login
            }
          }
        )

        .then(response => {
          this.estimateCarResult = response.data;
        })
        .catch(function(error) {
          if (error.response) {
            if (error.response.status == 401) {
              alert("Authetication token is missing");
              window.location.href = "/";
            }
          }
        });
    },

    loanAmount() {
      axios
        .get("http://localhost:9000/loans", {
          params: {
            principal: this.principal,
            term: this.term,
            interest: this.interest
          },
          headers: {
            "AUTH-TOKEN": this.token_login
          }
        })
        .then(response => {
          this.monthly = response.data;
          this.monthly = this.monthly.toFixed(2);
          this.loan = true;
        })
        .catch(function(error) {
          if (error.response) {
            if (error.response.status == 401) {
              alert("Authetication token is missing");
              window.location.href = "/";
            }
          }
        });
    },

    estimatePrice() {
      axios
        .get("http://localhost:9000/price", {
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
          },
          headers: {
            "AUTH-TOKEN": this.token_login
          }
        })
        .then(response => {
          this.estimateCarPrice = response.data.Predicted_Price;
          this.result = true;
        })
        .catch(function(error) {
          if (error.response) {
            if (error.response.status == 401) {
              alert("Authetication token is missing");
              window.location.href = "/";
            }
          }
        });
    },

    reliability() {
      axios
        .get(`http://localhost:9000/reliability`, {
          headers: {
            "AUTH-TOKEN": this.token_login
          },
          responseType: "arraybuffer"
        })
        .then(response => {
          this.pic_load = true;
          let blob = new Blob([response.data], {
            type: response.headers["content-type"]
          });
          let image = URL.createObjectURL(blob);
          this.src = image;
        })
        .catch(function(error) {
          if (error.response) {
            if (error.response.status == 401) {
              alert("Authetication token is missing");
              window.location.href = "/";
            }
          }
        });
    },
    compare() {
      axios
        .get("http://localhost:9000/graphcomparisons", {
          responseType: "arraybuffer",

          headers: {
            "AUTH-TOKEN": this.token_login
          },

          params: {
            Brand_1: this.selectedBrandComparison1,
            Brand_2: this.selectedBrandComparison2,
            Brand_3: this.selectedBrandComparison3
          }
        })
        .then(response => {
          this.compare_load = true;
          let blob = new Blob([response.data], {
            type: response.headers["content-type"]
          });
          let image = URL.createObjectURL(blob);
          this.cmp_src = image;
        })
        .catch(function(error) {
          if (error.response) {
            if (error.response.status == 401) {
              alert("Authetication token is missing");
              window.location.href = "/";
            }
          }
        });
      console.log("calling next");
      axios
        .get(`http://localhost:9000/comparisons`, {
          headers: {
            "AUTH-TOKEN": this.token_login
          },
          params: {
            Brand_1: this.selectedBrandComparison1,
            Brand_2: this.selectedBrandComparison2,
            Brand_3: this.selectedBrandComparison3
          }
        })

        .then(response => {
          console.log(response.data);
          this.brand1_rel = response.data.Brand_1_reliability;
          this.brand1_avgrep = response.data.Brand_1_avgcost;
          this.brand2_rel = response.data.Brand_2_reliability;
          this.brand2_avgrep = response.data.Brand_2_avgcost;
          this.brand3_rel = response.data.Brand_3_reliability;
          this.brand3_avgrep = response.data.Brand_3_avgcost;
        })
        .catch(function(error) {
          if (error.response) {
            if (error.response.status == 401) {
              alert("Authetication token is missing");
              window.location.href = "/";
            }
          }
        });
    }
  }
};
</script>
<style scoped>
</style>