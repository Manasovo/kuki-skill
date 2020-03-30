from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler


class KukiSkill(MycroftSkill):
    def __init__(self):
        super().__init__()
        self.learning = True

    def initialize(self):
        my_setting = self.settings.get('my_setting')

  
   @intent_handler(IntentBuilder('')
                    .require('HelloWorldKeyword'))
    def handle_hello_world_intent(self, message):
 
        self.speak_dialog("hello.world")

  
    def stop(self):
        pass

def create_skill():
    return KukiSkill()