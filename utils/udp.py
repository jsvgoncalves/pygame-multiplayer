# -*- coding: utf-8 -*-
#
## This file is part of PyTank.
## 2014 João Gonçalves.

import socket
import random
import select


def port_query(addr="127.0.0.1", serverport=9010):
    """Tries to contact server to ask for gameport.

    Sends a datagram (UDP) message to the server and waits
    (blocking) for the reply with the port.

    Args:
      addr (string): The server address.
      port (int): The server port.

    Returns:
        string: The new port for the TCP connection.

    """

    # UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Assign random client port
    clientport = random.randrange(8000, 8999)
    # And bind it
    sock.bind(("127.0.0.1", clientport))

    # Send message with "c" to the server
    sock.sendto("c", (addr, serverport))

    # Wait for the reply
    while True:
        readable, writable, exceptional = (
                        select.select([sock], [], [], 0)
                    )
        for f in readable:
            if f is sock:
                msg, addr = f.recvfrom(32)
                # Perform checks on the message,
                # try again if it doesn't look good.

                # Return the port
                return msg
