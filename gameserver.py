import socket
import select
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
        pass

    def get_name(self):
        return self.name


class GameServer(object):
    def __init__(self, port=9009, max_num_players=5):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind to localhost - set to external ip to connect
        # from other computers
        self.listener.bind(("127.0.0.1", port))
        self.read_list = [self.listener]
        self.write_list = []

        self.stepsize = 5
        self.players = {}

    def do_movement(self, mv, player):
        pos = self.players[player].position
        if mv == "u":
            pos = (pos[0], max(0, pos[1] - self.stepsize))
        elif mv == "d":
            pos = (pos[0], min(300, pos[1] + self.stepsize))
        elif mv == "l":
            pos = (max(0, pos[0] - self.stepsize), pos[1])
        elif mv == "r":
            pos = (min(400, pos[0] + self.stepsize), pos[1])

        self.players[player].position = pos

    def run(self):
        print "Waiting..."
        try:
            while True:
                readable, writable, exceptional = select.select(
                    self.read_list,
                    self.write_list,
                    [])

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
                                    self.do_movement(msg[1], addr)
                            elif cmd == "d":  # Player Quitting
                                if addr in self.players:
                                    del self.players[addr]
                            else:
                                print "Unexpected: {0}".format(msg)
                for addr, player in self.players.iteritems():
                    send = []
                    for addr2, playerpos in self.players.iteritems():
                        pos = (repr(playerpos.position[0]) + "," +
                               repr(playerpos.position[1]))
                        send.append(pos)
                    self.listener.sendto('|'.join(send), addr)
        except KeyboardInterrupt as e:
            print(e)
            pass

if __name__ == "__main__":
    g = GameServer()
    g.run()
