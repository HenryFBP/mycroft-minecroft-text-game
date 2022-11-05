import pickle
from io import StringIO
from typing import Tuple


class Player:
    def __init__(self):
        self.health = 100
        self.stamina = 100
        self.inventory = []
        self.position = [0, 0]
        self.steps_walked = 0

    def is_tired(self):
        return self.stamina <= 30

    def move(self, vec: Tuple[int, int]):
        if self.stamina > 0:
            self.stamina -= 10
            self.position[0] += vec[0]
            self.position[1] += vec[1]
            self.steps_walked += 1
        else:
            raise PlayerTooTiredException("Player is too tired to move!")

    def pretty_position(self):
        return "{} units North-South and {} units East-West".format(
            self.get_northsouth_position(),
            self.get_eastwest_position(),
        )

    def get_northsouth_position(self):
        return self.position[1]

    def get_eastwest_position(self):
        return self.position[0]


class GameState:

    def __init__(self):
        self.started = False
        self.player = Player()

    def start_game(self):
        self.started = True
        self.player = Player()

    def serialize(self) -> bytes:
        return pickle.dumps(self)

    @staticmethod
    def deserialize(pickled_gamestate: bytes):
        return pickle.loads(pickled_gamestate)

    def speak_long_summary_of_game(self):
        s = ""

        s += "You are {}. \n".format(self.pretty_position())
        s += "You have {} health and {} stamina. \n".format(self.player.health, self.player.stamina)
        s += "You have {} items in your inventory.\n".format(len(self.player.inventory))
        s += "You have walked {} steps.\n".format(self.player.steps_walked)

        return s

    def stop_game(self):
        self.started = False

    def speak_look_around(self):

        if self.player.get_northsouth_position() < -3:
            return "You see a vast, dry, cracked desert before you. A few acacia trees punctuate the otherwise unremarkable landscape."

        if self.player.get_northsouth_position() > 3:
            return "You see a snowy tundra. There are tall pine trees."

        return "You see a grassy field, dotted with trees and flowers. There might be animals in the distance."


class PlayerTooTiredException(Exception):
    pass
