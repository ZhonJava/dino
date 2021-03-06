This example is using JavaScript.

First we connect to the server:

    socket = io.connect(
        'http://' + document.domain + ':' + location.port + '/chat', 
        {transports:['websocket']}
    );

We'll receive a "connect" event back after successfully connecting. Now we have to send the "login" event to provide the
server with some extra user information and to do authentication:

    socket.on('connect', function() {
        socket.emit('login', {
            verb: 'login',
            actor: {
                id: '<user ID>',
                attachments: [
                    {
                        objectType: 'token',
                        content: '<auth token>'
                    }
                ]
            }
        });
    });
    
All events sent to the server will get a response with the same name plus a prefix of "gn_". For example, the login 
event sent above will get the following response, "gn_login", meaning we've successfully authenticated with the server.
Now we can start joining rooms, chatting, sending events etc.

    socket.on('gn_login', function(response) {
        socket.emit('list_channels', {
            verb: 'list'
        });
    });
    
The response from the server will be in JSON format. If no data is expected for the events, only a status code will be
in the response. For example, sending the "join" event to join a room won't return any data, but only the following
(if successful):

    {
        "status_code": 200
    }
    
Failure to execute an event on the server will return code 400:

    {
        "status_code": 400,
        "data": "<an error message, always a string>"
    }
    
If an internal server error occurs, code 500 is returned:

    {
        "status_code": 500,
        "data": "<an error message, always a string>"
    }
    
For events that contains data in the response, for example when sending the event "list_channels", we expect to get a list
of channels in the response. For these events the data part is always a JSON in the ActivityStreams 1.0 format:

    {
        "status_code": 400,
        "data": {       
            "object": {
                "objectType": "channels"
                "attachments": [
                    {
                        "id": "<channel ID 1>",
                        "content": "<channel name 1 in base64>"
                    },
                    {
                        "id": "<channel ID 2>",
                        "content": "<channel name 2 in base64>"
                    },
                    {
                        "id": "<channel ID 3>",
                        "content": "<channel name 3 in base64>"
                    }
                ]
            },
            "verb": "list"
        }
    }

## Encoding

All user names, room names, channel names and chat messages are expected to be base64 encoded unicode strings. All
responses and events originating from the server will also follow this practice, so when listing rooms/channels/users
all names will always be in base64.

## Authentication

If the `redis` authentication method is configured, then when clients send the `login` event to the server, the
supplied `token` and `actor.id` parameter must already exist in Redis. When the server gets the login event it will
check if the token matches the one stored in Redis for this user ID, otherwise it will not authenticate the session.

Therefor, before a client can login, these two values (and any other possible values used for permissions) needs to
first be set in the Redis `hset` with key `user:auth:<user ID>`.

Example:

    $ redis-cli
    127.0.0.1:6379> hset user:auth:1234 token 302fe6be-a72f-11e6-b5fc-330653beb4be
    127.0.0.1:6379> hset user:auth:1234 age 35
    127.0.0.1:6379> hset user:auth:1234 gender m