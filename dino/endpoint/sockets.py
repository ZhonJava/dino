# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import threading
import time
import traceback
import logging

from datetime import datetime
from typing import Union
from uuid import uuid4 as uuid

import activitystreams as as_parser
from activitystreams.exception import ActivityException
from activitystreams.models.activity import Activity
from flask_socketio import disconnect
from kombu import Connection
from kombu.mixins import ConsumerMixin

from dino import api
from dino import environ
from dino.config import ConfigKeys
from dino.config import SessionKeys
from dino.config import RedisKeys
from dino.utils.decorators import pre_process
from dino.utils.decorators import respond_with
from dino.utils.decorators import count_connections
from dino.forms import LoginForm
from dino.server import app, socketio
from dino.utils.handlers import GracefulInterruptHandler
from dino.endpoint.queue import QueueHandler

logger = logging.getLogger(__name__)
queue_handler = QueueHandler(socketio, environ.env)


class Worker(ConsumerMixin):
    def __init__(self, connection, signal_handler: GracefulInterruptHandler):
        self.connection = connection
        self.signal_handler = signal_handler

    def get_consumers(self, consumer, channel):
        return [consumer(queues=[environ.env.queue], callbacks=[self.process_task])]

    def on_iteration(self):
        if self.signal_handler.interrupted:
            self.should_stop = True

    def process_task(self, body, message):
        try:
            queue_handler.handle_server_activity(body, as_parser.parse(body))
        except (ActivityException, AttributeError) as e:
            logger.error('could not parse server message: "%s", message was: %s' % (str(e), body))
        message.ack()


def consume():
    with GracefulInterruptHandler() as interrupt_handler:
        while True:
            with Connection(environ.env.config.get(ConfigKeys.HOST, domain=ConfigKeys.QUEUE)) as conn:
                try:
                    environ.env.consume_worker = Worker(conn, interrupt_handler)
                    environ.env.consume_worker.run()
                except KeyboardInterrupt:
                    return

            if interrupt_handler.interrupted or environ.env.consume_worker.should_stop:
                return

            time.sleep(1)


if not environ.env.config.get(ConfigKeys.TESTING, False):
    def disconnect_by_sid(sid: str) -> None:
        if sid is None:
            raise ValueError('need sid to disconnect client')
        environ.env._force_disconnect_by_sid(sid, '/chat')

    # preferably "emit" should be set during env creation, but the socketio object is not created until after env is
    environ.env.out_of_scope_emit = socketio.emit
    environ.env._force_disconnect_by_sid = socketio.server.disconnect
    environ.env.disconnect_by_sid = disconnect_by_sid
    environ.env.consume_thread = threading.Thread(target=consume)
    environ.env.consume_thread.start()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm.create()
    form.token.data = str(uuid())
    if form.validate_on_submit():
        # only for the reference implementation, generate a user id and token
        user_id = int(float(''.join([str(ord(x)) for x in form.user_name.data])) % 1000000)

        environ.env.session[SessionKeys.user_id.value] = user_id
        environ.env.session[SessionKeys.token.value] = form.token.data
        environ.env.auth.redis.hset(RedisKeys.auth_key(str(user_id)), SessionKeys.user_id.value, user_id)
        environ.env.auth.redis.hset(RedisKeys.auth_key(str(user_id)), SessionKeys.token.value, form.token.data)

        for session_key in SessionKeys:
            key = session_key.value
            if not isinstance(key, str):
                continue
            if not hasattr(form, key):
                continue
            form_value = form.__getattribute__(key).data
            environ.env.session[key] = form_value
            environ.env.auth.redis.hset(RedisKeys.auth_key(str(user_id)), key, form_value)

        return environ.env.redirect(environ.env.url_for('.chat'))

    elif environ.env.request.method == 'GET':
        form.user_name.data = environ.env.session.get('user_name', '')
        form.age.data = environ.env.session.get('age', '')
        form.gender.data = environ.env.session.get('gender', '')
        form.membership.data = environ.env.session.get('membership', '')
        form.fake_checked.data = environ.env.session.get('fake_checked', '')
        form.has_webcam.data = environ.env.session.get('has_webcam', '')
        form.image.data = environ.env.session.get('image', '')
        form.country.data = environ.env.session.get('country', '')
        form.city.data = environ.env.session.get('city', '')
        form.token.data = environ.env.session.get('token', '')
    return environ.env.render_template('index.html', form=form)


@app.route('/chat')
def chat():
    user_id = environ.env.session.get('user_id', '')
    user_name = environ.env.session.get('user_name', '')
    if user_id == '':
        return environ.env.redirect(environ.env.url_for('.index'))

    return environ.env.render_template(
            'chat.html', name=user_id, room=user_id, user_id=user_id, user_name=user_name,
            gender=environ.env.session.get('gender', ''),
            age=environ.env.session.get('age', ''),
            membership=environ.env.session.get('membership', ''),
            fake_checked=environ.env.session.get('fake_checked', ''),
            has_webcam=environ.env.session.get('has_webcam', ''),
            image=environ.env.session.get('image', ''),
            country=environ.env.session.get('country', ''),
            city=environ.env.session.get('city', ''),
            token=environ.env.session.get('token', ''),
            version=environ.env.config.get(ConfigKeys.VERSION))


@app.route('/js/<path:path>')
def send_js(path):
    return environ.env.send_from_directory('templates/js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return environ.env.send_from_directory('templates/css', path)


# no pre-processing for connect event
@socketio.on('connect', namespace='/chat')
@respond_with('gn_connect')
@count_connections('connect')
def connect() -> (int, None):
    return api.connect()


@socketio.on('login', namespace='/chat')
@respond_with('gn_login')
@pre_process('on_login', should_validate_request=False)
def on_login(data: dict, activity: Activity) -> (int, str):
    try:
        status_code, msg = api.on_login(data, activity)
        if status_code != 200:
            disconnect()
        return status_code, msg
    except Exception as e:
        logger.error('could not login, will disconnect client: %s' % str(e))
        logger.exception(traceback.format_exc())
        return 500, str(e)


@socketio.on('message', namespace='/chat')
@respond_with('gn_message')
@pre_process('on_message')
def on_message(data: dict, activity: Activity) -> (int, Union[dict, str, None]):
    return api.on_message(data, activity)


@socketio.on('delete', namespace='/chat')
@respond_with('gn_delete')
@pre_process('on_delete')
def on_delete(data: dict, activity: Activity) -> (int, Union[dict, str, None]):
    return api.on_delete(data, activity)


@socketio.on('request_admin', namespace='/chat')
@respond_with('gn_request_admin')
@pre_process('on_request_admin')
def on_request_admin(data: dict, activity: Activity) -> (int, Union[str, dict, None]):
    return api.on_request_admin(data, activity)


@socketio.on('create', namespace='/chat')
@respond_with('gn_create')
@pre_process('on_create')
def on_create(data: dict, activity: Activity) -> (int, Union[dict, str, None]):
    return api.on_create(data, activity)


@socketio.on('invite', namespace='/chat')
@respond_with('gn_invite')
@pre_process('on_invite')
def on_invite(data: dict, activity: Activity) -> (int, Union[dict, str, None]):
    return api.on_invite(data, activity)


@socketio.on('whisper', namespace='/chat')
@respond_with('gn_whisper')
@pre_process('on_whisper')
def on_whisper(data: dict, activity: Activity) -> (int, Union[dict, str, None]):
    return api.on_whisper(data, activity)


@socketio.on('ban', namespace='/chat')
@respond_with('gn_ban')
@pre_process('on_ban')
def on_ban(data: dict, activity: Activity) -> (int, Union[dict, str, None]):
    return api.on_ban(data, activity)


@socketio.on('kick', namespace='/chat')
@respond_with('gn_kick')
@pre_process('on_kick')
def on_kick(data: dict, activity: Activity) -> (int, Union[dict, str, None]):
    return api.on_kick(data, activity)


@socketio.on('set_acl', namespace='/chat')
@respond_with('gn_set_acl')
@pre_process('on_set_acl')
def on_set_acl(data: dict, activity: Activity) -> (int, Union[str, dict, None]):
    return api.on_set_acl(data, activity)


@socketio.on('get_acl', namespace='/chat')
@respond_with('gn_get_acl')
@pre_process('on_get_acl')
def on_get_acl(data: dict, activity: Activity) -> (int, Union[str, dict, None]):
    return api.on_get_acl(data, activity)


@socketio.on('status', namespace='/chat')
@respond_with('gn_status')
@pre_process('on_status')
def on_status(data: dict, activity: Activity) -> (int, Union[str, dict, None]):
    return api.on_status(data, activity)


@socketio.on('history', namespace='/chat')
@respond_with('gn_history')
@pre_process('on_history')
def on_history(data: dict, activity: Activity) -> (int, Union[str, dict, None]):
    return api.on_history(data, activity)


@socketio.on('join', namespace='/chat')
@respond_with('gn_join')
@pre_process('on_join')
def on_join(data: dict, activity: Activity) -> (int, Union[str, dict, None]):
    return api.on_join(data, activity)


@socketio.on('users_in_room', namespace='/chat')
@respond_with('gn_users_in_room')
@pre_process('on_users_in_room')
def on_users_in_room(data: dict, activity: Activity) -> (int, Union[str, dict, None]):
    return api.on_users_in_room(data, activity)


@socketio.on('remove_room', namespace='/chat')
@respond_with('gn_remove_room')
@pre_process('on_remove_room')
def on_remove_room(data: dict, activity: Activity) -> (int, Union[str, dict, None]):
    return api.on_remove_room(data, activity)


@socketio.on('list_rooms', namespace='/chat')
@respond_with('gn_list_rooms')
@pre_process('on_list_rooms')
def on_list_rooms(data: dict, activity: Activity) -> (int, Union[str, dict, None]):
    return api.on_list_rooms(data, activity)


@socketio.on('report', namespace='/chat')
@respond_with('gn_report')
@pre_process('on_report')
def on_report(data: dict, activity: Activity) -> (int, Union[str, dict, None]):
    return api.on_report(data, activity)


@socketio.on('list_channels', namespace='/chat')
@respond_with('gn_list_channels')
@pre_process('on_list_channels')
def on_list_channels(data: dict, activity: Activity) -> (int, Union[str, dict, None]):
    return api.on_list_channels(data, activity)


@socketio.on('leave', namespace='/chat')
@respond_with('gn_leave')
@pre_process('on_leave')
def on_leave(data: dict, activity: Activity) -> (int, Union[str, dict, None]):
    return api.on_leave(data, activity)


# no pre-processing for disconnect event
@socketio.on('disconnect', namespace='/chat')
@count_connections('disconnect')
def on_disconnect() -> (int, None):
    return api.on_disconnect()
