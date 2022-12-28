# Chat
Chat client and server using pyside6. Communication between Server and Client is done using simple json format.

The first 4 bytes represend the length (n) of json data in bytes

The next n bytes are the json data

# Server side
1. Server waits for connection
2. When a client is connected:
    1.  Server assigns a unique id and sends this uid `{'id': uid} `
    2.  Server sends a list of all connected clients `{'clients':[{'id': uid, 'name': name}, ...]}` to the newly connected client
    3.  Server sends the newly connected client to all other clients `{'id': uid, 'name': name, 'info': 'add'}`
3. When a client sends data:
    1. If there is a `'name'` field with different value then server stores new name and sends new name to all other clients `{'id': uid, 'name': name, 'info': 'update'}`
    2. If there is a `'text'` field and a `'recipients'` field then server sends that text to all recipients `{'text': text, 'from': uid, 'msg_id': msg_id}`. If server cannot find a recipient then `{'info': 'Could not send message', 'msg_id': msg_id}` is sent back to the client
4. Whenever a client is disconnected:
    1. Server sends `{'id': uid, 'info': 'delete'}` to all clients


# Client side
1. Client connects and waits for server to send the newly assigned uid
2. Client waits for all other incoming data and is ready to send data
