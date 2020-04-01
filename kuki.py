""" A simple Python library for the Kuki Web API """

# importing the requests library 
import requests                       # http post & get
import json                           # json :-)
import uuid                           # mac
import socket                         # hostname
import random                         # generate serial
import string                         # generate serial


# defining the api-endpoint
self.log.error("DEBUG1")
API_URL = "https://as.kukacka.netbox.cz/api-v2/"


class KukiConnect(object):
      """ Implement the Kuki Connect API """
    self.log.error("DEBUG2")

    def generate_serial(StringLength=56):
    """Generate a random string of letters and digits """
    
        LettersAndDigits = string.ascii_letters + string.digits
        return "kuki2.0_" + ''.join(random.choice(LettersAndDigits) for i in range(StringLength))


def kuki_session(self):
        """ registration and session key """
        self.log.error("DEBUG3")

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
                    	'mac':seld.mac,
                   		'boot_mode':self.bootMode,
                   		'claimed_device_id':self.serial}

        # sending post request and saving response as response object 
        self.api_response = requests.post(url = API_URL + 'register' , data = self.api_post) 

        if json.loads(self.api_response.text)['state'] == 'NOT_REGISTERED':
            self.log.info('NOT REGISTERED')
            self.result = self.api_response.json()
            self.log.info(self.result['registration_url_web'])
            self.log.info(self.result['reg_token'])
        else:
             if json.loads(self.api_response.text)['state'] != 'NOT_REGISTERED':
          		  self.log.info('REGISTERED')

                  self.session = json.loads(api_response.text)['session_key']
	       		  return self.session
    

def kuki_devices(self):
        """ availabla device list from Kuki contract """
        self.log.error("DEBUG4")

        self.api_headers = {'X-SessionKey': self.session}
        self.api_get = requests.get(API_URL + 'device', headers = self.api_headers)

        self.result = json.loads(self.api_get.text)
        return self.result


