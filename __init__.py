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


class KukiSkill(MycroftSkill):
    """Kuki control through the Kuki API."""

     @intent_handler(IntentBuilder('').require('Spotify').require('Device'))
        def list_devices(self, message):
        """ List available devices. """
        if self.spotify:
            devices = [d['name'] for d in self.spotify.get_devices()]
            if len(devices) == 1:
                self.speak(devices[0])
            elif len(devices) > 1:
                self.speak_dialog('AvailableDevices',
                                  {'devices': ' '.join(devices[:-1]) + ' ' +
                                              self.translate('And') + ' ' +
                                              devices[-1]})
            else:
                self.speak_dialog('NoDevicesAvailable')
        else:
            self.failed_auth()



    @intent_handler(IntentBuilder('')
                    .require('Play'))
    def play_intent(self, message):
        self.speak_dialog("Play")
  
  

    def stop(self):
        pass

def create_skill():
    return KukiSkill()


    