from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_file_handler, intent_handler

import requests                                                         # http post & get
import json                                                             # json :-)
import uuid                                                             # mac
import socket                                                           # hostname
import random                                                           # generate serial
import string                                                           # generate serial                                      
from mycroft.filesystem import FileSystemAccess                         # file operation
from mycroft.util.parse import extract_datetime, extract_number, extract_duration         # read numbers
import sys                                                              # exit app
import re                                                               # clean alias from numbers, etc
from datetime import datetime, timezone                                 # for video seeking


#API_URL = "https://as.kukacka.netbox.cz/api-v2/"
API_URL = "https://as.kuki.cz/api-v2/"

#API_REMOTE_URL =  "https://as.kukacka.netbox.cz/api/remote/"
API_REMOTE_URL = "https://as.kuki.cz/api/remote/"

#API_REMOTE_STATE_URL =  "https://as.kukacka.netbox.cz/api/device-state/"
API_REMOTE_STATE_URL = "https://as.kuki.cz/api/device-state/"

#API_CHANNEL_URL = "https://aas.kukacka.netbox.cz/channel-list"
API_CHANNEL_URL = "https://as.kuki.cz/api-v2/channel-list"


sernum = ''                 # uniq serial number
session = ''                # token 
registration = ''           # paired to the Kuki servers 
paircode = ''               # code for registration
devices = ''                # all devices
preferred_device = ''       # alias
preferred_device_id = ''    # id
status_power = ''           # power of end device
status_playing = ''         # state of device
status_volume = ''          # volume of device
channel_play = ''           # ID of tv channel
time_actual = ''            # actual postition in timeshift
channel_list = ''           # list of all channels on contract


def failed_auth(self):
    self.speak_dialog("not.authorized", data={"paircode": paircode})
    sys.exit()  # program end

def generate_serial(StringLength=56):
    """Generate a random string of letters and digits """

    global sernum       # save serial number
    
    LettersAndDigits = string.ascii_letters + string.digits
    sernum = "kuki2.0_" + ''.join(random.choice(LettersAndDigits) for i in range(StringLength))
    return sernum


def serial(self):

    global sernum       # save serial number

    try:
        self.log.info("READING SERIAL NUMBER") 
        file_system = FileSystemAccess(str("skills/KukiSkill/"))
        file = file_system.open("kuki.serial", mode="r")
        data = file.read()
        file.close()
        
        sernum = data   # save data to sernum
        self.log.info("SERIAL: " + sernum) 
        return sernum

    except Exception as e:
        self.log.error("SERIAL NOT READ FROM FILE")
        self.log.error(e)
        #return False    

        self.log.info("GENERATING NEW SERIAL NUMBER AND SAVE") 
        generate_serial(StringLength=56)   # generate new serial number and save
        self.log.info("SERIAL: " + sernum) 

        try:           
            file_system = FileSystemAccess(str("skills/KukiSkill/"))
            file = file_system.open("kuki.serial", mode="w")
            file.write(sernum)
            file.close()
            return True
    
        except Exception as e:
            self.log.error("SERIAL NOT SAVE TO FILE")
            self.log.error(e)
            return False    
        

def kuki_reg(self):
        global session       # cache session
        global paircode      # paircode 

        """ registration and session key """
        self.log.debug("DEBUG REGISTER")

        #self.serial = sernum
        self.deviceType = "mobile"
        self.deviceModel = (socket.gethostname())
        self.product_name = "Mycroft"
        self.mac = (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
                   for ele in range(0,8*6,8)][::-1])) 
        self.bootMode = "unknown"

        # data to be sent to api 
        self.api_data = {'sn':sernum,
                        'device_type':self.deviceType,
                        'device_model':self.deviceModel, 
                        'product_name':self.product_name,
                        'mac':self.mac,
                        'boot_mode':self.bootMode,
                        'claimed_device_id':sernum}

        # sending post request and saving response as response object      
 
        api_post = requests.post(url = API_URL + 'register' , data = self.api_data)


        if json.loads(api_post.text)['state'] == 'NOT_REGISTERED':

            self.result = api_post.json()
            self.log.error('Kuki device is NOT REGISTERED try URL and pair code bellow:')
            self.log.error(self.result['registration_url_web'])
            
            paircode = self.result['reg_token']     # save pair code
            
            return failed_auth(self)

        else:
            if json.loads(api_post.text)['state'] != 'NOT_REGISTERED':
                self.log.info('Kuki device is REGISTERED')
                
                session = json.loads(api_post.text)['session_key']     # save token
        
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
        try:
            devices = list(map(lambda item: item['alias'], filter(lambda item: item['canPlay'] and item['deviceType'] in ['smarttv', 'fix'], self.result)))
        
        except:
            self.log.error("ERROR IN LOAD STATE")
        
        return init(self)


def preferred_dev(self):
        """ select of of many Kuki devices from contract """
        global preferred_device #cache preferred device alias
        global preferred_device_id #cache preferred device id

        self.log.debug("DEBUG PREFERRED DEVICES")   
        
        default_device = self.settings.get('default_device')    # load setting from Mycroft backend
        
        if default_device not in self.settings:
            self.log.error("NO DEFAULT DEVICE SELECED in Mycroft settings")

            self.log.debug(devices)
            preferred_device = devices[0]    # choose frist device from list
            self.log.info(preferred_device)

            # API get - get id from preferred alias
            self.api_headers = {'X-SessionKey': session}  
            self.api_get = requests.get(API_URL + 'device', headers = self.api_headers) # show all devices on contract
            self.result = json.loads(self.api_get.text)
            preferred_device_id = str(list(filter(lambda item: item['alias'] == preferred_device, self.result))[0]['id']) # select preferred device

            self.log.debug("DEFAULT DEVICE ID")
            self.log.debug(preferred_device_id)

            return init(self)
        
        else:
            self.log.info("DEFAULT DEVICE SELECED from Mycroft settings")
            self.log.info(default_device)
            preferred_device = default_device    # save default device like preferred           
           
            # API get - get all devices
            self.api_headers = {'X-SessionKey': session}  
            self.api_get = requests.get(API_URL + 'device', headers = self.api_headers) # show all devices on contract
            self.result = json.loads(self.api_get.text)
            
            try:
                # select alias from setting - default device
                preferred_device_id = str(list(filter(lambda item: item['alias'] == default_device, self.result))[0]['id']) # select default device
                self.log.debug("DEFAULT DEVICE ID")
                self.log.debug(preferred_device_id)
                return init(self)

            except IndexError:
                self.log.error("DEVICE " + default_device + " NOT FOUND")        
                self.speak_dialog('preferred.device.not.found', data={'named': default_device})
                sys.exit()   # program end


# status of preferred device
def status_device(self):
        
        global status_power     # power of end device
        global status_playing   # state of device
        global status_volume    # volume of device
        global time_actual      # time position of video
        global channel_play     # id of playing channel

        self.log.debug("DEBUG STATUS OF PREFERRED DEVICE")
        
        # API GET
        self.api_status = requests.get(API_REMOTE_STATE_URL + preferred_device_id + ".json", headers = self.api_headers)
        
        if self.api_status:
   
            try:
                self.status = json.loads(self.api_status.text)

            except:
                self.log.error("KUKI PREFFERED DEVICE IS POWER DOWN")
                status_power = 'POWERDOWN'
                self.speak_dialog('power.down')

            else:
                self.log.debug("KUKI DEVICE IS POWER ON - reading settings")
                self.status = json.loads(self.api_status.text)
                status_power = int(self.status['power'])
        
                if status_power == 0:
                    self.log.debug("KUKI DEVICE IS SLEEPING")
                    status_power = 'OFF'                                                        # save power state
                    self.speak_dialog('power.off')

                else:
                    self.log.debug("KUKI DEVICE IS AWAKE")

                    try:
                        status_playing = self.status['playing']                                  # read data from device
                        status_volume = int(self.status['audio']['volume'])
                        time_actual = int(self.status['player']['position'] / 1000)              # platform have a miliecond
                        channel_play = int(self.status['player']['nowplaying']['channelId'])
                        status_power = 'ON'                                                      # save power state
                    
                    except:
                        self.log.error("KUKI DEVICE NOT PLAYING - skip data read")
                        return "NOPLAY"


# power ON
def power_on(self):  
        
        global status_power 
        
        self.log.debug("DEBUG POWER ON")

        status_device(self)

        if status_power == "OFF":
            self.log.info("TRYING TO WAKEUP")  
            self.api_headers = {'X-SessionKey': session} 
            self.api_post = {'action':"poweron"}
            self.api_remote = requests.post(url = API_REMOTE_URL + preferred_device_id, headers = self.api_headers, data = self.api_post)
            status_power = 'ON' 

        else:
            self.log.info("DEVICE IS ALREADY WAKEUP")  


def init(self):
        """ initialize all data for perfect work """
        self.log.info("KUKI INITIALIZE")
        
        if sernum == "":
            self.log.info("SERIAL not found - reading from device")
            serial(self)
        else:
            self.log.debug("SERIAL found")


        if session == "":
            self.log.info("SESSION not found - create new")
            kuki_reg(self)       
        else:
            self.log.debug("SESSION found")


        if devices == "":
            self.log.info("DEVICES not found - looking for new")
            kuki_devices(self)       
        else:
            self.log.debug("DEVICES found")


        if preferred_device == "":
            self.log.info("PREFERRED DEVICE not found - choose new")
            preferred_dev(self)        
        else:
            self.log.debug("PREFERRED DEVICE found")

        
        if preferred_device_id == "":
            self.log.info("PREFERRED DEVICE ID not found - choose new")
            preferred_device(self)       
        else:
            self.log.debug("PREFERRED DEVICE ID found")


  # ============================ Mycroft STARTs ============================ #


class KukiSkill(MycroftSkill):
    """Kuki control through the Kuki API."""    


    # how to register Kuki device
    @intent_handler(IntentBuilder('HowToRegister.intent').require('HowTo').require('Register').optionally('New').optionally('Kuki').optionally('Device'))
    def howto_register_intent(self):
    
        self.speak_dialog('how.to.register')


    # show Kuki device connected on contract
    @intent_handler(IntentBuilder('ListOfDevices.intent').require('Show').require('Kuki').require('Device'))
    def list_devices_intent(self):
        """ List available devices. """
        self.log.debug("DEBUG LIST OF KUKI DEVICES")

        init(self)
        kuki_devices(self)
           
        if len(devices) == 1:
            self.speak(devices[0])

        elif len(devices) > 1:
            self.speak_dialog('available.devices',
                                {'devices': ' '.join(devices[:-1]) + ' ' +
                                            self.translate('and') + ' ' +
                                            devices[-1]})
        else:
            self.log.debug("DEBUG NO DEVICE AVAILABLE")
            self.speak_dialog('no.devices.available')


    # what is preferred device
    @intent_handler(IntentBuilder('ShowPreferredDevice.intent').require('Show').optionally('Kuki').require('Preferred').optionally('Device'))
    def preferred_device_intent(self, message):
        
        self.log.debug("DEBUG WHAT IS PREFERRED DEVICE")

        init(self)

        self.speak_dialog('preferred.device', data={'named': preferred_device})


    # change preferred device
    @intent_handler(IntentBuilder('ChangePreferredDevice.intent').require('Change').optionally('Kuki').require('Preferred').optionally('Device'))
    def change_device_intent(self, message):
        
        global preferred_device

        self.log.debug("DEBUG CHANGE preferred DEVICE")

        init(self)

        devices_list = list(enumerate(devices))                                         # generate list of aliases and numbers

        self.speak_dialog('available.devices', data={'devices': devices_list})
        
        try:
            preferred_device_id = self.get_response('select.device.number')             # choice number of preferred aliases
            preferred_device_id = int(preferred_device_id)
        
            preferred_alias = str(devices_list[preferred_device_id])                    # from number extract alias
            preferred_device = " ".join(re.findall("[a-zA-Z]+", preferred_alias))       # clean alias from numbers and characters and save to global variables

            self.settings['default_device'] = preferred_device                          # save preferred device as default to settings (setting will persist until a new setting is assigned locally by the Skill, or remotely by the user clicking save on the web view.)
        
            self.speak_dialog('preferred.device', data={'named': preferred_device})
           
        except:
            self.log.error("NUMBER ERROR")
            self.speak_dialog('no.device.number.found', data={'device_number': preferred_device_id})
        

    # status of device
    @intent_handler(IntentBuilder('StatusOfDevice.intent').optionally('Show').optionally('Kuki').require('Device').require('Status'))
    def status_intent(self, message):
        
        self.log.debug("DEBUG STATUS OF DEVICE")

        init(self)
        status_device(self)

        if status_power == "POWERDOWN":
            self.log.error("DEVICE IS POWERDOWN")

        elif status_power == "OFF":
            self.log.error("DEVICE IS OFF")

        else:
            self.api_headers = {'X-SessionKey': session}
            self.api_get = requests.get(API_CHANNEL_URL, headers = self.api_headers)        # load all channels on contract

            self.result = json.loads(self.api_get.content.decode())                         # get name from id
            
            try:
                channel_list = {}
                for ch in self.result:
                    channel_list[ch['id']] = ch['name']
            except:
                self.log.error("ERROR IN CHANNEL LIST")


            if status_playing == 1:
                channel_name = channel_list[channel_play] 
                self.speak_dialog('status.play.of.kuki.device', data={'named': preferred_device, 'channel': channel_name, 'volume': status_volume})

            else:
                self.speak_dialog('status.noplay.of.kuki.device', data={'named': preferred_device})


    # power ON
    @intent_handler(IntentBuilder('PowerOn.intent').require('PowerOn').require('Kuki').optionally('Device'))
    def power_on_intent(self, message):
       
        self.log.error("DEBUG POWER ON")

        init(self)
        power_on(self)

        if status_power == "ON":
            self.speak_dialog('power.on')

   
    # power OFF
    @intent_handler(IntentBuilder('PowerOff.intent').require('PowerOff').require('Kuki').optionally('Device'))
    def power_off_intent(self, message):
       
        global status_power

        self.log.debug("DEBUG POWER OFF")

        init(self) 
            
        # API POST data
        self.api_headers = {'X-SessionKey': session} 
        self.api_post = {'action': "poweroff"}
        self.api_remote = requests.post(url = API_REMOTE_URL + preferred_device_id, headers = self.api_headers, data = self.api_post)
        
        status_power = 'OFF'

        self.speak_dialog('power.off')
 
  
    # play live tv
    @intent_handler('play.live.intent')
    def live_intent(self, message):  

        self.log.error("DEBUG PLAY LIVE")

        init(self)
        power_on(self)

        if status_power == "ON":
            # API POST data
            self.api_headers = {'X-SessionKey': session} 
            self.api_post = {'action':"playLive",
                             'channel_id': 1,
                             'type':"live"}

            # sending post request and saving response as response object
            self.api_remote = requests.post(url = API_REMOTE_URL + preferred_device_id, headers = self.api_headers, data = self.api_post)
            self.speak_dialog('play.live')


    # play channel number
    @intent_handler(IntentBuilder('PlayChannel.intent').require('Play').optionally('To').require("Number").require("Numbers"))
    def play_channel_intent(self, message):
   
        init(self)
        power_on(self)

        if status_power == "ON":
            self.log.error("DEBUG SET CHANNEL NUMBER")

            channel_number = extract_number(message.data['utterance'])
            channel_number = int(channel_number)
        
            # we have data from numbers
            self.api_headers = {'X-SessionKey': session} 
            self.api_post = {'action':"playChannelByNumber",
                             'key': channel_number}

            self.api_remote = requests.post(url = API_REMOTE_URL + preferred_device_id, headers = self.api_headers, data = self.api_post)
            self.speak_dialog('set.channel.number', data={'channel_number': channel_number})
   

    # play from channel list
    @intent_handler('play.channel.intent')
    def channel_list_intent(self, message):

        global channel_list

        init(self)
        power_on(self)

        if status_power == "ON":
            self.log.debug("DEBUG CHANNEL LIST")

            channel_name = message.data.get('channels')                                     # extract channel name

            # API get
            self.api_headers = {'X-SessionKey': session}
            self.api_get = requests.get(API_CHANNEL_URL, headers = self.api_headers)        # load all channels on contract

            self.result = json.loads(self.api_get.content.decode())                         # decoding name and id from list of channels
        
            channel_list = {}
            for ch in self.result:
                channel_list[ch['name']] = ch['id']
        
            channel_list_lower_case =  {k.lower(): v for k, v in channel_list.items()}      # all channel names to lower case

            try:
                channel_id = channel_list_lower_case[channel_name]                          # select channel_id from channel_list by utterance name

                # API POST data
                self.api_post = {'action':"playLive",
                                 'channel_id': channel_id,
                                 'type':"live"}

                self.api_remote = requests.post(url = API_REMOTE_URL + preferred_device_id, headers = self.api_headers, data = self.api_post)
                self.speak_dialog('channel.play', data={'channel_name': channel_name})

            except KeyError:
                self.speak_dialog('channel.not.found', data={'channel_name': channel_name})


    # channel UP
    @intent_handler(IntentBuilder('ChannelUp.intent').optionally('Play').require('Channel').require('Up'))
    def channel_up_intent(self, message):

        init(self) 
        power_on(self)

        if status_power == "ON":
            self.log.debug("DEBUG CHANNEL UP")
            
            # API POST data
            self.api_headers = {'X-SessionKey': session} 
            self.api_post = {'action':"chup"}

            # sending post request and saving response as response object
            self.api_remote = requests.post(url = API_REMOTE_URL + preferred_device_id, headers = self.api_headers, data = self.api_post)


    # channel DOWN
    @intent_handler(IntentBuilder('ChannelDown.intent').optionally('Play').require('Channel').require('Down'))
    def channel_down_intent(self, message):

        init(self)
        power_on(self)

        if status_power == "ON":
            self.log.debug("DEBUG CHANNEL DOWN")
            
            # API POST data
            self.api_headers = {'X-SessionKey': session} 
            self.api_post = {'action':"chdown"}

            # sending post request and saving response as response object
            self.api_remote = requests.post(url = API_REMOTE_URL + preferred_device_id, headers = self.api_headers, data = self.api_post)


    # seeking
    @intent_handler('seek.intent')
    def seek_intent(self, message):

        global time_actual

        init(self)
        power_on(self)                                          # TODO solve API delay in fast seeking                                        

        if status_power == "ON":
            self.log.debug("DEBUG CHANNEL SEEK")                  

            if status_device(self) == "NOPLAY":
                self.log.info("KUKI IS NOT PLAYING ANY VIDEO")
                self.speak_dialog('shifting.no.play')
                sys.exit()                                      # TODO need refactor

            # check where actual video time is
            time_now = datetime.now().timestamp()               # actual time in UTC

            if time_actual == "":
                time_actual = time_now - 5                      # set actual time right now minus 5 sec (one chunk protection)
                self.log.debug("USE UTC TIME")
        
            else:
                if time_actual / 1000 > time_now:
                    time_actual = time_now - 5
                    self.log.debug("BACK FROM FUTURE")

                else:
                    actual_time_position = datetime.fromtimestamp(time_actual)
                    self.log.debug("USE ACTUAL TIME POSITION")

            # check if duration of datetime is present
            duration = message.data.get('duration')
            date_or_time = message.data.get('datetime')

            if duration is not None:
                self.log.debug("DURATION FOUND")
                move = extract_duration(message.data["utterance"])[1]       # seek direction
                duration = duration.replace("-", " ")                       # some STT engines return "5-minutes" not "5 minutes"
                time = extract_duration(duration)[0]                        # seek duration in seconds
                time_clean = int(time.seconds)                              # duration like integer

                # words of seek direction. TODO need refactor to detect locales and read data from localized files, self.lang etc.
                self.move_word = {
                              'zpět': "zpět",
                              'nazpět': "zpět",
                              'zpátky': "zpět",
                              'dozadu': "zpět",
                              'vrátit': "zpět",
                              'dopředu': "dopředu",
                              'vpřed': "dopředu",
                              'back': "back",
                              'rewind': "back",
                              'forward': "forward",
                              'fast forward': "forward",
                              'ahead': "forward"}

                move_direction = self.move_word[move]   # select move from word
 
                if move_direction == "zpět" or "back":
                    self.log.debug("SEEK BACK")
                    time_position = time_actual - time_clean


                elif move_direction == "dopředu" or "forward":
                    self.log.debug("SEEK FORWARD")
                    time_position = time_actual + time_clean
                
                else:
                    self.log.error("ERROR IN SEEKING")
                    sys.exit() 


            elif date_or_time is not None:
                self.log.info("DATETIME FOUND")

                when = message.data.get('utterance').lower()
                when = extract_datetime(when)[0]
                time_position = datetime.timestamp(when)
                move_direction = ''
        
            else:
                self.log.error("SEEK DATA NOT FOUND")
                sys.exit()

        
            #API POST
            self.api_headers = {'X-SessionKey': session} 
            self.api_post = {'action':"seek",
                             'position': time_position * 1000}   # Kuki platform needs milisecond

            self.api_remote = requests.post(url = API_REMOTE_URL + preferred_device_id, headers = self.api_headers, data = self.api_post)
        
            self.speak_dialog('shifting', data={'move': move_direction})


    # volume SET percent
    @intent_handler(IntentBuilder('SetVolume.intent').optionally("Set").require("Kuki").require("Volume").optionally("To").require("VolumeNumbers").optionally("Percent"))
    
    def handle_set_volume_percent_intent(self, message):
        
        global status_volume

        init(self)
        power_on(self)

        if status_power == "ON":
            self.log.debug("DEBUG VOLUME PERCENT")

            self.volume_words = {                           # need to refactor to support locales
                            'max': 100,
                            'maximum': 100,
                            'loud': 90,
                            'normal': 60,
                            'medium': 50,
                            'quiet': 30,
                            'mute': 0,
                            'zero': 0,
                            'nahlas': 90,
                            'normalně': 60,
                            'střed': 50,
                            'středně': 50,
                            'ticho': 30,
                            'potichu': 30,
                            'ztlumit': 0,
                            'nula': 0}

            default = None
            level_word = message.data.get('VolumeNumbers', default)
            
            try:    # try use word
                percent = self.volume_words[level_word]
        
            except KeyError:    # if error try numbers
                percent = extract_number(message.data['utterance'].replace('%', ''))
                percent = int(percent)
        
            # we have data from worlds or numbers
            self.api_headers = {'X-SessionKey': session} 

            # data to be sent to api 
            self.api_post = {'action':"volset",
                             'volume': percent}

            # sending post request and saving response as response object
            self.api_remote = requests.post(url = API_REMOTE_URL + preferred_device_id, headers = self.api_headers, data = self.api_post)
            self.speak_dialog('set.volume.percent', data={'level': percent})
            status_volume = percent
   

    # volume UP
    @intent_handler(IntentBuilder('VolumeUp.intent').require('Kuki').optionally('Volume').require('Up'))
    def volume_up_intent(self, message):

        global status_volume

        init(self)
        power_on(self)

        if status_power == "ON":
            self.log.debug("DEBUG VOLUME UP")
        
            if status_volume == "":
                status_device(self)     # reload status of device
            else:
                self.log.debug("USING CACHE VOLUME STATUS")    

            if status_volume == 100:
                status_volume = 100
                self.log.info("DEBUG VOLUME IS TOO HIGH")
                self.speak_dialog('volume.max')
                sys.exit()
        
            else:
                status_volume = status_volume + 10

                # API POST data
                self.api_headers = {'X-SessionKey': session} 
                self.api_post = {'action':"volup"}
      
                self.api_remote = requests.post(url = API_REMOTE_URL + preferred_device_id, headers = self.api_headers, data = self.api_post)
                self.speak_dialog('volume.up')


    # volume DOWN
    @intent_handler(IntentBuilder('VolumeDown.intent').require('Kuki').optionally('Volume').require('Down'))
    def volume_down_intent(self, message):

        global status_volume

        init(self)
        power_on(self)

        if status_power == "ON":
            self.log.debug("DEBUG VOLUME DOWN")

            if status_volume == "":
                status_device(self)     # reload status of device
            else:
                self.log.debug("USING CACHE VOLUME STATUS")  
        
            if status_volume == 0:
                status_volume = 0
                self.log.info("DEBUG VOLUME IS TOO LOW")
                self.speak_dialog('volume.min')
                sys.exit()
        
            else:
                status_volume = status_volume - 10

                # API POST data
                self.api_headers = {'X-SessionKey': session} 
                self.api_post = {'action':"voldown"}
        
                self.api_remote = requests.post(url = API_REMOTE_URL + preferred_device_id, headers = self.api_headers, data = self.api_post)
                self.speak_dialog('volume.down')


    def stop(self):
        pass

def create_skill():
    return KukiSkill()


    
