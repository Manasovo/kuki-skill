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
API_URL = "https://as.kukacka.netbox.cz/api-v2/"

def get_token(dev_cred):
    retry = False
    try:
 #       d = DeviceApi().get_oauth_token(dev_cred)
         d = requests.get(url = API_URL, params = PARAMS) 

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


class KukiConnect(MycroftSkill):
    """ Implement the Kuki Connect API """

    @refresh_auth
    def get_devices(self):
        """ Get a list of Kuki devices from the API.

        Returns:
            list of Kuki devices connected to the user.
        """
        try:
            # TODO: Cache for a brief time
            devices = self._get('me/player/devices')['devices']
            return devices
        except Exception as e:
            LOG.error(e)


def GenerateSerial(StringLength=56):
    """Generate a random string of letters and digits """
    LettersAndDigits = string.ascii_letters + string.digits
    return "kuki2.0_" + ''.join(random.choice(LettersAndDigits) for i in range(StringLength))


















# api call
#serial = GenerateSerial(56)
serial = "Manas_test_12345678"
deviceType = "mobile"
deviceModel = (socket.gethostname())
product_name = "MyCroft"
mac = (':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) 
        for ele in range(0,8*6,8)][::-1])) 
#versionVw = "1.0"
#versionPortal = "2.0.14"
bootMode = "unknown"

# data to be sent to api 
api_post = {'sn':serial,
        'device_type':deviceType,
        'device_model':deviceModel, 
        'product_name':product_name,
        'mac':mac,
#        'version_fw':versionVw,
#        'version_portal':versionPortal,
        'boot_mode':bootMode,
        'claimed_device_id':serial}

# sending post request and saving response as response object 
api_response = requests.post(url = API_URL + 'register' , data = api_post) 

if json.loads(api_response.text)['state'] == 'NOT_REGISTERED':
    print("NOT REGISTERED")
    result = api_response.json()
    print("Registracni odkaz pro parovani:",result ['registration_url_web'])
    print("Parovaci kod:",result['reg_token'])

else:
 
    if json.loads(api_response.text)['state'] != 'NOT_REGISTERED':
      print("REGISTERED")
      result = api_response.json()
      print("Session key:",result['session_key'])
