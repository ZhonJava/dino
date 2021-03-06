## GET /history

Request contains info on what time slice, target, origin to get history for:

    {
        "from_time": "2016-12-26T08:39:54Z",
        "to_time": "2016-12-28T08:39:54Z",
        "user_id": "124352",
        "room_id": "dedf878e-b25d-4713-8058-20c6f0547c59"
    }

Response would be something similar to the following:

    {
        "status_code": 200,
        "data": [{
            "deleted": false,
            "target_name": "YmFkIGtpZHo=",
            "target_id": "675eb2a5-17c6-45e4-bc0f-674241573f22",
            "timestamp": "2017-01-26T04:58:33Z",
            "from_user_name": "YmF0bWFu",
            "message_id": "37db81f2-4e16-4076-b759-8ce1c23a364e",
            "from_user_id": "997110",
            "channel_name": "U2hhbmdoYWk=",
            "body": "aG93IGFyZSB5b3U/",
            "domain": "room",
            "channel_id": "dedf878e-b25d-4713-8058-20c6f0547c59"
        }, {
            "deleted": false,
            "target_name": "YmFkIGtpZHo=",
            "target_id": "675eb2a5-17c6-45e4-bc0f-674241573f22",
            "timestamp": "2017-01-26T04:58:31Z",
            "from_user_name": "YmF0bWFu",
            "message_id": "416d3c60-7197-471c-a706-7dbeca090d11",
            "from_user_id": "997110",
            "channel_name": "U2hhbmdoYWk=",
            "body": "aGVsbG8gdGhlcmU=",
            "domain": "room",
            "channel_id": "dedf878e-b25d-4713-8058-20c6f0547c59"
        }, {
            "deleted": false,
            "target_name": "YmFkIGtpZHo=",
            "target_id": "675eb2a5-17c6-45e4-bc0f-674241573f22",
            "timestamp": "2017-01-26T04:58:16Z",
            "from_user_name": "YmF0bWFu",
            "message_id": "91655457-3712-4c2f-b6f2-c3b0f8be29e5",
            "from_user_id": "997110",
            "channel_name": "U2hhbmdoYWk=",
            "body": "ZmRzYQ==",
            "domain": "room",
            "channel_id": "dedf878e-b25d-4713-8058-20c6f0547c59"
        }]
    }

* If neither `from_time` nor `to_time` is specified, the last 7 days will be used as limit,
* If `from_time` is specified but no `to_time`, `to_time` will be `from_time + 7 days`,
* If `to_time` is specified but no `from_time`, `from_time` will be `to_time - 7 days`,
* Either `user_id` or `room_id` is required (both can be specified at the same time),
* `to_time` needs to be after `from_time`.

## POST /ban

Request contains info on who to ban where. For banning globally:

    {
        "1234": {
            "duration": "24h",
            "reason": "<optional base64 encoded free-text>",
            "admin_id": "<id of user banning (must already exist), or leave empty for default>",
            "type": "global"
        }
    }

Can also ban multiple users at the same time:

    {
        "<user id>": {
            "duration": "24h",
            "type": "global",
            "reason": "<option reason field, base64 encoded>",
            "admin_id": "<optional id of admin user who is banning>"
        },
        "<user id>": {
            "duration": "10m",
            "target": "<channel uuid>",
            "type": "channel",
            "reason": "<option reason field, base64 encoded>",
            "admin_id": "<optional id of admin user who is banning>"
        },
        "<user id>": {
            "duration": "7d",
            "target": "<room uuid>",
            "type": "room",
            "reason": "<option reason field, base64 encoded>",
            "admin_id": "<optional id of admin user who is banning>"
        }
    }

The "reason" field must be base64 encoded. If the "admin_id" field is specified it will be used, if not the default ID
"0" will be used.

Duration is an integer followed by a char for the unit, which can be one of "d", "h", "m", "s" (days, hours, minutes, 
seconds). Negative or 0 durations are not allowed.

When type is set to "global", no target is specified (meaning user is banned from the whole chat server).

Response will be something like the following:

    {
        "<user id>": {
            "status": "OK"
        },
        "<user id>": {
            "status": "FAIL",
            "message": "invalid duration 5k"
        },
        "<user id>": {
            "status": "FAIL",
            "message": "no such user"
        },
        "<user id>" {
            "status": "OK"
        }
    }

## POST /kick

Request contains:

    {
        "<user id>": {
            "target": "<room uuid>",
            "reason": "<option reason field, base64 encoded>",
            "admin_id": "<optional id of admin user who is kicking>"
        },
        "<user id>": {
            "target": "<room uuid>",
            "reason": "<option reason field, base64 encoded>",
            "admin_id": "<optional id of admin user who is kicking>"
        },
        "<user id>": {
            "target": "<room uuid>",
            "reason": "<option reason field, base64 encoded>",
            "admin_id": "<optional id of admin user who is kicking>"
        }
    }

The "reason" field must be base64 encoded. If the "admin_id" field is specified it will be used, if not the default ID
"0" will be used.

Response will be something like the following:

    {
        "<user id>": {
            "status": "OK"
        },
        "<user id>": {
            "status": "FAIL",
            "message": "no such user"
        },
        "<user id>" {
            "status": "OK"
        }
    }

## GET /roles

Request contains a list of user IDs, e.g.:

    {
        "users": [
            "124352",
            "5678"
        ]
    }

Response would be something similar to the following:

    {
        "data": {
            "124352": {
                "room": {
                    "1aa3f5f5-ba46-4aca-999a-978c7f2237c7": [
                        "moderator"
                    ],
                    "bb0ea500-cd94-11e6-b178-8323deb605bf": [
                        "owner"
                    ]
                },
                "channel": {
                    "dedf878e-b25d-4713-8058-20c6f0547c59": [
                        "admin", 
                        "owner"
                    ]
                },
                "global": [
                    "superuser"
                ]
            },
            "5678": {
                "room": {},
                "channel": {},
                "global": []
            }
        },
        "status_code": 200
    }

Possible roles are:

* global superuser
* channel owner
* channel admin
* room owner
* room moderator

## GET /rooms-for-users

Request contains a list of user IDs, e.g.:

    {
        "users": [
            "1234",
            "5678"
        ]
    }

Response would be all rooms each user is currently in (room names and channel names are base64 encoded):

    {
        "1234": [{
            "room_id": "efeca2fe-ba93-11e6-bc9a-4f6f56293063",
            "room_name": "b2gsIHNvIHlvdSBhY3R1YWxseSBjaGVja2VkIHdoYXQgaXMgd2FzPw==",
            "channel_id": "fb843140-ba93-11e6-b178-97f0297a6d4d",
            "channel_name": "dG9tIGlzIGEgZnJlbmNoIG1hZG1hbg=="
        }],
        "5678": [{
            "room_id": "ca1dc3b4-ba93-11e6-b835-7f1d961023a1",
            "room_name": "cmVhZCB1cCBvbiBoeXBlcmxvZ2xvZysr",
            "channel_id": "f621fcaa-ba93-11e6-8590-bfe35ff80c03",
            "channel_name": "YSByZWRidWxsIGEgZGF5IGtlZXBzIHRoZSBzYW5kbWFuIGF3YXk="
        }]
    }

## POST /delete-messages

Used to delete ALL messages for a specific user ID.

Request body looks like this:

    {
        "id": "<user ID>"
    }

Example response:

    {
        "status_code": 200, 
        "data": {
            "success": 4, 
            "failed": 0,
            "total": 4
        }
    }

Or if other kinds of failures:

    {
        "status_code": 500, 
        "data": "<error message, e.g. 'no id parameter in request'>"
    }

## GET /banned

No data required in request.

Response is all banned users, separated by channel, room and globally. Example response:

    {
        "channels": {},
        "global": {
            "185626": {
                "name": "bHVlbA==",
                "duration": "1h",
                "timestamp": "2016-12-05T03:50:24Z"
            }
        },
        "rooms": {
            "1aa3f5f5-ba46-4aca-999a-978c7f2237c7": {
                "name": "Y29vbCBndXlz",
                "users": {
                    "101108": {
                        "name": "bHVlbA==",
                        "duration": "30m",
                        "timestamp": "2016-12-05T03:20:24Z"
                    }
                }
            }
        }
    }

The "timestamp" in the response is the UTC timestamp for when the ban will expire. Names or channels, rooms and users
are all base64 encoded. The dictionary keys for "rooms" are the UUIDs of the rooms, same for channels, while for users
it's their user IDs as keys. The bans for "global" have no separation by room/channel IDs, and no "name" or "users" 
keys.

## User ID parameter

The `/banned` endpoint supports having a json with user ID's in the request body to only get bans for those users. E.g.:

    curl localhost:5400/banned -d '{"users":["110464"]}' -X GET -H "Content-Type: application/json"

Response would be (slightly different from above example without request body):

    {
        "data": {
            "110464": {
                "channel": {},
                "room": {
                    "1aa3f5f5-ba46-4aca-999a-978c7f2237c7": {
                        "name": "Y29vbCBndXlz",
                        "duration": "15m",
                        "timestamp": "2016-12-14T09:23:00Z"
                    },
                    "675eb2a5-17c6-45e4-bc0f-674241573f22": {
                        "name": "YmFkIGtpZHo=",
                        "duration": "2m",
                        "timestamp": "2016-12-14T09:15:51Z"
                    }
                },
                "global": {}
            }
        },
        "status_code": 200
    }
