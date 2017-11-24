from flask import Flask, request, make_response
import json
import requests
import socket
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

HEADER_APPL_JSON = {'content-type': 'application/json; charset=UTF-8'}

# A global variable to manage the hirings
HIRINGS = []
GROUP_MEMBERS = [{'name': 'Arne', 'url': 'url'}, {'name': 'Jerom', 'url': 'url'}]

# TODO do a research on how to use URIs (or what's meant here)
# userdata_user = "'user': '/users/Jaume',"
# userdata_idle = "'idle': False,"
# userdata_group = "'group': None,"
# userdata_hirings = "'hirings': '/hirings',"
# userdata_assignments = "'assignments': 'assignments',"
# userdata_messages = "'messages': '/messages'"
#
# userdata = {
# userdata_user + userdata_idle + userdata_group + userdata_hirings + userdata_assignments + userdata_messages}


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
def return_userdata():
    json.dumps(userdata)
    return json.dumps(userdata)


def check_hiring_data(request_data):
    # Are the keys given correct?
    group = request_data['group']
    quest = request_data['quest']
    message = request_data['message']
    # how many keys are there? > 3 raises an ERROR (caught in post_hiring())
    amount_of_keys = len(dict(request_data).keys())
    if amount_of_keys > 3:
        raise KeyError


@app.route('/hirings', methods=['POST'])
def post_hiring():
    if request.method == 'POST':
        request_data = json.loads(request.data)
        try:
            check_hiring_data(request_data)

        except KeyError:
            bad_request_response = make_response("The body needs to exactly contain the following keys: group, quest, "
                                                 "message", 400)
            return bad_request_response
        # HIRINGS are stored as dicts
        list.append(HIRINGS, request_data)
        print("actual value of HIRINGS: " + str(HIRINGS))
        response = make_response("Hiring posted successfully", 200)
        return response
    else:
        print("There is only a POST allowed here.")
        not_allowed_response = make_response(405)
        return not_allowed_response


# TODO dynamic IP
def get_ip():
    return 'http://172.19.0.63:80'


# POST delivers heroclass, capabilities, url
def register_at_tavern():
    print("register at tavern:")
    ip = get_ip()
    # TODO endpoint jaume erstellen
    # TODO IP eintragen in /users/Jaume
    url = ip + '/'
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

    global DISCOVERED_PORT
    DISCOVERED_PORT = port['blackboard_port']

    sourceip, sourceport = addr

    global BLACKBOARD_IP
    BLACKBOARD_IP = sourceip

    # assemble the whole blackboard URL with port and trailing "/"
    global BLACKBOARD_URL
    BLACKBOARD_URL = BLACKBOARD_IP + ":" + DISCOVERED_PORT + "/"
    print("adress: " + str(addr))


def create_group():
    # in case of creating a group, data is empty. The hint was "watch the location header"... TODO investigate that!
    data = ""
    requests.post(BLACKBOARD_URL, data)

    #####################Bully Algorithm########################

def bully():
        send_election()


def send_election():
        # throw exception if there are no bigger ones or if nobody is answering
        for member in GROUP_MEMBERS:
            if (member['name'] > 'Jaume'):
                #TODO: Send
                print member['name']

        #response = requests.post("http://0.0.0.0:80/election", {'payload': 'election'})

@app.route('/election', methods=['POST'])
def election():
    if request.data['payload'] == 'election':
        return request.data


#     @app.route('/hirings', methods=['POST'])
#     def post_hiring():
#         if request.method == 'POST':
#             request_data = json.loads(request.data)
#             try:
#                 check_hiring_data(request_data)
#
#             except KeyError:
#                 bad_request_response = make_response(
#                     "The body needs to exactly contain the following keys: group, quest, "
#                     "message", 400)
#                 return bad_request_response
#             # HIRINGS are stored as dicts
#             list.append(HIRINGS, request_data)
#             print("actual value of HIRINGS: " + str(HIRINGS))
#             response = make_response("Hiring posted successfully", 200)
#             return response
#         else:
#             print("There is only a POST allowed here.")
#             not_allowed_response = make_response(405)
#             return not_allowed_response


def main():
    print("HEJEHEHEHEJEHEJEH")
    # discovery()
    # global DISCOVERED_IP
    # DISCOVERED_IP = 'http://' + str(BLACKBOARD_IP) + ':' + str(DISCOVERED_PORT)
    # print(DISCOVERED_IP)
    # register_at_tavern()
    #bully()


main()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)




