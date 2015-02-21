import socket
import select
import threading
# import sys

# Messages:
#  Client->Server
#   One or two characters. First character is the command:
#     c: connect
#     u: update position
#     d: disconnect
#   Second character only applies to position and specifies direction (udlr)
#
#  Server->Client
#   '|' delimited pairs of positions to draw the players (there is no
#     distinction between the players - not even the client knows where its
#     player is.


class Player():
    def __init__(self, name="Bot"):
        self.name = name
        self.position = (0, 0)
        self.stepsize = 5
        pass

    def get_name(self):
        return self.name

    def do_movement(self, mv):
        pos = self.position
        if mv == "u":
            pos = (pos[0], max(0, pos[1] - self.stepsize))
        elif mv == "d":
            pos = (pos[0], min(300, pos[1] + self.stepsize))
        elif mv == "l":
            pos = (max(0, pos[0] - self.stepsize), pos[1])
        elif mv == "r":
            pos = (min(400, pos[0] + self.stepsize), pos[1])

        self.position = pos


class GameServer(object):
    def __init__(self, port=9011, max_num_players=5):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind to localhost - set to external ip to connect
        # from other computers
        self.listener.bind(("127.0.0.1", port))
        self.read_list = [self.listener]
        self.write_list = []

        self.players = {}

    def run(self):
        """Main server loop
        """
        print "Server ready."
        try:
            while True:
                # blocking select
                readable, writable, exceptional = select.select(
                    self.read_list,
                    self.write_list,
                    [])

                # Parses incoming message
                self.parse_message(readable)
                # Notifies players of changes
                self.update_players()

        except KeyboardInterrupt as e:
            print(e)
            pass

    def parse_message(self, readable):
        """Parses incoming message from socket
        """
        for f in readable:
            if f is self.listener:
                msg, addr = f.recvfrom(32)
                if len(msg) >= 1:
                    cmd = msg[0]
                    if cmd == "c":  # New Connection
                        self.players[addr] = Player(addr)
                    elif cmd == "u":  # Movement Update
                        if len(msg) >= 2 and addr in self.players:
                            # Second char of message is
                            # direction (udlr)
                            self.players[addr].do_movement(
                                msg[1])
                    elif cmd == "d":  # Player Quitting
                        if addr in self.players:
                            del self.players[addr]
                    else:
                        print "Unexpected: {0}".format(msg)

    def update_players(self):
        """Sends all the players the new game state
        """
        for addr, player in self.players.iteritems():
            send = []
            for addr2, playerpos in self.players.iteritems():
                pos = (repr(playerpos.position[0]) + "," +
                       repr(playerpos.position[1]))
                send.append(pos)
            self.listener.sendto('|'.join(send), addr)


class Dispatcher(threading.Thread):
    """Dispatcher for new incoming connections
    """
    def __init__(self, port=9010):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind to localhost - set to external ip to connect
        # from other computers
        self.sock.bind(("127.0.0.1", port))
        self.read_list = [self.sock]
        self.write_list = []
        self.exit = False

    def run(self):
        while not self.exit:
            # blocking select
            readable, writable, exceptional = select.select(
                self.read_list,
                self.write_list,
                [],
                0)

            # Parses incoming message
            self.parse_message(readable)
            # Notifies players of changes
            # self.update_players()

    def exit_request(self):
        self.exit = True

    def parse_message(self, readable):
        """Parses incoming message from socket
        """
        for f in readable:
            if f is self.sock:
                msg, addr = f.recvfrom(32)
                if len(msg) >= 1:
                    cmd = msg[0]
                    if cmd == "c":  # New Connection
                        self.sock.sendto("9011", addr)
                        # self.players[addr] = Player(addr)
                    else:
                        print "Unexpected: {0}".format(msg)


if __name__ == "__main__":
    # Start dispatcher for incoming connections
    d = Dispatcher()
    d.start()

    # Start GameServer
    g = GameServer()
    g.run()

    # Ask dispatcher to stop
    d.exit_request()
