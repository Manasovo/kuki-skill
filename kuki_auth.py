""" A simple Python library for the Kuki Web API """


# importing the requests library 
import requests
import json

# defining the api-endpoint  
API_URL = "https://as.kukacka.netbox.cz/api-v2/"

serial = "Manas_test_12345678"
deviceType = "mobile"
deviceModel = "PiCroft"
product_name = "MyCroft"
mac = "aa:bb:cc:dd:ee:ff"
versionVw = "1.0"
versionPortal = "2.0.14"
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
   print("BAD")

	#   console.log('Parovaci kod: ', response.reg_token);
	#   console.log('Registracni odkaz pro parovani: ', response.registration_url_web);
else:
	if json.loads(api_response.text)['state'] == 'REGISTERED':
   	   print("OK")

#   console.log('session_key', response.session_key);



#    private generateSerial(): string {
#        const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
#        let serial = 'kuki2.0_';
#        for (let i = 0; i < 56; i++) {
#            serial += possible.charAt(Math.floor(Math.random() * possible.length));
#        }
#        return serial;
#    }
#}
