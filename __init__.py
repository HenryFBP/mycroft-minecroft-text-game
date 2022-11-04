from mycroft import MycroftSkill, intent_file_handler


class MinecraftGame(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('game.minecraft.intent')
    def handle_game_minecraft(self, message):
        self.speak_dialog('game.minecraft')


def create_skill():
    return MinecraftGame()

