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
from dino.config import SessionKeys

__author__ = 'Oscar Eriksson <oscar.eriks@gmail.com>'


class OnLoginHooks(object):
    @staticmethod
    def update_session_and_join_private_room(arg: tuple) -> None:
        data, activity = arg
        user_id = activity.actor.id
        user_name = utils.b64d(activity.actor.display_name)
        environ.env.session[SessionKeys.user_id.value] = user_id
        environ.env.session[SessionKeys.user_name.value] = user_name

        if activity.actor.image is None:
            environ.env.session['image_url'] = ''
            environ.env.session[SessionKeys.image.value] = 'n'
        else:
            environ.env.session['image_url'] = activity.actor.image.url
            environ.env.session[SessionKeys.image.value] = 'y'

        utils.create_or_update_user(user_id, user_name)
        utils.set_sid_for_user_id(user_id, environ.env.request.sid)
        environ.env.join_room(user_id)

    @staticmethod
    def publish_activity(arg: tuple) -> None:
        data, activity = arg
        user_id = activity.actor.id
        user_name = environ.env.session.get(SessionKeys.user_name.value)

        activity_json = utils.activity_for_login(user_id, user_name)
        environ.env.publish(activity_json, external=True)

    @staticmethod
    def set_user_online(arg: tuple) -> None:
        data, activity = arg
        user_id = activity.actor.id
        environ.env.db.set_user_online(user_id)


@environ.env.observer.on('on_login')
def _on_login_set_user_online(arg: tuple) -> None:
    OnLoginHooks.set_user_online(arg)


@environ.env.observer.on('on_login')
def _on_login_update_session(arg: tuple) -> None:
    OnLoginHooks.update_session_and_join_private_room(arg)


@environ.env.observer.on('on_login')
def _on_login_publish_activity(arg: tuple) -> None:
    OnLoginHooks.publish_activity(arg)
