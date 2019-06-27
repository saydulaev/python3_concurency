#!/usr/bin/env python3
# Async callback

import socket
import selectors

'''
This example show how to use event driver programing for socket.
Each object of socket like server_socket or client_socket has associate objec like data=callable_object.
In event_loop function we get a tuple with a 'key' container with saved data (socket_object, callable_object)
From each tuple we get a 'key'  and then execute callable object with 'key.fileobj'.
'''

selector = selectors.DefaultSelector()

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 5001))
    server_socket.listen()

    # Add observable object for server_socket.
    # fileobj - object for observe.
    # events - type 'selector.EVENT_READ' for read operations.
    # data - callable object in this case a function 'accept_connection'
    selector.register(fileobj=server_socket, events=selectors.EVENT_READ, data=accept_connection)




def accept_connection(server_socket):
    client_socket, addr = server_socket.accept()
    print('Connection from ', addr)

    # Add observable object for client_socket
    selector.register(fileobj=client_socket, events=selectors.EVENT_READ, data=send_message)


def send_message(client_socket):
    request = client_socket.recv(4096)

    if request:
        responce = 'Hello world\n'.encode()
        client_socket.send(responce)
    else:
        # Before clossing a client_socket we should unregister object 'client_socket'
        selector.unregister(client_socket)
        client_socket.close()


def event_loop():
    while True:
        # We should get objects which will be ready to 'read' or 'write'
        # selector.select() receive a list of tuple from two elements (key, events) for each registered before objects ('server_socket', client_socket)
        # events this is bit-map mask of event (read/write). We has registered socket for read operation. In this app 'events' not applicable and not will be used.
        # . key it is object of SelectorKey (named tuple from collections module) This represents as lightly class object.
        # Key object serve for pin each other socket object event object and data. (like container for storing those elemetns (objects)).
        # Key object contains the same fields as we have set before namely:
        # .fileobj
        # .events
        # .data
        events = selector.select()
        for key, _ in events:
            callback = key.data     # Callable object which get key.fileobj (socket) object
            callback(key.fileobj)


if __name__ == '__main__':
    # Register first object run server()
    server()
    
    event_loop()