<template>
  <div class="dashboard">
    <h1 class="subheading grey--text">Dashboard</h1>

    <v-container class="my-5">

      <v-layout row justify-start class="mb-3">
        <v-tooltip top>
          <v-btn small flat color="grey" @click="sortBy('title')" slot="activator">
            <v-icon small left>folder</v-icon>
            <span class="caption text-lowercase">By alarm name</span>
          </v-btn>
          <span>Sort by alarm name</span>
        </v-tooltip>
        
      </v-layout>
      
      <v-card flat v-for="alarm in alarms" :key="alarm.title">
        <alarm-summary :alarm="alarm"></alarm-summary>
      
      </v-card>

    </v-container>
   
  </div>
</template>

<script>
import axios from 'axios';
import AlarmSummary from './AlarmSummary.vue';

export default {
  data() {
    return {
      info: null,
      alarms: []
    }
  }, mounted () {
    axios.get('http:///localhost:5000/alarm').then(response => (this.alarms = response['data']))
  },
    components: { AlarmSummary },

  methods: {
    sortBy(prop) {
      this.alarms.sort((a,b) => a[prop] < b[prop] ? -1 : 1)
    }
  }
}
</script>

<style>

.alarm.active{
  border-left: 4px solid #3cd1c2;
}
.alarm.ongoing{
  border-left: 4px solid #ffaa2c;
}
.alarm.inactive{
  border-left: 4px solid #f83e70;
}
.v-chip.active{
  background: #3cd1c2;
}
.v-chip.ongoing{
  background: #ffaa2c;
}
.v-chip.inactive{
  background: #f83e70;
}

</style>
