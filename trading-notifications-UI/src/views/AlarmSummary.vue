<template>      
      <v-card flat>
        <v-layout row wrap :class="`pa-3 alarm ${alarm.status}`">
          <v-flex xs6 sm4 md2>
            <div class="caption grey--text">Alarm title</div>
            <div>{{ alarm.title }}</div>
          </v-flex>
          <v-flex xs6 sm4 md2>
            <div class="caption grey--text">Indicator</div>
            <div>{{ alarm.indicator }}</div>
          </v-flex>
          <v-flex xs6 sm4 md2>
            <div class="caption grey--text">To phones</div>
            <div>{{ alarm.to_phones }}</div>
          </v-flex>
          <v-flex xs2 sm4 md2>
            <div class="right">
              <v-chip small :class="`${alarm.status} white--text my-2 caption`">{{ alarm.status }}</v-chip>
              <v-switch
      v-model="switch1"
      :label="`Activate:`"
    ></v-switch>
 
            </div>
          </v-flex>
          <v-flex xs2 sm4 md2>
            <div class="right">
            <v-btn color="error" @click="deleteAlarm">Delete</v-btn>
            </div>
          </v-flex>
        </v-layout>
        <v-divider></v-divider>
      </v-card>

</template>

<script>
import axios from 'axios';

export default {
  name: 'alarm-summary',
  props:['alarm'],
  data() {
    return {
      info: null,
      switch1: false
    }
  }, mounted () {
  },
  methods: {
    sortBy(prop) {
      this.alarms.sort((a,b) => a[prop] < b[prop] ? -1 : 1)
    },
    activate: function(event){
        debugger;
                fetch("http://localhost:8000/start_alarm/", {
              body: JSON.stringify(
                this.alarm
                 ),
              headers: {
                Accept: "application/json",
                "Content-Type": "application/json"
              },
              method: "POST"
            });
        this.alarm.status = 'active';
    },
    deleteAlarm: function(){
    axios.delete("http://localhost:8000/alarm/"+ String(this.alarm.id));
    //TODO Tick, refresh 
    }
  },
  watch: {
      switch1(newValue){
        //called whenever switch1 changes
        if(newValue){
        this.activate();
        }else{
            //TODO: Deactivate endpoint
        this.alarm.status = 'inactive';
        }
        console.log(newValue);
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
