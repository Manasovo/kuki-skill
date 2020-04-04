from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_file_handler, intent_handler

import requests                                         # http post & get
import json                                             # json :-)
import uuid                                             # mac
import socket                                           # hostname
import random                                           # generate serial
import string                                           # generate serial                                      
from mycroft.filesystem import FileSystemAccess         # file operation


#API_URL = "https://as.kukacka.netbox.cz/api-v2/"
API_URL = "https://as.kuki.cz/api-v2/"

#API_REMOTE_URL =  "https://as.kukacka.netbox.cz/api/remote/"
API_REMOTE_URL = "https://as.kuki.cz/api/remote/"

#API_REMOTE_STATE_URL =  "https://as.kukacka.netbox.cz/api/device-state/(?P<pk>\d+)"
API_REMOTE_STATE_URL = "https://as.kuki.cz/api/device-state/"

sernum = ''                 # uniq serial number
session = ''                # token 
devices = ''                # all devices
prefered_device = ''        # alias
prefered_device_id = ''     # id
status_power = ''           # power of end device
status_playing = ''         # state of device
status_volume = ''          # volume of device

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

    global sernum       # save serial number
    
    LettersAndDigits = string.ascii_letters + string.digits
    return "kuki2.0_" + ''.join(random.choice(LettersAndDigits) for i in range(StringLength))
    
    


def serial(self):
    try:
        self.log.error("READING SERIAL NUMBER") 
        file_system = FileSystemAccess(str("skills/KukiSkill/"))
        file = file_system.open("kuki.serial", mode="r")
        data = file.read()
        file.close()

        self.log.error(data)

        return data

    except Exception as e:
        self.log.error("SERIAL NOT READ FROM FILE " + filename)
        LOG.error(e)
        return False    

    try: 
        self.log.error("WRITE SERIAL") 
        file_system = FileSystemAccess(str("skills/KukiSkill/"))
        file = file_system.open("kuki.serial", mode="w")
        file.write(sernum)
        file.close()
        return True
    
    except Exception as e:
        self.log.error("SERIAL NOT SAVE TO FILE " + filename)
        LOG.error(e)
        return False    
        

  
def kuki_reg(self):
        global session #cache session

        """ registration and session key """
        self.log.error("DEBUG REGISTER")

        #serial = generate_serial(56)
        self.serial = "Manas_test_12345678"
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
        self.log.debug(self.api_response)

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

                  return init(self)
                  

def kuki_devices(self):
        """ availabla device list from Kuki contract """
        global devices # cache connected devices

        self.log.debug("DEBUG DEVICES")   
 
        # API get
        self.api_headers = {'X-SessionKey': session}
        self.api_get = requests.get(API_URL + 'device', headers = self.api_headers)

        self.result = json.loads(self.api_get.text)

        # only devices can play TV, only fix or smarrtv
        devices = list(map(lambda item: item['alias'], filter(lambda item: item['canPlay'] and item['deviceType'] in ['smarttv', 'fix'], self.result)))
        self.log.debug(devices) 
        
        return init(self)


def prefered_device(self):
        """ select of of many Kuki devices from contract """
        global prefered_device #cache prefered device alias
        global prefered_device_id #cache prefered device id

        self.log.error("DEBUG PREFERED DEVICES")   

        default_device = self.settings.get('default_device')    # load setting from Mycroft backend
     
        if default_device == '':
            self.log.error("NO DEFAULT DEVICE SELECED in Mycroft settings")
            
            self.log.debug(devices)
            prefered_device = devices[0]    # choose frist device from list
            self.log.info(prefered_device)

            # API get - get id from prefered alias
            self.api_headers = {'X-SessionKey': session}  
            self.api_get = requests.get(API_URL + 'device', headers = self.api_headers) # show all devices on contract
            self.result = json.loads(self.api_get.text)
            prefered_device_id = str(list(filter(lambda item: item['alias'] == prefered_device, self.result))[0]['id']) # select prefered device

            self.log.info("DEFAULT DEVICE ID")
            self.log.info(prefered_device_id)

            return init(self)
        
        else:
            self.log.info("DEFAULT DEVICE SELECED from Mycroft settings")
            self.log.info(default_device)
            #prefered_device = default_device

            # API get - get id from default alias
            self.api_headers = {'X-SessionKey': session}  
            self.api_get = requests.get(API_URL + 'device', headers = self.api_headers) # show all devices on contract
            self.result = json.loads(self.api_get.text)
            prefered_device_id = str(list(filter(lambda item: item['alias'] == default_device, self.result))[0]['id']) # select default device

            self.log.info("DEFAULT DEVICE ID")
            self.log.info(prefered_device_id)

            return init(self)


# status of prefered device
def status_device(self):
        
        global status_power # power of end device
        global status_playing # state of device
        global status_volume # volume of device

        self.log.error("DEBUG STATUS OF PREFERED DEVICE")
        
        # API GET
        self.api_status = requests.get(API_REMOTE_STATE_URL + prefered_device_id + ".json", headers = self.api_headers)
        
        if self.api_status:
   
            try:
                self.status = json.loads(self.api_status.text)

            except ValueError:
                self.log.error('Kuki PREFERED DEVICE IS POWER DOWN')
                
            else:
                self.log.info('Kuki DEVICE IS UP - reading settings')
                self.status = json.loads(self.api_status.text)
                status_power = int(self.status['power'])
        
                if status_power == 0:
                    self.log.info('Kuki DEVICE IS SLEEPing')
                    status_power = 'OFF'

                else: 
                    status_playing = self.status['playing']
                    status_volume = int(self.status['audio']['volume'])
                    status_power = 'ON'

# status of prefered device of volume
def status_volume_check(self):

        global status_volume # for saving volume

        self.log.error("DEBUG VOLUME STATUS")
        
        if status_volume == "":     # if volume is not set
            self.log.info("DEBUG VOLUME is not set")
            status_device(self)     # reload status of device

        else:
            self.log.info("DEBUG VOLUME if cached")


def init(self):
        """ initialize first start """
        self.log.error("DEBUG INITIALIZE")
        
        if sernum == "":
            self.log.error(sernum)
            self.log.error("SERIAL not found - reading from file")
            serial(self)

        else:
            self.log.error(sernum)
            self.log.info("SERIAL FOUND - use cache")       

        if session == "":
            self.log.error("SESSION not found - create new")
            kuki_reg(self)
           
        else:
            self.log.info("SESSION FOUND - use cache")
        
        if devices == "":
            self.log.error("DEVICES not found - search for new")
            kuki_devices(self)
           
        else:
            self.log.info("DEVICES FOUND - use cache")

        if prefered_device == "":
            self.log.error("PREFERED DEVICE not found - choose new")
            prefered_device(self)
          
        else:
            self.log.info("PREFERED DEVICE FOUND - use cache")
        
        if prefered_device_id == "":
            self.log.error("PREFERED DEVICE ID not found - choose new")
            prefered_device(self)
          
        else:
            self.log.info("PREFERED DEVICE FOUND ID - use cache")



  # ============================ Mycroft STARTs ============================ #


class KukiSkill(MycroftSkill):
    """Kuki control through the Kuki API."""    

    @intent_handler(IntentBuilder('').require('Show').require('Kuki').require('Device'))
    def list_devices(self, message):
        """ List available devices. """
        self.log.debug("DEBUG voice LIST DEVICES")

        init(self)
           
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
        
        self.log.error("DEBUG STATUS")

        init(self)
        status_device(self)

        if status_power == "OFF":
            self.speak_dialog('PowerOff')

        else:
            self.speak_dialog('WakeUp')
            # TODO stats of playing and volume 


    # power ON
    @intent_handler(IntentBuilder('').require('PowerOn'))
    def power_on_intent(self, message):
       
        self.log.error("DEBUG POWER ON")

        init(self) 
            
        # API POST data
        self.api_headers = {'X-SessionKey': session} 
        self.api_post = {'action':"poweron"}

        # sending post request and saving response as response object
        self.api_remote = requests.post(url = API_REMOTE_URL + prefered_device_id, headers = self.api_headers, data = self.api_post)
        self.speak_dialog('PowerOn')

   
    # power OFF
    @intent_handler(IntentBuilder('').require('PowerOff'))
    def power_off_intent(self, message):
       
        self.log.error("DEBUG POWER OFF")

        init(self) 
            
        # API POST data
        self.api_headers = {'X-SessionKey': session} 
        self.api_post = {'action':"poweroff"}

        # sending post request and saving response as response object
        self.api_remote = requests.post(url = API_REMOTE_URL + prefered_device_id, headers = self.api_headers, data = self.api_post)
        self.speak_dialog('PowerOff')
    

    # testing playing tv intent
    @intent_handler(IntentBuilder('').require('Play'))
    def play_intent(self, message):
        self.speak_dialog("Play")
  
  
    # volume UP
    @intent_handler(IntentBuilder('').require('VolumeUp'))
    def volume_up_intent(self, message):

        global status_volume    # need for writing status of volume
        
        self.log.error("DEBUG VOLUME UP")

        init(self) 
        status_volume_check(self)
   
        if status_volume == "100":    # if volume is more than 100% - TODO 2 REFACTOR
            self.log.info("DEBUG VOLUME IS TOO HIGH more than 100")
            self.speak_dialog('VolumeMax')

        else:
            self.log.info("DEBUG VOLUME IS OK between 0 and 100")
            # API POST data
            self.api_headers = {'X-SessionKey': session} 
            self.action = "volset"
            self.volume = str(int(status_volume) + 20)      # TODO - maximum 100
        
            self.log.info("SET VOLUME TO")
            self.log.info(self.volume)
        
            status_volume = self.volume     # save volume
        
            # data to be sent to api 
            self.api_post = {'action':self.action,
                            'volume': self.volume}

            # sending post request and saving response as response object
            self.api_remote = requests.post(url = API_REMOTE_URL + prefered_device_id, headers = self.api_headers, data = self.api_post)
            self.speak_dialog('VolumeUp')


    # volume DOWN
    @intent_handler(IntentBuilder('').require('VolumeDown'))
    def volume_down_intent(self, message):

        global status_volume    # need for writing status of volume
        
        self.log.error("DEBUG VOLUME DOWN")

        init(self) 
        status_volume_check(self)
        
        if status_volume == "0":    # if volume is less than 0% - TODO 2 REFACTOR
            self.log.info("DEBUG VOLUME IS TOO LOW less than 0")
            self.speak_dialog('VolumeMin')

        else:
            self.log.info("DEBUG VOLUME IS OK between 0 and 100")
            # API POST data
            self.api_headers = {'X-SessionKey': session} 
            self.action = "volset"
            self.volume = str(int(status_volume) - 20)      # TODO - maximum 100
        
            self.log.info("SET VOLUME TO")
            self.log.info(self.volume)
        
            status_volume = self.volume     # save volume
        
            # data to be sent to api 
            self.api_post = {'action':self.action,
                            'volume': self.volume}

            # sending post request and saving response as response object
            self.api_remote = requests.post(url = API_REMOTE_URL + prefered_device_id, headers = self.api_headers, data = self.api_post)
            self.speak_dialog('VolumeDown')


 # channel UP
    @intent_handler(IntentBuilder('').require('ChannelUp'))
    def channel_up_intent(self, message):
       
        self.log.error("DEBUG CHANNEL UP")

        init(self) 
            
        # API POST data
        self.api_headers = {'X-SessionKey': session} 
        self.api_post = {'action':"chup"}

        # sending post request and saving response as response object
        self.api_remote = requests.post(url = API_REMOTE_URL + prefered_device_id, headers = self.api_headers, data = self.api_post)
        self.speak_dialog('ChannelUp')


# channel Down
    @intent_handler(IntentBuilder('').require('ChannelDown'))
    def channel_down_intent(self, message):
       
        self.log.error("DEBUG CHANNEL DOWN")

        init(self) 
            
        # API POST data
        self.api_headers = {'X-SessionKey': session} 
        self.api_post = {'action':"chdown"}

        # sending post request and saving response as response object
        self.api_remote = requests.post(url = API_REMOTE_URL + prefered_device_id, headers = self.api_headers, data = self.api_post)
        self.speak_dialog('ChannelDown')


    # play live tv
    @intent_handler(IntentBuilder('').require('PlayLive'))
    def live_intent(self, message):  

        self.log.error("DEBUG PLAY LIVE")

        init(self)
        status_device(self)

        if status_power == "OFF":
            
            # WAKE UP
            self.api_headers = {'X-SessionKey': session} 
            self.api_post = {'action':"poweron"}

            # sending post request and saving response as response object
            self.api_remote = requests.post(url = API_REMOTE_URL + prefered_device_id, headers = self.api_headers, data = self.api_post)
            self.speak_dialog('PowerOn')

            # PLAY LIVE
            self.action = "playLive"
            self.op = "play"
            self.type = "live"
            self.channel = "1";
        
            # data to be sent to api 
            self.api_post = {'action':self.action,
                             'op': self.op,
                             'type':self.type,
                             'channel_id': self.channel}

            # sending post request and saving response as response object
            self.api_remote = requests.post(url = API_REMOTE_URL + prefered_device_id, headers = self.api_headers, data = self.api_post)
            self.speak_dialog('PlayLive')


        else:
            # API POST data
            self.api_headers = {'X-SessionKey': session}
            self.action = "playLive"
            self.op = "play"
            self.type = "live"
            self.channel = "1";
        
            # data to be sent to api 
            self.api_post = {'action':self.action,
                             'op': self.op,
                             'type':self.type,
                             'channel_id': self.channel}

            # sending post request and saving response as response object
            self.api_remote = requests.post(url = API_REMOTE_URL + prefered_device_id, headers = self.api_headers, data = self.api_post)
            self.speak_dialog('PlayLive')



    def stop(self):
        pass

def create_skill():
    return KukiSkill()


    
