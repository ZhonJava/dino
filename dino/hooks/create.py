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

from dino import environ
from dino import utils

__author__ = 'Oscar Eriksson <oscar.eriks@gmail.com>'


class OnCreateHooks(object):
    @staticmethod
    def create_room(arg: tuple) -> None:
        data, activity = arg
        room_name = activity.target.display_name
        room_id = activity.target.id
        channel_id = activity.object.url
        user_id = activity.actor.id
        user_name = activity.actor.display_name
        environ.env.db.create_room(room_name, room_id, channel_id, user_id, user_name)

    @staticmethod
    def emit_creation_event(arg: tuple) -> None:
        data, activity = arg
        activity_json = utils.activity_for_create_room(activity)
        environ.env.emit('gn_room_created', activity_json, broadcast=True, json=True, include_self=True)


@environ.env.observer.on('on_create')
def _on_create_create_room(arg: tuple) -> None:
    OnCreateHooks.create_room(arg)


@environ.env.observer.on('on_create')
def _on_create_emit_creation_event(arg: tuple) -> None:
    OnCreateHooks.emit_creation_event(arg)
