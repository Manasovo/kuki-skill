from mycroft import MycroftSkill, intent_file_handler


class Kuki(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('kuki.intent')
    def handle_kuki(self, message):
        self.speak_dialog('kuki')


def create_skill():
    return Kuki()

