from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
import os
from flask_cors import *
from trading_alarms.trading_alarm_process import TradingAlarmProcess

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)


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
  active_alarms.append(new_alarm)
  return jsonify({'status':200})

@app.route('/stop_alarm', methods=['POST','OPTIONS'])
@cross_origin()
def start_alarm():
    import ipdb; ipdb.set_trace()
    new_alarm = TradingAlarmProcess(request.json)
    active_alarms.append(new_alarm)
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
  app.run(host="0.0.0.0",debug=True)
