<template>
  <div>
    <p>{{ msg }}</p>
  </div>
</template>

<script>
  import axios from 'axios';
  export default {
  name: 'home_page',
  data() {
    return {
      msg: 'Hello!',
    };
  },
  methods: {
    getMessage() {
      const path = 'http://localhost:9000/landing';
      axios.get(path)
        .then((res) => {
          this.msg = res.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getMessage();
  },
};
</script>
