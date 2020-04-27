from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
import os
from flask_cors import *
from twilio.rest import Client
import multiprocessing
from multiprocessing import Process, Queue
import time 
import requests
from pandas import DataFrame, Series
from finta import TA
from finta.utils import to_dataframe
import datetime
import pandas as pd
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)

class TwilioNotifications:

    def __init__(self, account_sid, auth_token, message, from_phone, to_phones):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.client = Client(account_sid, auth_token)
        self.message = message
        self.from_phone = from_phone
        self.to_phones = to_phones

    def send_call(self ):
        for phone in self.to_phones.split(','):
            self.client.calls.create(
                twiml='<Response><Say language="eng-US" >' + self.message + '</Say></Response>',
                to= phone,
                from_=self.from_phone
                )

    def send_sms(self):
        for phone in self.to_phones.split(','):
            print(phone)
            self.client.messages.create(
                    body=self.message,
                    from_=self.from_phone,
                    to=phone
                )

class TradingAlarmProcess:
    def __init__(self, alarm):
        multiprocessing.freeze_support()
        self.alarm = alarm
        self.status = 'inactive'
        self.main_queu = Queue()
        self.tickerSymbol = alarm['tickerSymbol']
        self.frequencyType = 'minute'
        if 'day' in alarm['chartPeriod']:
            self.frequencyType = 'daily'            
        ##TODO add other frequencies
        ##For now it works only with min 1,5,10,15,30 and 1 day
        self.params = (  
            ('apikey', alarm['ameritrade_key']),  
            ('periodType', 'day'),  
            ('period', '1'),  
            ('frequencyType', 'minute'),  
            ('frequency', alarm['chartPeriod'][0] ),  
        )  
        self.headers = {  
                    'Authorization': '',  
            }   
        self.price_history_request_url =\
             'https://api.tdameritrade.com/v1/marketdata/' + self.tickerSymbol\
              + '/pricehistory'  
        self.set_indicator_function()    
        self.active = False

    def set_indicator_function(self ):
        indicator = self.alarm['indicator']
        kc = ''
        if indicator == 'Keltner Channel':
            self.indicator_main = kc,

    def start_alarm(self):
        self.active = True
        self.process = Process(target=self.main_alarm, args=(self.main_queu,))
        self.process.start()


    def main_alarm(self, q):
        while self.active: 
            if not q.empty():
                val = q.get()
                if val == 'STOP':
                    break
            #Currently for minutes only 1,5,10,15,30 
            time.sleep(5 * int(self.alarm['chartPeriod'][0] ))
            response = requests.get(self.price_history_request_url, headers=self.headers, params=self.params)
            df = pd.DataFrame(response.json()['candles'])
            kc = TA.KC(df)
            kc_tail = kc.tail(2)
            df_tail = df.tail(2)
            comparing = ''
            comparing_av = ''
            if self.alarm['kcband'] == 'Upper':
                comparing = kc_tail.KC_UPPER.values
            elif self.alarm['kcband'] == 'Lower':
                comparing = kc_tail.KC_LOWER.values
            if self.alarm['price'] == 'close':
                comparing_av = df_tail.close
            elif self.alarm['price'] == 'high':
                comparing_av = df_tail.high
            elif self.alarm['price'] == 'low':
                comparing_av = df_tail.low
            elif self.alarm['price'] == 'open':
                comparing_av = df_tail.open
            if self.alarm['crossingType'] == 'Above':
                if comparing_av.values[0] >= comparing[0] and comparing_av.values[1] <= comparing[1]:
                    message == self.tickerSymbol + ' / ' + self.alarm['chartPeriod'] +\
                        ' input ' + self.alarm['title'] + ' has been met - '+\
                            datetime.datetime.fromtimestamp(df_tail.datetime.values[1]).strftime("%H:%M:%S")
                    
            elif self.alarm['crossingType'] == 'Below':
                if comparing_av.values[0] <= comparing[0] and comparing_av.values[1] >= comparing[1]:
                    message == self.tickerSymbol + ' / ' + self.alarm['chartPeriod'] +\
                        ' input ' + self.alarm['title'] + ' has been met - '+\
                            datetime.datetime.fromtimestamp(df_tail.datetime.values[1]).strftime("%H:%M:%S")
            print('Alarm: ' + self.alarm['title'] + ' running')

    def create_notifications(self, message):
        notifications = TwilioNotifications(self.alarm['twilio_sid'], self.alarm['twilio_key'], message, self.alarm['from_phone'], self.alarm['to_phones'])
        if self.alarm['phone_call']:
            notifications.send_call()
        if self.alarm['sms']:
            notifications.send_sms()

    def main_stop_alarm(self):
        self.active = False
        self.main_queu.put('STOP')
        self.process.join()
        print("Alarm :"+ self.alarm['title'] + ' deactivated')



class Alarm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    twilio_key = db.Column(db.String)
    twilio_sid = db.Column(db.String)
    ameritrade_key = db.Column(db.String)
    tickerSymbol = db.Column(db.String)
    chartPeriod = db.Column(db.String)
    from_phone = db.Column(db.String)
    to_phones = db.Column(db.String)
    indicator = db.Column(db.String)
    kcband = db.Column(db.String)
    crossingType = db.Column(db.String)
    averageType = db.Column(db.String)
    trueRangeAverageType = db.Column(db.String)
    price = db.Column(db.String)
    displace = db.Column(db.Integer)
    factor = db.Column(db.Integer)
    length = db.Column(db.Integer)
    sms = db.Column(db.Boolean)
    phone_call = db.Column(db.Boolean)
    status = db.Column(db.String)


    def __init__(self,
        title,
        twilio_key,
        twilio_sid,
        ameritrade_key,
        tickerSymbol,
        chartPeriod,
        from_phone,
        to_phones,
        indicator,
        kcband,
        crossingType,
        averageType,
        trueRangeAverageType,
        price,
        displace,
        factor,
        length,
        sms,
        phone_call,
        status):
        self.title = title
        self.twilio_key = twilio_key
        self.twilio_sid = twilio_sid
        self.ameritrade_key = ameritrade_key
        self.tickerSymbol = tickerSymbol
        self.chartPeriod = chartPeriod
        self.from_phone = from_phone
        self.to_phones = to_phones
        self.indicator = indicator
        self.kcband = kcband
        self.crossingType = crossingType
        self.averageType = averageType
        self.trueRangeAverageType = trueRangeAverageType
        self.price = price
        self.displace = displace
        self.factor = factor
        self.length = length
        self.sms = sms
        self.phone_call = phone_call
        self.status = status


# Product Schema
class AlarmSchema(ma.Schema):
  class Meta:
    fields = (
      'id',
      'title',
      'twilio_key',
      'twilio_sid',
      'ameritrade_key',
      'tickerSymbol',
      'chartPeriod',
      'from_phone',
      'to_phones',
      'indicator',
      'kcband',
      'crossingType',
      'averageType',
      'trueRangeAverageType',
      'price',
      'displace',
      'factor',
      'length',
      'sms',
      'phone_call',
      'status')

alarm_schema = AlarmSchema()
alarms_schema = AlarmSchema(many=True )
db.create_all()

active_alarms = []

# Create a Alarm
@app.route('/alarm', methods=['POST'])
@cross_origin()
def add_alarm():
  title = request.json['title']
  twilio_key = request.json['twilio_key']
  twilio_sid = request.json['twilio_sid']
  ameritrade_key = request.json['ameritrade_key']
  tickerSymbol = request.json['tickerSymbol']
  chartPeriod = request.json['chartPeriod']
  from_phone = request.json['from_phone']
  to_phones = request.json['to_phones']
  indicator = request.json['indicator']
  kcband = request.json['kcband']
  crossingType = request.json['crossingType']
  averageType = request.json['averageType']
  trueRangeAverageType = request.json['trueRangeAverageType']
  price = request.json['price']
  displace = request.json['displace']
  factor = request.json['factor']
  length = request.json['length']
  sms = request.json['sms']
  phone_call = request.json['phone_call']
  status = request.json['status']
  new_alarm = Alarm(title,
        twilio_key,
        twilio_sid,
        ameritrade_key,
        tickerSymbol,
        chartPeriod,
        from_phone,
        to_phones,
        indicator,
        kcband,
        crossingType,
        averageType,
        trueRangeAverageType,
        price,
        displace,
        factor,
        length,
        sms,
        phone_call,
        status)

  db.session.add(new_alarm)
  db.session.commit()

  return alarm_schema.jsonify(new_alarm)

@app.route('/alarm', methods=['GET'])
@cross_origin()
def get_alarms():
  all_alarms = Alarm.query.all()
  result = alarms_schema.dump(all_alarms)
  return jsonify(result)

@app.route('/alarm/<id>', methods=['GET'])
@cross_origin()
def get_alarm(id):
  alarm = Alarm.query.get(id)
  return alarm_schema.jsonify(alarm)

@app.route('/start_alarm', methods=['POST','OPTIONS'])
@cross_origin()
def start_alarm():
  new_alarm = TradingAlarmProcess(request.json)
  new_alarm.start_alarm()
  active_alarms.append(new_alarm)
  return jsonify({'status':200})

@app.route('/send_sms', methods=['POST','OPTIONS'])
@cross_origin()
def send_sms():
  notification = TwilioNotifications(
      request.json['twilio_sid'],
      request.json['twilio_key'],
      'Hello, this is a test message. It is working',
      request.json['from_phone'],
      request.json['to_phones'],
  )
  notification.send_sms()
  return jsonify({'status':200})

@app.route('/send_call', methods=['POST','OPTIONS'])
@cross_origin()
def send_call():
  notification = TwilioNotifications(
      request.json['twilio_sid'],
      request.json['twilio_key'],
      'Hello, this is a test message. It is working',
      request.json['from_phone'],
      request.json['to_phones'],
  )
  notification.send_call()
  return jsonify({'status':200})


@app.route('/stop_alarm', methods=['POST','OPTIONS'])
@cross_origin()
def stop_alarm():
    for alarm in active_alarms:
        if alarm.alarm['id'] == request.json['id']:
          alarm.main_stop_alarm()
          active_alarms.remove(alarm)
          break
    return jsonify({'status':200})
# Update a Alarm
# @app.route('/alarm/<id>', methods=['PUT'])
# def update_alarm(id):
#   alarm = Alarm.query.get(id)

#   name = request.json['name']
#   description = request.json['description']
#   price = request.json['price']
#   qty = request.json['qty']

#   alarm.name = name
#   alarm.description = description
#   alarm.price = price
#   alarm.qty = qty

#   db.session.commit()

#   return alarm_schema.jsonify(alarm)

@app.route('/alarm/<id>', methods=['DELETE'])
@cross_origin()
def delete_alarm(id):
  alarm = Alarm.query.get(id)
  db.session.delete(alarm)
  db.session.commit()

  return alarm_schema.jsonify(alarm)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    app.run(host="0.0.0.0",debug=True)
