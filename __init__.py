from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_file_handler, intent_handler, adds_context
from typing import List, Dict, Tuple


def cardinal_vector_to_direction(vector: Tuple[int, int]) -> str:
    flat_vector = ''.join([str(x) for x in vector])

    lookup = {
        '01': "North",
        '10': "East",
        '0-1': "South",
        '-10': "West",
    }

    if flat_vector in lookup:
        return lookup[flat_vector]

    raise Exception(f"Could not convert {vector} to a cardinal direction!")


class PlayerTooTiredException(Exception):
    pass


class GameState:

    def __init__(self):
        self.started = False
        self.player_health = 0
        self.player_stamina = 0
        self.inventory = []
        self.position = [0, 0]

    def start_game(self):
        self.started = True
        self.player_health = 100
        self.player_stamina = 100
        self.inventory = []
        self.position = [0, 0]

    def move(self, vec: Tuple[int, int]):
        if self.player_stamina > 0:
            self.player_stamina -= 10
            self.position[0] += vec[0]
            self.position[1] += vec[1]
        else:
            raise PlayerTooTiredException("Player is too tired to move!")

    def is_tired(self):
        return self.player_stamina <= 30

    def pretty_position(self):
        return "{} units North-South and {} units East-West".format(self.get_northsouth_position(), self.get_eastwest_position())

    def get_northsouth_position(self):
        return self.position[1]

    def get_eastwest_position(self):
        return self.position[0]


class MinecraftGame(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.game_state = GameState()

    def ensure_game_started(self):
        if not self.game_state.started:
            self.speak_dialog('error.game.not.started')
            return False

        return True

    @intent_file_handler('start.game.intent')
    @adds_context('GameStartedContext')
    def handle_game_start(self, message):
        self.speak_dialog('starting.game')
        self.game_state.start_game()

        self.speak_dialog('opening.scene')

        resp = self.speak_dialog('next.action', expect_response=True)
        print(resp)

    @intent_file_handler('move.north.intent')
    def move_north(self, message):
        self.generic_move((0, 1), "North")

    @intent_file_handler('move.south.intent')
    def move_south(self, message):
        self.generic_move((0, -1), "South")

    @intent_file_handler('move.east.intent')
    def move_east(self, message):
        self.generic_move((1, 0), "East")

    @intent_file_handler('move.west.intent')
    def move_west(self, message):
        self.generic_move((-1, 0), "West")

    def generic_move(self, vector: Tuple[int, int], direction_name: str):
        if not self.ensure_game_started():
            return False

        self.speak_dialog('moving.direction', {'direction': direction_name})
        self.game_state.move(vector)

        self.speak_dialog('player.current.position', {'position': str(self.game_state.pretty_position())})

        if self.game_state.is_tired():
            self.speak_dialog('player.is.tired')


def create_skill():
    return MinecraftGame()
