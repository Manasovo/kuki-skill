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
        self.kuki = None
        self.__device_list = None
        self.__devices_fetched = 0



    def devices(self):
        """Devices, cached for 60 seconds."""
        if not self.kuki:
            return []  # No connection, no devices
        now = time.time()
        if not self.__device_list or (now - self.__devices_fetched > 60):
            self.__device_list = self.kuki.get_devices()
            self.__devices_fetched = now
        return self.__device_list

    def device_by_name(self, name):
        """Get a kuki devices from the API.

        Arguments:
            name (str): The device name (fuzzy matches)
        Returns:
            (dict) None or the matching device's description
        """
        devices = self.devices
        if devices and len(devices) > 0:
            # Otherwise get a device with the selected name
            devices_by_name = {d['name']: d for d in devices}
            key, confidence = match_one(name, list(devices_by_name.keys()))
            if confidence > 0.5:
                return devices_by_name[key]
        return None


    @intent_handler(IntentBuilder('').require('Kuki').require('Device'))
    def list_devices(self, message):
        """ List available devices. """
        if self.kuki:
            devices = [d['name'] for d in self.kuki.get_devices()]
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


    