""" A simple Python library for the Kuki Web API """

# importing the requests library 
import requests   # http post & get
import json       # json :-)
import uuid       # mac
import socket     # hostname
import random     # generate serial
import string     # generate serial

def GenerateSerial(StringLength=56):
    """Generate a random string of letters and digits """
    LettersAndDigits = string.ascii_letters + string.digits
    return "kuki2.0_" + ''.join(random.choice(LettersAndDigits) for i in range(StringLength))

# defining the api-endpoint  
API_URL = "https://as.kukacka.netbox.cz/api-v2/"

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
