import pygame
import pygame.locals
import socket
import select
import random
#  import time

from utils.udp import port_query


class GameClient(object):
    def __init__(self, addr="127.0.0.1", serverport=9011):
        self.clientport = random.randrange(8000, 8999)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind to localhost - set to external ip to connect
        # from other computers
        self.conn.bind(("127.0.0.1", self.clientport))
        self.addr = addr
        self.serverport = serverport

        self.read_list = [self.conn]
        self.write_list = []

        self.setup_pygame()

    def setup_pygame(self, width=400, height=300):
        self.screen = pygame.display.set_mode((width, height))

        self.image = pygame.image.load("player.png").convert_alpha()

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((80, 100, 60))

        pygame.event.set_allowed(None)
        pygame.event.set_allowed([pygame.locals.QUIT,
                                  pygame.locals.KEYDOWN])
        pygame.key.set_repeat(50, 50)

    def run(self):
        running = True
        clock = pygame.time.Clock()
        tickspeed = 30

        try:
            # Initialize connection to server
            self.conn.sendto("c", (self.addr, self.serverport))
            while running:
                clock.tick(tickspeed)

                # select on specified file descriptors
                readable, writable, exceptional = (
                    select.select(self.read_list, self.write_list, [], 0)
                )
                for f in readable:
                    if f is self.conn:
                        msg, addr = f.recvfrom(32)
                        # Draw the background
                        self.screen.blit(self.background, (0, 0))
                        for position in msg.split('|'):
                            x, sep, y = position.partition(',')
                            try:
                                self.screen.blit(self.image, (int(x), int(y)))
                            except:
                                # If something goes wrong, don't draw anything.
                                pass

                for event in pygame.event.get():
                    if (event.type == pygame.QUIT or
                       event.type == pygame.locals.QUIT):
                        running = False
                        break
                    elif event.type == pygame.locals.KEYDOWN:
                        if event.key == pygame.locals.K_UP:
                            self.conn.sendto("uu",
                                             (self.addr, self.serverport))
                        elif event.key == pygame.locals.K_DOWN:
                            self.conn.sendto("ud",
                                             (self.addr, self.serverport))
                        elif event.key == pygame.locals.K_LEFT:
                            self.conn.sendto("ul",
                                             (self.addr, self.serverport))
                        elif event.key == pygame.locals.K_RIGHT:
                            self.conn.sendto("ur",
                                             (self.addr, self.serverport))
                        pygame.event.clear(pygame.locals.KEYDOWN)

                pygame.display.update()

        finally:
            self.conn.sendto("d", (self.addr, self.serverport))


if __name__ == "__main__":
    # Get the gameport (launcher)
    print("## Launching network.")
    port = port_query()
    print("Gameport is " + port)
    print("##")

    # Create the client with the gameport
    g = GameClient("127.0.0.1", int(port))
    # And run it
    g.run()
