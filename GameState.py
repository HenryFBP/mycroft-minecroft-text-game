import pickle
from io import StringIO
from typing import Tuple


class GameState:

    def __init__(self):
        self.started = False
        self.player_health = 0
        self.player_stamina = 0
        self.inventory = []
        self.position = [0, 0]
        self.steps_walked = 0

    def start_game(self):
        self.started = True
        self.player_health = 100
        self.player_stamina = 100
        self.inventory = []
        self.position = [0, 0]
        self.steps_walked = 0

    def move(self, vec: Tuple[int, int]):
        if self.player_stamina > 0:
            self.player_stamina -= 10
            self.position[0] += vec[0]
            self.position[1] += vec[1]
            self.steps_walked += 1
        else:
            raise PlayerTooTiredException("Player is too tired to move!")

    def is_tired(self):
        return self.player_stamina <= 30

    def pretty_position(self):
        return "{} units North-South and {} units East-West".format(
            self.get_northsouth_position(),
            self.get_eastwest_position(),
        )

    def get_northsouth_position(self):
        return self.position[1]

    def get_eastwest_position(self):
        return self.position[0]

    def serialize(self) -> str:
        return pickle.dumps(self)

    @staticmethod
    def deserialize(pickled_gamestate: str):
        return pickle.loads(pickled_gamestate)

    def speak_long_summary_of_game(self):
        s = ""

        s += "You are {}. \n".format(self.pretty_position())
        s += "You have {} health and {} stamina. \n".format(self.player_health, self.player_stamina)
        s += "You have {} items in your inventory.\n".format(len(self.inventory))
        s += "You have walked {} steps.\n".format(self.steps_walked)

        return s

    def stop_game(self):
        self.started = False


class PlayerTooTiredException(Exception):
    pass
