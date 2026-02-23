'''
This main.py file is to be used with Railway

See chapter 9 for further detail
'''
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)


@app.route('/')
def homepage():
    return 'All working!'


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():

    from_number = request.form['From']
    body = request.form['Body']
    resp = MessagingResponse()

    msg = (f'Awwwww! Thanks so much for your message {from_number}, '
           f'"{body}" to you too. ')

    resp.message(msg)
    return str(resp)


if __name__ == '__main__':
    app.run()
