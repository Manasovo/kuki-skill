from mycroft.skills.core import intent_handler
from mycroft.util.parse import match_one, fuzzy_match
from mycroft.api import DeviceApi
from mycroft.messagebus import Message
from requests import HTTPError
from adapt.intent import IntentBuilder

import requests                       # http post & get
import json                           # json :-)
import uuid                           # mac
import socket                         # hostname
import random                         # generate serial
import string                         # generate serial

#from .kuki import *
#from .kuki import (KukiConnect, generate_serial)

API_URL = "https://as.kukacka.netbox.cz/api-v2/"


def generate_serial(StringLength=56):
    """Generate a random string of letters and digits """
    
    LettersAndDigits = string.ascii_letters + string.digits
    return "kuki2.0_" + ''.join(random.choice(LettersAndDigits) for i in range(StringLength))


def kuki_session(self):
        """ registration and session key """
        self.log.debug("DEBUG SESSION")

        #serial = generate_serial(56)
        self.serial = "Manas_test_12345678"
        self.deviceType = "mobile"
        self.deviceModel = (socket.gethostname())
        self.product_name = "MyCroft"
        self.mac = (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                   for ele in range(0,8*6,8)][::-1])) 
        self.bootMode = "unknown"

        # data to be sent to api 
        self.api_post = {'sn':self.serial,
                        'device_type':self.deviceType,
                        'device_model':self.deviceModel, 
                        'product_name':self.product_name,
                        'mac':self.mac,
                        'boot_mode':self.bootMode,
                        'claimed_device_id':self.serial}

        # sending post request and saving response as response object 
        self.api_response = requests.post(url = API_URL + 'register' , data = self.api_post)
        self.log.debug("API POST")

        if json.loads(self.api_response.text)['state'] == 'NOT_REGISTERED':
            self.log.info('Kuki device is NOT REGISTERED try URL and pair code bellow:')
            self.result = self.api_response.json()
            self.log.info(self.result['registration_url_web'])
            self.log.info(self.result['reg_token'])
            return "NOT_REGISTERED"

        else:
             if json.loads(self.api_response.text)['state'] != 'NOT_REGISTERED':
                  self.log.info('Kuki device is REGISTERED')
                  self.session = json.loads(self.api_response.text)['session_key']
                  
                  self.log.info('SESSION')
                  self.log.info(self.session)  

                  return self.session


def kuki_devices(self):
        """ availabla device list from Kuki contract """
        self.log.debug("DEBUG DEVICES")
        
        if kuki_session(self) == 'NOT_REGISTERED':
            self.log.error("Kuki is NOT REGISTERED quit from kuki_devices")

        else:
            self.log.error("Kuki is REGISTERED continue")      

            self.session = kuki_session(self)
            self.log.error(self.session)

            self.api_headers = {'X-SessionKey': self.session}
            self.api_get = requests.get(API_URL + 'device', headers = self.api_headers)

            self.result = json.loads(self.api_get.text)
            self.log.debug(self.result)

            return ([result_item['alias'] for result_item in self.result]) # all devices


class KukiSkill(MycroftSkill):
    """Kuki control through the Kuki API."""    

    @intent_handler(IntentBuilder('').require('Kuki').require('Device'))
    def list_devices(self, message):
        """ List available devices. """
        self.log.error("DEBUG voice LIST DEVICES")

        if kuki_session(self) == 'NOT_REGISTERED':
            self.log.error("Kuki is NOT REGISTERED quit")

        else:
            self.log.error("Kuki is REGISTERED continue")

            self.devices = kuki_devices(self)
            self.log.error(self.devices)

     

        
        #if self.devices(self):
        #    devices = [d['alias'] for d in kuki_devices()]
            
            if len(devices) == 1:
                self.speak(devices[0])

            elif len(devices) > 1:
                self.speak_dialog('AvailableDevices',
                                  {'devices': ' '.join(devices[:-1]) + ' ' +
                                              self.translate('And') + ' ' +
                                              devices[-1]})
            else:
               self.log.debug("DEBUG NO DEVICE AVAILABLE")
               self.speak_dialog('NoDevicesAvailable')
        else:
            self.log.debug("DEBUG KUKI AUTH FAILED")
            # self.failed_auth()


    # testing playing tv intent
    @intent_handler(IntentBuilder('').require('Play'))
    def play_intent(self, message):
        self.log.debug("DEBUG play")
        self.speak_dialog("Play")
  
  

    def stop(self):
        pass

def create_skill():
    return KukiSkill()


    