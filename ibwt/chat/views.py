import json
import datetime

from flask import Markup
from flask_user import login_required, current_user
from flask.ext.socketio import emit

from ibwt.app_and_db import socketio, session
from ibwt.chat.models import Message
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

@socketio.on('connect', namespace='/shoutbox')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/shoutbox')
def test_disconnect():
    print('Client disconnected')


@socketio.on('send_message', namespace='/shoutbox')
@login_required
def test_message(message):
    message['data'] = strip_tags(message['data'].strip())
    if message['data'].strip():
        # remove url
        if is_clean_message(message['data']):
            message['data'] = message['data']
        else:
            message['data'] = 'blocked for spam'
        emit('my response', {'data': 'im here 1', 'count': 0})
        messagedb = Message(text=message['data'],
                            user=current_user.email,
                            locale=session['language'],
                            at=datetime.datetime.utcnow())
        messagedb.save()
        ret_message = {'text': messagedb.text,
                       'user': Markup(messagedb.user),
                       'locale':messagedb.locale}
        emit('send_message_response', json.dumps(ret_message), broadcast=True,
             )


def is_clean_message(msg):
    return True
