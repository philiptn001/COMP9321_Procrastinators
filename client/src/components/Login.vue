<template>
  <div class="mt-12" align="center">
    <v-card light raised width="400">
      <p class="font-weight-light headline mt-12 pt-10 text-center">Login</p>

      <v-card-text class="mb-n8">
        <v-form>
          <v-text-field
            class="mb-n6"
            label="Username"
            prepend-inner-icon="mdi-account-circle"
            outlined
            v-model="username"
          />
          <v-text-field
            :type="showPassword ? 'text' : 'password'"
            label="Password"
            prepend-inner-icon="mdi-lock"
            :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
            @click:append="showPassword = !showPassword"
            outlined
            v-model="password"
          />
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-row align="center">
          <v-col class="text-center">
            <v-btn @click="getKey()" dark tile color="#5C6BC0" width="40%" class="mt-n6">Login</v-btn>
          </v-col>
        </v-row>
      </v-card-actions>
      <p class="text-center mt-n3 pb-2 subtitle-2 font-weight-light">
        New to our website?
        <router-link to="/register">Register</router-link>
      </p>
    </v-card>
  </div>
</template>


<script>
import axios from "axios";

export default {
  data() {
    return {
      username: "",
      password: "",
      showPassword: false
    };
  },
  methods: {
    getKey() {
      console.log(this.username, this.password);
      axios
        .post(`http://localhost:9000/session`, null, {
          params: {
            username: this.username,
            password: this.password
          }
        })
        .then(
          response => {
            console.log(response);
            if (response.status == 200) {
              this.token = response.data.token;

              //this.$root.$emit('token', this.token);
              this.$router.push({
                name: "landing",
                params: {
                  token: this.token
                }
              });
            }
          },
          error => {
            console.log(error);
          }
        );
    }
  }
};
</script>
