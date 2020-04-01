from mycroft.skills.core import intent_handler
from mycroft.util.parse import match_one, fuzzy_match
from mycroft.api import DeviceApi
from mycroft.messagebus import Message
from requests import HTTPError
from adapt.intent import IntentBuilder

from .kuki import (KukiConnect, GenerateSerial, kuki_session, kuki_devices)


class KukiSkill(MycroftSkill):
    """Kuki control through the Kuki API."""    

    @intent_handler(IntentBuilder('').require('Kuki').require('Device'))
    def list_devices(self, message):
        """ List available devices. """
        
        self.log.error("DEBUG")
        self.kuki = GenerateSerial(self)
    
        self.log.error(self.kuki)
        self.log.error("TEST")
        

        if self.kuki:
            devices = [d['alias'] for d in self.kuki.kuki_devices()]
            
            if len(devices) == 1:
                self.speak(devices[0])

            elif len(devices) > 1:
                self.speak_dialog('AvailableDevices',
                                  {'devices': ' '.join(devices[:-1]) + ' ' +
                                              self.translate('And') + ' ' +
                                              devices[-1]})
            else:
               self.log.error("NO DEVICE AVAILABLE")
               self.speak_dialog('NoDevicesAvailable')
        else:
            self.log.error("KUKI AUTH FAILED")
            # self.failed_auth()


    # testing playing tv intent
    @intent_handler(IntentBuilder('').require('Play'))
    def play_intent(self, message):
        self.speak_dialog("Play")
  
  

    def stop(self):
        pass

def create_skill():
    return KukiSkill()


    