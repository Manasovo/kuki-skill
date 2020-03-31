from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel

from enum import Enum

class DeviceType(Enum):
    DEFAULT = 1
    FIRSTBEST = 2
    NOTFOUND = 3


"""
class KukiSkill(MycroftSkill):
    def __init__(self):
        super().__init__()
        self.learning = True


    def initialize(self):
        my_setting = self.settings.get('default_device')
"""


class KukiSkill(CommonPlaySkill):
    """Kuki control through the Kuki API."""

    def __init__(self):
        super(KukiSkill, self).__init__()
        self.index = 0
        self.kuki = None
        self.process = None
        self.device_name = None
      



    @intent_handler(IntentBuilder('')
                    .require('play'))
    def handle_hello_world_intent(self, message):
        self.speak_dialog("play")
  
    def stop(self):
        pass

def create_skill():
    return KukiSkill()


    