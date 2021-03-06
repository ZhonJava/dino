#!/usr/bin/env python

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

from zope.interface import Interface

__author__ = 'Oscar Eriksson <oscar.eriks@gmail.com>'


class ICache(Interface):
    def set_is_room_ephemeral(self, room_id: str, is_ephemeral: bool) -> None:
        """
        set whether aroom is ephemeral (temporary) or not

        :param room_id: the uuid of the room
        :param is_ephemeral: boolean for whether or not it is ephemeral
        :return: nothing
        """

    def is_room_ephemeral(self, room_id: str) -> bool:
        """
        check if a room is ephemeral (temporary) or not

        :param room_id: the uuid of the room
        :return: true if ephemeral, false if not, or None of not in cache or TTL expired
        """

    def get_admin_room(self) -> str:
        """
        get the room uuid of the admin room, or None if no such room exists

        :return: the uuid of the admin room, or None of not found
        """

    def remove_from_black_list(self, word: str) -> None:
        """
        remove a word from the black list

        :param word: a word to remove if it exists
        :return: nothing
        """

    def add_to_black_list(self, word: str) -> None:
        """
        add a word to the black list

        :param word: a word to add
        :return: nothing
        """

    def get_black_list(self) -> set:
        """
        return the cached black list; a set of forbidden words

        :return: a set of forbidden words, or None of not in the cache
        """

    def set_black_list(self, the_list: set) -> None:
        """
        set the black list in the cache

        :param the_list: a set of forbidden words
        :return: nothing
        """

    def reset_user_roles(self, user_id: str) -> None:
        """
        invalidate roles in cache; used when roles change in db
        :param user_id: the id of the user to invalidate the cache for
        :return: nothing
        """

    def get_user_roles(self, user_id: str) -> dict:
        """
        get all the user roles for a user

        :param user_id: the id of the user
        :return: a dict of global, channel and room roles
        """

    def set_user_roles(self, user_id: str, roles: dict) -> None:
        """
        set all the roles for a user

        :param user_id: the id of the user
        :param roles: all the roles for this user
        :return: nothing
        """

    def set_global_ban_timestamp(self, user_id: str, duration: str, timestamp: str, username: str) -> None:
        """
        set the global ban timestamp for a user to a given timestamp

        :param user_id: the id of the user
        :param duration: the duration, e.g. 12d
        :param timestamp: the timestamp
        :param username: the username of this user
        :return: nothing
        """

    def set_channel_ban_timestamp(self, channel_id: str, user_id: str, duration: str, timestamp: str, username: str) -> None:
        """
        set the ban timestamp on channel for a user to a given timestamp

        :param user_id: the id of the user
        :param channel_id: the uuid of the channel
        :param duration: the duration, e.g. 12d
        :param timestamp: the timestamp
        :param username: the username of this user
        :return: nothing
        """

    def set_room_ban_timestamp(self, room_id: str, user_id: str, duration: str, timestamp: str, username: str) -> None:
        """
        set the ban timestamp on a room for a user to a given timestamp

        :param user_id: the id of the user
        :param room_id: the uuid of the room
        :param duration: the duration, e.g. 12d
        :param timestamp: the timestamp
        :param username: the username of this user
        :return: nothing
        """

    def get_global_ban_timestamp(self, user_id: str) -> str:
        """
        get the ban timestamp of the user in the given room, or empty string if no ban exist

        :param user_id: the id of the user
        :return: the timestamp in ConfigKeys.DEFAULT_DATE_FORMAT format, or '' if no ban exists
        """

    def get_channel_ban_timestamp(self, channel_id: str, user_id: str) -> str:
        """
        get the ban timestamp of the user in the given channel, or empty string if no ban exist

        :param channel_id: the uuid of the channel
        :param user_id: the id of the user
        :return: the timestamp in ConfigKeys.DEFAULT_DATE_FORMAT format, or '' if no ban exists
        """

    def get_room_ban_timestamp(self, room_id: str, user_id: str) -> str:
        """
        get the ban timestamp of the user in the given room, or empty string if no ban exist

        :param room_id: the uuid of the room
        :param user_id: the id of the user
        :return: the timestamp in ConfigKeys.DEFAULT_DATE_FORMAT format, or '' if no ban exists
        """

    def get_room_id_for_name(self, channel_id: str, room_name: str) -> str:
        """

        :param channel_id:
        :param room_name:
        :return:
        """

    def set_room_id_for_name(self, channel_id, room_name, room_id):
        """

        :param channel_id:
        :param room_name:
        :param room_id:
        :return:
        """

    def get_user_name(self, user_id: str) -> str:
        """
        the the name of the user from the id

        :param user_id: the id of the user
        :return: the name of the user
        """

    def set_user_name(self, user_id: str, user_name: str) -> None:
        """
        set the name of a user in the cache

        :param user_id: the id of the user
        :param user_name: the name of the user
        :return: nothing
        """

    def remove_room_exists(self, channel_id, room_id):
        """
        when removing a room we wan't to be able to remove it from the cache as well

        :param channel_id: the uuid of the channel
        :param room_id: the uuid of the room
        :return: nothing
        """

    def set_admin_room(self, room_id: str) -> None:
        """

        :param room_id:
        :return:
        """

    def set_user_status(self, user_id: str, status: str) -> None:
        """

        :param user_id:
        :param status:
        :return:
        """

    def set_channel_name(self, channel_id: str, channel_name: str) -> None:
        """

        :param channel_id:
        :param channel_name:
        :return:
        """

    def get_room_exists(self, channel_id, room_id):
        """

        :param channel_id:
        :param room_id:
        :return:
        """

    def get_channel_name(self, channel_id: str) -> str:
        """

        :param channel_id:
        :return:
        """

    def get_room_name(self, room_id: str) -> str:
        """

        :param room_id:
        :return:
        """

    def set_room_exists(self, channel_id, room_id, room_name):
        """

        :param channel_id:
        :param room_id:
        :param room_name:
        :return:
        """

    def set_channel_exists(self, channel_id: str) -> None:
        """

        :param channel_id:
        :return:
        """

    def set_channel_for_room(self, channel_id: str, room_id: str) -> None:
        """

        :param channel_id:
        :param room_id:
        :return:
        """

    def get_channel_exists(self, channel_id):
        """

        :param channel_id:
        :return:
        """

    def get_channel_for_room(self, room_id):
        """

        :param room_id:
        :return:
        """

    def get_user_status(self, user_id: str):
        """

        :param user_id:
        :return:
        """

    def user_check_status(self, user_id, other_status):
        """

        :param user_id:
        :param other_status:
        :return:
        """

    def user_is_offline(self, user_id):
        """

        :param user_id:
        :return:
        """

    def user_is_online(self, user_id):
        """

        :param user_id:
        :return:
        """

    def user_is_invisible(self, user_id):
        """

        :param user_id:
        :return:
        """

    def set_user_offline(self, user_id: str) -> None:
        """

        :param user_id:
        :return:
        """

    def set_user_online(self, user_id: str) -> None:
        """

        :param user_id:
        :return:
        """

    def set_user_invisible(self, user_id: str) -> None:
        """

        :param user_id:
        :return:
        """
