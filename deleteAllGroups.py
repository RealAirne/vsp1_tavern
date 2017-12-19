import requests
from requests.auth import HTTPBasicAuth
import time


CREDENTIALS = "Jaume"

i = 1

while i < 1000:
    response = requests.delete("http://172.19.0.7:5000/taverna/groups/" + str(i), auth=HTTPBasicAuth(CREDENTIALS, CREDENTIALS))
    print(response.status_code)
    time.sleep(1)
    i = i+1

