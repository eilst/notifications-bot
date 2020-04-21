<template>
  <div class="alarms">
    <h1 class="subheading grey--text">Alarms</h1>

    <v-container class="my-5">
      <v-expansion-panel>
        <v-expansion-panel-content v-for="alarm in alarms" :key="alarm.title">
          <div slot="header" class="py-1">{{ alarm.title }}</div>
          <v-card>
            <v-card-text class="px-4 grey--text">
              <div class="font-weight-bold">Indicator: {{ alarm.indicator }}</div>
              <div><b>From phone: </b> {{ alarm.from_phone }}</div>
              <div><b>To phones: </b> {{ alarm.to_phones }}</div>
              <div><b>KC band: </b>{{ alarm.kcband }}</div>
              <div><b>Crossing Type: </b>{{ alarm.crossingType }}</div>
              <div><b>Average Type: </b>{{ alarm.averageType }}</div>
              <div><b>True Range Average Type: </b>{{ alarm.trueRangeAverageType }}</div>
              <div><b>Price: </b>{{ alarm.price }}</div>
              <div><b>Displace: </b>{{ alarm.displace }}</div>
              <div><b>Factor: </b>{{ alarm.factor }}</div>
              <div><b>Length: </b>{{ alarm.length }}</div>
              <div><b>SMS: </b>{{ alarm.sms }}</div>
              <div><b>Phone Call: </b>{{ alarm.phone_call }}</div>
            </v-card-text>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-container>
    
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      alarms: []
    }
  },
  mounted () {
    axios.get('http://localhost:8000/alarms').then(response => (this.alarms = response['data']))
  },
  computed: {
   
  }
}
</script>
