#!/usr/bin/env python3

# Generator async
# This example we will be use 

import socket
from select import select

# A list of tuple ('kind of operation', socket object).
tasks = []

to_read = {}    # Read events. Store socket as key, and generation function as value
to_write = {}   # Write events.

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 5001))
    server_socket.listen()

    while True:
        # What happend in this ? 
        # 1. Until we reach a blocking action ".accept()" we return "server_socket" and pause the function execution the same time return manage control to calling function.
        # And next execution of function 'server' will be continue when socket will be ready without delay.
        # 2. We have to catch this server_socket and push it into the select() function.
        # 3. Select function make a sampling of sockets which is ready
        # 4. Execute 'next' function from appropriate generator. 

        # A yield return tuple where first item has to show us what kind of socket buffer must be observed by select function. Second item is a socket object.
        # Socket buffer will be use in select to check where buffer is ready depends on its file descriptor. 
        yield ('read', server_socket)
        
        client_socket, addr = server_socket.accept()    # READ. blockable
        
        print('Connection from', addr)
        print("Put a first result ('ready', client_socket) of generator client() to tasks list")
        # Phase 2.
        tasks.append(client(client_socket))


def client(client_socket):
    while True:
        # Firstly. (Phase 2) Return a new 'readable' client socket before blocking operation '.recv()'.
        yield ('read', client_socket)
        request = client_socket.recv(4096)  # READ. blockable

        if not request:
            break
        else:
            responce = 'Hello world\n'.encode()
            # Secondly. Return a new 'writable' client socket before blocking operation '.send()'.
            yield ('write', client_socket)
            client_socket.send(responce)    # WRITE. blockable

    client_socket.close()


def event_loop():
    # Use 'any' function to define that least one from many iterable objects it not epty.
    # NOTE... There is one object won't be epty. 'tasks'. All dict objects are empty yet.
    # If all object in list is epty, function return False and iteration will stop.
    while any([tasks, to_read, to_write]):

        # Circle rotation for upload tasks list.
        # Tasks list always must be working. Main purpose for reach that behavior to feed a generator of ready socket objects to it.
        while not tasks:
            # Define what socket is ready.
            # Function select has a inner loop which extracts a keys from dicts.
            # Becouse a keys are socket object (file descriptor object).
            # Then select define which FD buffer is ready to read or write.
            # If buffer is full it mean that it FD is ready for 'read'
            # If buffer is empty it mean that it FD is ready for write.
            ready_to_read, ready_to_write, _ = select(to_read, to_write, [])

            for sock in ready_to_read:
                # push a generator of sock to tasks list
                tasks.append(to_read.pop(sock))

            for sock in ready_to_write:
                tasks.append(to_write.pop(sock))

        try:
            # Get generator
            # For first execution of program it always will be a 'server_socket'
            task = tasks.pop(0)

            # Parse generator tuple.
            reason, sock = next(task)

            # Define which socket object put to relation dict.
            if reason == 'read':
                # Put 
                to_read[sock] = task
            if reason == 'write':
                # {socket_type: generator,}
                to_write[sock] = task
        except StopIteration as err:
            print('Done!')
    pass


if __name__ == '__main__':
    # Phase 1. Append a new server_socket tuple.
    tasks.append(server())
    event_loop()
