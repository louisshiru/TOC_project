
import sys
from io import BytesIO

import telegram
from flask import Flask, request, send_file

from fsm import TocMachine

API_TOKEN = '504232298:AAGAPYhVAKKO5UpPHay3oXR4ce9af1EdLUk'
WEBHOOK_URL = 'https://aa4890d9.ngrok.io/hook'

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
machine = TocMachine(
    states=[
        'user',
        'state1',
        'state2',
        'state3',
        'ask',
        'askwhy',
        'askdicision',
        'askmission',
        'notrasher',
        'no'
    ],
    transitions=[
        
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'state1',
            'conditions': 'is_going_to_state1'
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'state2',
            'conditions': 'is_going_to_state2'
        },
        
        {
            'trigger':'advance',
            'source': 'state1',
            'dest': 'state3',
            'conditions': 'is_going_to_state3'
        },
        
        {
            'trigger': 'go_back',
            'source': [
                'state1',
                'state2',
                'no',
            ],
            'dest': 'user'
        },
        
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'ask',
            'conditions': 'is_going_to_ask'
        },

        {
            'trigger': 'advance',
            'source': 'ask',
            'dest': 'askwhy',
            'conditions': 'is_going_to_askwhy'
        },

        {
            'trigger': 'advance',
            'source': 'ask',
            'dest': 'no',
            'conditions': 'is_going_to_no'
        }

    ],
    initial='user'
#    auto_transitions=False,
#    show_conditions=True,
)


def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))


@app.route('/hook', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    machine.advance(update)
    return 'ok'


@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')


if __name__ == "__main__":
    _set_webhook()
    app.run()