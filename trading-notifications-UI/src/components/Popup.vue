<template>
  <v-dialog max-width="600px">
    <v-btn flat slot="activator" class="success">Add New Alarm</v-btn>
    <v-card>
      <v-card-title>
        <h2>Add a New Alarm</h2>
      </v-card-title>
      <v-card-text>
        <v-form class="px-3" ref="form">
          <v-text-field v-model="title" label="Title"  :rules="inputRules"></v-text-field>
          <v-text-field  
            :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'" 
            :type="show ? 'text' : 'password'"
            v-model="twilio_key"
            hint="Your Twilio Api Key"
            label="Twilio Api Key"

            :rules="inputRules"
            class="input-group--focused"
            @click:append="show = !show"></v-text-field>
            <v-text-field  
            :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'" 
            :type="show ? 'text' : 'password'"
            v-model="twilio_sid"
            hint="Your Twilio Account SID"
            label="Twilio Account SID"

            :rules="inputRules"
            class="input-group--focused"
            @click:append="show = !show"></v-text-field>
          <v-text-field v-model="from_phone" label="From Phone Number (Twilio number)"  :rules="inputRules"></v-text-field>
           <v-combobox
    v-model="to_phones"
    :items="items"
    to_phones
    clearable
    label="To phone numbers (notifications)"
    multiple
    prepend-icon="filter_list"
    solo
  >
    <template v-slot:selection="{ attrs, item, select, selected }">
      <v-chip
        v-bind="attrs"
        :input-value="selected"
        close
        @click="select"
        @click:close="remove(item)"
      >
        <strong>{{ item }}</strong>&nbsp;
        <span>(interest)</span>
      </v-chip>
    </template>
  </v-combobox>
          <v-text-field  
            :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'" 
            :type="show ? 'text' : 'password'"
            v-model="ameritrade_key"
            hint="Your TDAmeritrade Api Key"
            label="TDAmeritrade Api Key"

            :rules="inputRules"
            class="input-group--focused"
            @click:append="show = !show"></v-text-field>
        
        <v-text-field v-model="tickerSymbol" label="Ticker Symbol"  ></v-text-field>
       <label>Chart Period</label>
         <v-select
          :items="chartPeriods"
          v-model="chartPeriod"
          label="Indicator"
          hint="Chart Period"
          solo
        ></v-select>

        <label>Indicator</label>
         <v-select
          :items="indicators"
           @input="selectIndicator"
          label="Indicator"
          hint="Indicator"
          solo
        ></v-select>


          <v-spacer></v-spacer>
          <div  v-if="indicator=='Keltner Channel'">
           <label>Type of crossing</label>
          <v-select
          v-if="indicator=='Keltner Channel'"
          :items="kcbands"
          v-model="kcband"
          label="Select band"
          hint="Select band"
          :rules="inputRules"
          solo
        ></v-select>

          <label>Type of crossing</label>
          <v-select
          v-if="indicator=='Keltner Channel'"
          :items="crossingTypes"
           @input="selectCrossingType"
          label="Type of crossing"
          hint="Type of crossing"
          :rules="inputRules"
          solo
        ></v-select>
        <v-text-field
        v-if="indicator=='Keltner Channel'"
          v-model="displace"
          type="number"
          label="Displace (default is 0)"
        ></v-text-field>
         <v-text-field
        v-if="indicator=='Keltner Channel'"
          v-model="factor"
          type="number"
          label="Factor"
          hint="The factor by which the ATR value is multiplied to calculate the distance"
        ></v-text-field>
         <v-text-field
        v-if="indicator=='Keltner Channel'"
          v-model="length"
          type="number"
          label="Length"
          hint="Length"
        ></v-text-field>
         <label>Price</label>
         <v-select
          v-if="indicator=='Keltner Channel'"
          v-model="price"
          :items="prices"
          label="Price"
          hint="Price"
          :rules="inputRules"
          solo
        ></v-select>
        <label>Average Type</label>
        <v-select
          v-if="indicator=='Keltner Channel'"
          v-model="averageType"
          :items="averageTypes"
          label="Average Type"
          hint="Average Type"
          :rules="inputRules"
          solo
        ></v-select>

        <label>True Range Average Type</label>
         <v-select
          v-if="indicator=='Keltner Channel'"
          v-model="trueRangeAverageType"
          :items="trueRangeAverageTypes"
          label="True Range Average Type"
          hint="True Range Average Type"
          :rules="inputRules"
          solo
        ></v-select>
        </div>
         <v-switch
              v-model="sms"
              label="SMS"
              color="red"
              hide-details
            ></v-switch>
             <v-switch
              v-model="phoneCall"
              label="Phone Call"
              color="red"
              hide-details
            ></v-switch>
          <v-spacer></v-spacer>

          <v-btn flat @click="submit" class="success mx-0 mt-3">Add Alarm</v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>


<script>
import format from 'date-fns/format'

export default {
  data() {
    return {
      title: '',
      content: '',
      due: null,
      sms: true,
      phoneCall: false,
      tickerSymbol: '',
      chartPeriod: '',
      chartPeriods:['1 min',
      '2 mins',
      '5 mins',
      '15 mins',
      '30 mins',
      '1 hour',
      '4 hours',
      '1 day',
      '1 week',
      '1 month',
      '1 year'],
      indicators: ['Keltner Channel'],
      kcbands: ['Upper', 'Middle', 'Lower'],
      kcband:'',
      crossingTypes: ['Above','Below'],
      crossingType: '',
      indicator:'',
      from_phone: '',
      ameritrade_key: '',
      twilio_key: '',
      twilio_sid: '',
      displace:0,
      factor:2,
      length:20,
      prices: ['close','open','high','low'],
      price: 'close',
      averageTypes:['Exponential', 'Weighted', 'Wilders', 'Simple', 'Hull'],
      averageType:'Exponential',
      trueRangeAverageTypes:['Exponential', 'Weighted', 'Wilders', 'Simple', 'Hull'],
      trueRangeAverageType:'Exponential',
      show: false,
      menu: false,
        to_phones: [],
        items: ['Default numbers can be added',],
      inputRules: [
        v => !!v || 'This field is required',
        v => v.length >= 3 || 'Minimum length is 3 characters'
      ]
    }
  },
  methods: {
    submit() {
      if(this.$refs.form.validate()) {
        debugger;
        fetch("http://10.42.0.54:5000/alarm", {
              body: JSON.stringify({
                    "title":this.title,
                    "twilio_key": this.twilio_key,
                    "twilio_sid": this.twilio_sid,
                    "ameritrade_key": this.ameritrade_key,
                    "from_phone": this.from_phone,
                    "to_phones": String(this.to_phones),
                    "indicator": this.indicator,
                    "kcband": this.kcband,
                    "crossingType": this.crossingType,
                    "displace": this.displace,
                    "factor": this.factor,
                    "length": this.length,
                    "price": this.price,
                    "averageType": this.averageType,
                    "trueRangeAverageType": this.trueRangeAverageType,
                    "sms": this.sms,
                    "tickerSymbol": this.tickerSymbol,
                    "chartPeriod": this.chartPeriod,
                    "phone_call": this.phoneCall,
                    "status":'inactive'
                 }),
              headers: {
                Accept: "application/json",
                "Content-Type": "application/json"
              },
              method: "POST"
            });


        console.log(this.title, this.content)
      }
    },
     remove (item) {
        this.to_phones.splice(this.to_phones.indexOf(item), 1)
        this.to_phones = [...this.to_phones]
      },
      selectIndicator: function(indicator){
      this.indicator = indicator;
    },
    selectCrossingType: function(crossingType){
      this.crossingType = crossingType;
    },
    selectTrueRangeAverageType: function(trueRangeAverageType){
      this.trueRangeAverageType = trueRangeAverageType;
    },
    selectAverageTypes: function(averageType){
      this.averageType = averageType;
    }
  },
  computed: {
    formattedDate () {
      console.log(this.due)
      return this.due ? format(this.due, 'Do MMM YYYY') : ''
    }
  }
}
</script>
