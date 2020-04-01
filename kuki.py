""" A simple Python library for the Kuki Web API """

# importing the requests library 
import requests                       # http post & get
import json                           # json :-)
import uuid                           # mac
import socket                         # hostname
import random                         # generate serial
import string                         # generate serial

from mycroft.api import DeviceApi     # testing
from mycroft.util.log import LOG      # testing
import time                           # testing


# defining the api-endpoint  
#API_URL = "https://as.kukacka.netbox.cz/api-v2/"

def get_token(dev_cred):
    retry = False
    try:
 #       d = DeviceApi().get_oauth_token(dev_cred)
         d = requests.get(url = API_URL, params = "/device")


    except HTTPError as e:
        if e.response.status_code == 404:  # Token doesn't exist
            raise
        if e.response.status_code == 401:  # Device isn't paired
            raise
        else:
            retry = True
    if retry:
        d = DeviceApi().get_oauth_token(dev_cred)
    return d


class MycroftKukiAuth(object):
    """ Credentials object renewing through the Mycroft backend."""
    def __init__(self, dev_cred):
        self.dev_cred = dev_cred
        self.access_token = None
        self.expiration_time = None
        self.get_access_token()

    def get_access_token(self, force=False):
        if (not self.access_token or time.time() > self.expiration_time or
                force):
            d = get_token(self.dev_cred)
            self.access_token = d['access_token']
            # get expiration time from message, if missing assume 1 hour
            self.expiration_time = d.get('expiration') or time.time() + 3600
        return self.access_token


class KukiConnect(MycroftKukiAuth):
    """ Implement the Kuki Connect API """


    def GenerateSerial(StringLength=56):
        """Generate a random string of letters and digits """
        LettersAndDigits = string.ascii_letters + string.digits
        return "kuki2.0_" + ''.join(random.choice(LettersAndDigits) for i in range(StringLength))


#    @refresh_auth
    def get_session(self):

        # api call
        #serial = GenerateSerial(56)
        self.get_session_token()
        self.serial = "Manas_test_12345678"
        self.deviceType = "mobile"
        self.deviceModel = (socket.gethostname())
        self.product_name = "MyCroft"
        self.mac = (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
             	   for ele in range(0,8*6,8)][::-1])) 
        #versionVw = "1.0"
        #versionPortal = "2.0.14"
        self.bootMode = "unknown"

        # data to be sent to api 
        self.api_post = {'sn':self.serial,
                    	'device_type':self.deviceType,
                    	'device_model':self.deviceModel, 
                   		'product_name':self.product_name,
                    	'mac':seld.mac,
#                   'version_fw':versionVw,
#                   'version_portal':versionPortal,
                   		 'boot_mode':self.bootMode,
                   		 'claimed_device_id':self.serial}

# sending post request and saving response as response object 
        self.api_response = requests.post(url = API_URL + 'register' , data = self.api_post) 

        if json.loads(self.api_response.text)['state'] == 'NOT_REGISTERED':
            self.log.info('NOT REGISTERED')
#            print("NOT REGISTERED")
            self.esult = self.api_response.json()
            self.log.info(self.result['registration_url_web'])
            self.log.info(self.result['reg_token'])
 #           print("Registracni odkaz pro parovani:",result ['registration_url_web'])
 #           print("Parovaci kod:",result['reg_token'])
        else:
             if json.loads(self.api_response.text)['state'] != 'NOT_REGISTERED':
          		  self.log.info('REGISTERED')
#                  print("REGISTERED")
 #                 result = api_response.json()                  
#                  print("Session key:",result['session_key'])
                  self.session = json.loads(api_response.text)['session_key']
	       		  self.log.info(result['session_key'])
                  return self.session
    

#s = requests.Session()
#s.auth = ('user', 'pass')
#s.headers.update({'x-test': 'true'})

# both 'x-test' and 'x-test2' are sent
#s.get('https://as.kukacka.netbox.cz/api-v2/devices', headers={'x-test2': 'true'})

#print (s)


  #  print(d) 

#        try:
#            # TODO: Cache for a brief time
#            devices = self._get('me/player/devices')['devices']
#            return devices
#        except Exception as e:
#            LOG.error(e)

#d = requests.get(url = API_URL, header = self.get_devices")
#print(self.get_devices)
#print(d)









