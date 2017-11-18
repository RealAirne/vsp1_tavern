from flask import Flask
import json
import requests
import socket
from requests.auth import HTTPBasicAuth

app = Flask(__name__)


HEADER_APPL_JSON = {'content-type': 'application/json; charset=UTF-8'}

userdata = {'user': 'link to the registered user account',
            'idle': False,
            'group': 'url to the group you are in',
            'hirings': 'uri to which one may post to hire you for a group',
            'assignments': 'uri to which one may post an assignment',
            'messages': 'ri to which one may post messages'
            }


#def get_login_token(user, passw):
 #   response = requests.get(url=DISCOVERED_IP + '/login', auth=HTTPBasicAuth(user, passw))
  #  print(response.content)
   # token = response.json()['token']
    #return token


# GET returns
@app.route('/')
def hello_world():
    json.dumps(userdata)
    return json.dumps(userdata)


# POST delivers heroclass, capabilities, url
def get_ip():
    return '172.19.0.63'


def register_at_tavern():
    print("register at tavern:")
    ip = get_ip()
    #TODO endpoint jaume erstellen
    url = ip + '/jaume'
    json_data = {'heroclass': 'Catalonian Chiller', 'capabilities': '', 'url': '' + url}
    taverna_url = 'http://172.19.0.3:5000/taverna/adventurers'
    response = requests.post(url=taverna_url, headers=HEADER_APPL_JSON, json=json_data)
    print("response (register at tavern)" + repr(response.status_code))
    print("hello")


def discovery():
    UDP_IP = ''
    UDP_PORT = 24000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    # working = True
    buffersize = 1024
    # while working:
    data, addr = sock.recvfrom(buffersize)  # buffer size is 1024 bytes
    print("received message:" + str(data))  # addr ist die discvory address

    port = json.loads(data.decode())

    global DISCOVERED_PORT
    DISCOVERED_PORT = port['blackboard_port']

    sourceip, sourceport = addr

    global BLACKBOARD_IP
    BLACKBOARD_IP = sourceip

    print("adress: " + str(addr))


def main():
    print("HEJEHEHEHEJEHEJEH")
    #discovery()
    #global DISCOVERED_IP
    #DISCOVERED_IP = 'http://' + str(BLACKBOARD_IP) + ':' + str(DISCOVERED_PORT)
    #print(DISCOVERED_IP)
    register_at_tavern()

main()


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
