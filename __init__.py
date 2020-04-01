import re
from mycroft.skills.core import intent_handler
from mycroft.util.parse import match_one, fuzzy_match
from mycroft.api import DeviceApi
from mycroft.messagebus import Message
from requests import HTTPError
from adapt.intent import IntentBuilder

import time
from os.path import abspath, dirname, join
from subprocess import call, Popen, DEVNULL
import signal
from socket import gethostname

import random

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel

from enum import Enum

from .kuki import (KukiConnect)



class KukiSkill(MycroftSkill):
    """Kuki control through the Kuki API."""    

    @intent_handler(IntentBuilder('').require('Kuki').require('Device'))
    def list_devices(self, message):
        """ List available devices. """
        
        self.kuki = KukiConnect(get_devices)
        
        self.log.error(self.kuki)
        self.log.error("TEST")
        

        if self.kuki:
            devices = [d['alias'] for d in self.kuki.get_devices()]
            
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


    