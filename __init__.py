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

from .kuki import (MycroftKukiAuth, KukiConnect)


class DeviceType(Enum):
    DEFAULT = 1
    FIRSTBEST = 2
    NOTFOUND = 3

class KukiSkill(MycroftSkill):
    """Kuki control through the Kuki API."""
    
    def __init__(self):
        super(KukiSkill, self).__init__()
        self.kuki = None
        self.__device_list = None
        self.__devices_fetched = 0


    def failed_auth(self):
        if 'user' not in self.settings:
            self.log.error('Settings hasn\'t been received yet')
            self.speak_dialog('NoSettingsReceived')
        elif not self.settings.get("user"):
            self.log.error('User info has not been set.')
            # Assume this is initial setup
            self.speak_dialog('NotConfigured')
        else:
            # Assume password changed or there is a typo
            self.log.error('User info has been set but Auth failed.')
            self.speak_dialog('NotAuthorized')


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
        print(self.session)
  
  

    def stop(self):
        pass

def create_skill():
    return KukiSkill()


    