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

import logging
import traceback

from dino import environ
from dino import utils
from dino.config import SessionKeys

logger = logging.getLogger(__name__)

__author__ = 'Oscar Eriksson <oscar.eriks@gmail.com>'


class OnDisconnectHooks(object):
    @staticmethod
    def leave_private_room(arg: tuple):
        data, activity = arg
        try:
            # todo: only broadcast 'offline' status if current status is 'online' (i.e. don't broadcast if e.g. 'invisible')
            user_id = activity.actor.id
            user_name = environ.env.session.get(SessionKeys.user_name.value)
            logger.debug('a user disconnected, id "%s" name "%s"' % (user_id, user_name))

            if user_id is None or len(user_id.strip()) == 0:
                return
            environ.env.leave_room(user_id)
        except Exception as e:
            logger.error('could not leave private room: %s' % str(e))
            logger.debug('request for failed leave_private_room(): %s' % str(data))
            logger.exception(traceback.format_exc())

    @staticmethod
    def leave_all_public_rooms_and_emit_leave_events(arg: tuple):
        data, activity = arg
        try:
            user_id = activity.actor.id
            user_name = environ.env.session.get(SessionKeys.user_name.value)
            rooms = environ.env.db.rooms_for_user(user_id)

            for room_id, room_name in rooms.items():
                utils.remove_user_from_room(user_id, user_name, room_id)
                environ.env.emit('gn_user_left', utils.activity_for_leave(user_id, user_name, room_id, room_name), room=room_id)

            environ.env.db.remove_current_rooms_for_user(user_id)
        except Exception as e:
            logger.error('could not leave all public rooms: %s' % str(e))
            logger.debug('request for failed leave_all_public_rooms_and_emit_leave_events(): %s' % str(data))
            logger.exception(traceback.format_exc())

    @staticmethod
    def set_user_offline(arg: tuple):
        data, activity = arg
        try:
            user_id = activity.actor.id
            environ.env.db.set_user_offline(user_id)
        except Exception as e:
            logger.error('could not set user offline: %s' % str(e))
            logger.debug('request for failed set_user_offline(): %s' % str(data))
            logger.exception(traceback.format_exc())

    @staticmethod
    def emit_disconnect_event(arg: tuple) -> None:
        data, activity = arg
        try:
            user_id = activity.actor.id
            user_name = environ.env.session.get(SessionKeys.user_name.value)
            activity_json = utils.activity_for_disconnect(user_id, user_name)
            environ.env.publish(activity_json, external=True)
        except Exception as e:
            logger.error('could not emit disconnect event: %s' % str(e))
            logger.debug('request for failed emit_disconnect_event(): %s' % str(data))
            logger.exception(traceback.format_exc())


@environ.env.observer.on('on_disconnect')
def _on_disconnect_leave_private_room(arg: tuple) -> None:
    OnDisconnectHooks.leave_private_room(arg)


@environ.env.observer.on('on_disconnect')
def _on_disconnect_leave_all_public_rooms_and_emit_leave_events(arg: tuple) -> None:
    OnDisconnectHooks.leave_all_public_rooms_and_emit_leave_events(arg)


@environ.env.observer.on('on_disconnect')
def _on_disconnect_set_user_offline(arg: tuple) -> None:
    OnDisconnectHooks.set_user_offline(arg)


@environ.env.observer.on('on_disconnect')
def _on_disconnect_emit_disconnect_event(arg: tuple) -> None:
    OnDisconnectHooks.emit_disconnect_event(arg)
