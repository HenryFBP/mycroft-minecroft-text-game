from mycroft import MycroftSkill, intent_file_handler, adds_context
from typing import Tuple

from .GameState import GameState


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
        self.save_current_game_to_file()

    @intent_file_handler('reset.game.intent' )
    def handle_game_reset(self, message):

        self.speak(
            "About to delete the game save. Are you sure? A long summary: {}".format(
                self.game_state.speak_long_summary_of_game())
        )

        user_response = self.ask_yesno("With that summary in mind, do you still want to delete your game save?")
        if user_response == 'yes':
            self.delete_saved_game_and_reset()
            self.speak("Game was reset.")
            return
        elif user_response == 'no':
            pass
        else:
            self.speak("Could not understand '{}'".format(user_response))
        self.speak("Aborting game save deletion. Game save was not deleted.")

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

        # save after move
        self.save_current_game_to_file()

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
