from twilio.rest import Client

class TwilioNotifications:

    def __init__(self, accont_sid, auth_token, message, from_phone, to_phones):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.client = Client(account_sid, auth_token)
        self.message = message
        self.from_phone = from_phone
        self.to_phones = to_phones

    def send_call(self, message ):
        for phone in self.to_phones:
            client.calls.create(
                twiml='<Response><Say language="eng-US" >' + self.message + '</Say></Response>',
                to= phone,
                from_=self.from_phone
                )