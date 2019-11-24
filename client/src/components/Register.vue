<template>
  <div class="mt-12" align="center">
    <v-card light raised width="400">
      <p class="font-weight-light headline mt-12 pt-10 text-center">Register</p>

      <v-card-text class="mb-n8">
        <v-form>
          <v-text-field
            class="mb-n1"
            dense
            tile
            label="Name"
            outlined
            v-model="firstname"
            required
            :rules="nameRules"
          />

          <v-text-field
            dense
            class="mb-n1"
            label="Email"
            outlined
            v-model="email"
            required
            :rules="emailRules"
          />

          <v-text-field dense
            class="mb-n1"
            label="Username"
            prepend-inner-icon="mdi-account-circle"
            outlined
            v-model="username"
            :rules="nameRules"
          />
          <v-text-field dense
            :type="showPassword ? 'text' : 'password'"
            label="Password"
            prepend-inner-icon="mdi-lock"
            :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
            @click:append="showPassword = !showPassword"
            outlined
            v-model="password"
            :rules="nameRules"
          />
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn tile dark color="#5C6BC0" width="40%" class="mx-auto mt-2" @click="signUp()">Sign Up</v-btn>
      </v-card-actions>
      <p class="text-center pb-2 subtitle-2 font-weight-light">
        Already a member?
        <router-link to="/" >Login</router-link>
      </p>
    </v-card>
  </div>
</template>


<script>
import axios from "axios";
export default {
  data() {
    return {
      valid: true,
      firstname: "",
      lastname: "",
      email: "",
      username: "",
      emailRules: [
        v => !!v || "Email is required",
        v => /.+@.+/.test(v) || "Email must be valid"
      ],
      nameRules: [v => !!v || "Field is required"],
      password: "",
      showPassword: false,
    };
  },
  created() {
    console.log("checking");
    // this.getMessage();
  },

  methods: {
      signUp(){
        console.log(this.username, this.password);
      axios
        .post("http://localhost:9000/user", null, {
          params: {
            username: this.username,
            password: this.password
          }
        })
        .then(
          response => {
            console.log(response);
            if(response.status == 200){
              this.$router.push({
                  name: "login",
      });
            }
          },
          error => {
            console.log(error);
          }
        );
      }
    /* getMessage() {
      const path = "http://localhost:9000/landing";
      axios
        .get(path)
        .then(res => {
          this.msg = res.data;
        })
        .catch(error => {
          // eslint-disable-next-line
          console.error(error);
        }); */
  //}
  //},
  //created() {
  //this.getMessage();
  } 
};
</script>
