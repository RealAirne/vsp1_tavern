import json
import socket
import requests
from requests.auth import HTTPBasicAuth

username = "Jaume"
password = "Jaume"


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
    BLACKBOARD_URL = str(BLACKBOARD_IP) + ":" + str(DISCOVERED_PORT) + "/"
    print("adress: " + str(addr))


def create_group():
    # in case of creating a group, data is empty. The hint was "watch the location header"... TODO investigate that!
    data = ""
    reply = requests.post(BLACKBOARD_URL, data)
    return reply
# {
#     "message": "Created Group",
#     "object": [
#         {
#             "_links": {
#                 "members": "/taverna/groups/55/members", TODO moegliche Verwechsungen!!
#                 "self": "/taverna/groups/55"
#             },
#             "id": 55,
#             "members": [],
#             "owner": "Jaume"
#         }
#     ],
#     "status": "success"
# }


def extract_member_url(json_var):
    object_var = json_var['object'][1]
    links = object_var['_links']
    members_url = links['members']
    group_url = links['self']
    return members_url, group_url


def main():
    discovery()
    # Create a new group
    group_reply = create_group()
    group_status = group_reply.status_code
    print("group_status: " + group_status)

    # gather the information from the group_request to obtain the member_url and join it
    reply_as_json = group_reply.request.get_json()
    member_url, group_url = extract_member_url(reply_as_json)

    #TODO find Jaume and send him an invite him (sending member_url), quest und message sind prototypen
    hiring_data = {"group": group_url, "quest": "pi", "message": "many danks"}
    jaume_reply = requests.post("172.19.0.81/hirings", json.dumps(hiring_data))
    jaume_status = jaume_reply.status_code
    print("Jaume Status: " + jaume_status)

main()
