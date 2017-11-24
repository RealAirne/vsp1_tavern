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


# def get_login_token(user, passw):
#   response = requests.get(url=DISCOVERED_IP + '/login', auth=HTTPBasicAuth(user, passw))
#  print(response.content)
# token = response.json()['token']
# return token


# GET returns
@app.route('/')
def hello_world():
    json.dumps(userdata)
    return json.dumps(userdata)


# POST delivers heroclass, capabilities, url
# TODO dynamic IP
def get_ip():
    return '172.19.0.63'


def register_at_tavern():
    print("register at tavern:")
    ip = get_ip()
    # TODO endpoint jaume erstellen
    # TODO IP eintragen in /users/Jaume
    url = ip + '/jaume'
    json_data = {'heroclass': 'Catalonian Chiller', 'capabilities': '', 'url': '' + url}
    taverna_url = 'http://172.19.0.3:5000/taverna/adventurers'
    response = requests.post(url=taverna_url, headers=HEADER_APPL_JSON, json=json_data,
                             auth=HTTPBasicAuth("Jaume", "Jaume"))
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

    DISCOVERED_PORT = port['blackboard_port']
    global DISCOVERED_PORT

    sourceip, sourceport = addr

    BLACKBOARD_IP = sourceip
    global BLACKBOARD_IP

    # assemble the whole blackboard URL with port and trailing "/"
    BLACKBOARD_URL = BLACKBOARD_IP + ":" + DISCOVERED_PORT + "/"
    global BLACKBOARD_URL
    print("adress: " + str(addr))


def create_group():
    # in case of creating a group, data is empty. The hint was "watch the location header"... TODO investigate that!
    data = ""
    requests.post(BLACKBOARD_URL, data)


def main():
    print("HEJEHEHEHEJEHEJEH")
    # discovery()
    # global DISCOVERED_IP
    # DISCOVERED_IP = 'http://' + str(BLACKBOARD_IP) + ':' + str(DISCOVERED_PORT)
    # print(DISCOVERED_IP)
    register_at_tavern()


main()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
