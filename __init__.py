import os
import time

from mycroft import MycroftSkill, intent_file_handler

import pickle
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

    def pretty_position_long(self):
        return "{} units North-South and {} units East-West".format(
            self.get_northsouth_position(),
            self.get_eastwest_position(),
        )

    def pretty_position_short(self):
        return "{} comma {}".format(
            self.get_northsouth_position(),
            self.get_eastwest_position()
        )

    def get_northsouth_position(self):
        return self.position[1]

    def get_eastwest_position(self):
        return self.position[0]

    def recover_stamina(self):
        self.stamina = 100


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

        s += "You are {}. \n".format(self.player.pretty_position_long())
        s += "You have {} health and {} stamina. \n".format(self.player.health, self.player.stamina)
        s += "You have {} items in your inventory.\n".format(len(self.player.inventory))
        s += "You have walked {} steps.\n".format(self.player.steps_walked)

        return s

    def speak_short_summary_of_game(self):
        s = "At heading {}.\n".format(self.player.pretty_position_short())
        s += "You have {} hp, {} stamina, {} items.\n".format(
            self.player.health,
            self.player.stamina,
            len(self.player.inventory)
        )
        s += "Walked {} steps.\n".format(self.player.steps_walked)

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


def game_must_be_started(function):
    """Decorate with me if you only want to execute the function if the game has started."""

    print("in @game_must_be_started")

    def wrapper(self, *args, **kwargs):
        if not self.game_state.started:
            self.speak_dialog('error.game.not.started')
            return

        return function(self, *args, **kwargs)

    return wrapper


def ensure_game_saved_after(function):
    """Decorate with me if you want to save the game after the decorated function has finished executing."""

    print("in @ensure_game_saved_after")

    def wrapper(self, *args, **kwargs):
        result = function(self, *args, **kwargs)

        self.save_current_game_to_file()

        return result

    return wrapper


class MinecraftGame(MycroftSkill):
    SAVE_PATH = 'game_state.pkl'
    game_state: GameState = None

    def __init__(self):
        MycroftSkill.__init__(self)
        if self.has_saved_game_file():
            print("Using existing saved game at " + self.SAVE_PATH)
            self.load_game_from_file()
            self.save_current_game_to_file()
        else:
            print("You don't have a saved game. Creating one!")
            self.delete_saved_game_and_reset()

    @intent_file_handler('game.start.intent')
    def handle_game_start(self, message):
        self.speak_dialog('game.starting')
        self.game_state.start_game()
        self.save_current_game_to_file()
        self.speak(self.game_state.speak_long_summary_of_game())

    @intent_file_handler('recover.stamina.intent')
    @game_must_be_started
    def handle_recover_stamina(self, message):
        time.sleep(5)
        self.game_state.player.recover_stamina()
        self.speak("You feel full of energy.")

    @intent_file_handler('game.stop.intent')
    @game_must_be_started
    def handle_game_stop(self, message):
        self.speak_dialog('game.stopping')
        self.game_state.stop_game()
        self.save_current_game_to_file()

    @intent_file_handler('game.reset.intent')
    def handle_game_reset(self, message):

        self.speak(
            "About to delete the game save. Are you sure? A long summary: {}".format(
                self.game_state.speak_long_summary_of_game())
        )

        user_response = self.ask_yesno("With that summary in mind, do you still want to delete your game save?")
        if user_response.lower() == 'yes':
            self.delete_saved_game_and_reset()
            self.speak("Game was reset.")
            return
        elif user_response.lower() == 'no':
            pass
        else:
            self.speak("Could not understand '{}'".format(user_response))
        self.speak("Aborting game save deletion. Game save was not deleted.")

    @intent_file_handler('inspect.surroundings.intent')
    @game_must_be_started
    @ensure_game_saved_after
    def handle_look_around(self, message):
        self.speak(self.game_state.speak_short_summary_of_game())
        self.speak(self.game_state.speak_look_around())

    @intent_file_handler('player.confused.intent')
    def player_needs_help(self, message):
        self.speak("todo implement help")

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

    @game_must_be_started
    @ensure_game_saved_after
    def generic_move(self, vector: Tuple[int, int], direction_name: str):

        try:
            self.game_state.player.move(vector)
            self.speak_dialog('moving.direction', {'direction': direction_name})
        except PlayerTooTiredException:
            self.speak_dialog('error.player.too.tired.to.move')
            return False

        self.speak_dialog('player.current.position', {'position': str(self.game_state.player.pretty_position_long())})

        if self.game_state.player.is_tired():
            self.speak_dialog('player.is.tired')

    def save_current_game_to_file(self):
        with self.file_system.open(self.SAVE_PATH, 'wb') as my_file:
            data = self.game_state.serialize()
            print(data)
            my_file.write(data)

    def has_saved_game_file(self):
        return self.file_system.exists(self.SAVE_PATH)

    def load_game_from_file(self) -> GameState:
        with self.file_system.open(self.SAVE_PATH, 'rb') as my_file:
            content: str = my_file.read()
            print(content)
            if content == b'':
                print("WARNING: File at " + self.SAVE_PATH + " seems to be empty.")
                self.reset_gamestate()
            else:
                self.game_state = GameState.deserialize(content)
                print("Loaded GameState: " + self.game_state.speak_long_summary_of_game())

            return self.game_state

    def delete_saved_game_and_reset(self):
        self.reset_gamestate()
        self.save_current_game_to_file()

    def reset_gamestate(self):
        self.game_state = GameState()


def create_skill():
    return MinecraftGame()
