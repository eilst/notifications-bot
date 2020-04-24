import multiprocessing
from multiprocessing import Process, Queue
import time 
from indicators import kc
import requests
from pandas import DataFrame, Series
from finta import TA
from finta.utils import to_dataframe
from notifications.twilio_notification import TwilioNotifications
import datetime
import pandas as pd

class TradingAlarmProcess:
    def __init__(self, alarm):
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
        self.active = True
        self.condition = True 
        self.start_alarm()

    def set_indicator_function(self ):
        indicator = self.alarm['indicator']
        if indicator == 'Keltner Channel':
            self.indicator_main = kc,

    def start_alarm(self):
        self.process = Process(target=self.main_alarm)
        self.process.start()


    def main_alarm(self):
        while self.active: 
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
            pass
            #notifications.send_sms()

    def main_stop_alarm(self):
        self.active = False
        self.process.join()


