from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_file_handler, intent_handler

import requests                       # http post & get
import json                           # json :-)
import uuid                           # mac
import socket                         # hostname
import random                         # generate serial
import string                         # generate serial

#from .kuki import *
#from .kuki import (KukiConnect, generate_serial)

#API_URL = "https://as.kukacka.netbox.cz/api-v2/"
API_URL = "https://as.kuki.cz/api-v2/"
session = ''

#session ostra
#session = "c466192e-1cf0-49c5-af1e-8dd80682b447"

#session testovka
#session = "4fb565d2-b386-4fc9-9d35-84d11cb05c0b"


def kuki_session(self):
        self.log.debug("DEBUG SESSION")
        self.log.debug(session)

        if session == "":
            self.log.info("SESSION not found generation new")
            kuki_reg(self)
        
        else:
            self.log.info("SESSION found using")
            return session

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


def generate_serial(StringLength=56):
    """Generate a random string of letters and digits """
    
    LettersAndDigits = string.ascii_letters + string.digits
    return "kuki2.0_" + ''.join(random.choice(LettersAndDigits) for i in range(StringLength))


def kuki_reg(self):
        global session #cache session

        """ registration and session key """
        self.log.debug("DEBUG REGISTER")

        #serial = generate_serial(56)
        self.serial = "Manas_test_123456789"
        self.deviceType = "fix"
        self.deviceModel = (socket.gethostname())
        self.product_name = "Mycroft"
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
            self.result = self.api_response.json()
            self.log.error('Kuki device is NOT REGISTERED try URL and pair code bellow:')
            self.log.error(self.result['registration_url_web'])
            self.log.error(self.result['reg_token'])

            return "NOT_REGISTERED"
            failed_auth(self)

        else:
             if json.loads(self.api_response.text)['state'] != 'NOT_REGISTERED':
                  self.log.info('Kuki device is REGISTERED')
                  
                  session = json.loads(self.api_response.text)['session_key']
                  self.log.info(session)  

                  return session
                  

def kuki_devices(self):
        """ availabla device list from Kuki contract """
            
        self.log.debug("DEBUG DEVICES")   
 
        # API get
        self.api_headers = {'X-SessionKey': session}
        self.api_get = requests.get(API_URL + 'device', headers = self.api_headers)

        self.result = json.loads(self.api_get.text)

        # only devices can play TV, only fix or smarrtv
        devices = list(map(lambda item: item['alias'], filter(lambda item: item['canPlay'] and item['deviceType'] in ['smarttv', 'fix'], self.result)))
        self.log.debug(devices) 
        
        return devices


class KukiSkill(MycroftSkill):
    """Kuki control through the Kuki API."""    

    @intent_handler(IntentBuilder('').require('Show').require('Kuki').require('Device'))
    def list_devices(self, message):
        """ List available devices. """
        self.log.debug("DEBUG voice LIST DEVICES")

        kuki_session(self)

        devices = kuki_devices(self)
        self.log.debug(devices)
           
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



    # status of device
    @intent_handler(IntentBuilder('').require('Status').require('Kuki').require('Device'))
    def status_intent(self, message):
    
        kuki_session(self)

        # API get - TODO prefered devices
        self.api_headers = {'X-SessionKey': session}
        self.api_get = requests.get(API_URL + 'device', headers = self.api_headers)

        self.result = json.loads(self.api_get.text)
        self.prefered_device = list(map(lambda item: item['id'], filter(lambda item: item['alias'] == 'Mother Fucker', self.result)))
        self.log.error(self.prefered_device)
        
        self.speak_dialog("Status")
    

    # testing playing tv intent
    @intent_handler(IntentBuilder('').require('Play'))
    def play_intent(self, message):
        self.speak_dialog("Play")
  
  
    # volume on devices
    @intent_handler(IntentBuilder('').require('VolumeUp').require('VolumeDown'))
    def volume_intent(self, message):

        kuki_session(self)
        
        # API get - TODO set prefered devices
        self.api_headers = {'X-SessionKey': session}
        API_REMOTE_URL = "https://admin.as.kuki.tv/api/remote/" 
        DEVICE_ID = "123"

        self.api_get = requests.get(API_URL + 'device', headers = self.api_headers)

        self.result = json.loads(self.api_get.text)
        self.prefered_device = list(map(lambda item: item['id'], filter(lambda item: item['alias'] == 'Mother Fucker', self.result)))
        self.log.error(self.prefered_device)

        # data to be sent to api 
        self.api_post = {'action':volset,
                        'volume':"10"}

        # sending post request and saving response as response object
        self.api_response = requests.post(url = API_REMOTE_URL + DEVICE_ID +".json", headers = self.api_headers, data = self.api_post)
        
        prdel = json.loads(self.api_response.text)
        print(prdel)

        self.speak_dialog("Volume")


        # play live tv
    @intent_handler(IntentBuilder('').require('PlayLive'))
    def live_intent(self, message):

        self.log.error("DEBUG PLAY LIVE")

        kuki_session(self)
        
        # API get - TODO set prefered devices
        self.api_headers = {'X-SessionKey': session}
        API_REMOTE_URL = "https://admin.as.kuki.tv/api/remote/" 
        DEVICE_ID = "5034042"

        self.api_get = requests.get(API_URL + 'device', headers = self.api_headers)

        self.result = json.loads(self.api_get.text)
        self.play_live = list(map(lambda item: item['id'], filter(lambda item: item['alias'] == 'Mother Fucker', self.result)))
        
        self.log.error(self.play_live)



        #API POST data
        self.remote = "remote"
        self.live = "live"
        
        # data to be sent to api 
        self.api_post = {'action':self.remote,
                        'type':self.live}


        # sending post request and saving response as response object
        self.api_response = requests.post(url = API_REMOTE_URL + DEVICE_ID + ".json", headers = self.api_headers, data = self.api_post)
        
        prdel = json.loads(self.api_response.text)
        print(prdel)

        self.speak_dialog("Playlive")




    def stop(self):
        pass

def create_skill():
    return KukiSkill()


    