from mycroft import MycroftSkill, intent_file_handler


class MinecraftGame(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('start.game.intent')
    def handle_game_start(self, message):
        self.speak_dialog('starting.game')


def create_skill():
    return MinecraftGame()

