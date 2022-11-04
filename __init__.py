from mycroft import MycroftSkill, intent_file_handler


class MinecraftGame(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('blockgame.intent.start_game')
    def handle_game_start(self, message):
        self.speak_dialog('blockgame.response.starting_game')


def create_skill():
    return MinecraftGame()

