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

    def __init__(self):
        super(KukiSkill, self).__init__()
        self.learning = True
        self.index = 0
        self.kuki = None
        self.process = None
        self.device_name = None
      

    def get_default_device(self):
        """Get preferred playback device."""
        if self.kuki:
            # When there is an active Kuki device somewhere, use it
            if (self.devices and len(self.devices) > 0 and
                    self.kuki.is_playing()):
                for dev in self.devices:
                    if dev['is_active']:
                        self.log.info('Playing on an active device '
                                      '[{}]'.format(dev['name']))
                        return dev  # Use this device
       
            # No playing device found, use the default Kuki device
            default_device = self.settings.get('default_device', '')
            dev = None
            device_type = DeviceType.NOTFOUND
            if default_device:
                dev = self.device_by_name(default_device)
                self.is_player_remote = True
                device_type = DeviceType.DEFAULT
              # use first best device if none of the prioritized works
            if not dev and len(self.devices) > 0:
                dev = self.devices[0]
                self.is_player_remote = True  # ?? Guessing it is remote
                device_type = DeviceType.FIRSTBEST

            if dev and not dev['is_active']:
                self.kuki.transfer_playback(dev['id'], False)
            self.log.info('Device detected: {}'.format(device_type))
            return dev

        return None


    @intent_handler(IntentBuilder('')
                    .require('play'))
    def handle_hello_world_intent(self, message):
        self.speak_dialog("play")
  
    def stop(self):
        pass

def create_skill():
    return KukiSkill()


    